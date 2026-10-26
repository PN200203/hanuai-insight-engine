# Task 1 Report: Scraping Challenges & Customer-Insight Summary

> **Status of numbers:** the build environment had no internet access, so the BestBuy.ca scrape was **not executed here**.
> The insight section below is therefore a *ready-to-fill template plus a demo run on synthetic data*. After you run
> `python -m task1_voice_of_customer.src.run_pipeline --api` (or the notebook with `RUN_LIVE=True`) on a connected machine,
> `reports/insights.md` is regenerated automatically from the real reviews - paste it into section 2.

## 1. Solution for scraping challenges

| Challenge | What the code does (`src/resilience.py`, `src/scraper.py`) | Further options at scale |
|---|---|---|
| Must stay within site policy | Reads `robots.txt` first and **stops** if the path is disallowed; only public fields collected; no login | Check ToS/legal; ask BestBuy for a partner data feed or use a licensed review-syndication provider |
| Dynamic "Show More" loading | Strategy A calls the same JSON endpoint the page uses, page by page (lighter than a browser); Strategy B uses Selenium to click *Show More* until it vanishes | Playwright for more stable waits |
| Cap on reviews per sort order | Re-runs under **5 filters** (Relevant, Helpful, Newest, Highest, Lowest) and merges; de-duplicates on review ID so each review appears once, with the list of filters that surfaced it | Add rating-star and "verified purchase" sub-filters |
| Rate limiting / HTTP 429 | Jittered 2-5 s delay, exponential backoff, session/User-Agent reset on 403/429/5xx, hard page cap | Lower concurrency; schedule off-peak |
| IP blocking | Optional proxy pool (`config.PROXIES`) rotated on each identity reset | Residential/rotating proxy provider; run from a few stable IPs rather than hundreds |
| CAPTCHA | **Detect and stop** (retries exhaust, run ends with partial data saved) | Reduce request rate so it is not triggered; use an official API. Automated CAPTCHA solving is deliberately *not* implemented - it circumvents access controls |
| Layout / selector changes | Text-based XPaths, tolerant JSON key mapping | Selector health-check test + alert when review count drops to 0 |
| Re-runs & resumability | Idempotent de-dup; raw CSV saved before analysis | Incremental scrape of "Newest" only, on a schedule |

## 2. Customer insights (fill from real run)

Structure the stakeholder summary as follows - each item is auto-computed in `insights.md`:

1. **Headline:** review count, mean rating, positive/neutral/negative mix.
2. **Top satisfaction drivers:** aspects with highest net sentiment and enough mentions (>= 5).
3. **Top dissatisfaction drivers:** aspects with lowest net sentiment, plus aspects most cited in 1-2 star reviews.
4. **Time view:** has sentiment on a driver moved in the last 3-6 months (firmware / batch change)?
5. **Recommendations:** protect and market the strengths; open root-cause tickets for the weakest aspects (QA plan, supplier audit, firmware/app fix, packaging/support scripts); track net sentiment per aspect monthly as a KPI.

### Demo run (SYNTHETIC reviews - format illustration only)
See `reports/insights_DEMO.md` and `reports/aspect_net_sentiment_DEMO.png`. The synthetic set shows Sound Quality and
App & Controls as strengths and Durability & Defects / Battery Life as weaknesses *because the generator was written that way*;
these are **not findings about any real product**.

## 3. Method notes & limitations
- **Sentiment model:** transparent aspect-based lexicon (negation, intensifiers) blended with star rating. Strength: explainable, matches the required `['Aspect (Pos)']` output. Weakness: sarcasm, domain slang, and misspellings. Upgrade path: `sentiment.transformer_overall()` (RoBERTa) or an LLM with a fixed aspect schema, validated against ~200 hand-labelled reviews.
- **Selection bias:** reviews skew to extremes and to verified buyers; read trends, not absolutes.
- **Validate before presenting:** hand-check 50 random tagged reviews and report accuracy.
