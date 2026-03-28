"""Mocked end-to-end demo — no external data required."""
from __future__ import annotations

from whipped.app import evaluate
from whipped.domain.models import Listing

# 20 synthetic Ford Fiesta comparables (2019-2022, petrol)
_FIESTA_COMPS = [
    Listing(make="ford", model="fiesta", year=y, fuel_type="petrol",
            mileage_miles=m, price_gbp=p)
    for y, m, p in [
        (2020, 30_000, 9_500), (2020, 35_000, 9_200), (2021, 22_000, 10_800),
        (2021, 28_000, 10_200), (2019, 45_000, 8_400), (2019, 50_000, 8_100),
        (2020, 40_000, 9_000), (2022, 15_000, 12_500), (2022, 18_000, 12_000),
        (2019, 38_000, 8_700), (2020, 32_000, 9_300), (2021, 25_000, 10_500),
        (2019, 55_000, 7_900), (2020, 42_000, 8_900), (2021, 30_000, 10_000),
        (2022, 20_000, 11_800), (2019, 48_000, 8_300), (2020, 36_000, 9_100),
        (2021, 27_000, 10_300), (2020, 33_000, 9_400),
    ]
]

SCENARIOS = [
    (
        "Fair deal",
        Listing(make="ford", model="fiesta", year=2020, fuel_type="petrol",
                mileage_miles=33_000, transmission="manual",
                engine_size_l=1.0, price_gbp=9_300),
    ),
    (
        "Overpriced deal",
        Listing(make="ford", model="fiesta", year=2019, fuel_type="petrol",
                mileage_miles=50_000, transmission="manual",
                engine_size_l=1.0, price_gbp=13_500),
    ),
    (
        "Suspiciously cheap / risky",
        Listing(make="ford", model="fiesta", year=2019, fuel_type="petrol",
                mileage_miles=98_000, transmission="manual",
                engine_size_l=1.0, price_gbp=4_200,
                seller_type="private"),
    ),
]


def _print_verdict(label: str, v: object) -> None:  # type: ignore[type-arg]
    from whipped.domain.models import WhippedVerdict
    assert isinstance(v, WhippedVerdict)
    print(f"\n{'='*55}")
    print(f"  {label}")
    print(f"{'='*55}")
    l = v.listing
    print(f"  {l.year} {l.make.title()} {l.model.title()} | {l.mileage_miles:,} mi | £{l.price_gbp:,}")
    pr = v.price_range
    print(f"  Fair range : £{pr.lower_gbp:,}–£{pr.upper_gbp:,}  (mid £{pr.mid_gbp:,})")
    print(f"  Confidence : {pr.confidence:.0%}  |  strategy: {pr.strategy_used}")
    print(f"  Ripoff     : {v.ripoff.ripoff_index}/100 — {v.ripoff.ripoff_band}  [{v.ripoff.pricing_position}]")
    print(f"  Risk       : {v.risk.risk_score}/100 — {v.risk.risk_band}")
    if v.risk.flags:
        for flag in v.risk.flags:
            print(f"               • {flag}")
    if v.suggested_counteroffer_gbp:
        print(f"  Counteroffer: £{v.suggested_counteroffer_gbp:,}")
    print(f"\n  {v.explanation}")


def main() -> None:
    for label, listing in SCENARIOS:
        verdict = evaluate(listing, _FIESTA_COMPS)
        _print_verdict(label, verdict)


if __name__ == "__main__":
    main()
