"""Assess hidden risks in a listing."""
from __future__ import annotations

from whipped.domain.models import FeatureVector, Listing, RiskScore

HIGH_MILEAGE_PER_YEAR = 15_000


def assess(listing: Listing, features: FeatureVector) -> RiskScore:
    factors: list[str] = []

    if features.age > 0 and features.mileage:
        avg_annual = features.mileage / features.age
        if avg_annual > HIGH_MILEAGE_PER_YEAR:
            factors.append(f"high mileage for age ({int(avg_annual):,}/yr)")

    if listing.mileage is None:
        factors.append("mileage not disclosed")

    if listing.fuel_type is None:
        factors.append("fuel type not specified")

    if features.mileage_band == "very_high":
        factors.append("very high total mileage")

    score = min(100, len(factors) * 25)
    return RiskScore(score=score, factors=factors)
