from __future__ import annotations

from dataclasses import replace
from typing import Callable

from whipped.domain.models import CounterfactualResult, DriverProfile, Listing, WhippedVerdict

Evaluator = Callable[[Listing, list[Listing], DriverProfile | None], WhippedVerdict]


def simulate(
    listing: Listing,
    comparables: list[Listing],
    driver: DriverProfile | None,
    baseline: WhippedVerdict,
    evaluator: Evaluator,
) -> list[CounterfactualResult]:
    """Run deterministic scenarios and report deltas against baseline."""
    scenarios: list[tuple[str, str, Listing, DriverProfile | None]] = [
        (
            "mileage_plus_10k",
            "Mileage +10k miles",
            replace(listing, mileage_miles=(listing.mileage_miles or 0) + 10_000),
            driver,
        ),
        (
            "offer_at_midpoint",
            "Offer at model midpoint",
            replace(listing, price_gbp=baseline.price_range.mid_gbp),
            driver,
        ),
    ]

    if driver is not None:
        stress_driver = replace(
            driver,
            claims_last_5y=driver.claims_last_5y + 1,
            annual_mileage=(driver.annual_mileage or 10_000) + 3_000,
            parking="street",
        )
        safer_driver = replace(
            driver,
            no_claims_years=(driver.no_claims_years or 0) + 2,
            claims_last_5y=max(0, driver.claims_last_5y - 1),
            parking="garage",
        )
        scenarios.extend(
            [
                ("insurance_stress", "Insurance stress case", listing, stress_driver),
                ("insurance_optimized", "Insurance optimized case", listing, safer_driver),
            ]
        )

    results: list[CounterfactualResult] = []
    baseline_total = _total_ownership_5y(baseline)
    for key, title, alt_listing, alt_driver in scenarios:
        alt = evaluator(alt_listing, comparables, alt_driver)
        alt_total = _total_ownership_5y(alt)
        results.append(
            CounterfactualResult(
                scenario_key=key,
                title=title,
                asking_price_gbp=alt_listing.price_gbp,
                mid_price_gbp=alt.price_range.mid_gbp,
                ripoff_index=alt.ripoff.ripoff_index,
                total_ownership_5y_gbp=alt_total,
                counteroffer_gbp=alt.suggested_counteroffer_gbp,
                delta_mid_price_gbp=alt.price_range.mid_gbp - baseline.price_range.mid_gbp,
                delta_ripoff_index=alt.ripoff.ripoff_index - baseline.ripoff.ripoff_index,
                delta_total_ownership_5y_gbp=alt_total - baseline_total,
            )
        )

    return results


def _total_ownership_5y(verdict: WhippedVerdict) -> int:
    return (
        verdict.ownership.estimated_insurance_5y_gbp
        + verdict.ownership.estimated_depreciation_5y_gbp
        + verdict.ownership.estimated_repairs_5y_gbp
    )
