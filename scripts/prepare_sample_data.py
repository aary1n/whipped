"""Generate sample.csv with realistic synthetic prices (no negatives)."""
from __future__ import annotations

import csv
import random

from whipped.config import SAMPLE_DIR

SAMPLE_SIZE = 100
OUTPUT = SAMPLE_DIR / "sample.csv"

MAKES_MODELS = [
    ("ford", "fiesta"), ("ford", "focus"), ("vauxhall", "corsa"),
    ("bmw", "3series"), ("audi", "a3"), ("toyota", "yaris"),
    ("honda", "civic"), ("vw", "golf"), ("mercedes", "cclass"),
]

BASE_PRICE = 16_000
ANNUAL_DEPRECIATION = 0.87   # 13% per year
MIN_PRICE = 500


def _synthetic_price(year: int, mileage: int, rng: random.Random) -> int:
    age = 2024 - year
    base = BASE_PRICE * (ANNUAL_DEPRECIATION ** age)
    mileage_factor = max(0.55, 1.0 - mileage / 350_000)
    noise = rng.gauss(0, max(300, base * 0.07))
    return max(MIN_PRICE, int(base * mileage_factor + noise))


def main() -> None:
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(42)

    with open(OUTPUT, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "make", "model", "year", "mileage", "fuel_type",
            "transmission", "engine_size", "price",
        ])
        writer.writeheader()
        for _ in range(SAMPLE_SIZE):
            make, model = rng.choice(MAKES_MODELS)
            year = rng.randint(2010, 2024)
            mileage = rng.randint(5_000, 120_000)
            writer.writerow({
                "make": make,
                "model": model,
                "year": year,
                "mileage": mileage,
                "fuel_type": rng.choice(["petrol", "diesel", "hybrid"]),
                "transmission": rng.choice(["manual", "automatic"]),
                "engine_size": round(rng.uniform(1.0, 3.0), 1),
                "price": _synthetic_price(year, mileage, rng),
            })

    print(f"Wrote {SAMPLE_SIZE} rows to {OUTPUT}")


if __name__ == "__main__":
    main()
