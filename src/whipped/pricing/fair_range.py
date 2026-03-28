"""Estimate fair price range from comparable listings."""
from __future__ import annotations

import statistics

from whipped.domain.models import FeatureVector, Listing, PriceRange

MIN_COMPARABLES = 3
DEFAULT_CONFIDENCE = 0.1


def estimate(target: FeatureVector, comparables: list[Listing]) -> PriceRange:
    prices = _filter_comparable_prices(target, comparables)

    if len(prices) < MIN_COMPARABLES:
        return PriceRange(low=0, mid=0, high=0, confidence=DEFAULT_CONFIDENCE, n_comparables=len(prices))

    prices.sort()
    n = len(prices)
    low = prices[max(0, n // 10)]
    mid = int(statistics.median(prices))
    high = prices[min(n - 1, n * 9 // 10)]
    spread = high - low if high > low else 1
    confidence = min(1.0, n / 50) * max(0.3, 1.0 - spread / mid)

    return PriceRange(low=low, mid=mid, high=high, confidence=round(confidence, 2), n_comparables=n)


def _filter_comparable_prices(target: FeatureVector, listings: list[Listing]) -> list[int]:
    """Filter listings to those comparable to target, return their prices."""
    prices: list[int] = []
    for listing in listings:
        if listing.asking_price is None:
            continue
        age = _listing_age(listing)
        if age is not None and abs(age - target.age) > 3:
            continue
        if target.fuel_type and listing.fuel_type and listing.fuel_type.lower() != target.fuel_type.lower():
            continue
        prices.append(listing.asking_price)
    return prices


def _listing_age(listing: Listing) -> int | None:
    from datetime import date
    if listing.year:
        return date.today().year - listing.year
    return None
