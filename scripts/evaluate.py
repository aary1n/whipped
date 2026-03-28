"""Evaluate a single listing against the full Kaggle dataset.

Usage:
    python scripts/evaluate.py --make ford --model fiesta --year 2020 \
        --mileage 33000 --fuel petrol --price 9300

Falls back to sample CSV if Kaggle raw data is not present.
"""
from __future__ import annotations

import argparse

from whipped.app import evaluate
from whipped.config import KAGGLE_RAW_DIR, SAMPLE_CSV
from whipped.domain.models import Listing
from whipped.ingest.datasets import load_csv, load_kaggle_raw


def load_comparables() -> list[Listing]:
    if KAGGLE_RAW_DIR.exists() and any(KAGGLE_RAW_DIR.glob("*.csv")):
        listings = load_kaggle_raw(KAGGLE_RAW_DIR)
        if listings:
            print(f"Loaded {len(listings):,} comparables from Kaggle raw data.\n")
            return listings
    if SAMPLE_CSV.exists():
        listings = load_csv(SAMPLE_CSV)
        print(f"Kaggle raw data not found — loaded {len(listings):,} comparables from sample CSV.\n")
        return listings
    print("ERROR: No comparables found. Run scripts/download_data.py first.")
    return []


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate a used-car listing.")
    p.add_argument("--make",    required=True)
    p.add_argument("--model",   required=True)
    p.add_argument("--year",    required=True, type=int)
    p.add_argument("--price",   required=True, type=int, help="Asking price in GBP")
    p.add_argument("--mileage", type=int,   default=None)
    p.add_argument("--fuel",    default=None, dest="fuel_type",
                   choices=["petrol", "diesel", "hybrid", "electric"])
    p.add_argument("--transmission", default=None, choices=["manual", "automatic"])
    p.add_argument("--seller",  default=None, dest="seller_type",
                   choices=["dealer", "private"])
    return p.parse_args()


def main() -> None:
    args = parse_args()
    listing = Listing(
        make=args.make.lower(),
        model=args.model.lower(),
        year=args.year,
        price_gbp=args.price,
        mileage_miles=args.mileage,
        fuel_type=args.fuel_type,
        transmission=args.transmission,
        seller_type=args.seller_type,
    )

    comps = load_comparables()
    if not comps:
        return

    v = evaluate(listing, comps)
    pr = v.price_range

    print(f"{'='*50}")
    print(f"  {args.make.title()} {args.model.title()} {args.year}")
    print(f"{'='*50}")
    print(f"  Asking price : £{listing.price_gbp:,}")
    print(f"  Fair range   : £{pr.lower_gbp:,} – £{pr.upper_gbp:,}  (mid £{pr.mid_gbp:,})")
    print(f"  Strategy     : {pr.strategy_used}  |  n={pr.comparable_count}  |  confidence={pr.confidence:.0%}")
    print(f"  Ripoff       : {v.ripoff.ripoff_index}/100 — {v.ripoff.ripoff_band}  [{v.ripoff.pricing_position}]")
    print(f"  Risk         : {v.risk.risk_score}/100 — {v.risk.risk_band}")
    for flag in v.risk.flags:
        print(f"               • {flag}")
    if v.suggested_counteroffer_gbp:
        print(f"  Counteroffer : £{v.suggested_counteroffer_gbp:,}")
    print()
    print(f"  5-year ownership:")
    own = v.ownership
    print(f"    Insurance    £{own.estimated_insurance_5y_gbp:,}  ({own.insurance_band})")
    print(f"    Depreciation £{own.estimated_depreciation_5y_gbp:,}")
    print(f"    Repairs      £{own.estimated_repairs_5y_gbp:,}  ({own.repair_risk_pct}% risk)")
    print(f"    Annual cost  £{own.annual_running_cost_gbp:,}  ({own.ownership_band})")
    print()
    print(f"  Verdict: {v.explanation}")


if __name__ == "__main__":
    main()
