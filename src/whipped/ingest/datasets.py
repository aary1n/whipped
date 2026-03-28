from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from whipped.domain.models import Listing

MIN_VALID_PRICE = 500
MIN_VALID_YEAR = 1990
MAX_VALID_YEAR = date.today().year + 1
MAX_VALID_MILEAGE = 500_000

# Filename stem → canonical make name.
# focus.csv and cclass.csv are model-specific subsets of ford.csv / merc.csv — excluded.
FILENAME_TO_MAKE: dict[str, str] = {
    "ford":     "ford",
    "vauxhall": "vauxhall",
    "bmw":      "bmw",
    "merc":     "mercedes",
    "audi":     "audi",
    "vw":       "vw",
    "toyota":   "toyota",
    "hyundi":   "hyundai",
    "skoda":    "skoda",
}


def load_kaggle_raw(raw_dir: Path | None = None) -> list[Listing]:
    """Load all clean Kaggle CSVs from raw_dir, deriving make from filename."""
    from whipped.config import KAGGLE_RAW_DIR
    raw_dir = raw_dir or KAGGLE_RAW_DIR

    if not raw_dir.exists():
        print(f"[datasets] Raw dir not found: {raw_dir}. Run scripts/download_data.py.")
        return []

    all_listings: list[Listing] = []
    for stem, make in FILENAME_TO_MAKE.items():
        path = raw_dir / f"{stem}.csv"
        if not path.exists():
            print(f"[datasets] Missing expected file: {path.name} — skipping.")
            continue
        listings = _load_kaggle_file(path, make)
        all_listings.extend(listings)

    valid = [l for l in all_listings if is_valid_comparable(l)]
    rejected = len(all_listings) - len(valid)
    print(f"[datasets] Loaded {len(valid):,} valid rows from {raw_dir.name} ({rejected:,} rejected).")
    return valid


def make_from_filename(filename: str) -> str | None:
    """Return canonical make for a Kaggle CSV filename, or None if not recognised."""
    stem = Path(filename).stem.lower()
    return FILENAME_TO_MAKE.get(stem)


def load_csv(path: Path) -> list[Listing]:
    """Load a single generic CSV (make column expected or already set)."""
    df = pd.read_csv(path)
    listings = [_row_to_listing(row) for _, row in df.iterrows()]
    valid = [l for l in listings if is_valid_comparable(l)]
    rejected = len(listings) - len(valid)
    if rejected:
        print(f"[datasets] Rejected {rejected}/{len(listings)} rows with invalid data.")
    return valid


def is_valid_comparable(listing: Listing) -> bool:
    if not listing.make or not listing.model:
        return False
    if listing.price_gbp is None or listing.price_gbp < MIN_VALID_PRICE:
        return False
    if listing.year < MIN_VALID_YEAR or listing.year > MAX_VALID_YEAR:
        return False
    if listing.mileage_miles is not None:
        if listing.mileage_miles < 0 or listing.mileage_miles > MAX_VALID_MILEAGE:
            return False
    return True


# --- Kaggle-specific ingestion ---

def _load_kaggle_file(path: Path, make: str) -> list[Listing]:
    df = pd.read_csv(path)
    # Normalise tax(£) column name
    df.columns = [c.replace("tax(£)", "tax").replace("tax(£)", "tax") for c in df.columns]
    return [_kaggle_row_to_listing(row, make) for _, row in df.iterrows()]


def _kaggle_row_to_listing(row: pd.Series, make: str) -> Listing:
    return Listing(
        make=make,
        model=_norm_str(row.get("model")),
        year=_safe_int(row.get("year")) or 0,
        price_gbp=_safe_int(row.get("price")),
        mileage_miles=_safe_int(row.get("mileage")),
        fuel_type=_norm_str(row.get("fuelType")),
        transmission=_norm_str(row.get("transmission")),
        engine_size_l=_safe_float(row.get("engineSize")),
        source="kaggle:adityadesai13/used-car-dataset-ford-and-mercedes",
    )


# --- Generic CSV ingestion (original format with make column) ---

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


# --- Helpers ---

def _norm_str(val: object) -> str | None:
    """Strip, lowercase, return None if empty."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    s = str(val).strip().lower()
    return s if s else None


def _safe_int(val: object) -> int | None:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    try:
        return int(float(str(val)))
    except (ValueError, TypeError):
        return None


def _safe_float(val: object) -> float | None:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    try:
        return float(str(val))
    except (ValueError, TypeError):
        return None


def _safe_str(val: object) -> str | None:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    return str(val)
