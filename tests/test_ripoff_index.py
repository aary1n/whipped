from whipped.domain.models import PriceRange
from whipped.scoring.ripoff import compute


def _pr(low: int, mid: int, high: int) -> PriceRange:
    return PriceRange(lower_gbp=low, mid_gbp=mid, upper_gbp=high,
                      confidence=0.8, comparable_count=20)


def test_bargain():
    r = compute(4_500, _pr(5_000, 7_000, 9_000))
    assert r.ripoff_index < 20
    assert r.ripoff_band == "bargain"
    assert r.pricing_position == "below range"


def test_within_range_fair():
    r = compute(7_000, _pr(5_000, 7_000, 9_000))
    assert 30 <= r.ripoff_index <= 70
    assert r.pricing_position == "within range"


def test_above_range_ripoff():
    r = compute(9_500, _pr(5_000, 7_000, 9_000))
    assert r.ripoff_index > 80
    assert r.pricing_position == "above range"


def test_at_midpoint_is_fair():
    r = compute(7_000, _pr(5_000, 7_000, 9_000))
    assert r.ripoff_band in ("good_deal", "fair")


def test_no_data():
    r = compute(5_000, PriceRange(lower_gbp=0, mid_gbp=0, upper_gbp=0,
                                  confidence=0.0, comparable_count=0))
    assert r.ripoff_band == "unknown"
    assert r.pricing_position == "unknown"
