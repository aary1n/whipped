"""Quick sanity check of the pipeline against the synthetic sample dataset."""
from __future__ import annotations

from whipped.app import evaluate
from whipped.config import SAMPLE_CSV
from whipped.domain.models import Listing
from whipped.ingest.datasets import load_csv

CASES = [
    ("Ford Fiesta 2020",      Listing(make="ford",     model="fiesta",  year=2020, mileage_miles=33_000, fuel_type="petrol",  price_gbp=9_300)),
    ("Vauxhall Corsa 2019",   Listing(make="vauxhall", model="corsa",   year=2019, mileage_miles=45_000, fuel_type="petrol",  price_gbp=7_500)),
    ("BMW 3 Series 2018",     Listing(make="bmw",      model="3 series", year=2018, mileage_miles=60_000, fuel_type="diesel",  price_gbp=14_000)),
    ("Toyota Yaris 2021",     Listing(make="toyota",   model="yaris",   year=2021, mileage_miles=20_000, fuel_type="hybrid",  price_gbp=13_000)),
    ("Unknown make (sparse)", Listing(make="rover",    model="75",      year=2001, mileage_miles=120_000,                     price_gbp=1_500)),
]


def main() -> None:
    if not SAMPLE_CSV.exists():
        print(f"ERROR: {SAMPLE_CSV} not found — run `python scripts/prepare_sample_data.py` first.")
        return

    comps = load_csv(SAMPLE_CSV)
    print(f"Loaded {len(comps)} comparables from {SAMPLE_CSV.name}\n")

    for label, listing in CASES:
        v = evaluate(listing, comps)
        pr = v.price_range
        print(f"--- {label} ---")
        print(f"  Asking      : £{listing.price_gbp:,}")
        print(f"  Fair range  : £{pr.lower_gbp:,}–£{pr.upper_gbp:,}  (mid £{pr.mid_gbp:,})")
        print(f"  Strategy    : {pr.strategy_used}  |  n={pr.comparable_count}  |  confidence={pr.confidence:.0%}")
        print(f"  Ripoff      : {v.ripoff.ripoff_index}/100 — {v.ripoff.ripoff_band}  [{v.ripoff.pricing_position}]")
        print(f"  Risk        : {v.risk.risk_score}/100 — {v.risk.risk_band}")
        if v.risk.flags:
            for f in v.risk.flags:
                print(f"                • {f}")
        if v.suggested_counteroffer_gbp:
            print(f"  Counteroffer: £{v.suggested_counteroffer_gbp:,}")
        print()


if __name__ == "__main__":
    main()
