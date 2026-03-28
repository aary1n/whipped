from __future__ import annotations

from whipped.domain.models import Listing, OwnershipProjection, PriceRange, RipoffAssessment, RiskAssessment

MIN_CONFIDENCE_FOR_OFFER = 0.3
MIN_COMPARABLES_FOR_OFFER = 8
MIN_PRICE_FLOOR = 500
_NO_VALUATION_STRATEGIES = {"no_data"}

_ACTION_LABELS: dict[str, str] = {
    "strong_buy":        "Strong buy — asking is already below the fair range.",
    "negotiate":         "Negotiate — there is room to push back on price.",
    "avoid":             "Avoid or negotiate hard — asking is well above the fair range.",
    "insufficient_data": "Insufficient comparable data to make a strong recommendation.",
}


def explain(
    listing: Listing,
    price_range: PriceRange,
    ripoff: RipoffAssessment,
    risk: RiskAssessment,
    ownership: OwnershipProjection,
) -> tuple[str, int | None, str]:
    """Return (explanation, suggested_counteroffer_gbp, action_recommendation)."""
    action = _action(listing.price_gbp, price_range, ripoff)
    offer  = _offer(listing.price_gbp, price_range, risk, action)

    parts: list[str] = []

    if price_range.strategy_used in _NO_VALUATION_STRATEGIES:
        parts.append("Insufficient comparable data to estimate a fair price.")
    elif price_range.mid_gbp > 0:
        parts.append(
            f"Fair range: £{price_range.lower_gbp:,}–£{price_range.upper_gbp:,} "
            f"(mid £{price_range.mid_gbp:,}, {price_range.comparable_count} comparables, "
            f"confidence {price_range.confidence:.0%})."
        )
        if listing.price_gbp:
            delta = listing.price_gbp - price_range.mid_gbp
            direction = "above" if delta >= 0 else "below"
            parts.append(
                f"Asking £{listing.price_gbp:,} is £{abs(delta):,} {direction} the midpoint "
                f"— {ripoff.ripoff_band} ({ripoff.ripoff_index}/100)."
            )

    parts.append(_ACTION_LABELS.get(action, action))

    if risk.flags:
        parts.append(f"Risk [{risk.risk_band}]: {risk.notes}")

    parts.append(
        f"Five-year ownership: insurance ~£{ownership.estimated_insurance_5y_gbp:,} "
        f"(~£{ownership.estimated_insurance_annual_gbp:,}/yr), "
        f"depreciation ~£{ownership.estimated_depreciation_5y_gbp:,}, "
        f"repairs ~£{ownership.estimated_repairs_5y_gbp:,} "
        f"({ownership.repair_risk_pct}% repair likelihood)."
    )

    if offer is not None:
        parts.append(f"Suggested offer: £{offer:,}.")

    return " ".join(parts), offer, action


def _action(asking: int | None, price_range: PriceRange, ripoff: RipoffAssessment) -> str:
    if price_range.strategy_used in _NO_VALUATION_STRATEGIES or price_range.mid_gbp <= 0:
        return "insufficient_data"
    if price_range.confidence < MIN_CONFIDENCE_FOR_OFFER:
        return "insufficient_data"
    if asking is None:
        return "insufficient_data"
    if asking < price_range.lower_gbp:
        return "strong_buy"
    if asking > price_range.upper_gbp:
        return "avoid" if ripoff.ripoff_index > 80 else "negotiate"
    return "negotiate"


def _offer(asking: int | None, price_range: PriceRange, risk: RiskAssessment, action: str) -> int | None:
    if action in ("insufficient_data", "strong_buy") or asking is None:
        return None
    if price_range.comparable_count < MIN_COMPARABLES_FOR_OFFER:
        return None

    if asking <= price_range.upper_gbp:
        # within range: request a modest 5% discount on asking
        offer = max(MIN_PRICE_FLOOR, int(asking * 0.95))
    else:
        # above range: anchor to mid with risk-adjusted discount
        risk_discount = (risk.risk_score / 100) * 0.25
        offer = max(MIN_PRICE_FLOOR, int(price_range.mid_gbp * (1 - risk_discount)))

    # hard cap: offer must never reach or exceed asking
    return offer if offer < asking else None
