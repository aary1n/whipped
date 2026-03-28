from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Listing:
    make: str
    model: str
    year: int
    price_gbp: int | None = None
    mileage_miles: int | None = None
    fuel_type: str | None = None
    transmission: str | None = None
    engine_size_l: float | None = None
    variant: str | None = None
    body_type: str | None = None
    seller_type: str | None = None  # "dealer" | "private"
    location: str | None = None
    source: str | None = None
    listing_id: str | None = None
    raw_text: str | None = None


@dataclass
class DriverProfile:
    age: int | None = None
    sex: str | None = None
    years_licensed: int | None = None
    no_claims_years: int | None = None
    claims_last_5y: int = 0
    convictions_last_5y: int = 0
    annual_mileage: int | None = None
    postcode_area: str | None = None
    parking: str | None = None
    cover_type: str | None = None


@dataclass
class FeatureVector:
    make: str
    model: str
    age: int
    mileage_miles: int | None = None
    mileage_band: str | None = None
    fuel_type: str | None = None
    transmission: str | None = None
    engine_size_l: float | None = None


@dataclass
class PriceRange:
    lower_gbp: int
    mid_gbp: int
    upper_gbp: int
    confidence: float          # 0.0–1.0
    comparable_count: int = 0
    strategy_used: str = "unknown"


@dataclass
class RipoffAssessment:
    ripoff_index: int          # 0 (bargain) – 100 (extreme ripoff)
    ripoff_band: str           # "bargain" | "good_deal" | "fair" | "overpriced" | "ripoff" | "extreme_ripoff"
    pricing_position: str      # "below range" | "within range" | "above range" | "unknown"
    notes: str = ""


@dataclass
class RiskAssessment:
    risk_score: int            # 0–100
    risk_band: str             # "low" | "medium" | "high" | "very_high"
    flags: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class OwnershipProjection:
    estimated_insurance_annual_gbp: int
    estimated_insurance_5y_gbp: int
    estimated_depreciation_5y_gbp: int
    repair_risk_pct: int
    estimated_repairs_5y_gbp: int
    annual_running_cost_gbp: int
    ownership_band: str
    insurance_band: str
    notes: list[str] = field(default_factory=list)


@dataclass
class BrandTaxResult:
    brand_tax_gbp: int           # positive = premium over DNA twins, negative = discount
    avg_twin_price_gbp: int
    twin_count: int
    twins: list[dict]            # [{make, model, year, price_gbp, brand_tax_gbp}]
    is_good_deal: bool
    recommendations: list[dict] = field(default_factory=list)  # cluster members cheaper than target, sorted asc by price


@dataclass
class WhippedVerdict:
    listing: Listing
    price_range: PriceRange
    risk: RiskAssessment
    ripoff: RipoffAssessment
    ownership: OwnershipProjection
    explanation: str
    action_recommendation: str = "unknown"   # strong_buy | negotiate | avoid | insufficient_data
    suggested_counteroffer_gbp: int | None = None
    brand_tax: BrandTaxResult | None = None
