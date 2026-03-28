from whipped.domain.models import Listing
from whipped.pricing.brand_tax import compute


def test_brand_tax_uses_cross_brand_year_window_and_recommendations() -> None:
    target = Listing(
        make="ford",
        model="fiesta",
        year=2020,
        price_gbp=9_800,
        mileage_miles=34_000,
        engine_size_l=1.0,
        fuel_type="petrol",
        transmission="manual",
        body_type="hatchback",
    )
    comparables = [
        Listing(make="vw", model="polo", year=2020, price_gbp=9_200, mileage_miles=35_000, engine_size_l=1.0, fuel_type="petrol", transmission="manual", body_type="hatchback"),
        Listing(make="toyota", model="yaris", year=2019, price_gbp=8_900, mileage_miles=33_500, engine_size_l=1.0, fuel_type="petrol", transmission="manual", body_type="hatchback"),
        Listing(make="honda", model="jazz", year=2021, price_gbp=9_300, mileage_miles=36_000, engine_size_l=1.1, fuel_type="petrol", transmission="manual", body_type="hatchback"),
        Listing(make="bmw", model="1series", year=2020, price_gbp=11_200, mileage_miles=34_000, engine_size_l=1.5, fuel_type="petrol", transmission="automatic", body_type="hatchback"),
        Listing(make="audi", model="a1", year=2020, price_gbp=10_100, mileage_miles=31_000, engine_size_l=1.0, fuel_type="petrol", transmission="manual", body_type="hatchback"),
        Listing(make="seat", model="ibiza", year=2019, price_gbp=8_700, mileage_miles=37_000, engine_size_l=1.0, fuel_type="petrol", transmission="manual", body_type="hatchback"),
    ]

    result = compute(target, comparables)

    assert result is not None
    assert result.twin_count == 5
    assert any(t["year"] == 2019 for t in result.twins) or any(t["year"] == 2021 for t in result.twins)
    assert result.recommendations
    assert min(r["price_gbp"] for r in result.recommendations) < target.price_gbp
