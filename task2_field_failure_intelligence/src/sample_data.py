"""SYNTHETIC field-failure dataset used ONLY because the assessment's Excel file was not
available when this project was built. Mimics typical messy service/warranty logs:
free-text technician notes, missing values, duplicates, inconsistent labels.
Drop the real file into data/raw/ and the pipeline will use it instead."""
import random
import numpy as np, pandas as pd

COMPONENTS = ["battery pack", "motor", "pump", "control board", "wiring harness", "sensor", "display", "hydraulic hose", "bearing", "connector"]
SYMPTOMS = {"battery pack": ["not holding charge", "overheating", "swollen"], "motor": ["overheating", "grinding noise", "stalling"],
            "pump": ["leaking", "pressure drop", "noisy"], "control board": ["short circuit", "not powering on", "error code E{n}"],
            "wiring harness": ["frayed insulation", "loose connection", "short circuit"], "sensor": ["false readings", "no signal", "calibration drift"],
            "display": ["flickering", "blank screen", "cracked"], "hydraulic hose": ["leaking", "cracked", "burst"],
            "bearing": ["grinding noise", "seized", "excess vibration"], "connector": ["corroded", "loose connection", "intermittent contact"]}
ACTIONS = ["replaced", "repaired", "reseated", "recalibrated", "cleaned", "tightened"]
CONDS = ["after heavy rain", "in high ambient heat", "during cold start", "under full load", "after 3 months in service", "after vibration on rough roads"]
MODELS = ["RX-200", "RX-300", "TX-500"]; REGIONS = ["North", "South", "East", "West", "south ", "NORTH"]

def make_failures(n=1200, seed=11) -> pd.DataFrame:
    r, rows = random.Random(seed), []
    for i in range(n):
        comp = r.choices(COMPONENTS, [14, 12, 10, 14, 9, 11, 6, 8, 8, 8])[0]
        model = r.choices(MODELS, [.4, .35, .25])[0]
        if model == "RX-300" and r.random() < .35: comp = "battery pack"               # planted pattern: RX-300 battery issue
        sym = r.choice(SYMPTOMS[comp]).format(n=r.randint(10, 99)); date = pd.Timestamp("2024-01-01") + pd.Timedelta(days=r.randint(0, 650))
        if comp == "battery pack" and date > pd.Timestamp("2025-03-01") and r.random() < .5: sym = "overheating"   # planted trend
        note = f"Customer reported {comp} {sym} {r.choice(CONDS)}. Technician {r.choice(ACTIONS)} the {comp}." + (f" Part no. {r.choice('ABC')}{r.randint(1000,9999)} used." if r.random() < .6 else "")
        rows.append({"ticket_id": f"T{100000+i}", "date": date, "product_model": model, "region": r.choice(REGIONS),
                     "technician_notes": note, "customer_complaint": f"{comp} {sym}".capitalize() if r.random() < .7 else None,
                     "downtime_hours": round(abs(np.random.default_rng(i).normal(6, 4)), 1), "repair_cost": round(abs(np.random.default_rng(i + 1).normal(180, 120)), 2),
                     "severity": r.choice(["Low", "Medium", "High", "high", "HIGH", None])})
    df = pd.DataFrame(rows)
    df.loc[df.sample(frac=.04, random_state=1).index, "technician_notes"] = None                   # missing text
    df.loc[df.sample(frac=.03, random_state=2).index, "repair_cost"] = np.nan                       # missing numeric
    df.loc[df.sample(frac=.01, random_state=3).index, "downtime_hours"] = -5                         # impossible value
    df = pd.concat([df, df.sample(30, random_state=4)], ignore_index=True)                          # exact duplicates
    df["date"] = df["date"].dt.strftime("%Y-%m-%d"); df.loc[df.sample(10, random_state=5).index, "date"] = "not available"
    return df
