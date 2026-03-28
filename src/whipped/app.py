from __future__ import annotations

from whipped.domain.models import DriverProfile, Listing, WhippedVerdict
from whipped.features.extract import extract
from whipped.pricing.brand_tax import compute as compute_brand_tax
from whipped.pricing.fair_range import estimate
from whipped.scoring.explain import explain
from whipped.scoring.ownership import project_ownership
from whipped.scoring.ripoff import compute as compute_ripoff
from whipped.scoring.risk import assess as assess_risk


def evaluate(
    listing: Listing,
    comparables: list[Listing],
    driver: DriverProfile | None = None,
) -> WhippedVerdict:
    features = extract(listing)
    price_range = estimate(features, comparables)

    asking = listing.price_gbp or price_range.mid_gbp
    ripoff = compute_ripoff(asking, price_range)
    risk = assess_risk(listing, features, price_range)
    ownership = project_ownership(listing, features, price_range, risk, driver)
    explanation_text, counteroffer, action = explain(listing, price_range, ripoff, risk, ownership)

    return WhippedVerdict(
        listing=listing,
        price_range=price_range,
        risk=risk,
        ripoff=ripoff,
        ownership=ownership,
        explanation=explanation_text,
        action_recommendation=action,
        suggested_counteroffer_gbp=counteroffer,
        brand_tax=compute_brand_tax(listing, comparables),
    )
