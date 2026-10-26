"""CLI:  python -m task2_field_failure_intelligence.src.run_pipeline [--input path.xlsx]
Without --input it uses the first file in data/raw/, else the SYNTHETIC demo set."""
import argparse
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns
from . import eda, textmining as tm, topics
from .sample_data import make_failures

ROOT = Path(__file__).resolve().parents[1]; RAW, PROC, REP = ROOT / "data/raw", ROOT / "data/processed", ROOT / "reports"
FIG = REP / "figures"

def find_cols(d):
    """Auto-detect: date column, free-text columns, numeric KPI columns."""
    prof = eda.profile(d)
    return (next((c for c in d if "date" in c.lower()), None), list(prof[prof.is_free_text].column),
            [c for c in d.select_dtypes("number") if not c.endswith("_was_missing")])

def trends(d, date_col):
    """Monthly counts of each issue category + recent-vs-baseline change (last 3 months vs prior 3 months)."""
    m = d.dropna(subset=[date_col]).assign(month=lambda x: x[date_col].dt.to_period("M").dt.to_timestamp())
    piv = m.pivot_table(index="month", columns="issue_category", values=m.columns[0], aggfunc="size", fill_value=0)
    last, prev = piv.tail(3).sum(), piv.iloc[-6:-3].sum()
    chg = pd.DataFrame({"prev_3m": prev, "last_3m": last}); chg["change_%"] = ((chg.last_3m - chg.prev_3m) / chg.prev_3m.replace(0, np.nan) * 100).round(1)
    return piv, chg.sort_values("change_%", ascending=False)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--input"); a = ap.parse_args()
    for p in (PROC, FIG): p.mkdir(parents=True, exist_ok=True)
    files = [f for f in RAW.glob("*") if f.suffix.lower() in (".xlsx", ".xls", ".csv") and "SYNTHETIC" not in f.name]
    src = a.input or (files[0] if files else None)
    demo = src is None
    raw = make_failures() if demo else eda.load_any(src)
    if demo: raw.to_csv(RAW / "failures_SYNTHETIC_DEMO.csv", index=False)
    prof = eda.profile(raw); d, log = eda.clean(raw); date_col, text_cols, num_cols = find_cols(d)
    print("free-text columns:", text_cols, "| date:", date_col)
    eda.plot_eda(d, FIG)
    m = tm.mine(d, text_cols); m["primary_condition"] = m["conditions"].map(lambda l: l[0] if l else "Unknown")
    m["cluster_id"], k, ctop, sil = topics.cluster_failures(m, text_cols)
    m["cluster_label"] = m["cluster_id"].map(ctop); m["nmf_topic"], ntop = topics.nmf_topics(m, text_cols)
    # Drivers are *context* variables only (model / region / operating condition). Using symptom as a driver of
    # component would be circular (a 'blank screen' obviously implies a display), so it is excluded on purpose.
    drv = [c for c in ("product_model", "region", "primary_condition") if c in m]
    rc = pd.concat([topics.root_cause_screen(m, outcome=o, drivers=drv) for o in ("primary_component", "issue_category")]).sort_values("lift", ascending=False)
    piv, chg = trends(m, date_col) if date_col else (None, None)

    # ---- charts
    top = m["issue_category"].value_counts(); plt.figure(figsize=(7, 4)); top[::-1].plot.barh(color="#b5442e"); plt.title("Failures by issue category"); plt.tight_layout(); plt.savefig(FIG / "03_issue_categories.png", dpi=120); plt.close()
    plt.figure(figsize=(8, 4)); m["primary_component"].value_counts().head(10)[::-1].plot.barh(color="#3b6ea5"); plt.title("Top failing components"); plt.tight_layout(); plt.savefig(FIG / "04_top_components.png", dpi=120); plt.close()
    if piv is not None: piv.plot(figsize=(9, 4.5), marker="o", ms=3); plt.title("Monthly failures by issue category"); plt.legend(fontsize=7, loc="upper left", bbox_to_anchor=(1, 1)); plt.tight_layout(); plt.savefig(FIG / "05_monthly_trend.png", dpi=120); plt.close()
    if "product_model" in m: sns.heatmap(pd.crosstab(m.primary_component, m.product_model), annot=True, fmt="d", cmap="Reds"); plt.title("Component failures x product model"); plt.tight_layout(); plt.savefig(FIG / "06_component_x_model.png", dpi=120); plt.close()

    # ---- deliverable workbook
    tag = "_SYNTHETIC_DEMO" if demo else ""
    keep = [c for c in m.columns if c.endswith("_str")] + ["primary_component", "primary_symptom", "primary_condition", "issue_category", "cluster_id", "cluster_label", "nmf_topic"]
    with pd.ExcelWriter(PROC / f"mined_tags{tag}.xlsx") as xw:
        m[[c for c in m.columns if c not in keep or c in ("primary_component",)][:len(d.columns)] + keep].drop(columns=["components", "symptoms", "actions", "conditions", "part_numbers", "error_codes"], errors="ignore").loc[:, lambda x: ~x.columns.duplicated()].to_excel(xw, sheet_name="Records+Tags", index=False)
        prof.to_excel(xw, sheet_name="Data profile", index=False); log.to_excel(xw, sheet_name="Cleaning log", index=False)
        top.rename("count").to_frame().to_excel(xw, sheet_name="Issue categories")
        pd.DataFrame({"cluster": list(ctop), "top_terms": list(ctop.values()), "size": m.cluster_id.value_counts().sort_index().values}).to_excel(xw, sheet_name="Clusters", index=False)
        pd.DataFrame({"topic": list(ntop), "terms": list(ntop.values())}).to_excel(xw, sheet_name="NMF topics", index=False)
        rc.head(40).to_excel(xw, sheet_name="Root-cause screen", index=False)
        if chg is not None: chg.to_excel(xw, sheet_name="Trend change")
    # ---- insight text (numbers computed, never typed)
    L = [("> WARNING: SYNTHETIC demo data - illustrates the format only.\n" if demo else ""), f"Rows after cleaning: **{len(d)}** (raw {len(raw)}). Clusters: **k={k}** (silhouette {sil:.2f}).",
         "\n**Top issue categories**\n" + top.head(5).to_markdown(), "\n**Top components**\n" + m.primary_component.value_counts().head(5).to_markdown(),
         "\n**Strongest root-cause candidates (lift)**\n" + rc.head(8).to_markdown(index=False)]
    if chg is not None: L.append("\n**Recent 3-month change by category**\n" + chg.to_markdown())
    for c in ("downtime_hours", "repair_cost"):
        if c in m: L.append(f"\n**{c} by issue category (mean)**\n" + m.groupby("issue_category")[c].mean().round(1).sort_values(ascending=False).to_markdown())
    (REP / f"auto_insights{tag}.md").write_text("\n".join(L)); print("\n".join(L))

if __name__ == "__main__":
    main()
