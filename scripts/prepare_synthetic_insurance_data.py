from __future__ import annotations

import argparse

from whipped.config import INSURANCE_SYNTHETIC_CSV
from whipped.insurance.synthetic import generate_synthetic_insurance_dataset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a synthetic insurance quote dataset for local model training.")
    parser.add_argument("--rows", type=int, default=6000)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frame = generate_synthetic_insurance_dataset(
        INSURANCE_SYNTHETIC_CSV,
        rows=args.rows,
        seed=args.seed,
    )
    print(f"Wrote {len(frame)} rows to {INSURANCE_SYNTHETIC_CSV}")


if __name__ == "__main__":
    main()
