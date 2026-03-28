"""Generate human-readable explanation and counteroffer."""
from __future__ import annotations

from whipped.domain.models import Listing, PriceRange, RipoffIndex, RiskScore


def explain(
    listing: Listing,
    price_range: PriceRange,
    ripoff: RipoffIndex,
    risk: RiskScore,
) -> tuple[str, int | None]:
    """Return (explanation_text, suggested_counteroffer)."""
    parts: list[str] = []

    if price_range.mid > 0:
        parts.append(
            f"Fair price range: £{price_range.low:,}–£{price_range.high:,} "
            f"(based on {price_range.n_comparables} comparables)."
        )

    if listing.asking_price:
        parts.append(f"Asking £{listing.asking_price:,} — rated '{ripoff.label}' ({ripoff.score}/100).")

    if risk.factors:
        parts.append(f"Risks: {'; '.join(risk.factors)}.")

    counteroffer = _suggest_counteroffer(listing, price_range, risk)
    if counteroffer and listing.asking_price and counteroffer < listing.asking_price:
        parts.append(f"Suggested counteroffer: £{counteroffer:,}.")

    return " ".join(parts), counteroffer


def _suggest_counteroffer(
    listing: Listing, price_range: PriceRange, risk: RiskScore
) -> int | None:
    if price_range.mid == 0:
        return None
    discount = risk.score / 200  # up to 50% discount for max risk
    return int(price_range.mid * (1 - discount))
