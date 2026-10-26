"""Anti-blocking toolkit: robots.txt check, jittered delays, UA/proxy rotation,
exponential-backoff retries. NOTE: deliberately NO captcha-solving code. If a captcha or
persistent 403 wall appears we back off and stop - bypassing it would violate site terms."""
import random, time, logging
import requests
from urllib import robotparser
from . import config as C

log = logging.getLogger("resilience")

def robots_allows(path: str) -> bool:
    """Respect robots.txt before touching any URL. Conservative: unreadable robots => False."""
    rp = robotparser.RobotFileParser()
    try:
        rp.set_url(C.BASE_URL + "/robots.txt"); rp.read()
        return rp.can_fetch("*", C.BASE_URL + path)
    except Exception as e:
        log.warning("robots.txt unreadable (%s); assuming NOT allowed", e)
        return False

def polite_sleep():
    time.sleep(random.uniform(C.MIN_DELAY, C.MAX_DELAY))

def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": random.choice(C.USER_AGENTS),
                      "Accept": "application/json, text/plain, */*",
                      "Accept-Language": "en-CA,en;q=0.9"})
    if C.PROXIES:
        p = random.choice(C.PROXIES); s.proxies.update({"http": p, "https": p})
    return s

def get_with_retry(session, url):
    """GET with exponential backoff + identity rotation on 403/429/5xx. Returns Response or None."""
    for attempt in range(1, C.MAX_RETRIES + 1):
        try:
            r = session.get(url, timeout=C.REQUEST_TIMEOUT)
            if r.status_code == 200:
                return r
            if r.status_code in (403, 429) or r.status_code >= 500:
                wait = min(60, 2 ** attempt + random.random())
                log.warning("HTTP %s (attempt %d): sleep %.1fs, rotate identity", r.status_code, attempt, wait)
                time.sleep(wait); session = make_session()
                continue
            log.error("HTTP %s for %s - giving up", r.status_code, url); return None
        except requests.RequestException as e:
            wait = 2 ** attempt; log.warning("network error %s - retry in %ss", e, wait); time.sleep(wait)
    return None
