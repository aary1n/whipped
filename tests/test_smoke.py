from whipped.app import evaluate
from whipped.domain.models import Listing, WhippedVerdict
from whipped.features.extract import extract
from whipped.ingest.datasets import is_valid_comparable
from whipped.ingest.listings import parse_listing

# 10 valid comparables — enough for a usable but not strong range
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


# --- existing tests ---

def test_parse_listing_extracts_make():
    listing = parse_listing("2019 Ford Fiesta 1.0l petrol 30,000 miles £7,500")
    assert listing.make.lower() == "ford"
    assert listing.price_gbp == 7_500


def test_feature_extraction():
    listing = Listing(make="ford", model="fiesta", year=2020,
                      mileage_miles=50_000, fuel_type="petrol")
    fv = extract(listing)
    assert fv.age >= 4
    assert fv.mileage_band == "medium"
    assert fv.make == "ford"


def test_end_to_end_returns_verdict():
    listing = Listing(make="ford", model="fiesta", year=2020,
                      mileage_miles=33_000, fuel_type="petrol", price_gbp=9_300)
    verdict = evaluate(listing, _COMPS)
    assert isinstance(verdict, WhippedVerdict)
    assert verdict.price_range.mid_gbp > 0
    assert 0 <= verdict.ripoff.ripoff_index <= 100
    assert 0 <= verdict.risk.risk_score <= 100
    assert verdict.explanation


def test_fair_deal_ripoff_band():
    listing = Listing(make="ford", model="fiesta", year=2020,
                      mileage_miles=33_000, fuel_type="petrol", price_gbp=9_300)
    verdict = evaluate(listing, _COMPS)
    assert verdict.ripoff.ripoff_band in ("good_deal", "fair", "overpriced")


def test_risk_high_mileage_flag():
    listing = Listing(make="ford", model="fiesta", year=2019,
                      mileage_miles=98_000, fuel_type="petrol", price_gbp=4_200,
                      seller_type="private")
    verdict = evaluate(listing, _COMPS)
    flag_text = " ".join(verdict.risk.flags)
    assert "mileage" in flag_text or "private" in flag_text


# --- safety / guardrail tests ---

def test_invalid_prices_rejected_by_validator():
    assert not is_valid_comparable(Listing(make="ford", model="fiesta", year=2020, price_gbp=-500))
    assert not is_valid_comparable(Listing(make="ford", model="fiesta", year=2020, price_gbp=0))
    assert not is_valid_comparable(Listing(make="ford", model="fiesta", year=2020, price_gbp=None))
    assert not is_valid_comparable(Listing(make="ford", model="fiesta", year=1985, price_gbp=5_000))
    assert is_valid_comparable(Listing(make="ford", model="fiesta", year=2020, price_gbp=500))


def test_fair_range_never_negative():
    listing = Listing(make="ford", model="fiesta", year=2020, price_gbp=9_300)
    verdict = evaluate(listing, _COMPS)
    assert verdict.price_range.lower_gbp >= 0
    assert verdict.price_range.mid_gbp >= 0
    assert verdict.price_range.upper_gbp >= 0


def test_fair_range_internally_ordered():
    listing = Listing(make="ford", model="fiesta", year=2020, price_gbp=9_300)
    verdict = evaluate(listing, _COMPS)
    pr = verdict.price_range
    assert pr.lower_gbp <= pr.mid_gbp <= pr.upper_gbp


def test_counteroffer_never_negative():
    # Use a listing where counteroffer might be generated
    listing = Listing(make="ford", model="fiesta", year=2020,
                      mileage_miles=33_000, fuel_type="petrol", price_gbp=15_000)
    verdict = evaluate(listing, _COMPS)
    if verdict.suggested_counteroffer_gbp is not None:
        assert verdict.suggested_counteroffer_gbp >= 500


def test_sparse_comps_confidence_capped():
    sparse = [
        Listing(make="ford", model="fiesta", year=2020, price_gbp=p)
        for p in [8_000, 9_000, 9_500, 8_500]  # only 4 comps
    ]
    listing = Listing(make="ford", model="fiesta", year=2020, price_gbp=9_000)
    verdict = evaluate(listing, sparse)
    assert verdict.price_range.confidence <= 0.25


def test_sparse_comps_no_counteroffer():
    sparse = [
        Listing(make="ford", model="fiesta", year=2020, price_gbp=p)
        for p in [8_000, 9_000, 9_500, 8_500]  # only 4 comps — below threshold
    ]
    listing = Listing(make="ford", model="fiesta", year=2020, price_gbp=15_000)
    verdict = evaluate(listing, sparse)
    assert verdict.suggested_counteroffer_gbp is None


def test_unknown_vehicle_no_data_no_counteroffer():
    listing = Listing(make="lada", model="niva", year=2005, price_gbp=2_000)
    verdict = evaluate(listing, _COMPS)
    assert verdict.price_range.strategy_used == "no_data"
    assert verdict.price_range.confidence == 0.0
    assert verdict.suggested_counteroffer_gbp is None


def test_no_comparables_returns_low_confidence():
    listing = Listing(make="rover", model="75", year=2001,
                      mileage_miles=120_000, price_gbp=1_500)
    verdict = evaluate(listing, _COMPS)
    assert verdict.price_range.confidence == 0.0
