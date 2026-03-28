from __future__ import annotations

from whipped.domain.models import ExplanationFactor, Listing, WhippedVerdict


def build_explainability(listing: Listing, verdict: WhippedVerdict) -> tuple[list[ExplanationFactor], list[str]]:
    """Build ranked contribution factors and practical negotiation points."""
    factors = _factors(listing, verdict)
    ranked = sorted(factors, key=lambda f: abs(f.impact_gbp), reverse=True)
    points = _negotiation_points(listing, verdict, ranked)
    return ranked, points


def _factors(listing: Listing, verdict: WhippedVerdict) -> list[ExplanationFactor]:
    asking = listing.price_gbp or verdict.price_range.mid_gbp
    price_gap = asking - verdict.price_range.mid_gbp
    confidence_penalty = int((1.0 - verdict.price_range.confidence) * 700)
    risk_load = verdict.risk.risk_score * 45
    insurance_load = verdict.ownership.estimated_insurance_annual_gbp - 1_000
    mileage_load = _mileage_load(listing.mileage_miles)

    return [
        _factor("Price vs market midpoint", price_gap, f"Asking compared with market midpoint (£{verdict.price_range.mid_gbp:,})."),
        _factor("Risk score pressure", risk_load, f"Risk score {verdict.risk.risk_score}/100 pushes expected downside higher."),
        _factor("Insurance burden", insurance_load, f"Annual insurance estimate is about £{verdict.ownership.estimated_insurance_annual_gbp:,}."),
        _factor("Mileage effect", mileage_load, "Mileage level shifts expected wear, resale value, and repair exposure."),
        _factor("Comparable confidence", confidence_penalty, f"Confidence is {verdict.price_range.confidence:.0%} across {verdict.price_range.comparable_count} comparables."),
    ]


def _factor(name: str, impact_gbp: int, detail: str) -> ExplanationFactor:
    if impact_gbp > 0:
        direction = "up"
    elif impact_gbp < 0:
        direction = "down"
    else:
        direction = "neutral"
    return ExplanationFactor(name=name, impact_gbp=impact_gbp, direction=direction, detail=detail)


def _mileage_load(mileage_miles: int | None) -> int:
    if mileage_miles is None:
        return 120
    if mileage_miles <= 30_000:
        return -150
    if mileage_miles <= 70_000:
        return 60
    if mileage_miles <= 110_000:
        return 260
    return 420


def _negotiation_points(
    listing: Listing,
    verdict: WhippedVerdict,
    factors: list[ExplanationFactor],
) -> list[str]:
    points: list[str] = []
    asking = listing.price_gbp or verdict.price_range.mid_gbp

    if asking > verdict.price_range.mid_gbp:
        gap = asking - verdict.price_range.mid_gbp
        points.append(f"Asking is £{gap:,} above the model midpoint; anchor close to £{verdict.price_range.mid_gbp:,}.")

    for factor in factors:
        if factor.impact_gbp <= 0:
            continue
        points.append(f"{factor.name}: +£{factor.impact_gbp:,} pressure ({factor.detail})")
        if len(points) >= 4:
            break

    if verdict.suggested_counteroffer_gbp is not None:
        points.append(f"Start near £{verdict.suggested_counteroffer_gbp:,} and justify using risk and ownership costs.")

    if not points:
        points.append("Listing appears close to fair value; negotiate on service history, tires, and warranty add-ons.")

    return points[:5]
