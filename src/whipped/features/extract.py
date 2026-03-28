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
    return FeatureVector(
        make=listing.make.lower(),
        model=listing.model.lower(),
        age=age,
        mileage_miles=listing.mileage_miles,
        mileage_band=_mileage_band(listing.mileage_miles),
        fuel_type=listing.fuel_type,
        transmission=listing.transmission,
        engine_size_l=listing.engine_size_l,
    )


def _mileage_band(mileage: int | None) -> str | None:
    if mileage is None:
        return None
    for threshold, band in MILEAGE_BANDS:
        if mileage <= threshold:
            return band
    return "very_high"
