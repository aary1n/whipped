from whipped.domain.models import DriverProfile, FeatureVector, Listing, PriceRange, RiskAssessment
from whipped.scoring.ownership import project_ownership


def test_project_ownership_returns_five_year_estimates() -> None:
    listing = Listing(
        make="ford",
        model="fiesta",
        year=2020,
        price_gbp=9_300,
        mileage_miles=33_000,
        fuel_type="petrol",
        transmission="manual",
        engine_size_l=1.0,
        body_type="hatchback",
    )
    features = FeatureVector(
        make="ford",
        model="fiesta",
        age=5,
        mileage_miles=33_000,
        mileage_band="medium",
        fuel_type="petrol",
        transmission="manual",
        engine_size_l=1.0,
    )
    price_range = PriceRange(8_900, 9_300, 9_700, 0.8, 12, "make_model_year")
    risk = RiskAssessment(20, "low", [])

    projection = project_ownership(listing, features, price_range, risk)

    assert projection.estimated_insurance_annual_gbp > 0
    assert projection.estimated_insurance_5y_gbp > 0
    assert projection.estimated_depreciation_5y_gbp > 0
    assert projection.estimated_repairs_5y_gbp > 0
    assert 0 < projection.repair_risk_pct <= 100
    assert len(projection.notes) == 4


def test_older_high_mileage_cars_have_higher_repair_risk() -> None:
    low_risk = project_ownership(
        Listing(make="ford", model="fiesta", year=2022, price_gbp=11_000, mileage_miles=20_000, fuel_type="petrol"),
        FeatureVector(make="ford", model="fiesta", age=3, mileage_miles=20_000, mileage_band="low"),
        PriceRange(10_000, 11_000, 12_000, 0.8, 10, "make_model_year"),
        RiskAssessment(20, "low", []),
    )
    high_risk = project_ownership(
        Listing(make="ford", model="fiesta", year=2014, price_gbp=4_800, mileage_miles=110_000, fuel_type="diesel"),
        FeatureVector(make="ford", model="fiesta", age=11, mileage_miles=110_000, mileage_band="very_high"),
        PriceRange(4_000, 4_800, 5_300, 0.6, 8, "make_model"),
        RiskAssessment(80, "very_high", ["very high mileage"]),
    )

    assert high_risk.repair_risk_pct > low_risk.repair_risk_pct
    assert high_risk.estimated_repairs_5y_gbp > low_risk.estimated_repairs_5y_gbp


def test_higher_risk_driver_has_higher_insurance_forecast() -> None:
    listing = Listing(make="ford", model="fiesta", year=2020, price_gbp=9_000, mileage_miles=30_000, fuel_type="petrol")
    features = FeatureVector(make="ford", model="fiesta", age=5, mileage_miles=30_000, mileage_band="medium")
    price_range = PriceRange(8_500, 9_000, 9_600, 0.8, 8, "make_model_year")
    risk = RiskAssessment(25, "low", [])

    safer = project_ownership(
        listing,
        features,
        price_range,
        risk,
        DriverProfile(age=38, years_licensed=18, no_claims_years=10, annual_mileage=8_000, postcode_area="BA", parking="garage"),
    )
    riskier = project_ownership(
        listing,
        features,
        price_range,
        risk,
        DriverProfile(age=20, years_licensed=1, no_claims_years=0, claims_last_5y=1, annual_mileage=14_000, postcode_area="E", parking="street"),
    )

    assert riskier.estimated_insurance_annual_gbp > safer.estimated_insurance_annual_gbp
    assert riskier.estimated_insurance_5y_gbp > safer.estimated_insurance_5y_gbp
