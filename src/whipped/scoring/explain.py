from __future__ import annotations

from whipped.domain.models import Listing, PriceRange, RipoffAssessment, RiskAssessment


def explain(
    listing: Listing,
    price_range: PriceRange,
    ripoff: RipoffAssessment,
    risk: RiskAssessment,
) -> tuple[str, int | None]:
    """Return (explanation, suggested_counteroffer_gbp)."""
    parts: list[str] = []

    if price_range.mid_gbp > 0:
        parts.append(
            f"Fair range: £{price_range.lower_gbp:,}–£{price_range.upper_gbp:,} "
            f"({price_range.comparable_count} comparables, {price_range.strategy_used})."
        )

    if listing.price_gbp:
        parts.append(f"Asking £{listing.price_gbp:,} — {ripoff.ripoff_band} ({ripoff.ripoff_index}/100). {ripoff.notes}")

    if risk.flags:
        parts.append(f"Risk [{risk.risk_band}]: {risk.notes}")

    counteroffer = _counteroffer(listing, price_range, risk)
    if counteroffer and listing.price_gbp and counteroffer < listing.price_gbp:
        parts.append(f"Suggested offer: £{counteroffer:,}.")

    return " ".join(parts), counteroffer


def _counteroffer(listing: Listing, price_range: PriceRange, risk: RiskAssessment) -> int | None:
    if price_range.mid_gbp == 0:
        return None
    # Base: midpoint; discount up to 25% for max risk
    discount = (risk.risk_score / 100) * 0.25
    return int(price_range.mid_gbp * (1 - discount))
