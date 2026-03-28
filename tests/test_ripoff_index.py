from whipped.domain.models import PriceRange
from whipped.scoring.ripoff import compute


def test_bargain():
    pr = PriceRange(low=5000, mid=7000, high=9000, confidence=0.8, n_comparables=20)
    result = compute(4500, pr)
    assert result.score < 20
    assert result.label == "bargain"


def test_fair():
    pr = PriceRange(low=5000, mid=7000, high=9000, confidence=0.8, n_comparables=20)
    result = compute(7000, pr)
    assert 30 <= result.score <= 70


def test_ripoff():
    pr = PriceRange(low=5000, mid=7000, high=9000, confidence=0.8, n_comparables=20)
    result = compute(9500, pr)
    assert result.score > 80


def test_zero_range():
    pr = PriceRange(low=0, mid=0, high=0, confidence=0.1, n_comparables=0)
    result = compute(5000, pr)
    assert result.label == "unknown"
