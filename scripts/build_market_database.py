"""Build a local SQLite market database from Auto Trader-style CSV exports."""
from __future__ import annotations

import argparse
from pathlib import Path

from whipped.config import MARKET_DB
from whipped.ingest.market_database import build_market_database


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import Auto Trader CSV exports into a local SQLite database.",
    )
    parser.add_argument(
        "csv_files",
        nargs="+",
        type=Path,
        help="One or more CSV exports with car listing data.",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=MARKET_DB,
        help=f"Output SQLite file. Defaults to {MARKET_DB}.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    inserted = build_market_database(args.csv_files, args.db)
    print(f"Imported {inserted} listings into {args.db}")


if __name__ == "__main__":
    main()
