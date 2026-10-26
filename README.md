# HanuAI Insight Engine - ML Assessment (Tasks 1 & 2)

Two self-contained pipelines that share one philosophy: **raw text -> structured tags -> counted, ranked, explained insights.**

```
hanuai-insight-engine/
├── README.md
├── requirements.txt
├── tools/build_notebooks.py                 # regenerates both .ipynb files
├── task1_voice_of_customer/                 # BestBuy.ca reviews -> aspect sentiment
│   ├── src/  config.py  resilience.py  scraper.py  sentiment.py  report_builder.py  sample_data.py  run_pipeline.py
│   ├── notebooks/01_scrape_and_sentiment.ipynb        # DELIVERABLE 1 (commented)
│   ├── data/raw/  data/processed/reviews_sentiment*.csv|xlsx   # DELIVERABLE 2
│   └── reports/Task1_Report.md  insights*.md  *.png   # DELIVERABLE 3
└── task2_field_failure_intelligence/        # failure logs -> tags -> clusters -> root causes
    ├── src/  eda.py  textmining.py  topics.py  run_pipeline.py  sample_data.py
    ├── notebooks/02_eda_text_mining.ipynb             # DELIVERABLE 1 (commented)
    ├── data/raw/  data/processed/mined_tags*.xlsx     # DELIVERABLE 2 (8 sheets)
    └── reports/Task2_Report.md  auto_insights*.md  figures/*.png   # DELIVERABLE 3
```

## Run
```bash
pip install -r requirements.txt
# Task 2: copy the assessment Excel into task2_field_failure_intelligence/data/raw/ then
python -m task2_field_failure_intelligence.src.run_pipeline
# Task 1: edit task1_voice_of_customer/src/config.py (SKU, URL, verify API template in DevTools), then on a connected machine
python -m task1_voice_of_customer.src.run_pipeline --api        # or --selenium
python -m task1_voice_of_customer.src.run_pipeline --demo       # offline format check
```

## Honest status
| Item | Status |
|---|---|
| Task 1 sentiment, aspect table, exports, report generator | Built and **run on synthetic demo reviews** (`*_DEMO` files) |
| Task 1 live scraping | **Written but NOT executed** - no internet in the build sandbox. The JSON endpoint template in `config.py` is an *unverified best guess*; confirm it (or use the Selenium path, whose selectors may also need tweaks). Must run on your machine; needs >= 50 reviews |
| Task 2 | Built and run end-to-end, but on a **synthetic dataset** because the assessment Excel wasn't provided. Drop in the real file and re-run |
| Notebooks | Code cells verified by executing them in order; not run through Jupyter itself |
| Reports | Markdown; numbers in Task 2 are demo numbers; Task 1 insights get filled by the live run |
