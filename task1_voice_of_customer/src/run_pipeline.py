"""CLI:  python -m task1_voice_of_customer.src.run_pipeline [--demo | --api | --selenium]"""
import argparse, logging
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from . import config as C, scraper
from .sentiment import run_sentiment, aspect_table
from .sample_data import make_demo
from .report_builder import build_insights

def main():
    ap = argparse.ArgumentParser(); g = ap.add_mutually_exclusive_group()
    g.add_argument("--demo", action="store_true"); g.add_argument("--api", action="store_true"); g.add_argument("--selenium", action="store_true")
    a = ap.parse_args(); logging.basicConfig(level=logging.INFO)
    C.RAW_DIR.mkdir(parents=True, exist_ok=True); C.PROC_DIR.mkdir(parents=True, exist_ok=True)
    demo = a.demo or not (a.api or a.selenium)
    df = make_demo() if demo else (scraper.scrape_via_api() if a.api else scraper.scrape_via_selenium())
    df.to_csv(C.RAW_DIR / ("reviews_raw_DEMO.csv" if demo else "reviews_raw.csv"), index=False)
    res = run_sentiment(df)
    cols = ["review_id", "title", "review_text", "date", "rating", "source", "reviewer_name", "overall_sentiment", "sentiment_tags_str"]
    tag = "_DEMO" if demo else ""
    res[cols].to_csv(C.PROC_DIR / f"reviews_sentiment{tag}.csv", index=False)
    with __import__("pandas").ExcelWriter(C.PROC_DIR / f"reviews_sentiment{tag}.xlsx") as xw:
        res[cols].to_excel(xw, sheet_name="Reviews+Sentiment", index=False); aspect_table(res).to_excel(xw, sheet_name="Aspect summary")
    at = aspect_table(res).sort_values("net_sentiment"); at["net_sentiment"].plot.barh(color=["#c0392b" if v < 0 else "#2e8b57" for v in at.net_sentiment])
    plt.title("Net sentiment by aspect" + (" (SYNTHETIC DEMO)" if demo else "")); plt.tight_layout(); plt.savefig(C.REPORT_DIR / f"aspect_net_sentiment{tag}.png", dpi=130)
    (C.REPORT_DIR / f"insights{tag}.md").write_text(build_insights(res, demo))
    print(f"{len(res)} reviews processed -> {C.PROC_DIR}")

if __name__ == "__main__":
    main()
