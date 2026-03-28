from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Listing:
    make: str
    model: str
    year: int
    mileage: int | None = None
    fuel_type: str | None = None
    transmission: str | None = None
    engine_size: float | None = None
    asking_price: int | None = None
    raw_text: str | None = None


@dataclass
class FeatureVector:
    age: int
    mileage: int | None = None
    mileage_band: str | None = None
    fuel_type: str | None = None
    transmission: str | None = None
    engine_size: float | None = None


@dataclass
class PriceRange:
    low: int
    mid: int
    high: int
    confidence: float  # 0.0 to 1.0
    n_comparables: int = 0


@dataclass
class RipoffIndex:
    score: int  # 0 (great deal) to 100 (extreme ripoff)
    label: str  # e.g. "fair", "overpriced", "bargain"


@dataclass
class RiskScore:
    score: int  # 0 (low risk) to 100 (high risk)
    factors: list[str] = field(default_factory=list)


@dataclass
class Verdict:
    listing: Listing
    price_range: PriceRange
    ripoff: RipoffIndex
    risk: RiskScore
    explanation: str
    counteroffer: int | None = None
