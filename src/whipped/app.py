from __future__ import annotations

from whipped.domain.models import Listing, WhippedVerdict
from whipped.features.extract import extract
from whipped.pricing.fair_range import estimate
from whipped.scoring.explain import explain
from whipped.scoring.ripoff import compute as compute_ripoff
from whipped.scoring.risk import assess as assess_risk


def evaluate(listing: Listing, comparables: list[Listing]) -> WhippedVerdict:
    features = extract(listing)
    price_range = estimate(features, comparables)

    asking = listing.price_gbp or price_range.mid_gbp
    ripoff = compute_ripoff(asking, price_range)
    risk = assess_risk(listing, features, price_range)
    explanation_text, counteroffer = explain(listing, price_range, ripoff, risk)

    return WhippedVerdict(
        listing=listing,
        price_range=price_range,
        risk=risk,
        ripoff=ripoff,
        explanation=explanation_text,
        suggested_counteroffer_gbp=counteroffer,
    )
