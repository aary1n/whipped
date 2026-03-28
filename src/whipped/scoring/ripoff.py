"""Compute how overpriced a listing is relative to its fair range."""
from __future__ import annotations

from whipped.domain.models import PriceRange, RipoffIndex

LABELS = [
    (20, "bargain"),
    (40, "good_deal"),
    (60, "fair"),
    (80, "overpriced"),
    (100, "ripoff"),
]


def compute(asking_price: int, price_range: PriceRange) -> RipoffIndex:
    if price_range.mid == 0:
        return RipoffIndex(score=50, label="unknown")

    spread = price_range.high - price_range.low
    if spread == 0:
        position = 50
    else:
        position = (asking_price - price_range.low) / spread * 100

    score = max(0, min(100, int(position)))
    label = _label_for(score)
    return RipoffIndex(score=score, label=label)


def _label_for(score: int) -> str:
    for threshold, label in LABELS:
        if score <= threshold:
            return label
    return "extreme_ripoff"
