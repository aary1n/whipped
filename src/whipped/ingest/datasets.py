from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from whipped.domain.models import Listing

MIN_VALID_PRICE = 500
MIN_VALID_YEAR = 1990
MAX_VALID_YEAR = date.today().year + 1
MAX_VALID_MILEAGE = 500_000


def load_csv(path: Path) -> list[Listing]:
    df = pd.read_csv(path)
    listings = [_row_to_listing(row) for _, row in df.iterrows()]
    valid = [l for l in listings if is_valid_comparable(l)]
    rejected = len(listings) - len(valid)
    if rejected:
        print(f"[datasets] Rejected {rejected}/{len(listings)} rows with invalid data.")
    return valid


def is_valid_comparable(listing: Listing) -> bool:
    """Return True if the listing is fit to use as a comparable."""
    if listing.price_gbp is None or listing.price_gbp < MIN_VALID_PRICE:
        return False
    if listing.year < MIN_VALID_YEAR or listing.year > MAX_VALID_YEAR:
        return False
    if listing.mileage_miles is not None and listing.mileage_miles > MAX_VALID_MILEAGE:
        return False
    return True


def _row_to_listing(row: pd.Series) -> Listing:
    return Listing(
        make=str(row.get("make", "unknown")),
        model=str(row.get("model", "unknown")),
        year=int(row.get("year", 0)),
        mileage_miles=_safe_int(row.get("mileage")),
        fuel_type=_safe_str(row.get("fuel_type") or row.get("fuelType")),
        transmission=_safe_str(row.get("transmission")),
        engine_size_l=_safe_float(row.get("engine_size") or row.get("engineSize")),
        price_gbp=_safe_int(row.get("price")),
    )


def _safe_int(val: object) -> int | None:
    if pd.isna(val):
        return None
    return int(val)  # type: ignore[arg-type]


def _safe_float(val: object) -> float | None:
    if pd.isna(val):
        return None
    return float(val)  # type: ignore[arg-type]


def _safe_str(val: object) -> str | None:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    return str(val)
