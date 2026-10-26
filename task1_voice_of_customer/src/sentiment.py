"""Aspect-based sentiment (ABSA) - transparent, dependency-free, and fast.

Why this design: the assignment's example output is aspect-level  e.g. ['Good Design Quality (Pos)'],
not a single positive/negative score. So we (1) split a review into sentences, (2) detect which
product ASPECT each sentence talks about, (3) score the sentence polarity with a small lexicon
that handles negation + intensifiers, (4) emit "<Aspect> (Pos|Neg|Neu)" tags, and (5) blend the
text score with the star rating for an overall label.
An optional transformer upgrade is provided in `transformer_overall()`."""
import re
from collections import Counter
import pandas as pd

ASPECTS = {   # aspect -> trigger stems (edit freely for another product category)
    "Sound Quality":      ["sound", "audio", "bass", "treble", "volume", "music", "noise cancel", "anc"],
    "Battery Life":       ["battery", "charge", "charging", "charged", "last", "hours", "power"],
    "Comfort & Fit":      ["comfort", "fit", "fits", "ear", "tight", "heavy", "light", "wear", "wearing"],
    "Connectivity":       ["bluetooth", "connect", "pair", "pairing", "disconnect", "drop", "lag", "latency", "range"],
    "Build & Design":     ["design", "build", "look", "looks", "colour", "color", "quality", "sturdy", "plastic", "case", "finish"],
    "Price & Value":      ["price", "value", "worth", "cheap", "expensive", "money", "deal", "sale", "cost"],
    "Call & Mic Quality": ["mic", "microphone", "call", "calls", "voice"],
    "App & Controls":     ["app", "control", "controls", "touch", "button", "buttons", "gesture", "setup", "set up"],
    "Durability & Defects": ["broke", "broken", "stopped", "defect", "died", "dead", "crack", "faulty", "failed", "warranty", "return", "refund"],
    "Delivery & Service": ["shipping", "delivery", "arrived", "packaging", "service", "support", "staff"],
}
POS = set("good great excellent amazing awesome love loved perfect nice best fantastic happy comfortable clear crisp solid sturdy easy fast reliable impressed recommend worth stable pretty beautiful smooth long satisfied superb".split())
NEG = set("bad poor terrible awful hate hated worst broke broken cheap disappointed disappointing uncomfortable tight loose flimsy laggy lag drops dropping died dead useless faulty defective fail failed fails stopped issue issues problem problems muffled tinny weak short expensive difficult annoying refund return waste".split())
NEGATORS = {"not", "no", "never", "dont", "don't", "doesnt", "doesn't", "didnt", "didn't", "isnt", "isn't", "wasnt", "wasn't", "cant", "can't", "hardly", "without"}
BOOST = {"very": 1.5, "really": 1.5, "extremely": 1.8, "super": 1.5, "so": 1.3, "too": 1.4}

def _sentences(t: str):
    return [s.strip() for s in re.split(r"(?<=[.!?\n])\s+|\n+", str(t)) if s.strip()]

def _polarity(sentence: str) -> float:
    toks = re.findall(r"[a-z']+", sentence.lower()); score = 0.0
    for i, w in enumerate(toks):
        val = 1.0 if w in POS else -1.0 if w in NEG else 0.0
        if not val: continue
        window = toks[max(0, i - 3):i]
        if any(x in NEGATORS for x in window): val *= -0.8     # "not good" flips
        for x in window:
            val *= BOOST.get(x, 1.0)
        score += val
    return score

def _label(s: float) -> str:
    return "Pos" if s > 0.4 else "Neg" if s < -0.4 else "Neu"

def aspect_tags(text: str):
    """Return (list of 'Aspect (Pol)' tags, overall text score)."""
    per_aspect, total = {}, 0.0
    for sent in _sentences(text):
        p = _polarity(sent); total += p; low = sent.lower()
        for asp, kws in ASPECTS.items():
            if any(re.search(rf"\b{re.escape(k)}", low) for k in kws):
                per_aspect[asp] = per_aspect.get(asp, 0.0) + p
    return [f"{a} ({_label(s)})" for a, s in per_aspect.items() if _label(s) != "Neu" or True], total

def overall_label(text_score: float, rating) -> str:
    """Blend lexicon score with stars: stars are the stronger, user-given signal."""
    r = 0.0 if pd.isna(rating) else (float(rating) - 3) / 2          # -1..+1
    blend = 0.6 * r + 0.4 * max(-1, min(1, text_score / 3))
    return "Positive" if blend > 0.2 else "Negative" if blend < -0.2 else "Neutral"

def preprocess(text: str) -> str:
    """Light cleaning only (lowercasing would hurt nothing here, but we keep case for readability)."""
    t = re.sub(r"<[^>]+>|https?://\S+", " ", str(text))
    return re.sub(r"\s+", " ", t).strip()

def run_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["clean_text"] = (out["title"].fillna("") + ". " + out["review_text"].fillna("")).map(preprocess)
    res = out["clean_text"].map(aspect_tags)
    out["sentiment_tags"] = res.map(lambda r: r[0]); out["text_score"] = res.map(lambda r: round(r[1], 2))
    out["overall_sentiment"] = [overall_label(s, r) for s, r in zip(out["text_score"], out["rating"])]
    out["sentiment_tags_str"] = out["sentiment_tags"].map(lambda l: "; ".join(l) if l else "General (Neu)")
    return out

def aspect_table(df: pd.DataFrame) -> pd.DataFrame:
    """Aspect x polarity counts -> net sentiment; the backbone of the business insights."""
    c = Counter(t for tags in df["sentiment_tags"] for t in tags)
    rows = {}
    for tag, n in c.items():
        a, p = tag.rsplit(" (", 1); rows.setdefault(a, {"Pos": 0, "Neg": 0, "Neu": 0})[p.rstrip(")")] = n
    t = pd.DataFrame(rows).T.fillna(0).astype(int)
    t["mentions"] = t.sum(axis=1).astype(int); t["net_sentiment"] = ((t["Pos"] - t["Neg"]) / t["mentions"]).round(2)
    return t.sort_values("mentions", ascending=False)

def transformer_overall(texts):
    """OPTIONAL upgrade (needs `pip install transformers torch`): contextual model for overall polarity."""
    from transformers import pipeline
    clf = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
    return [r["label"].capitalize() for r in clf(list(texts), truncation=True)]
