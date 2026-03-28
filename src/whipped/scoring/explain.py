from __future__ import annotations

from whipped.domain.models import Listing, OwnershipProjection, PriceRange, RipoffAssessment, RiskAssessment

MIN_CONFIDENCE_FOR_COUNTEROFFER = 0.3
MIN_COMPARABLES_FOR_COUNTEROFFER = 8
MIN_PRICE_FLOOR = 500
_NO_VALUATION_STRATEGIES = {"no_data"}


def explain(
    listing: Listing,
    price_range: PriceRange,
    ripoff: RipoffAssessment,
    risk: RiskAssessment,
    ownership: OwnershipProjection,
) -> tuple[str, int | None]:
    """Return (explanation, suggested_counteroffer_gbp)."""
    parts: list[str] = []

    if price_range.strategy_used in _NO_VALUATION_STRATEGIES:
        parts.append("Insufficient comparable data to estimate a fair price.")
    elif price_range.mid_gbp > 0:
        confidence_pct = f"{price_range.confidence:.0%}"
        parts.append(
            f"Fair range: £{price_range.lower_gbp:,}–£{price_range.upper_gbp:,} "
            f"({price_range.comparable_count} comparables, {price_range.strategy_used}, "
            f"confidence {confidence_pct})."
        )
        if listing.price_gbp:
            parts.append(
                f"Asking £{listing.price_gbp:,} — {ripoff.ripoff_band} ({ripoff.ripoff_index}/100). "
                f"{ripoff.notes}"
            )

    if risk.flags:
        parts.append(f"Risk [{risk.risk_band}]: {risk.notes}")

    parts.append(
        "Five-year ownership: "
        f"insurance ~£{ownership.estimated_insurance_5y_gbp:,}, "
        f"depreciation ~£{ownership.estimated_depreciation_5y_gbp:,}, "
        f"repairs ~£{ownership.estimated_repairs_5y_gbp:,} "
        f"with repair likelihood around {ownership.repair_risk_pct}%."
    )

    counteroffer = _counteroffer(listing, price_range, risk)
    if counteroffer and listing.price_gbp and counteroffer < listing.price_gbp:
        parts.append(f"Suggested offer: £{counteroffer:,}.")

    return " ".join(parts), counteroffer


def _counteroffer(listing: Listing, price_range: PriceRange, risk: RiskAssessment) -> int | None:
    if price_range.strategy_used in _NO_VALUATION_STRATEGIES:
        return None
    if price_range.mid_gbp <= 0:
        return None
    if price_range.confidence < MIN_CONFIDENCE_FOR_COUNTEROFFER:
        return None
    if price_range.comparable_count < MIN_COMPARABLES_FOR_COUNTEROFFER:
        return None
    discount = (risk.risk_score / 100) * 0.25
    return max(MIN_PRICE_FLOOR, int(price_range.mid_gbp * (1 - discount)))
