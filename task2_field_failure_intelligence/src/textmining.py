"""Part 2 - Text mining: unstructured notes -> structured tags.

Approach (hybrid, explainable, no GPU needed):
  1. Dictionary + regex entity extraction (component, symptom, action, condition, part no., error code).
     Dictionaries are *seeded* then EXPANDED from the data with frequent noun phrases, so unseen vocab is caught.
  2. Rule-based mapping of symptoms/components -> 'type of issue' categories.
  3. Optional: an open-source LLM (e.g. a local Ollama/Llama model) can be plugged into `llm_extract()`
     to fill rows where the rules found nothing."""
import re
from collections import Counter
import pandas as pd

LEX = {
 "component": ["battery pack", "battery", "motor", "pump", "control board", "circuit board", "pcb", "wiring harness", "harness", "wire", "wiring", "sensor", "display", "screen",
               "hydraulic hose", "hose", "bearing", "connector", "fuse", "relay", "valve", "seal", "gasket", "filter", "switch", "controller", "fan", "gearbox", "belt", "bracket", "cable"],
 "symptom":   ["not holding charge", "overheating", "overheat", "swollen", "grinding noise", "stalling", "leaking", "leak", "pressure drop", "noisy", "short circuit", "not powering on",
               "no power", "frayed insulation", "loose connection", "false readings", "no signal", "calibration drift", "flickering", "blank screen", "cracked", "burst", "seized",
               "excess vibration", "vibration", "corroded", "corrosion", "intermittent contact", "intermittent", "worn", "broken", "rust", "melted", "burnt", "stuck", "vibrating"],
 "action":    ["replaced", "repaired", "reseated", "recalibrated", "cleaned", "tightened", "adjusted", "reset", "rewired", "lubricated", "reflashed", "inspected", "swapped"],
 "condition": ["after heavy rain", "in high ambient heat", "during cold start", "under full load", "after 3 months in service", "after vibration on rough roads",
               "heavy rain", "high ambient heat", "cold start", "full load", "rough roads", "high temperature", "low temperature", "humidity", "dust", "overload", "water ingress"],
}
PART_RE  = re.compile(r"\b(?:part\s*(?:no\.?|number|#)\s*)?([A-Z]{1,3}[-]?\d{3,6})\b")
ERROR_RE = re.compile(r"\b(?:error\s*code\s*|err\s*|code\s*)?(E-?\d{2,3})\b", re.I)

# Issue taxonomy: category -> keywords seen in symptom / component text. First strongest match wins.
ISSUE_RULES = {
  "Electrical / Short & Power":  ["short circuit", "not powering on", "no power", "frayed", "loose connection", "intermittent", "melted", "burnt", "fuse", "relay", "harness", "wiring", "e\\d{2}"],
  "Thermal / Overheating":       ["overheat", "swollen", "melted"],
  "Energy Storage (Battery)":    ["battery", "not holding charge", "swollen"],
  "Leakage / Fluid System":      ["leak", "pressure drop", "burst", "hose", "pump", "seal", "valve"],
  "Mechanical Wear / Vibration": ["grinding", "seized", "vibration", "bearing", "stalling", "worn", "noisy", "gearbox", "belt"],
  "Sensor / Calibration":        ["false readings", "no signal", "calibration", "sensor"],
  "Display / UI":                ["flicker", "blank screen", "display", "screen"],
  "Corrosion / Environmental":   ["corrod", "rust", "connector"],
}

def _find(text: str, vocab):
    low = f" {text.lower()} "
    hits = [v for v in sorted(vocab, key=len, reverse=True) if re.search(rf"\b{re.escape(v)}\b", low)]
    out = []                                                   # drop terms contained in a longer hit (battery vs battery pack)
    for h in hits:
        if not any(h != o and h in o for o in out): out.append(h)
    return out

def expand_lexicon(texts: pd.Series, top=15):
    """Data-driven discovery: frequent bigrams right after 'the'/'reported' hint at components/symptoms we missed."""
    cnt = Counter()
    for t in texts.dropna().str.lower():
        cnt.update(re.findall(r"(?:the|reported)\s+([a-z]+\s[a-z]+)", t))
    known = {w for v in LEX.values() for w in v}
    return [(p, n) for p, n in cnt.most_common(top * 3) if p not in known][:top]

def categorise(components, symptoms, conditions=None) -> str:
    """Category is derived from WHAT failed (component + symptom) only. Operating conditions are deliberately
    excluded: they are the *explanatory* variables in the root-cause screen, so using them here would be circular."""
    blob = " ".join(components + symptoms).lower(); best, score = "Uncategorised", 0
    for cat, kws in ISSUE_RULES.items():
        s = sum(bool(re.search(k, blob)) for k in kws)
        if s > score: best, score = cat, s
    return best

def extract_row(text: str) -> dict:
    t = str(text) if pd.notna(text) else ""
    comps, syms = _find(t, LEX["component"]), _find(t, LEX["symptom"])
    acts, conds = _find(t, LEX["action"]), _find(t, LEX["condition"])
    return {"components": comps, "symptoms": syms, "actions": acts, "conditions": conds,
            "part_numbers": sorted(set(PART_RE.findall(t))), "error_codes": sorted(set(m.upper() for m in ERROR_RE.findall(t))),
            "issue_category": categorise(comps, syms, conds)}

def llm_extract(text: str) -> dict:   # pragma: no cover - plug-in point
    """Fallback for rows where rules found nothing. Example with a local open-source model (Ollama):
        import ollama; r = ollama.chat(model='llama3', messages=[{'role':'user','content': PROMPT + text}])
    Ask for strict JSON {components, symptoms, actions, conditions} and parse it."""
    raise NotImplementedError

def mine(df: pd.DataFrame, text_cols) -> pd.DataFrame:
    d = df.copy(); d["_text"] = d[text_cols].fillna("").astype(str).agg(". ".join, axis=1)
    ext = pd.DataFrame(d["_text"].map(extract_row).tolist(), index=d.index)
    d = pd.concat([d.drop(columns="_text"), ext], axis=1)
    d["primary_component"] = d["components"].map(lambda l: l[0] if l else "Unknown")
    d["primary_symptom"] = d["symptoms"].map(lambda l: l[0] if l else "Unknown")
    for c in ["components", "symptoms", "actions", "conditions", "part_numbers", "error_codes"]: d[c + "_str"] = d[c].map(", ".join)
    return d
