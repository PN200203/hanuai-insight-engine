"""Central configuration for Task 1 (BestBuy.ca review mining).
Everything tunable lives here so the scraper code stays free of magic numbers."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR, PROC_DIR, REPORT_DIR = ROOT / "data/raw", ROOT / "data/processed", ROOT / "reports"

BASE_URL = "https://www.bestbuy.ca"
# >>> Pick any product with 50+ reviews and paste its URL / SKU here <<<
PRODUCT_URL = "https://www.bestbuy.ca/en-ca/product/<slug>/<SKU>"
SKU = "<SKU>"

# The reviews widget is fed by a JSON endpoint. The exact path/params can change, so verify
# it once in Chrome DevTools > Network > Fetch/XHR while clicking "Show More", then paste the
# URL pattern here. {sku}, {page}, {size}, {sort} are filled in by the scraper.
# (This template is a best guess and is NOT verified - the build sandbox had no internet.)
REVIEWS_API_TEMPLATE = (BASE_URL + "/api/reviews/v2/products/{sku}/reviews"
                        "?source=us&lang=en-CA&pageSize={size}&page={page}&sortBy={sort}")
PAGE_SIZE = 20

# UI filter label -> API sort value (the assignment's five filters).
FILTERS = {
    "Most Relevant": "relevancy",
    "Most Helpful": "helpfulness",
    "Newest": "submissionTime",
    "Highest Rating": "ratingHigh",
    "Lowest Rating": "ratingLow",
}

MIN_DELAY, MAX_DELAY = 2.0, 5.0      # polite jittered delay between requests (seconds)
MAX_RETRIES = 5
REQUEST_TIMEOUT = 20
MAX_PAGES_PER_FILTER = 60            # hard stop so a bug can never loop forever
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
]
PROXIES: list = []                   # e.g. ["http://user:pass@host:port"]; empty = direct connection
