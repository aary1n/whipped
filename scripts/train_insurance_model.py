from __future__ import annotations

import argparse
from pathlib import Path

from whipped.config import INSURANCE_MODEL
from whipped.insurance.model import train_insurance_model


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the insurance premium model from real quote CSV exports.")
    parser.add_argument("csv_files", nargs="+", type=Path, help="One or more CSV files containing real quote data.")
    parser.add_argument("--output", type=Path, default=INSURANCE_MODEL, help=f"Model output path. Defaults to {INSURANCE_MODEL}.")
    parser.add_argument("--epochs", type=int, default=800)
    parser.add_argument("--learning-rate", type=float, default=0.01)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    model = train_insurance_model(args.csv_files, args.output, epochs=args.epochs, learning_rate=args.learning_rate)
    print(f"Trained insurance model on {model.training_rows} rows and wrote {args.output}")


if __name__ == "__main__":
    main()
