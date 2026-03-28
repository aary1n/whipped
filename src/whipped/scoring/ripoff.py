from __future__ import annotations

from whipped.domain.models import PriceRange, RipoffAssessment

BANDS = [
    (20, "bargain"),
    (40, "good_deal"),
    (60, "fair"),
    (80, "overpriced"),
    (100, "ripoff"),
]


def compute(asking_price: int, price_range: PriceRange) -> RipoffAssessment:
    if price_range.mid_gbp == 0:
        return RipoffAssessment(
            ripoff_index=50, ripoff_band="unknown",
            pricing_position="unknown", notes="No comparable data available.",
        )

    spread = price_range.upper_gbp - price_range.lower_gbp
    if spread == 0:
        index = 50
    else:
        index = int((asking_price - price_range.lower_gbp) / spread * 100)

    index = max(0, min(100, index))
    band = _band_for(index)
    position = _position(asking_price, price_range)
    notes = _notes(asking_price, price_range, band)

    return RipoffAssessment(
        ripoff_index=index,
        ripoff_band=band,
        pricing_position=position,
        notes=notes,
    )


def _band_for(index: int) -> str:
    for threshold, band in BANDS:
        if index <= threshold:
            return band
    return "extreme_ripoff"


def _position(asking: int, pr: PriceRange) -> str:
    if asking < pr.lower_gbp:
        return "below range"
    if asking > pr.upper_gbp:
        return "above range"
    return "within range"


def _notes(asking: int, pr: PriceRange, band: str) -> str:
    diff = asking - pr.mid_gbp
    direction = "above" if diff >= 0 else "below"
    return f"Asking is £{abs(diff):,} {direction} the market midpoint ({band})."
