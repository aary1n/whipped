"""Extract features from a Listing for pricing and scoring."""
from __future__ import annotations

from datetime import date

from whipped.domain.models import FeatureVector, Listing

CURRENT_YEAR = date.today().year

MILEAGE_BANDS = [
    (10_000, "very_low"),
    (30_000, "low"),
    (60_000, "medium"),
    (100_000, "high"),
]


def extract(listing: Listing) -> FeatureVector:
    age = CURRENT_YEAR - listing.year
    mileage_band = _mileage_band(listing.mileage)

    return FeatureVector(
        age=age,
        mileage=listing.mileage,
        mileage_band=mileage_band,
        fuel_type=listing.fuel_type,
        transmission=listing.transmission,
        engine_size=listing.engine_size,
    )


def _mileage_band(mileage: int | None) -> str | None:
    if mileage is None:
        return None
    for threshold, band in MILEAGE_BANDS:
        if mileage <= threshold:
            return band
    return "very_high"
