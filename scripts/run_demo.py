"""Presentation-friendly end-to-end demo with optional rich output.

Run:
    python scripts/run_demo.py
    python scripts/run_demo.py --plain
    python scripts/run_demo.py --scenario fair_deal
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass

from whipped.app import evaluate
from whipped.domain.models import DriverProfile, Listing, WhippedVerdict

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    _HAS_RICH = True
except ImportError:
    _HAS_RICH = False


# 20 synthetic Ford Fiesta comparables (2019-2022, petrol)
_FIESTA_COMPS = [
    Listing(make="ford", model="fiesta", year=y, fuel_type="petrol", mileage_miles=m, price_gbp=p)
    for y, m, p in [
        (2020, 30_000, 9_500),
        (2020, 35_000, 9_200),
        (2021, 22_000, 10_800),
        (2021, 28_000, 10_200),
        (2019, 45_000, 8_400),
        (2019, 50_000, 8_100),
        (2020, 40_000, 9_000),
        (2022, 15_000, 12_500),
        (2022, 18_000, 12_000),
        (2019, 38_000, 8_700),
        (2020, 32_000, 9_300),
        (2021, 25_000, 10_500),
        (2019, 55_000, 7_900),
        (2020, 42_000, 8_900),
        (2021, 30_000, 10_000),
        (2022, 20_000, 11_800),
        (2019, 48_000, 8_300),
        (2020, 36_000, 9_100),
        (2021, 27_000, 10_300),
        (2020, 33_000, 9_400),
    ]
]


@dataclass(frozen=True)
class DemoScenario:
    key: str
    title: str
    listing: Listing
    driver: DriverProfile | None = None


SCENARIOS = [
    DemoScenario(
        key="fair_deal",
        title="Fair Deal",
        listing=Listing(
            make="ford",
            model="fiesta",
            year=2020,
            fuel_type="petrol",
            mileage_miles=33_000,
            transmission="manual",
            engine_size_l=1.0,
            price_gbp=9_300,
        ),
    ),
    DemoScenario(
        key="overpriced",
        title="Overpriced Listing",
        listing=Listing(
            make="ford",
            model="fiesta",
            year=2019,
            fuel_type="petrol",
            mileage_miles=50_000,
            transmission="manual",
            engine_size_l=1.0,
            price_gbp=13_500,
        ),
    ),
    DemoScenario(
        key="cheap_risky",
        title="Suspiciously Cheap And Risky",
        listing=Listing(
            make="ford",
            model="fiesta",
            year=2019,
            fuel_type="petrol",
            mileage_miles=98_000,
            transmission="manual",
            engine_size_l=1.0,
            seller_type="private",
            price_gbp=4_200,
        ),
    ),
    DemoScenario(
        key="young_driver",
        title="Same Car, Young Driver",
        listing=Listing(
            make="ford",
            model="fiesta",
            year=2020,
            fuel_type="petrol",
            mileage_miles=33_000,
            transmission="manual",
            engine_size_l=1.0,
            body_type="hatchback",
            price_gbp=9_300,
        ),
        driver=DriverProfile(
            age=20,
            years_licensed=1,
            no_claims_years=0,
            claims_last_5y=1,
            annual_mileage=14_000,
            postcode_area="E",
            parking="street",
            cover_type="comprehensive",
        ),
    ),
    DemoScenario(
        key="experienced_driver",
        title="Same Car, Experienced Driver",
        listing=Listing(
            make="ford",
            model="fiesta",
            year=2020,
            fuel_type="petrol",
            mileage_miles=33_000,
            transmission="manual",
            engine_size_l=1.0,
            body_type="hatchback",
            price_gbp=9_300,
        ),
        driver=DriverProfile(
            age=38,
            years_licensed=18,
            no_claims_years=10,
            claims_last_5y=0,
            annual_mileage=8_000,
            postcode_area="BA",
            parking="garage",
            cover_type="comprehensive",
        ),
    ),
]


def _fmt_currency(value: int | None) -> str:
    return f"GBP {value:,}" if value is not None else "n/a"


def _print_plain(verdict: WhippedVerdict, title: str) -> None:
    listing = verdict.listing
    pr = verdict.price_range
    own = verdict.ownership

    print(f"\n{'=' * 70}")
    print(f"{title}")
    print(f"{'=' * 70}")
    print(f"Listing      : {listing.year} {listing.make.title()} {listing.model.title()} | {_fmt_currency(listing.price_gbp)} | {listing.mileage_miles:,} mi")
    print(f"Fair range   : {_fmt_currency(pr.lower_gbp)} - {_fmt_currency(pr.upper_gbp)} (mid {_fmt_currency(pr.mid_gbp)})")
    print(f"Confidence   : {pr.confidence:.0%} | strategy {pr.strategy_used} | comps {pr.comparable_count}")
    print(f"Ripoff       : {verdict.ripoff.ripoff_index}/100 ({verdict.ripoff.ripoff_band})")
    print(f"Risk         : {verdict.risk.risk_score}/100 ({verdict.risk.risk_band})")
    if verdict.risk.flags:
        for flag in verdict.risk.flags:
            print(f"  - {flag}")
    print(f"Action       : {verdict.action_recommendation}")
    print(f"Counteroffer : {_fmt_currency(verdict.suggested_counteroffer_gbp)}")
    print(f"Insurance    : {_fmt_currency(own.estimated_insurance_annual_gbp)}/yr, {_fmt_currency(own.estimated_insurance_5y_gbp)} over 5y")
    print(f"Ownership    : {_fmt_currency(own.annual_running_cost_gbp)}/yr, band {own.ownership_band}")
    print(f"Explanation  : {verdict.explanation}")


def _print_rich(console: Console, verdict: WhippedVerdict, title: str) -> None:
    listing = verdict.listing
    pr = verdict.price_range
    own = verdict.ownership

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="bold")
    table.add_column("Value")

    table.add_row("Listing", f"{listing.year} {listing.make.title()} {listing.model.title()} | {_fmt_currency(listing.price_gbp)} | {listing.mileage_miles:,} mi")
    table.add_row("Fair range", f"{_fmt_currency(pr.lower_gbp)} - {_fmt_currency(pr.upper_gbp)} (mid {_fmt_currency(pr.mid_gbp)})")
    table.add_row("Confidence", f"{pr.confidence:.0%} | strategy {pr.strategy_used} | comps {pr.comparable_count}")
    table.add_row("Ripoff", f"{verdict.ripoff.ripoff_index}/100 ({verdict.ripoff.ripoff_band})")
    table.add_row("Risk", f"{verdict.risk.risk_score}/100 ({verdict.risk.risk_band})")
    table.add_row("Action", verdict.action_recommendation)
    table.add_row("Counteroffer", _fmt_currency(verdict.suggested_counteroffer_gbp))
    table.add_row("Insurance", f"{_fmt_currency(own.estimated_insurance_annual_gbp)}/yr, {_fmt_currency(own.estimated_insurance_5y_gbp)} over 5y")
    table.add_row("Ownership", f"{_fmt_currency(own.annual_running_cost_gbp)}/yr, band {own.ownership_band}")
    if verdict.risk.flags:
        table.add_row("Flags", ", ".join(verdict.risk.flags))

    console.print(Panel(table, title=title, border_style="green"))
    console.print(Panel(verdict.explanation, title="Explanation", border_style="yellow"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run local demo scenarios for whipped.")
    parser.add_argument("--plain", action="store_true", help="Force plain output even if rich is installed.")
    parser.add_argument(
        "--scenario",
        action="append",
        choices=[s.key for s in SCENARIOS],
        help="Run only selected scenario key. Can be provided more than once.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    selected_keys = set(args.scenario or [])
    selected = [scenario for scenario in SCENARIOS if not selected_keys or scenario.key in selected_keys]

    if not selected:
        print("No scenarios selected.")
        return

    use_rich = _HAS_RICH and not args.plain
    if not use_rich and not args.plain:
        print("rich not installed. Running plain output. Install with: pip install rich")

    console = Console() if use_rich else None
    for scenario in selected:
        verdict = evaluate(scenario.listing, _FIESTA_COMPS, scenario.driver)
        if use_rich and console is not None:
            _print_rich(console, verdict, scenario.title)
        else:
            _print_plain(verdict, scenario.title)


if __name__ == "__main__":
    main()
