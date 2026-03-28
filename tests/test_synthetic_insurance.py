from __future__ import annotations

from pathlib import Path

from whipped.insurance.synthetic import generate_synthetic_insurance_dataset


def test_generate_synthetic_insurance_dataset(tmp_path: Path) -> None:
    csv_path = tmp_path / "synthetic_quotes.csv"

    frame = generate_synthetic_insurance_dataset(csv_path, rows=200, seed=7)

    assert len(frame) == 200
    assert csv_path.exists()
    assert "annual_premium_gbp" in frame.columns
    assert "sex" in frame.columns
    assert "condition_score" in frame.columns
    assert "postcode_area" in frame.columns
    assert frame["postcode_area"].nunique() > 20
    assert frame["annual_premium_gbp"].min() > 0
