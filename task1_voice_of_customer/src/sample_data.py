"""SYNTHETIC demo reviews so the pipeline can be tested without internet access.
!!! NOT real BestBuy data. Every row is tagged source='SYNTHETIC-DEMO'. Delete once you scrape. !!!"""
import random
import pandas as pd

POS = ["The sound is crisp and the bass is great.", "Battery easily lasts the whole workday.", "Very comfortable, I forget I'm wearing them.",
       "Bluetooth pairing was quick and stable.", "Great value for the price.", "Love the design, the case looks premium.",
       "Mic is clear on calls.", "Setup through the app was easy.", "Fast delivery and nice packaging."]
NEG = ["The left earbud stopped working after two months.", "Bluetooth keeps disconnecting and there is lag in videos.",
       "Battery is poor, it died in under three hours.", "Not comfortable, they feel tight and hurt my ears.",
       "Cheap plastic build, the case hinge feels flimsy.", "The mic is muffled on calls.", "Too expensive for what you get.",
       "The app is confusing and controls are annoying.", "Customer service refused a refund."]
NEU = ["Arrived on a Tuesday.", "Bought these for my son.", "Using them for the gym."]
NAMES = ["Alex", "Priya", "Sam", "Jordan", "Mei", "Luc", "Fatima", "Chris", "Noor", "Dana"]

def make_demo(n=180, seed=7) -> pd.DataFrame:
    rnd, rows = random.Random(seed), []
    for i in range(n):
        rating = rnd.choices([1, 2, 3, 4, 5], [0.10, 0.08, 0.10, 0.27, 0.45])[0]
        pos_n = {5: 3, 4: 2, 3: 1, 2: 1, 1: 0}[rating]; neg_n = {5: 0, 4: 1, 3: 1, 2: 2, 1: 3}[rating]
        txt = " ".join(rnd.sample(POS, pos_n) + rnd.sample(NEG, neg_n) + rnd.sample(NEU, 1))
        rows.append({"review_id": f"DEMO{i+1:04d}", "title": {5: "Love them", 4: "Pretty good", 3: "It's okay", 2: "Disappointed", 1: "Do not buy"}[rating],
                     "review_text": txt, "date": (pd.Timestamp("2025-01-01") + pd.Timedelta(days=rnd.randint(0, 600))).strftime("%Y-%m-%d"),
                     "rating": rating, "source": "SYNTHETIC-DEMO", "reviewer_name": rnd.choice(NAMES),
                     "helpful_votes": rnd.randint(0, 20), "filters_surfaced_in": "Most Relevant"})
    return pd.DataFrame(rows)
