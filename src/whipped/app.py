"""Pipeline orchestrator — wires all stages together."""
from __future__ import annotations

from whipped.domain.models import Listing, Verdict
from whipped.features.extract import extract
from whipped.ingest.datasets import load_csv
from whipped.pricing.fair_range import estimate
from whipped.scoring.explain import explain
from whipped.scoring.ripoff import compute as compute_ripoff
from whipped.scoring.risk import assess as assess_risk
from whipped.config import SAMPLE_CSV


def evaluate(listing: Listing, comparables: list[Listing] | None = None) -> Verdict:
    if comparables is None:
        comparables = load_csv(SAMPLE_CSV)

    features = extract(listing)
    price_range = estimate(features, comparables)

    asking = listing.asking_price or price_range.mid
    ripoff = compute_ripoff(asking, price_range)
    risk = assess_risk(listing, features)
    explanation_text, counteroffer = explain(listing, price_range, ripoff, risk)

    return Verdict(
        listing=listing,
        price_range=price_range,
        ripoff=ripoff,
        risk=risk,
        explanation=explanation_text,
        counteroffer=counteroffer,
    )
