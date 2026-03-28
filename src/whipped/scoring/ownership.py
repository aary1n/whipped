from __future__ import annotations

from functools import lru_cache

from whipped.config import INSURANCE_MODEL
from whipped.domain.models import DriverProfile, FeatureVector, Listing, OwnershipProjection, PriceRange, RiskAssessment
from whipped.insurance.model import load_insurance_model

BASE_INSURANCE_BY_FUEL = {
    "petrol": 900,
    "diesel": 950,
    "hybrid": 1_000,
    "electric": 1_100,
}

BODY_INSURANCE_LOAD = {
    "hatchback": -50,
    "saloon": 25,
    "estate": 25,
    "suv": 175,
    "coupe": 125,
    "convertible": 225,
}

POSTCODE_AREA_LOAD = {
    "b": 40,
    "e": 220,
    "g": 35,
    "l": 60,
    "m": 55,
    "n": 190,
    "se": 175,
    "sw": 145,
    "w": 150,
}

PARKING_LOAD = {
    "garage": -90,
    "driveway": -40,
    "street": 80,
    "car_park": 25,
}

COVER_LOAD = {
    "third_party": -120,
    "third_party_fire_theft": -40,
    "comprehensive": 0,
}


def project_ownership(
    listing: Listing,
    features: FeatureVector,
    price_range: PriceRange,
    risk: RiskAssessment,
    driver: DriverProfile | None = None,
) -> OwnershipProjection:
    insurance_annual = _annual_insurance(listing, features, driver)
    insurance_5y = int(round(insurance_annual * 5 * 1.12))

    base_value = listing.price_gbp or price_range.mid_gbp
    depreciation_rate = _five_year_depreciation_rate(features, listing)
    depreciation_5y = int(round(base_value * depreciation_rate))

    repair_risk_pct = _repair_risk_pct(features, risk)
    repairs_5y = _repairs_cost_5y(base_value, features, risk, repair_risk_pct)

    annual_running = int(round((insurance_5y + depreciation_5y + repairs_5y) / 5))
    ownership_band = _ownership_band(annual_running)
    notes = _ownership_notes(insurance_annual, depreciation_rate, repair_risk_pct, repairs_5y)

    return OwnershipProjection(
        estimated_insurance_annual_gbp=insurance_annual,
        estimated_insurance_5y_gbp=insurance_5y,
        estimated_depreciation_5y_gbp=depreciation_5y,
        repair_risk_pct=repair_risk_pct,
        estimated_repairs_5y_gbp=repairs_5y,
        annual_running_cost_gbp=annual_running,
        ownership_band=ownership_band,
        insurance_band=_insurance_band(insurance_annual),
        notes=notes,
    )


def _annual_insurance(listing: Listing, features: FeatureVector, driver: DriverProfile | None) -> int:
    if driver is not None:
        model = _get_trained_model()
        if model is not None:
            try:
                return model.predict_annual_premium(listing, driver)
            except Exception:
                pass

    fuel = (listing.fuel_type or "").lower()
    body = (listing.body_type or "").lower()
    transmission = (listing.transmission or "").lower()
    engine_size = listing.engine_size_l or 1.5
    age = max(features.age, 0)

    annual = BASE_INSURANCE_BY_FUEL.get(fuel, 950)
    annual += BODY_INSURANCE_LOAD.get(body, 0)
    annual += int(max(0.0, engine_size - 1.4) * 120)
    annual += 75 if transmission == "automatic" else 0
    annual += min(250, age * 18)
    annual += _driver_insurance_adjustment(driver)
    return max(650, annual)


@lru_cache(maxsize=1)
def _get_trained_model():
    return load_insurance_model(INSURANCE_MODEL)


def _driver_insurance_adjustment(driver: DriverProfile | None) -> int:
    if driver is None:
        return 0

    annual = 0
    age = driver.age
    years_licensed = driver.years_licensed or 0
    no_claims = driver.no_claims_years or 0
    annual_mileage = driver.annual_mileage or 10_000
    postcode_area = (driver.postcode_area or "").strip().lower()
    parking = (driver.parking or "").strip().lower()
    cover_type = (driver.cover_type or "").strip().lower()

    if age is not None:
        if age < 21:
            annual += 1_400
        elif age < 25:
            annual += 850
        elif age < 30:
            annual += 320
        elif age < 70:
            annual -= 40
        else:
            annual += 210

    if years_licensed < 2:
        annual += 260
    elif years_licensed >= 10:
        annual -= 70

    annual -= min(220, no_claims * 28)
    annual += driver.claims_last_5y * 180
    annual += driver.convictions_last_5y * 260
    annual += min(260, max(0, annual_mileage - 8_000) // 2_500 * 35)
    annual += _postcode_load(postcode_area)
    annual += PARKING_LOAD.get(parking, 0)
    annual += COVER_LOAD.get(cover_type, 0)
    return annual


def _postcode_load(postcode_area: str) -> int:
    if not postcode_area:
        return 0
    if postcode_area in POSTCODE_AREA_LOAD:
        return POSTCODE_AREA_LOAD[postcode_area]
    return POSTCODE_AREA_LOAD.get(postcode_area[:1], 0)


def _five_year_depreciation_rate(features: FeatureVector, listing: Listing) -> float:
    age = max(features.age, 0)
    fuel = (listing.fuel_type or "").lower()
    mileage = features.mileage_miles or 40_000

    rate = 0.38
    rate += min(0.22, age * 0.015)
    rate += min(0.12, mileage / 200_000)
    if fuel == "diesel":
        rate += 0.06
    elif fuel == "hybrid":
        rate -= 0.02
    elif fuel == "electric":
        rate += 0.03
    return min(0.82, max(0.2, rate))


def _repair_risk_pct(features: FeatureVector, risk: RiskAssessment) -> int:
    age = max(features.age, 0)
    mileage = features.mileage_miles or 40_000

    pct = 12
    pct += min(35, age * 3)
    pct += min(25, mileage // 12_000)
    pct += int(risk.risk_score * 0.25)
    if features.mileage_band in {"high", "very_high"}:
        pct += 10
    return max(10, min(95, pct))


def _repairs_cost_5y(
    base_value: int,
    features: FeatureVector,
    risk: RiskAssessment,
    repair_risk_pct: int,
) -> int:
    age = max(features.age, 0)
    mileage = features.mileage_miles or 40_000

    expected_major = max(150, base_value * (repair_risk_pct / 100) * 0.18)
    wear_and_tear = 900 + age * 120 + min(1_400, mileage * 0.015)
    risk_load = risk.risk_score * 12
    return int(round(expected_major + wear_and_tear + risk_load))


def _ownership_band(annual_running: int) -> str:
    if annual_running <= 2_000:
        return "low"
    if annual_running <= 3_500:
        return "moderate"
    if annual_running <= 5_000:
        return "high"
    return "very_high"


def _insurance_band(annual_insurance: int) -> str:
    if annual_insurance <= 900:
        return "low"
    if annual_insurance <= 1_400:
        return "moderate"
    if annual_insurance <= 2_100:
        return "high"
    return "very_high"


def _ownership_notes(
    insurance_annual: int,
    depreciation_rate: float,
    repair_risk_pct: int,
    repairs_5y: int,
) -> list[str]:
    return [
        f"Estimated insurance averages about £{insurance_annual:,} per year.",
        f"Expected five-year depreciation is roughly {round(depreciation_rate * 100)}% of current value.",
        f"Repair likelihood is estimated at {repair_risk_pct}% over the next five years.",
        f"Expected maintenance and repair spend is about £{repairs_5y:,} over five years.",
    ]
