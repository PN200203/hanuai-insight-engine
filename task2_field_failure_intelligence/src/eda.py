"""Part 1 - EDA: profile, detect problems, fix them (and log every fix)."""
import re
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns

def load_any(path):
    p = str(path)
    return pd.read_excel(p) if p.lower().endswith((".xlsx", ".xls")) else pd.read_csv(p)

def _is_texty(s: pd.Series) -> bool:
    """Dtype-agnostic 'is this a string column' (works for object, string[python] and pandas>=3 str)."""
    return not (pd.api.types.is_numeric_dtype(s) or pd.api.types.is_datetime64_any_dtype(s) or pd.api.types.is_bool_dtype(s))

def _text_like(d: pd.DataFrame):
    return [c for c in d if _is_texty(d[c])]

def profile(df: pd.DataFrame) -> pd.DataFrame:
    """One row per column: dtype, missing %, unique count, sample, and an automatic free-text flag."""
    rows = []
    for c in df.columns:
        s = df[c]; txt = _is_texty(s) and s.dropna().astype(str).str.split().str.len().mean() >= 5 if s.dropna().size else False
        rows.append({"column": c, "dtype": str(s.dtype), "missing_%": round(s.isna().mean() * 100, 1), "unique": s.nunique(),
                     "sample": str(s.dropna().iloc[0])[:60] if s.dropna().size else "", "is_free_text": bool(txt)})
    return pd.DataFrame(rows)

def clean(df: pd.DataFrame):
    """Returns (clean_df, log). Each step records how many rows/cells it touched."""
    log, d = [], df.copy()
    n = len(d); d = d.drop_duplicates(); log.append(("exact duplicate rows removed", n - len(d)))
    for c in _text_like(d):                                        # trim + normalise categorical labels
        if d[c].nunique() < 30 and "date" not in c.lower(): d[c] = d[c].astype("string").str.strip().str.title()
    for c in d.columns:                                                         # parse dates
        if "date" in c.lower():
            parsed = pd.to_datetime(d[c], errors="coerce"); log.append((f"unparseable '{c}' values -> NaT", int(parsed.isna().sum() - d[c].isna().sum()))); d[c] = parsed
    for c in d.select_dtypes("number"):                                        # impossible negatives -> NaN, then median impute
        bad = (d[c] < 0).sum()
        if bad: d.loc[d[c] < 0, c] = np.nan; log.append((f"negative '{c}' set to NaN", int(bad)))
        miss = d[c].isna().sum()
        if miss: d[c + "_was_missing"] = d[c].isna(); d[c] = d[c].fillna(d[c].median()); log.append((f"'{c}' median-imputed (flag col added)", int(miss)))
    for c in _text_like(d):                                                     # categorical gaps stay explicit
        if d[c].isna().any() and d[c].nunique() < 30: log.append((f"'{c}' blanks -> 'Unknown'", int(d[c].isna().sum()))); d[c] = d[c].fillna("Unknown")
    return d.reset_index(drop=True), pd.DataFrame(log, columns=["step", "rows_or_cells"])

def plot_eda(d: pd.DataFrame, out):
    sns.set_theme(style="whitegrid"); out.mkdir(parents=True, exist_ok=True)
    nums = [c for c in d.select_dtypes("number") if not c.endswith("_was_missing")]
    fig, ax = plt.subplots(1, len(nums), figsize=(5 * len(nums), 3.5))
    for a, c in zip(np.atleast_1d(ax), nums): sns.histplot(d[c], kde=True, ax=a); a.set_title(f"Distribution: {c}")
    plt.tight_layout(); plt.savefig(out / "01_numeric_distributions.png", dpi=120); plt.close()
    cats = [c for c in _text_like(d) if 1 < d[c].nunique() < 15]
    fig, ax = plt.subplots(1, len(cats), figsize=(4.5 * len(cats), 3.5))
    for a, c in zip(np.atleast_1d(ax), cats): d[c].value_counts().plot.barh(ax=a, color="#3b6ea5"); a.set_title(c)
    plt.tight_layout(); plt.savefig(out / "02_categorical_counts.png", dpi=120); plt.close()
