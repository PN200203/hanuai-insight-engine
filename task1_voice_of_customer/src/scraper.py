"""
TASK 1 - BEST BUY CANADA REVIEW SCRAPER

Purpose:
    Scrape publicly visible product reviews from Best Buy Canada.

Assignment requirements covered:
    - Selenium-based scraping
    - Publicly visible data only
    - Product review extraction
    - Multiple review sorting/filter options
    - Show More pagination
    - Duplicate removal
    - Date normalization
    - Rating extraction
    - CSV output
    - Primary key generation

Important:
    - No login is used.
    - No CAPTCHA is bypassed.
    - No proxy rotation is implemented to evade blocking.
    - The script uses delays between browser actions.
    - If Best Buy blocks access or requests CAPTCHA, stop the scraper.
"""

from __future__ import annotations

import re
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    WebDriverException,
)


# =========================================================
# CONFIGURATION
# =========================================================

PRODUCT_URL = (
    "https://www.bestbuy.ca/en-ca/product/"
    "roku-50-select-series-4k-uhd-hdr-qled-smart-tv-50r5d5ca-2026-only-at-best-buy/"
    "19832884"
)

REVIEW_URL = PRODUCT_URL + "/review"

# Save data inside:
# task1_voice_of_customer/data/raw/
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"

OUTPUT_FILE = OUTPUT_DIR / "bestbuy_roku_reviews.csv"

# Maximum number of unique reviews to collect.
MAX_REVIEWS = 100

# Maximum number of Show More clicks per filter.
MAX_SHOW_MORE_CLICKS = 20

# Delay between browser actions.
ACTION_DELAY = 2

# Initial page loading wait.
PAGE_LOAD_DELAY = 5


# =========================================================
# SELENIUM DRIVER
# =========================================================

def create_driver():
    """
    Create a Chrome Selenium WebDriver.

    Chrome is intentionally kept visible during development
    so that the page can be inspected manually.
    """

    options = Options()

    # Keep browser visible.
    options.add_argument("--start-maximized")

    # Disable browser notifications.
    options.add_argument("--disable-notifications")

    # Reduce unnecessary Chrome logging.
    options.add_experimental_option(
        "excludeSwitches",
        ["enable-logging"]
    )

    driver = webdriver.Chrome(options=options)

    return driver


# =========================================================
# DATE NORMALIZATION
# =========================================================

def normalize_date(date_text: str) -> str:
    """
    Convert review dates into YYYY-MM-DD.

    Examples:
        July 21, 2026 -> 2026-07-21
        November 19, 2025 -> 2025-11-19
    """

    if not date_text:
        return ""

    date_text = re.sub(
        r"\s+",
        " ",
        date_text
    ).strip()

    formats = [
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%d %b %Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(
                date_text,
                fmt
            ).strftime("%Y-%m-%d")

        except ValueError:
            continue

    return ""


# =========================================================
# RATING EXTRACTION
# =========================================================

def extract_rating(text: str):
    """
    Extract a rating from review text.

    Supported examples:
        5 out of 5 stars
        4 out of 5 stars
        Customer rating: 5
    """

    if not text:
        return None

    # Example:
    # 5 out of 5 stars
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:out of|/)\s*5",
        text,
        re.IGNORECASE
    )

    if match:
        return float(match.group(1))

    # Example:
    # Customer rating: 5
    match = re.search(
        r"Customer\s+rating\s*:?\s*(\d+(?:\.\d+)?)",
        text,
        re.IGNORECASE
    )

    if match:
        return float(match.group(1))

    return None


# =========================================================
# TEXT CLEANING
# =========================================================

def clean_text(text: str) -> str:
    """
    Clean unnecessary whitespace from text.
    """

    if not text:
        return ""

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# =========================================================
# REVIEWER + DATE
# =========================================================

def extract_reviewer_and_date(text: str):
    """
    Extract reviewer name and review date.

    Expected visible format:

        Reviewed by pk - July 21, 2026

    Returns:
        reviewer_name, date
    """

    if not text:
        return "", ""

    pattern = re.compile(
        r"Reviewed\s+by\s+(.+?)\s*-\s*"
        r"("
        r"[A-Za-zÀ-ÿ]+\s+\d{1,2},?\s+\d{4}"
        r"|"
        r"\d{1,2}\s+[A-Za-zÀ-ÿ]+\s+\d{4}"
        r")",
        re.IGNORECASE
    )

    match = pattern.search(text)

    if not match:
        return "", ""

    reviewer = clean_text(
        match.group(1)
    )

    date = normalize_date(
        match.group(2)
    )

    return reviewer, date


# =========================================================
# REVIEW TEXT CLEANING
# =========================================================

def extract_clean_review_text(raw_text: str):
    """
    Extract the actual customer review text.

    Removes:
        - Rating information
        - Reviewed by information
        - Recommendation information
        - Helpful / Not helpful
        - Report
        - Original-posting information
    """

    if not raw_text:
        return ""

    text = clean_text(raw_text)

    # -----------------------------------------------------
    # Remove rating
    # -----------------------------------------------------

    text = re.sub(
        r"\d+(?:\.\d+)?\s*out of\s*5\s*stars?",
        "",
        text,
        flags=re.IGNORECASE
    )

    # -----------------------------------------------------
    # Remove "Reviewed by NAME - DATE"
    # -----------------------------------------------------

    text = re.sub(
        r"Reviewed\s+by\s+.+?\s*-\s*"
        r"("
        r"[A-Za-zÀ-ÿ]+\s+\d{1,2},?\s+\d{4}"
        r"|"
        r"\d{1,2}\s+[A-Za-zÀ-ÿ]+\s+\d{4}"
        r")",
        "",
        text,
        flags=re.IGNORECASE
    )

    # -----------------------------------------------------
    # Remove recommendation statement
    # -----------------------------------------------------

    text = re.sub(
        r"Yes,\s*I would recommend this to a friend\.?",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"No,\s*I would not recommend this to a friend\.?",
        "",
        text,
        flags=re.IGNORECASE
    )

    # -----------------------------------------------------
    # Remove original posting statement
    # -----------------------------------------------------

    text = re.sub(
        r"Review originally posted on [^.]+\.?",
        "",
        text,
        flags=re.IGNORECASE
    )

    # -----------------------------------------------------
    # Remove helpful/report controls
    # -----------------------------------------------------

    text = re.sub(
        r"Helpful\s*\(\d+\)",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"Not helpful\s*\(\d+\)",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\bReport\b",
        "",
        text,
        flags=re.IGNORECASE
    )

    # -----------------------------------------------------
    # Remove common UI labels
    # -----------------------------------------------------

    text = re.sub(
        r"Customer rating\s*:?\s*\d+(?:\.\d+)?",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = clean_text(text)

    return text


# =========================================================
# REVIEW TITLE
# =========================================================

def extract_title(element, full_text: str, reviewer: str):
    """
    Extract review title.

    First tries heading elements.

    If no heading exists, attempts to identify the text
    appearing before 'Reviewed by'.
    """

    # -----------------------------------------------------
    # Try heading tags first.
    # -----------------------------------------------------

    heading = element.find(
        ["h1", "h2", "h3", "h4", "h5"]
    )

    if heading:

        title = clean_text(
            heading.get_text(
                " ",
                strip=True
            )
        )

        if title and len(title) < 300:
            return title

    # -----------------------------------------------------
    # Fallback:
    # text before "Reviewed by"
    # -----------------------------------------------------

    match = re.search(
        r"^(.*?)Reviewed\s+by",
        full_text,
        re.IGNORECASE
    )

    if match:

        title = clean_text(
            match.group(1)
        )

        # Remove rating-related text.
        title = re.sub(
            r"\d+(?:\.\d+)?\s*out of\s*5\s*stars?",
            "",
            title,
            flags=re.IGNORECASE
        )

        title = clean_text(title)

        if title and len(title) < 300:
            return title

    return ""


# =========================================================
# REVIEW CARD DETECTION
# =========================================================

def find_review_containers(soup):
    """
    Find likely review containers.

    Instead of treating every div as a review,
    this function searches for elements containing
    'Reviewed by' and rating information.

    The smallest suitable containers are preferred.
    """

    candidates = []

    all_elements = soup.find_all(
        ["article", "section", "div"]
    )

    for element in all_elements:

        text = element.get_text(
            " ",
            strip=True
        )

        if not text:
            continue

        lower_text = text.lower()

        # Must contain reviewer information.
        if "reviewed by" not in lower_text:
            continue

        # Must contain rating.
        if "out of 5 stars" not in lower_text:
            continue

        # Avoid huge page-level containers.
        if len(text) > 2500:
            continue

        # Avoid tiny elements.
        if len(text) < 30:
            continue

        candidates.append(element)

    # -----------------------------------------------------
    # Remove nested duplicate candidates.
    # -----------------------------------------------------

    final_candidates = []

    for candidate in candidates:

        has_smaller_candidate = False

        for other in candidates:

            if candidate is other:
                continue

            if candidate in other.parents:

                other_text = other.get_text(
                    " ",
                    strip=True
                )

                if len(other_text) < len(
                    candidate.get_text(
                        " ",
                        strip=True
                    )
                ):

                    has_smaller_candidate = True
                    break

        if not has_smaller_candidate:
            final_candidates.append(candidate)

    return final_candidates


# =========================================================
# EXTRACT REVIEWS FROM PAGE
# =========================================================

def extract_reviews_from_page(driver):
    """
    Extract reviews from the currently loaded page.
    """

    soup = BeautifulSoup(
        driver.page_source,
        "html.parser"
    )

    containers = find_review_containers(
        soup
    )

    reviews = []

    for element in containers:

        full_text = clean_text(
            element.get_text(
                " ",
                strip=True
            )
        )

        # -------------------------------------------------
        # Rating
        # -------------------------------------------------

        rating = extract_rating(
            full_text
        )

        if rating is None:
            continue

        # -------------------------------------------------
        # Reviewer + date
        # -------------------------------------------------

        reviewer, review_date = (
            extract_reviewer_and_date(
                full_text
            )
        )

        # -------------------------------------------------
        # Title
        # -------------------------------------------------

        title = extract_title(
            element,
            full_text,
            reviewer
        )

        # -------------------------------------------------
        # Review text
        # -------------------------------------------------

        review_text = extract_clean_review_text(
            full_text
        )

        # -------------------------------------------------
        # Basic validation
        # -------------------------------------------------

        if not review_text:
            continue

        if len(review_text) < 5:
            continue

        # Avoid obvious UI-only content.
        if review_text.lower() in [
            "write your review",
            "show more",
            "helpful",
            "not helpful",
        ]:
            continue

        reviews.append(
            {
                "title": title,
                "review_text": review_text,
                "date": review_date,
                "rating": rating,
                "source": "Best Buy Canada",
                "reviewer_name": reviewer,
            }
        )

    return reviews


# =========================================================
# DEDUPLICATION
# =========================================================

def deduplicate_reviews(reviews):
    """
    Remove duplicate reviews.

    Primary practical duplicate key:
        reviewer + date + title + review text

    This prevents the same review from being added
    repeatedly after clicking Show More.
    """

    unique = {}

    for review in reviews:

        key = (
            clean_text(
                review.get(
                    "reviewer_name",
                    ""
                )
            ).lower(),

            clean_text(
                review.get(
                    "date",
                    ""
                )
            ).lower(),

            clean_text(
                review.get(
                    "title",
                    ""
                )
            ).lower(),

            clean_text(
                review.get(
                    "review_text",
                    ""
                )
            ).lower(),
        )

        if key not in unique:
            unique[key] = review

    return list(
        unique.values()
    )


# =========================================================
# SHOW MORE
# =========================================================

def click_show_more(driver):
    """
    Find and click a visible 'Show More' button.

    Returns:
        True  = button clicked
        False = button not found
    """

    xpath = (
        "//*[self::button or self::a or @role='button']"
        "[contains("
        "translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),"
        "'show more'"
        ")]"
    )

    try:

        buttons = driver.find_elements(
            By.XPATH,
            xpath
        )

        visible_buttons = []

        for button in buttons:

            try:

                if (
                    button.is_displayed()
                    and button.is_enabled()
                ):
                    visible_buttons.append(
                        button
                    )

            except StaleElementReferenceException:
                continue

        if not visible_buttons:
            return False

        # Usually the last visible Show More
        # belongs to the review section.
        button = visible_buttons[-1]

        driver.execute_script(
            """
            arguments[0].scrollIntoView({
                block: 'center'
            });
            """,
            button
        )

        time.sleep(1)

        driver.execute_script(
            "arguments[0].click();",
            button
        )

        time.sleep(
            ACTION_DELAY
        )

        return True

    except Exception as error:

        print(
            f"Show More click failed: {error}"
        )

        return False


# =========================================================
# APPLY SORT / FILTER
# =========================================================

def apply_review_sort(driver, sort_name):
    """
    Try to apply a Best Buy review sorting option.

    Supported assignment options:

        Most Helpful
        Newest
        Highest Rating
        Lowest Rating
        Most Relevant

    Because website UI can change, the function searches
    visible buttons, links and option elements by text.

    Returns:
        True  = sort option clicked
        False = option not found
    """

    print(
        f"\nTrying review filter: {sort_name}"
    )

    normalized_sort = sort_name.lower()

    # -----------------------------------------------------
    # Possible text variations
    # -----------------------------------------------------

    variations = {
        "Most Helpful": [
            "Most Helpful",
            "Most helpful",
        ],

        "Newest": [
            "Newest",
            "New",
            "Most Recent",
        ],

        "Highest Rating": [
            "Highest Rating",
            "Highest rating",
            "Highest",
        ],

        "Lowest Rating": [
            "Lowest Rating",
            "Lowest rating",
            "Lowest",
        ],

        "Most Relevant": [
            "Most Relevant",
            "Most relevant",
            "Relevant",
        ],
    }

    texts = variations.get(
        sort_name,
        [sort_name]
    )

    # -----------------------------------------------------
    # First try exact visible text
    # -----------------------------------------------------

    for text_value in texts:

        xpath = (
            "//*[self::button or self::a or "
            "@role='button' or @role='option']"
            "[contains("
            "translate(normalize-space(.),"
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
            "'abcdefghijklmnopqrstuvwxyz'),"
            f"'{text_value.lower()}'"
            ")]"
        )

        try:

            elements = driver.find_elements(
                By.XPATH,
                xpath
            )

            for element in elements:

                try:

                    if not element.is_displayed():
                        continue

                    if not element.is_enabled():
                        continue

                    driver.execute_script(
                        """
                        arguments[0].scrollIntoView({
                            block: 'center'
                        });
                        """,
                        element
                    )

                    time.sleep(1)

                    driver.execute_script(
                        "arguments[0].click();",
                        element
                    )

                    time.sleep(
                        ACTION_DELAY
                    )

                    print(
                        f"Applied filter: {sort_name}"
                    )

                    return True

                except (
                    StaleElementReferenceException,
                    WebDriverException,
                ):
                    continue

        except Exception:
            continue

    print(
        f"Filter not found: {sort_name}"
    )

    return False


# =========================================================
# SCRAPE ONE FILTER
# =========================================================

def scrape_for_filter(
    driver,
    filter_name,
    existing_reviews
):
    """
    Scrape reviews after applying one sorting option.
    """

    print("\n" + "=" * 60)
    print(
        f"PROCESSING FILTER: {filter_name}"
    )
    print("=" * 60)

    # Try to apply filter.
    apply_review_sort(
        driver,
        filter_name
    )

    # Allow page to refresh.
    time.sleep(
        ACTION_DELAY
    )

    for iteration in range(
        MAX_SHOW_MORE_CLICKS
    ):

        print(
            f"Collecting reviews - "
            f"{filter_name} - "
            f"iteration {iteration + 1}"
        )

        current_reviews = (
            extract_reviews_from_page(
                driver
            )
        )

        existing_reviews.extend(
            current_reviews
        )

        existing_reviews = (
            deduplicate_reviews(
                existing_reviews
            )
        )

        print(
            f"Total unique reviews: "
            f"{len(existing_reviews)}"
        )

        # Stop when target reached.
        if len(existing_reviews) >= MAX_REVIEWS:
            break

        # Try Show More.
        clicked = click_show_more(
            driver
        )

        if not clicked:

            print(
                "No more Show More button found."
            )

            break

    return existing_reviews


# =========================================================
# MAIN SCRAPER
# =========================================================

def scrape_reviews():

    """
    Main scraping function.

    Workflow:

        1. Open Best Buy review page
        2. Extract visible reviews
        3. Apply different review sorting options
        4. Click Show More
        5. Deduplicate
        6. Generate primary IDs
        7. Save CSV
    """

    # -----------------------------------------------------
    # Create output directory
    # -----------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------------------------------
    # Create browser
    # -----------------------------------------------------

    driver = create_driver()

    all_reviews = []

    try:

        # -------------------------------------------------
        # Open review page
        # -------------------------------------------------

        print(
            "\nOpening Best Buy review page..."
        )

        driver.get(
            REVIEW_URL
        )

        # -------------------------------------------------
        # Wait for page
        # -------------------------------------------------

        wait = WebDriverWait(
            driver,
            30
        )

        wait.until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "body")
            )
        )

        time.sleep(
            PAGE_LOAD_DELAY
        )

        print(
            "Page loaded successfully."
        )

        # -------------------------------------------------
        # Check for CAPTCHA / blocking
        # -------------------------------------------------

        page_text = driver.find_element(
            By.TAG_NAME,
            "body"
        ).text.lower()

        blocked_words = [
            "captcha",
            "verify you are human",
            "access denied",
            "robot check",
        ]

        for word in blocked_words:

            if word in page_text:

                print(
                    "\nWebsite protection detected."
                )

                print(
                    "The scraper will stop without "
                    "attempting to bypass it."
                )

                return None

        # -------------------------------------------------
        # Initial scraping
        # -------------------------------------------------

        print(
            "\nCollecting initial visible reviews..."
        )

        initial_reviews = (
            extract_reviews_from_page(
                driver
            )
        )

        all_reviews.extend(
            initial_reviews
        )

        all_reviews = (
            deduplicate_reviews(
                all_reviews
            )
        )

        print(
            f"Initial unique reviews: "
            f"{len(all_reviews)}"
        )

        # -------------------------------------------------
        # Required sorting/filter options
        # -------------------------------------------------

        filters = [
            "Most Helpful",
            "Newest",
            "Highest Rating",
            "Lowest Rating",
            "Most Relevant",
        ]

        # -------------------------------------------------
        # Process filters
        # -------------------------------------------------

        for filter_name in filters:

            if len(all_reviews) >= MAX_REVIEWS:
                break

            try:

                all_reviews = scrape_for_filter(
                    driver,
                    filter_name,
                    all_reviews
                )

            except Exception as error:

                print(
                    f"Error while processing "
                    f"{filter_name}: {error}"
                )

                continue

        # -------------------------------------------------
        # Final deduplication
        # -------------------------------------------------

        all_reviews = (
            deduplicate_reviews(
                all_reviews
            )
        )

        # -------------------------------------------------
        # Limit to requested number
        # -------------------------------------------------

        all_reviews = all_reviews[
            :MAX_REVIEWS
        ]

        # -------------------------------------------------
        # Generate primary key
        # -------------------------------------------------

        output = []

        for index, review in enumerate(
            all_reviews,
            start=1
        ):

            output.append(
                {
                    "id": f"BBR_{index:05d}",

                    "title": clean_text(
                        review.get(
                            "title",
                            ""
                        )
                    ),

                    "review_text": clean_text(
                        review.get(
                            "review_text",
                            ""
                        )
                    ),

                    "date": review.get(
                        "date",
                        ""
                    ),

                    "rating": review.get(
                        "rating",
                        None
                    ),

                    "source": "Best Buy Canada",

                    "reviewer_name": clean_text(
                        review.get(
                            "reviewer_name",
                            ""
                        )
                    ),
                }
            )

        # -------------------------------------------------
        # Create DataFrame
        # -------------------------------------------------

        df = pd.DataFrame(
            output
        )

        columns = [
            "id",
            "title",
            "review_text",
            "date",
            "rating",
            "source",
            "reviewer_name",
        ]

        df = df.reindex(
            columns=columns
        )

        # -------------------------------------------------
        # Remove completely empty review rows
        # -------------------------------------------------

        df = df[
            df["review_text"]
            .fillna("")
            .str.strip()
            .ne("")
        ]

        # -------------------------------------------------
        # Save CSV
        # -------------------------------------------------

        df.to_csv(
            OUTPUT_FILE,
            index=False,
            encoding="utf-8-sig"
        )

        # -------------------------------------------------
        # Final report
        # -------------------------------------------------

        print("\n" + "=" * 60)
        print(
            "SCRAPING COMPLETE"
        )
        print("=" * 60)

        print(
            f"Reviews collected: {len(df)}"
        )

        print(
            f"CSV output: {OUTPUT_FILE}"
        )

        # -------------------------------------------------
        # Data quality information
        # -------------------------------------------------

        print("\nDATA QUALITY")

        print(
            f"Missing titles: "
            f"{df['title'].eq('').sum()}"
        )

        print(
            f"Missing reviewer names: "
            f"{df['reviewer_name'].eq('').sum()}"
        )

        print(
            f"Missing dates: "
            f"{df['date'].eq('').sum()}"
        )

        print(
            f"Missing review text: "
            f"{df['review_text'].eq('').sum()}"
        )

        print(
            f"Missing ratings: "
            f"{df['rating'].isna().sum()}"
        )

        # -------------------------------------------------
        # Preview
        # -------------------------------------------------

        print("\nFIRST 10 REVIEWS")

        print(
            df.head(10).to_string(
                index=False
            )
        )

        return df

    except TimeoutException:

        print(
            "\nPage loading timed out."
        )

        return None

    except WebDriverException as error:

        print(
            "\nBrowser/Selenium error:"
        )

        print(error)

        return None

    finally:

        # -------------------------------------------------
        # Close browser
        # -------------------------------------------------

        print(
            "\nClosing browser..."
        )

        driver.quit()


# =========================================================
# PROGRAM ENTRY POINT
# =========================================================

if __name__ == "__main__":

    scrape_reviews()