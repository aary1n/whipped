from whipped.domain.models import Listing
from whipped.features.extract import extract
from whipped.ingest.listings import parse_listing


def test_parse_listing_extracts_make():
    listing = parse_listing("2019 Ford Fiesta 1.0l petrol 30,000 miles £7,500")
    assert listing.make.lower() == "ford"
    assert listing.asking_price == 7_500


def test_feature_extraction_age():
    listing = Listing(make="ford", model="fiesta", year=2020)
    features = extract(listing)
    assert features.age >= 4  # test written 2024+


def test_feature_extraction_mileage_band():
    listing = Listing(make="bmw", model="3series", year=2018, mileage=50_000)
    features = extract(listing)
    assert features.mileage_band == "medium"
