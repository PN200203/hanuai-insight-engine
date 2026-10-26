"""Turns the aspect table into a stakeholder insight narrative (markdown)."""
import pandas as pd
from .sentiment import aspect_table

def build_insights(df: pd.DataFrame, demo: bool) -> str:
    at = aspect_table(df); n = len(df)
    mix = df["overall_sentiment"].value_counts(normalize=True).mul(100).round(1).to_dict()
    best = at[at.mentions >= 5].sort_values("net_sentiment", ascending=False).head(3)
    worst = at[at.mentions >= 5].sort_values("net_sentiment").head(3)
    low = df[df.rating <= 2]
    low_aspects = pd.Series([t for tags in low["sentiment_tags"] for t in tags if t.endswith("(Neg)")]).value_counts().head(3)
    L = [f"**Reviews analysed:** {n} | **Mean rating:** {df.rating.mean():.2f}/5 | **Overall mix:** {mix}", ""]
    L.append("### Top drivers of satisfaction"); L += [f"- **{a}** - net sentiment {r.net_sentiment:+.2f} across {int(r.mentions)} mentions" for a, r in best.iterrows()]
    L.append("\n### Top drivers of dissatisfaction"); L += [f"- **{a}** - net sentiment {r.net_sentiment:+.2f} across {int(r.mentions)} mentions" for a, r in worst.iterrows()]
    L.append("\n### What 1-2 star reviewers complain about most")
    L += [f"- {t.replace(' (Neg)','')}: {c} reviews" for t, c in low_aspects.items()] or ["- (no low-rating reviews)"]
    L.append("\n### Recommendations")
    for a, _ in worst.iterrows():
        L.append(f"- **{a}:** prioritise a root-cause review (QA test plan, supplier audit, firmware/app fix) and track its net sentiment monthly.")
    for a, _ in best.iterrows():
        L.append(f"- **{a}:** protect and promote - lead marketing copy and listings with it.")
    if demo: L.insert(0, "> WARNING: computed on SYNTHETIC demo data - illustrates the format only, not BestBuy reality.\n")
    return "\n".join(L)
