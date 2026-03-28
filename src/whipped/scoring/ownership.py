from __future__ import annotations

from whipped.domain.models import FeatureVector, Listing, OwnershipProjection, PriceRange, RiskAssessment

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


def project_ownership(
    listing: Listing,
    features: FeatureVector,
    price_range: PriceRange,
    risk: RiskAssessment,
) -> OwnershipProjection:
    insurance_annual = _annual_insurance(listing, features)
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
        estimated_insurance_5y_gbp=insurance_5y,
        estimated_depreciation_5y_gbp=depreciation_5y,
        repair_risk_pct=repair_risk_pct,
        estimated_repairs_5y_gbp=repairs_5y,
        annual_running_cost_gbp=annual_running,
        ownership_band=ownership_band,
        notes=notes,
    )


def _annual_insurance(listing: Listing, features: FeatureVector) -> int:
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
    return max(650, annual)


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
