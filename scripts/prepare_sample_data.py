"""Generate sample.csv from a raw dataset or create synthetic sample data."""
from __future__ import annotations

import csv
import random
from pathlib import Path

from whipped.config import SAMPLE_DIR

SAMPLE_SIZE = 100
OUTPUT = SAMPLE_DIR / "sample.csv"

MAKES_MODELS = [
    ("ford", "fiesta"), ("ford", "focus"), ("vauxhall", "corsa"),
    ("bmw", "3series"), ("audi", "a3"), ("toyota", "yaris"),
    ("honda", "civic"), ("vw", "golf"), ("mercedes", "cclass"),
]


def main() -> None:
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    random.seed(42)

    with open(OUTPUT, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "make", "model", "year", "mileage", "fuel_type",
            "transmission", "engine_size", "price",
        ])
        writer.writeheader()
        for _ in range(SAMPLE_SIZE):
            make, model = random.choice(MAKES_MODELS)
            year = random.randint(2010, 2024)
            mileage = random.randint(5_000, 120_000)
            writer.writerow({
                "make": make,
                "model": model,
                "year": year,
                "mileage": mileage,
                "fuel_type": random.choice(["petrol", "diesel", "hybrid"]),
                "transmission": random.choice(["manual", "automatic"]),
                "engine_size": round(random.uniform(1.0, 3.0), 1),
                "price": int(3_000 + (2024 - year) * -200 + mileage * -0.02 + random.gauss(0, 2000)),
            })

    print(f"Wrote {SAMPLE_SIZE} rows to {OUTPUT}")


if __name__ == "__main__":
    main()
