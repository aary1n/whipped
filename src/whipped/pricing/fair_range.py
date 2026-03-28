from __future__ import annotations

import statistics
from datetime import date

from whipped.domain.models import FeatureVector, Listing, PriceRange

CURRENT_YEAR = date.today().year
MIN_COMPARABLES = 3      # absolute minimum to attempt a range
MAX_YEAR_DELTA = 3
MIN_PRICE_FLOOR = 500    # no output price below this

# Hard confidence caps by comparable count
_CONFIDENCE_CAPS = [
    (8,  0.25),   # n < 8:  very weak indication only
    (15, 0.55),   # 8 ≤ n < 15: moderate
]                 # n ≥ 15: formula runs uncapped (max ~1.0)

NO_DATA = PriceRange(lower_gbp=0, mid_gbp=0, upper_gbp=0,
                     confidence=0.0, comparable_count=0, strategy_used="no_data")


def estimate(target: FeatureVector, comparables: list[Listing]) -> PriceRange:
    for strategy, prices in _strategies(target, comparables):
        if len(prices) >= MIN_COMPARABLES:
            return _build_range(prices, strategy)
    return NO_DATA


def _strategies(
    target: FeatureVector, comparables: list[Listing]
) -> list[tuple[str, list[int]]]:
    make, model, age = target.make, target.model, target.age
    fuel = target.fuel_type

    def prices_for(subset: list[Listing]) -> list[int]:
        return [c.price_gbp for c in subset if c.price_gbp and c.price_gbp >= MIN_PRICE_FLOOR]

    s1 = [
        c for c in comparables
        if c.make.lower() == make and c.model.lower() == model
        and abs(CURRENT_YEAR - c.year - age) <= MAX_YEAR_DELTA
        and (not fuel or not c.fuel_type or c.fuel_type.lower() == fuel.lower())
    ]
    s2 = [
        c for c in comparables
        if c.make.lower() == make and c.model.lower() == model
        and abs(CURRENT_YEAR - c.year - age) <= MAX_YEAR_DELTA
    ]
    s3 = [c for c in comparables if c.make.lower() == make and c.model.lower() == model]
    s4 = [
        c for c in comparables
        if c.make.lower() == make
        and abs(CURRENT_YEAR - c.year - age) <= MAX_YEAR_DELTA
    ]

    return [
        ("make_model_year_fuel", prices_for(s1)),
        ("make_model_year",      prices_for(s2)),
        ("make_model",           prices_for(s3)),
        ("make_year",            prices_for(s4)),
    ]


def _build_range(prices: list[int], strategy: str) -> PriceRange:
    prices = sorted(prices)
    n = len(prices)

    raw_lower = prices[max(0, n // 10)]
    raw_mid   = int(statistics.median(prices))
    raw_upper = prices[min(n - 1, (n * 9) // 10)]

    # Clamp and preserve ordering
    lower = max(MIN_PRICE_FLOOR, raw_lower)
    mid   = max(lower, raw_mid)
    upper = max(mid, raw_upper)

    spread_ratio = (upper - lower) / mid if mid > 0 else 1.0
    data_conf    = min(1.0, n / 30)
    tightness    = max(0.0, 1.0 - spread_ratio)
    confidence   = round(data_conf * (0.5 + 0.5 * tightness), 2)

    # Apply hard cap for sparse data
    for threshold, cap in _CONFIDENCE_CAPS:
        if n < threshold:
            confidence = min(confidence, cap)
            break

    return PriceRange(
        lower_gbp=lower,
        mid_gbp=mid,
        upper_gbp=upper,
        confidence=confidence,
        comparable_count=n,
        strategy_used=strategy,
    )
