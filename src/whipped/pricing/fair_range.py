from __future__ import annotations

import statistics
from datetime import date

from whipped.domain.models import FeatureVector, Listing, PriceRange

CURRENT_YEAR = date.today().year
MIN_COMPARABLES = 3
MAX_YEAR_DELTA = 3


def estimate(target: FeatureVector, comparables: list[Listing]) -> PriceRange:
    # Try progressively looser filters until we have enough comparables
    for strategy, prices in _strategies(target, comparables):
        if len(prices) >= MIN_COMPARABLES:
            return _build_range(prices, strategy)

    # Insufficient data — return wide low-confidence fallback
    all_prices = [c.price_gbp for c in comparables if c.price_gbp is not None]
    if all_prices:
        mid = int(statistics.median(all_prices))
        return PriceRange(
            lower_gbp=int(mid * 0.7),
            mid_gbp=mid,
            upper_gbp=int(mid * 1.3),
            confidence=0.1,
            comparable_count=len(all_prices),
            strategy_used="corpus_fallback",
        )

    return PriceRange(lower_gbp=0, mid_gbp=0, upper_gbp=0, confidence=0.0,
                      comparable_count=0, strategy_used="no_data")


def _strategies(
    target: FeatureVector, comparables: list[Listing]
) -> list[tuple[str, list[int]]]:
    make, model, age = target.make, target.model, target.age
    fuel = target.fuel_type

    def prices_for(listings: list[Listing]) -> list[int]:
        return [c.price_gbp for c in listings if c.price_gbp is not None]

    # 1. make + model + year + fuel
    s1 = [
        c for c in comparables
        if c.make.lower() == make and c.model.lower() == model
        and abs(CURRENT_YEAR - c.year - age) <= MAX_YEAR_DELTA
        and (not fuel or not c.fuel_type or c.fuel_type.lower() == fuel.lower())
    ]
    # 2. make + model + year (drop fuel)
    s2 = [
        c for c in comparables
        if c.make.lower() == make and c.model.lower() == model
        and abs(CURRENT_YEAR - c.year - age) <= MAX_YEAR_DELTA
    ]
    # 3. make + model (drop year)
    s3 = [c for c in comparables if c.make.lower() == make and c.model.lower() == model]
    # 4. make + year
    s4 = [
        c for c in comparables
        if c.make.lower() == make
        and abs(CURRENT_YEAR - c.year - age) <= MAX_YEAR_DELTA
    ]

    return [
        ("make_model_year_fuel", prices_for(s1)),
        ("make_model_year", prices_for(s2)),
        ("make_model", prices_for(s3)),
        ("make_year", prices_for(s4)),
    ]


def _build_range(prices: list[int], strategy: str) -> PriceRange:
    prices = sorted(prices)
    n = len(prices)
    lower = prices[max(0, n // 10)]
    mid = int(statistics.median(prices))
    upper = prices[min(n - 1, (n * 9) // 10)]

    spread_ratio = (upper - lower) / mid if mid > 0 else 1.0
    data_confidence = min(1.0, n / 30)
    tightness = max(0.0, 1.0 - spread_ratio)
    confidence = round(data_confidence * (0.5 + 0.5 * tightness), 2)

    return PriceRange(
        lower_gbp=lower,
        mid_gbp=mid,
        upper_gbp=upper,
        confidence=confidence,
        comparable_count=n,
        strategy_used=strategy,
    )
