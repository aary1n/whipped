from __future__ import annotations

from whipped.domain.models import FeatureVector, Listing, PriceRange, RiskAssessment

HIGH_MILEAGE_PER_YEAR = 15_000
MAX_REASONABLE_AGE = 15
SUSPICIOUS_PRICE_RATIO = 0.75   # asking < 75% of lower_gbp
WIDE_SPREAD_RATIO = 0.6         # (upper-lower)/mid > 0.6
MIN_CONFIDENT_COMPARABLES = 5
RISK_BASELINE = 5               # every used car has some inherent uncertainty

_BAND = [(25, "low"), (50, "medium"), (75, "high")]


def assess(listing: Listing, features: FeatureVector, price_range: PriceRange) -> RiskAssessment:
    flags: list[str] = []

    # --- listing-only flags ---
    if features.mileage_miles is None:
        flags.append("mileage not disclosed")
    elif features.age > 0:
        avg = features.mileage_miles / features.age
        if avg > HIGH_MILEAGE_PER_YEAR:
            flags.append(f"high mileage for age ({int(avg):,} mi/yr)")

    if features.mileage_band == "very_high":
        flags.append("very high total mileage (>100k)")

    if features.age > MAX_REASONABLE_AGE:
        flags.append(f"older vehicle ({features.age} yrs)")

    if listing.fuel_type is None:
        flags.append("fuel type not specified")

    if listing.seller_type == "private":
        flags.append("private seller (no dealer warranty)")

    # --- pricing-aware flags ---
    if price_range.comparable_count < MIN_CONFIDENT_COMPARABLES:
        flags.append(f"sparse comparables ({price_range.comparable_count})")

    if price_range.mid_gbp > 0:
        spread_ratio = (price_range.upper_gbp - price_range.lower_gbp) / price_range.mid_gbp
        if spread_ratio > WIDE_SPREAD_RATIO:
            flags.append("wide price spread in comparables")

        if listing.price_gbp and listing.price_gbp < price_range.lower_gbp * SUSPICIOUS_PRICE_RATIO:
            flags.append("suspiciously low price — inspect carefully")

    score = max(RISK_BASELINE, min(100, len(flags) * 20))
    band = _band_for(score)
    notes = "; ".join(flags) if flags else "No significant risk factors identified."

    return RiskAssessment(risk_score=score, risk_band=band, flags=flags, notes=notes)


def _band_for(score: int) -> str:
    for threshold, band in _BAND:
        if score <= threshold:
            return band
    return "very_high"
