from __future__ import annotations

import sqlite3
from pathlib import Path

from whipped.ingest.market_database import build_market_database, load_training_frame


def test_build_market_database_creates_expected_labels(tmp_path: Path) -> None:
    csv_path = tmp_path / "autotrader_export.csv"
    csv_path.write_text(
        "\n".join(
            [
                "make,model,year,price,mileage,fuel_type,transmission,seller_type",
                "ford,fiesta,2020,9500,30000,petrol,manual,dealer",
                "ford,fiesta,2020,9300,32000,petrol,manual,dealer",
                "ford,fiesta,2020,9200,35000,petrol,manual,dealer",
                "ford,fiesta,2020,12000,31000,petrol,manual,dealer",
            ]
        ),
        encoding="utf-8",
    )
    db_path = tmp_path / "market.sqlite"

    inserted = build_market_database([csv_path], db_path)

    assert inserted == 4

    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT price_gbp, expected_price_gbp, is_overpriced, investment_signal
            FROM market_listings
            ORDER BY price_gbp ASC
            """
        ).fetchall()

    assert rows[0][2] == 0
    assert rows[-1][2] == 1
    assert rows[-1][3] == "avoid"


def test_load_training_frame_returns_ml_ready_columns(tmp_path: Path) -> None:
    csv_path = tmp_path / "autotrader_export.csv"
    csv_path.write_text(
        "\n".join(
            [
                "make,model,year,price,mileage,fuel_type,transmission",
                "bmw,3series,2021,18000,25000,petrol,automatic",
                "bmw,3series,2021,17500,27000,petrol,automatic",
                "bmw,3series,2021,21000,24000,petrol,automatic",
            ]
        ),
        encoding="utf-8",
    )
    db_path = tmp_path / "market.sqlite"

    build_market_database([csv_path], db_path)
    training = load_training_frame(db_path)

    assert "is_overpriced" in training.columns
    assert "investment_score" in training.columns
    assert len(training) == 3
