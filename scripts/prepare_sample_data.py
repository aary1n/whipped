"""Build data/sample/sample.csv from the local Kaggle CSVs.

Falls back to a synthetic generator if the raw data is not present.
Run: python scripts/prepare_sample_data.py
"""
from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path

import pandas as pd

from whipped.config import KAGGLE_RAW_DIR, SAMPLE_DIR
from whipped.ingest.datasets import (
    FILENAME_TO_MAKE,
    is_valid_comparable,
    _kaggle_row_to_listing,
    _load_kaggle_file,
)

OUTPUT = SAMPLE_DIR / "sample.csv"
PROFILE = SAMPLE_DIR / "profile.json"
ROWS_PER_MODEL = 20      # max rows sampled per (make, model) group
RANDOM_SEED = 42


def main() -> None:
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

    if KAGGLE_RAW_DIR.exists() and any(KAGGLE_RAW_DIR.glob("*.csv")):
        _build_from_kaggle()
    else:
        print(f"Raw data not found at {KAGGLE_RAW_DIR}. Run scripts/download_data.py first.")
        print("Falling back to synthetic sample.")
        _build_synthetic()


def _build_from_kaggle() -> None:
    rng = random.Random(RANDOM_SEED)
    frames: list[pd.DataFrame] = []

    for stem, make in FILENAME_TO_MAKE.items():
        path = KAGGLE_RAW_DIR / f"{stem}.csv"
        if not path.exists():
            continue
        df = pd.read_csv(path)
        df["make"] = make
        # Normalise column name quirk
        df.columns = [c.replace("tax(£)", "tax") for c in df.columns]
        frames.append(df)

    if not frames:
        print("No Kaggle files found — nothing to sample.")
        return

    combined = pd.concat(frames, ignore_index=True)

    # Normalise for grouping
    combined["_make_key"] = combined["make"].str.strip().str.lower()
    combined["_model_key"] = combined["model"].fillna("").str.strip().str.lower()

    # Sample up to ROWS_PER_MODEL per (make, model) group
    groups: dict[tuple[str, str], list[int]] = defaultdict(list)
    for idx, row in combined.iterrows():
        key = (row["_make_key"], row["_model_key"])
        groups[key].append(idx)  # type: ignore[arg-type]

    selected_indices: list[int] = []
    for key, indices in sorted(groups.items()):
        sample = rng.sample(indices, min(ROWS_PER_MODEL, len(indices)))
        selected_indices.extend(sample)

    sampled = combined.loc[selected_indices].copy()
    sampled = sampled.drop(columns=["_make_key", "_model_key"], errors="ignore")

    # Validate: keep only rows that pass is_valid_comparable
    valid_rows: list[dict] = []
    for _, row in sampled.iterrows():
        listing = _kaggle_row_to_listing(row, str(row.get("make", "")))
        if is_valid_comparable(listing):
            valid_rows.append({
                "make":          listing.make,
                "model":         listing.model,
                "year":          listing.year,
                "mileage":       listing.mileage_miles,
                "fuel_type":     listing.fuel_type,
                "transmission":  listing.transmission,
                "engine_size":   listing.engine_size_l,
                "price":         listing.price_gbp,
            })

    out = pd.DataFrame(valid_rows)
    out.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(out):,} rows to {OUTPUT}")

    # Profile
    profile: dict = {
        "source": "kaggle:adityadesai13/used-car-dataset-ford-and-mercedes",
        "total_rows": len(out),
        "rows_per_model_cap": ROWS_PER_MODEL,
        "per_make_model": {},
    }
    for (mk, mo), count in sorted(
        out.groupby(["make", "model"]).size().items()
    ):
        profile["per_make_model"][f"{mk}/{mo}"] = int(count)

    PROFILE.write_text(json.dumps(profile, indent=2))
    print(f"Wrote profile to {PROFILE}")


def _build_synthetic() -> None:
    """Fallback: generate a small synthetic sample with realistic prices."""
    BASE_PRICE = 16_000
    DEPRECIATION = 0.87
    rng = random.Random(RANDOM_SEED)
    MAKES_MODELS = [
        ("ford", "fiesta"), ("ford", "focus"), ("vauxhall", "corsa"),
        ("bmw", "3 series"), ("audi", "a3"), ("toyota", "yaris"),
        ("vw", "golf"), ("mercedes", "c class"), ("skoda", "octavia"),
    ]
    rows = []
    for _ in range(150):
        make, model = rng.choice(MAKES_MODELS)
        year = rng.randint(2012, 2024)
        mileage = rng.randint(5_000, 120_000)
        age = 2024 - year
        price = max(500, int(BASE_PRICE * (DEPRECIATION ** age) * max(0.55, 1 - mileage / 350_000)
                              + rng.gauss(0, 600)))
        rows.append({
            "make": make, "model": model, "year": year, "mileage": mileage,
            "fuel_type": rng.choice(["petrol", "diesel", "hybrid"]),
            "transmission": rng.choice(["manual", "automatic"]),
            "engine_size": round(rng.uniform(1.0, 3.0), 1),
            "price": price,
        })
    pd.DataFrame(rows).to_csv(OUTPUT, index=False)
    print(f"Wrote {len(rows)} synthetic rows to {OUTPUT}")


if __name__ == "__main__":
    main()
