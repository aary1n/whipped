"""Run the pipeline on a sample listing and print the verdict."""
from __future__ import annotations

from whipped.app import evaluate
from whipped.domain.models import Listing


def main() -> None:
    listing = Listing(
        make="ford",
        model="fiesta",
        year=2018,
        mileage=45_000,
        fuel_type="petrol",
        transmission="manual",
        engine_size=1.0,
        asking_price=8_500,
    )

    verdict = evaluate(listing)

    print(f"Make/Model: {verdict.listing.make} {verdict.listing.model}")
    print(f"Year: {verdict.listing.year} | Mileage: {verdict.listing.mileage:,}")
    print(f"Asking: £{verdict.listing.asking_price:,}")
    print(f"Fair range: £{verdict.price_range.low:,}–£{verdict.price_range.high:,}")
    print(f"Confidence: {verdict.price_range.confidence}")
    print(f"Ripoff index: {verdict.ripoff.score}/100 ({verdict.ripoff.label})")
    print(f"Risk score: {verdict.risk.score}/100")
    if verdict.risk.factors:
        print(f"Risk factors: {', '.join(verdict.risk.factors)}")
    print(f"\n{verdict.explanation}")


if __name__ == "__main__":
    main()
