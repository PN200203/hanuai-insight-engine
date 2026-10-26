"""Generates the two .ipynb files (keeps notebooks reproducible & diff-friendly)."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]

def nb(cells):
    out = []
    for kind, src in cells:
        c = {"cell_type": kind, "metadata": {}, "source": src.strip("\n").splitlines(True)}
        if kind == "code": c.update(execution_count=None, outputs=[])
        out.append(c)
    return {"cells": out, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}

T1 = [
("markdown", """# Task 1 - Voice of Customer: BestBuy.ca scraping + aspect-based sentiment
**Flow:** compliance check -> scrape (API-first, Selenium fallback) -> clean -> aspect sentiment -> insights -> export.
Set `RUN_LIVE = True` on a machine with internet access; otherwise the notebook runs on clearly-labelled SYNTHETIC demo reviews."""),
("code", """
# --- Setup: make the project's src package importable from the notebook ---
import sys, pathlib; sys.path.insert(0, str(pathlib.Path.cwd().parents[1]))
import pandas as pd, matplotlib.pyplot as plt
from task1_voice_of_customer.src import config as C, scraper, sentiment
from task1_voice_of_customer.src.resilience import robots_allows
from task1_voice_of_customer.src.sample_data import make_demo
from task1_voice_of_customer.src.report_builder import build_insights
pd.set_option("display.max_colwidth", 80)
"""),
("markdown", "## 1. Scraping\nEdit `src/config.py` (product URL + SKU, API template) first. Strategy A calls the site's own JSON endpoint once per filter (Most Relevant / Most Helpful / Newest / Highest / Lowest) and merges + de-duplicates; Strategy B clicks *Show More* with Selenium."),
("code", """
RUN_LIVE = False          # <-- set True when you have internet + a real SKU configured
STRATEGY = "api"          # "api" (preferred) or "selenium" (fallback)

if RUN_LIVE:
    # Compliance first: robots.txt must allow the path, else we stop (never work around it).
    assert robots_allows("/en-ca/product/"), "robots.txt disallows this path - do not scrape"
    raw = scraper.scrape_via_api() if STRATEGY == "api" else scraper.scrape_via_selenium()
    demo = False
else:
    raw = make_demo(); demo = True      # SYNTHETIC rows, source='SYNTHETIC-DEMO'
print(len(raw), "unique reviews;", "need >= 50 for the assignment")
raw.head()
"""),
("code", """
# --- Data quality checks before modelling ---
print(raw.isna().mean().round(3))                         # missing values per field
print("duplicates:", raw.duplicated("review_id").sum())    # should be 0 after finalize()
print(raw["rating"].value_counts().sort_index())           # rating distribution (1-5)
raw["date"].min(), raw["date"].max()                       # YYYY-MM-DD as required
"""),
("markdown", "## 2. Sentiment categorisation\nAspect-based: every review gets tags like `Battery Life (Neg)` plus an overall label (text score blended with the star rating). See `src/sentiment.py` for the lexicon, negation and intensifier handling."),
("code", """
res = sentiment.run_sentiment(raw)
res[["review_id", "title", "review_text", "overall_sentiment", "sentiment_tags_str"]].head(8)
"""),
("code", """
# Aspect x polarity table: the base for every business insight
at = sentiment.aspect_table(res)
display(at) if "display" in globals() else print(at)
# Sanity check: does text sentiment agree with stars? (should rise with rating)
print(res.groupby("rating")["text_score"].mean().round(2))
"""),
("code", """
at.sort_values("net_sentiment")["net_sentiment"].plot.barh(color=["#c0392b" if v < 0 else "#2e8b57" for v in at.sort_values("net_sentiment").net_sentiment])
plt.title("Net sentiment by aspect" + (" (SYNTHETIC DEMO)" if demo else "")); plt.tight_layout(); plt.show()
"""),
("markdown", "## 3. Business insights + export"),
("code", """
print(build_insights(res, demo))
tag = "_DEMO" if demo else ""
cols = ["review_id", "title", "review_text", "date", "rating", "source", "reviewer_name", "overall_sentiment", "sentiment_tags_str"]
res[cols].to_csv(C.PROC_DIR / f"reviews_sentiment{tag}.csv", index=False)      # deliverable 2
"""),
("markdown", """## 4. Anti-blocking cheat-sheet (implemented in `src/resilience.py`)
robots.txt check - jittered delays - UA rotation - optional proxy pool - exponential backoff + identity reset on 403/429/5xx - hard page cap - de-dup so re-runs are idempotent. **Not implemented on purpose:** CAPTCHA solving / fingerprint spoofing (violates site terms)."""),
]

T2 = [
("markdown", """# Task 2 - Advanced EDA + Text Mining of field failures
**Flow:** load -> profile -> clean (logged) -> detect free-text -> extract tags -> categorise issues -> cluster/topic-model -> trends -> root-cause screen -> export.
Put the assessment Excel in `data/raw/`; with no file present the notebook uses a SYNTHETIC demo set."""),
("code", """
import sys, pathlib; sys.path.insert(0, str(pathlib.Path.cwd().parents[1]))
import pandas as pd, matplotlib.pyplot as plt
from task2_field_failure_intelligence.src import eda, textmining as tm, topics
from task2_field_failure_intelligence.src.sample_data import make_failures
from task2_field_failure_intelligence.src.run_pipeline import RAW, PROC, FIG, find_cols, trends
files = [f for f in RAW.glob("*") if f.suffix.lower() in (".xlsx", ".xls", ".csv") and "SYNTHETIC" not in f.name]
demo = not files
raw = make_failures() if demo else eda.load_any(files[0])
print("DEMO DATA" if demo else files[0].name, raw.shape)
"""),
("markdown", "## 1. EDA - types, volume, per-column characteristics"),
("code", """
prof = eda.profile(raw); prof          # dtype, missing %, cardinality, sample, automatic free-text flag
"""),
("code", """
# Cleaning is a function that RETURNS A LOG, so every fix is auditable in the report.
d, log = eda.clean(raw); print(log)
eda.plot_eda(d, FIG)                   # distributions of numeric KPIs + counts of categorical fields (saved to reports/figures)
d.describe().round(2)
"""),
("markdown", "## 2. Text mining - unstructured -> structured"),
("code", """
date_col, text_cols, num_cols = find_cols(d); print("free text:", text_cols, "| date:", date_col)
print("vocabulary the dictionaries may be missing:", tm.expand_lexicon(d[text_cols[0]]))
m = tm.mine(d, text_cols)             # adds components / symptoms / actions / conditions / part_numbers / error_codes / issue_category
m["primary_condition"] = m["conditions"].map(lambda l: l[0] if l else "Unknown")
m[text_cols + ["components_str", "symptoms_str", "actions_str", "conditions_str", "issue_category"]].head(8)
"""),
("code", """
# Extraction coverage = how much of the free text we managed to structure (report this honestly)
print("rows with a component:", (m.primary_component != "Unknown").mean().round(3), "| with a symptom:", (m.primary_symptom != "Unknown").mean().round(3))
m["issue_category"].value_counts()
"""),
("markdown", "## 3. Patterns, clusters, topics"),
("code", """
piv, chg = trends(m, date_col); piv.plot(figsize=(9, 4), marker="o", ms=3); plt.title("Monthly failures by category"); plt.show(); chg
"""),
("code", """
m["cluster_id"], k, ctop, sil = topics.cluster_failures(m, text_cols); print("k =", k, "silhouette =", round(sil, 3)); print(ctop)
m["nmf_topic"], ntop = topics.nmf_topics(m, text_cols); print(ntop)
"""),
("markdown", "## 4. Root-cause screening\nLift = how over-represented an outcome is inside a driver group. `actionable` = lift >= 1.3 AND chi-square p < 0.05. This shows **association**, not proof - hand candidates to engineering for confirmation."),
("code", """
drv = [c for c in ("product_model", "region", "primary_condition") if c in m]
rc = pd.concat([topics.root_cause_screen(m, outcome=o, drivers=drv) for o in ("primary_component", "issue_category")]).sort_values("lift", ascending=False)
rc.head(12)
"""),
("code", """
tag = "_SYNTHETIC_DEMO" if demo else ""
keep = [c for c in m.columns if c.endswith("_str")] + ["primary_component", "primary_symptom", "primary_condition", "issue_category", "cluster_id", "nmf_topic"]
m[list(d.columns) + keep].loc[:, lambda x: ~x.columns.duplicated()].to_excel(PROC / f"notebook_tags{tag}.xlsx", index=False)   # deliverable 2
"""),
]
(ROOT / "task1_voice_of_customer/notebooks/01_scrape_and_sentiment.ipynb").write_text(json.dumps(nb(T1), indent=1))
(ROOT / "task2_field_failure_intelligence/notebooks/02_eda_text_mining.ipynb").write_text(json.dumps(nb(T2), indent=1))
print("notebooks written")
