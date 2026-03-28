"""Tests for negotiation semantics: counteroffer correctness and action recommendations."""
from whipped.app import evaluate
from whipped.domain.models import Listing

# 10 solid comparables — enough for confident valuations (mid ~£9,300)
_COMPS = [
    Listing(make="ford", model="fiesta", year=y, fuel_type="petrol",
            mileage_miles=m, price_gbp=p)
    for y, m, p in [
        (2020, 30_000, 9_500), (2020, 35_000, 9_200), (2021, 22_000, 10_800),
        (2021, 28_000, 10_200), (2019, 45_000, 8_400), (2019, 50_000, 8_100),
        (2020, 40_000, 9_000), (2019, 38_000, 8_700), (2020, 32_000, 9_300),
        (2021, 25_000, 10_500),
    ]
]


# --- bargain cases ---

def test_bargain_no_counteroffer_above_asking():
    """When asking is below fair range, never suggest an offer above asking."""
    listing = Listing(make="ford", model="fiesta", year=2020,
                      mileage_miles=33_000, fuel_type="petrol", price_gbp=6_000)
    v = evaluate(listing, _COMPS)
    if v.suggested_counteroffer_gbp is not None:
        assert v.suggested_counteroffer_gbp < listing.price_gbp


def test_bargain_action_is_strong_buy():
    listing = Listing(make="ford", model="fiesta", year=2020,
                      mileage_miles=33_000, fuel_type="petrol", price_gbp=6_000)
    v = evaluate(listing, _COMPS)
    assert v.action_recommendation == "strong_buy"


def test_bargain_no_counteroffer():
    """Bargain cases should omit the counteroffer — ask is already a deal."""
    listing = Listing(make="ford", model="fiesta", year=2020,
                      mileage_miles=33_000, fuel_type="petrol", price_gbp=6_000)
    v = evaluate(listing, _COMPS)
    assert v.suggested_counteroffer_gbp is None


# --- fair / within-range cases ---

def test_within_range_action_is_negotiate():
    listing = Listing(make="ford", model="fiesta", year=2020,
                      mileage_miles=33_000, fuel_type="petrol", price_gbp=9_300)
    v = evaluate(listing, _COMPS)
    assert v.action_recommendation == "negotiate"


def test_within_range_offer_below_asking():
    listing = Listing(make="ford", model="fiesta", year=2020,
                      mileage_miles=33_000, fuel_type="petrol", price_gbp=9_300)
    v = evaluate(listing, _COMPS)
    if v.suggested_counteroffer_gbp is not None:
        assert v.suggested_counteroffer_gbp < listing.price_gbp


# --- overpriced cases ---

def test_overpriced_offer_below_asking():
    listing = Listing(make="ford", model="fiesta", year=2020,
                      mileage_miles=33_000, fuel_type="petrol", price_gbp=15_000)
    v = evaluate(listing, _COMPS)
    if v.suggested_counteroffer_gbp is not None:
        assert v.suggested_counteroffer_gbp < listing.price_gbp


def test_overpriced_action_is_avoid_or_negotiate():
    listing = Listing(make="ford", model="fiesta", year=2020,
                      mileage_miles=33_000, fuel_type="petrol", price_gbp=15_000)
    v = evaluate(listing, _COMPS)
    assert v.action_recommendation in ("avoid", "negotiate")


def test_overpriced_offer_anchored_below_midpoint():
    """Offer for an overpriced listing should be near or below mid, not near asking."""
    listing = Listing(make="ford", model="fiesta", year=2020,
                      mileage_miles=33_000, fuel_type="petrol", price_gbp=15_000)
    v = evaluate(listing, _COMPS)
    if v.suggested_counteroffer_gbp is not None:
        assert v.suggested_counteroffer_gbp <= v.price_range.upper_gbp


# --- low confidence / sparse ---

def test_low_confidence_no_offer():
    sparse = [
        Listing(make="ford", model="fiesta", year=2020, price_gbp=p)
        for p in [8_000, 9_000, 9_500, 8_500]
    ]
    listing = Listing(make="ford", model="fiesta", year=2020, price_gbp=15_000)
    v = evaluate(listing, sparse)
    assert v.suggested_counteroffer_gbp is None
    assert v.action_recommendation == "insufficient_data"


def test_no_data_action_is_insufficient_data():
    listing = Listing(make="lada", model="niva", year=2005, price_gbp=2_000)
    v = evaluate(listing, _COMPS)
    assert v.action_recommendation == "insufficient_data"
    assert v.suggested_counteroffer_gbp is None


# --- universal safety invariants ---

def test_offer_never_above_asking():
    cases = [5_000, 9_300, 15_000, 20_000]
    for price in cases:
        listing = Listing(make="ford", model="fiesta", year=2020,
                          mileage_miles=33_000, fuel_type="petrol", price_gbp=price)
        v = evaluate(listing, _COMPS)
        if v.suggested_counteroffer_gbp is not None:
            assert v.suggested_counteroffer_gbp < price, (
                f"price={price}, offer={v.suggested_counteroffer_gbp}"
            )


def test_offer_never_negative():
    cases = [5_000, 9_300, 15_000]
    for price in cases:
        listing = Listing(make="ford", model="fiesta", year=2020,
                          mileage_miles=33_000, fuel_type="petrol", price_gbp=price)
        v = evaluate(listing, _COMPS)
        if v.suggested_counteroffer_gbp is not None:
            assert v.suggested_counteroffer_gbp >= 500


# --- risk floor ---

def test_risk_score_never_zero():
    """Every used car should have at least a baseline non-zero risk score."""
    listing = Listing(make="ford", model="fiesta", year=2022,
                      mileage_miles=10_000, fuel_type="petrol",
                      transmission="manual", price_gbp=9_500)
    v = evaluate(listing, _COMPS)
    assert v.risk.risk_score > 0


def test_risk_floor_is_low_band():
    """Baseline risk should still be classified as 'low', not medium/high."""
    listing = Listing(make="ford", model="fiesta", year=2022,
                      mileage_miles=10_000, fuel_type="petrol",
                      transmission="manual", price_gbp=9_500)
    v = evaluate(listing, _COMPS)
    assert v.risk.risk_band == "low"
