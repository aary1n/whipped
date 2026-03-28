from __future__ import annotations

import statistics
from datetime import date

from whipped.domain.models import FeatureVector, Listing, PriceRange

CURRENT_YEAR = date.today().year
MIN_COMPARABLES = 5
MIN_PRICE_FLOOR = 500    # no output price below this
MAX_SPREAD_RATIO = 0.60

_TIER_CONFIGS = [
    ("exact_make_model_tier1", 1, 0.15, True),
    ("exact_make_model_tier2", 2, 0.20, False),
    ("exact_make_model_tier3", 3, 0.30, False),
    ("wide_make_model_tier4", 4, None, False),
]

_TIER_SCORES = {
    "exact_make_model_tier1": 1.00,
    "exact_make_model_tier2": 0.85,
    "exact_make_model_tier3": 0.70,
    "wide_make_model_tier4": 0.55,
}


NO_DATA = PriceRange(lower_gbp=0, mid_gbp=0, upper_gbp=0,
                     confidence=0.0, comparable_count=0, strategy_used="no_data")


def estimate(target: FeatureVector, comparables: list[Listing]) -> PriceRange:
    best_sparse: tuple[str, list[int]] | None = None
    for strategy, prices in _strategies(target, comparables):
        if len(prices) >= MIN_COMPARABLES:
            return _build_range(prices, strategy, target, sparse=False)
        if prices and (best_sparse is None or len(prices) > len(best_sparse[1])):
            best_sparse = (strategy, prices)

    if best_sparse:
        strategy, prices = best_sparse
        return _build_range(prices, strategy, target, sparse=True)

    return NO_DATA


def _strategies(
    target: FeatureVector, comparables: list[Listing]
) -> list[tuple[str, list[int]]]:
    make, model = target.make, target.model
    target_year = CURRENT_YEAR - target.age

    def prices_for(subset: list[Listing]) -> list[int]:
        return [c.price_gbp for c in subset if c.price_gbp and c.price_gbp >= MIN_PRICE_FLOOR]

    results: list[tuple[str, list[int]]] = []
    for strategy, year_delta, mileage_tolerance, require_fuel_transmission in _TIER_CONFIGS:
        subset = [
            c for c in comparables
            if _is_comparable(
                target,
                c,
                make=make,
                model=model,
                target_year=target_year,
                year_delta=year_delta,
                mileage_tolerance=mileage_tolerance,
                require_fuel_transmission=require_fuel_transmission,
            )
        ]
        results.append((strategy, prices_for(subset)))
    return results


def _is_comparable(
    target: FeatureVector,
    candidate: Listing,
    *,
    make: str,
    model: str,
    target_year: int,
    year_delta: int,
    mileage_tolerance: float | None,
    require_fuel_transmission: bool,
) -> bool:
    if candidate.make.lower() != make or candidate.model.lower() != model:
        return False
    if abs(candidate.year - target_year) > year_delta:
        return False
    if mileage_tolerance is not None and target.mileage_miles and candidate.mileage_miles:
        max_delta = int(target.mileage_miles * mileage_tolerance)
        if abs(candidate.mileage_miles - target.mileage_miles) > max_delta:
            return False
    if require_fuel_transmission:
        if not _matches_optional(target.fuel_type, candidate.fuel_type):
            return False
        if not _matches_optional(target.transmission, candidate.transmission):
            return False
    return True


def _build_range(prices: list[int], strategy: str, target: FeatureVector, *, sparse: bool) -> PriceRange:
    prices = sorted(prices)
    n = len(prices)

    raw_lower = _percentile(prices, 0.25)
    raw_mid = int(statistics.median(prices))
    raw_upper = _percentile(prices, 0.75)

    # Clamp and preserve ordering
    lower = max(MIN_PRICE_FLOOR, raw_lower)
    mid = max(lower, raw_mid)
    upper = max(mid, raw_upper)

    confidence = _confidence(
        n=n,
        lower=lower,
        mid=mid,
        upper=upper,
        strategy=strategy,
        target=target,
        sparse=sparse,
    )

    return PriceRange(
        lower_gbp=lower,
        mid_gbp=mid,
        upper_gbp=upper,
        confidence=confidence,
        comparable_count=n,
        strategy_used=strategy,
    )


def _percentile(prices: list[int], pct: float) -> int:
    if not prices:
        return 0
    index = int(round((len(prices) - 1) * pct))
    return prices[index]


def _confidence(
    *,
    n: int,
    lower: int,
    mid: int,
    upper: int,
    strategy: str,
    target: FeatureVector,
    sparse: bool,
) -> float:
    spread_ratio = (upper - lower) / max(mid, 1)
    count_score = min(1.0, n / 20)
    spread_score = max(0.0, 1.0 - (spread_ratio / MAX_SPREAD_RATIO))
    tier_score = _TIER_SCORES.get(strategy, 0.4)

    missing_fields = [target.mileage_miles, target.fuel_type, target.transmission]
    missingness_penalty = min(0.30, 0.10 * sum(v is None for v in missing_fields))

    confidence = 0.05 + (0.45 * count_score) + (0.30 * spread_score) + (0.20 * tier_score)
    confidence -= missingness_penalty

    if sparse:
        confidence = min(confidence, 0.20)

    return round(max(0.0, min(1.0, confidence)), 2)


def _matches_optional(target_value: str | None, candidate_value: str | None) -> bool:
    if not target_value:
        return True
    if not candidate_value:
        return True
    return target_value.lower() == candidate_value.lower()
