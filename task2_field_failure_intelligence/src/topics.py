"""Clustering / topic modelling + root-cause screening."""
import numpy as np, pandas as pd
from scipy.stats import fisher_exact
from sklearn.cluster import KMeans
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.metrics import silhouette_score

# boilerplate that appears in nearly every ticket and would dominate clusters
DOMAIN_STOP = list(ENGLISH_STOP_WORDS | {"reported", "customer", "technician", "used", "part", "no", "replaced", "repaired", "reseated", "recalibrated", "cleaned", "tightened"})

def _text(d, cols): return d[cols].fillna("").astype(str).agg(" ".join, axis=1).str.lower().str.replace(r"\b[a-z]\d{3,}\b|\b\d+\b", " ", regex=True)

def cluster_failures(d, cols, k_range=range(4, 10), seed=0):
    """TF-IDF -> KMeans; k chosen by silhouette. Returns (labels, k, top-terms per cluster, silhouette)."""
    vec = TfidfVectorizer(stop_words=DOMAIN_STOP, ngram_range=(1, 2), min_df=3, max_df=0.6)
    X = vec.fit_transform(_text(d, cols)); best = (-1, None, None)
    for k in k_range:
        km = KMeans(k, n_init=10, random_state=seed).fit(X); s = silhouette_score(X, km.labels_, sample_size=min(2000, X.shape[0]), random_state=seed)
        if s > best[0]: best = (s, k, km)
    s, k, km = best; terms = np.array(vec.get_feature_names_out())
    top = {i: ", ".join(terms[np.argsort(km.cluster_centers_[i])[::-1][:6]]) for i in range(k)}
    return km.labels_, k, top, s

def nmf_topics(d, cols, n=6, seed=0):
    """NMF topics are additive & easy to read: each complaint = mixture of topics."""
    vec = TfidfVectorizer(stop_words=DOMAIN_STOP, min_df=3, max_df=0.6); X = vec.fit_transform(_text(d, cols))
    m = NMF(n, random_state=seed, init="nndsvd", max_iter=400).fit(X); terms = np.array(vec.get_feature_names_out())
    topics = {i: ", ".join(terms[np.argsort(c)[::-1][:7]]) for i, c in enumerate(m.components_)}
    return m.transform(X).argmax(axis=1), topics

def root_cause_screen(d, outcome="primary_component", drivers=("product_model", "region", "primary_condition"), min_n=15):
    """For each (driver value, outcome value) cell: LIFT = P(outcome|driver)/P(outcome) plus a one-sided Fisher exact
    p-value for THAT cell (is this outcome over-represented in this group?). Cell-level testing matters: one strong
    effect must not make every other cell in the same table look significant. Bonferroni-corrected over all cells
    tested. 'actionable' = lift >= 1.3 AND corrected p < 0.05. Association, not proof - engineering must confirm."""
    rows = []
    for drv in drivers:
        if drv not in d: continue
        sub = d[(d[drv] != "Unknown") & (d[outcome] != "Unknown")]     # missing text is Unknown on BOTH axes -> fake dependence
        base = sub[outcome].value_counts(normalize=True); ct = pd.crosstab(sub[drv], sub[outcome]); N = ct.values.sum()
        for dv in ct.index[ct.sum(axis=1) >= min_n]:
            for ov in ct.columns:
                a = int(ct.loc[dv, ov]); 
                if a < 8: continue
                b = int(ct.loc[dv].sum() - a); c = int(ct[ov].sum() - a); e = int(N - a - b - c)
                p = fisher_exact([[a, b], [c, e]], alternative="greater")[1]
                rows.append({"driver": drv, "driver_value": dv, "outcome": ov, "count": a, "lift": round((a / (a + b)) / base[ov], 2), "p_value": p})
    out = pd.DataFrame(rows)
    if out.empty: return out
    out["p_adj"] = (out.p_value * len(out)).clip(upper=1.0)             # Bonferroni
    out["actionable"] = (out.lift >= 1.3) & (out.p_adj < 0.05)
    return out.sort_values("lift", ascending=False)
