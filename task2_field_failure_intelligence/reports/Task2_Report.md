# Task 2 Report: Advanced EDA & Text Mining

> **Status of numbers:** the assessment Excel file was **not available** when this project was built, so every number below
> comes from a **synthetic** failure log that mimics typical service data (planted patterns: an RX-300 battery issue,
> messy labels, duplicates, missing values). Re-run on the real file (`data/raw/`) and the tables below regenerate in
> `reports/auto_insights.md`. Treat the demo numbers as proof the *method works*, not as business findings.

## 1. Synthesis of the data & potential value
- **Shape:** 1,230 raw rows, 9 columns -> 1,202 after cleaning (28 exact duplicates removed). One free-text column (`technician_notes`) holds the most diagnostic information; structured columns (model, region, cost, downtime) provide context.
- **Quality issues found & fixed (all logged in the `Cleaning log` sheet):** duplicates; inconsistent labels (`high`/`HIGH`/`High`, `south `/`South`); unparseable dates (10); impossible negative downtimes (12 -> NaN); missing cost (36) and downtime values median-imputed with `*_was_missing` flags so imputation is traceable; blank severity kept explicit as `Unknown` rather than guessed.
- **Value for the customer:** turns thousands of unread notes into a searchable, countable failure taxonomy, so quality teams can rank failure modes by frequency *and* cost, see which product models/conditions over-index, and spot emerging issues months earlier than manual review.

## 2. Text mining
- **Free-text detection:** automatic (mean >= 5 words per value) -> `technician_notes`.
- **Entities extracted:** component, symptom, action taken, operating condition, part number, error code (regex + dictionaries that are expanded from the data via frequent phrases; LLM fallback hook provided in `llm_extract`).
- **Coverage:** ~96% of rows yielded a component and ~93% a symptom (remaining rows had empty notes).
- **Issue categories:** Electrical, Energy Storage (Battery), Thermal, Leakage/Fluid, Mechanical Wear, Sensor/Calibration, Display/UI, Corrosion. Categories are assigned from *what failed* only; operating conditions are excluded on purpose so they can serve as independent explanatory variables.
- **Clustering/topics:** TF-IDF + KMeans (k chosen by silhouette, k=9, silhouette ~0.25) and NMF (6 topics). Clusters align with component families (battery pack, motor/bearing, control board, wiring harness, pump/hydraulic, sensor, connector, display) - a useful sanity check that mined tags and unsupervised structure agree. A low silhouette is expected for short, formulaic notes.

## 3. Patterns, trends and root-cause candidates (demo data)
- **Most frequent:** Electrical (271 records), then Energy Storage, Mechanical, Thermal (~171-173 each); `battery pack` is the single most failing component (301, ~25%).
- **Recent 3-month change** (last 3 vs previous 3 months): Leakage/Fluid +33%, Sensor -48% - small counts, so flagged as *watch*, not conclusions.
- **Root-cause screen:** only one candidate survives a Bonferroni-corrected, cell-level Fisher test: **model RX-300 x battery pack failures (lift ~1.9x, p_adj ~1e-18)**. Several tempting associations (e.g. "under full load" and pumps, lift 1.6) did **not** survive correction and are reported as hypotheses only.
- **Two analysis bugs caught and fixed during the build** (worth stating to stakeholders because they change conclusions): (1) category rules originally used operating conditions, which made "heavy rain -> corrosion" look real when it was circular; (2) missing-note rows were "Unknown" on both axes, creating a fake dependence in the chi-square test.

## 4. Actionable recommendations & business impact
| # | Action | Evidence | Expected impact |
|---|---|---|---|
| 1 | Open a design/supplier investigation on the RX-300 battery pack (cell lot, BMS thermal limits) | Lift 1.9x, statistically robust; battery tickets also show the highest mean downtime (6.8h vs 6.0-6.5h elsewhere - a small gap in the demo data, so verify on real data) | Largest single reduction in repeat failures, warranty cost and downtime |
| 2 | Add a pre-delivery thermal/charge-cycle test for battery packs; monitor `overheating` mentions monthly | Overheating symptom concentrated in battery + motor | Safety risk reduction; earlier escape detection |
| 3 | Standardise technician note entry (dropdown for component + symptom, free text for detail) | 4% empty notes; ~7% rows with no extractable symptom | Cleaner analytics, faster triage |
| 4 | Track Leakage/Fluid trend; inspect hose/pump supplier batches if increase persists 2 more months | +33% recent change (small n) | Early warning before it becomes a top-3 category |
| 5 | Stand up a monthly dashboard: top categories, lift table, cost & downtime by category | All sheets in `mined_tags.xlsx` | Moves from reactive to proactive quality management |

## 5. Key learnings & next improvements
- Always **log cleaning decisions** and avoid circular features - two such errors were found only by sanity-checking results.
- Report **extraction coverage** and validate tags on a hand-labelled sample (target >= 90% precision) before trusting counts.
- Next: (a) swap/augment rules with an open-source LLM (e.g. Llama 3 via Ollama) for rows with no rule match, with a fixed JSON schema; (b) sentence-embedding clustering (e.g. `all-MiniLM`) to catch paraphrases; (c) survival / time-to-failure analysis if install dates exist; (d) cost-weighted Pareto charts; (e) anomaly alerts on weekly category counts.
