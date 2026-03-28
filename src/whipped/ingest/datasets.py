"""Load CSV datasets into Listing objects."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from whipped.domain.models import Listing


def load_csv(path: Path) -> list[Listing]:
    df = pd.read_csv(path)
    return [_row_to_listing(row) for _, row in df.iterrows()]


def _row_to_listing(row: pd.Series) -> Listing:
    return Listing(
        make=str(row.get("make", "unknown")),
        model=str(row.get("model", "unknown")),
        year=int(row.get("year", 0)),
        mileage=_safe_int(row.get("mileage")),
        fuel_type=_safe_str(row.get("fuel_type") or row.get("fuelType")),
        transmission=_safe_str(row.get("transmission")),
        engine_size=_safe_float(row.get("engine_size") or row.get("engineSize")),
        asking_price=_safe_int(row.get("price")),
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
