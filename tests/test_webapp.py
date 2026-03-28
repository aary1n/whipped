from __future__ import annotations

from whipped.domain.models import Listing
from whipped.webapp import WhippedWebApp, _investment_view


def test_webapp_renders_input_and_output_sections() -> None:
    app = WhippedWebApp()

    html = app._render_page(
        {
            "make": "ford",
            "model": "fiesta",
            "year": "2020",
            "price_gbp": "9300",
            "mileage_miles": "33000",
            "engine_size_l": "1.0",
            "fuel_type": "petrol",
            "transmission": "manual",
            "seller_type": "dealer",
            "driver_age": "28",
            "sex": "female",
            "years_licensed": "8",
            "postcode_area": "SW",
        }
    )

    assert "Input Data" in html
    assert "Output" in html
    assert "Comparable Data Used" in html
    assert "Ripoff Score" in html
    assert "Total 5-Year Cost Of Ownership" in html
    assert "Longevity Forecast" in html
    assert "Insurance Per Year" in html
    assert "Driver Profile" in html
    assert "Brand Tax Analysis" in html


def test_webapp_falls_back_to_sample_comparables() -> None:
    app = WhippedWebApp()
    listing = Listing(make="unknown", model="unknown", year=2020, price_gbp=5_000)

    comparables = app._find_comparables(listing)

    assert comparables


def test_investment_view() -> None:
    class _Verdict:
        class ripoff:
            ripoff_index = 20

        class risk:
            risk_score = 25

    assert _investment_view(_Verdict()) == "Potential buy"
