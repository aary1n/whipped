"""Build a local market database from Auto Trader-style CSV exports."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

import pandas as pd

EXPECTED_COLUMNS = {
    "make": ["make", "manufacturer", "brand"],
    "model": ["model"],
    "year": ["year", "registration_year", "registration year"],
    "price_gbp": ["price", "price_gbp", "advertised_price", "asking_price"],
    "mileage_miles": ["mileage", "miles", "odometer", "odometer_miles"],
    "fuel_type": ["fuel_type", "fuel", "fuel type"],
    "transmission": ["transmission", "gearbox"],
    "body_type": ["body_type", "body", "body type"],
    "seller_type": ["seller_type", "seller", "seller type"],
    "location": ["location", "town", "dealer_location"],
    "engine_size_l": ["engine_size_l", "engine_size", "engine", "engine size"],
    "variant": ["variant", "trim", "derivative"],
    "listing_id": ["listing_id", "advert_id", "ad_id", "id"],
    "source_url": ["source_url", "url", "listing_url"],
}

TEXT_COLUMNS = [
    "make",
    "model",
    "fuel_type",
    "transmission",
    "body_type",
    "seller_type",
    "location",
    "variant",
]

GROUPINGS = [
    ["make", "model", "year", "fuel_type", "transmission"],
    ["make", "model", "year"],
    ["make", "model"],
]


def build_market_database(csv_paths: Iterable[Path], db_path: Path) -> int:
    frames = [_load_export(path) for path in csv_paths]
    if not frames:
        raise ValueError("At least one CSV path is required.")

    market = pd.concat(frames, ignore_index=True)
    market = market.drop_duplicates(subset=["listing_id", "source_url", "make", "model", "year", "price_gbp"])
    market = _derive_market_features(market)

    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as connection:
        market.to_sql("market_listings", connection, if_exists="replace", index=False)
    return int(len(market))


def load_training_frame(db_path: Path) -> pd.DataFrame:
    with sqlite3.connect(db_path) as connection:
        return pd.read_sql_query(
            """
            SELECT
                listing_id,
                make,
                model,
                year,
                age_years,
                price_gbp,
                mileage_miles,
                fuel_type,
                transmission,
                body_type,
                seller_type,
                engine_size_l,
                expected_price_gbp,
                price_gap_gbp,
                price_gap_pct,
                is_overpriced,
                investment_score,
                investment_signal
            FROM market_listings
            """,
            connection,
        )


def _load_export(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    renamed = frame.rename(columns={column: _canonical_name(column) for column in frame.columns})
    normalized = pd.DataFrame()

    for column in EXPECTED_COLUMNS:
        normalized[column] = renamed[column] if column in renamed.columns else None

    normalized["source_file"] = path.name
    normalized["source"] = "autotrader_export"

    normalized["make"] = _normalize_text(normalized["make"])
    normalized["model"] = _normalize_text(normalized["model"])
    normalized["fuel_type"] = _normalize_text(normalized["fuel_type"])
    normalized["transmission"] = _normalize_text(normalized["transmission"])
    normalized["body_type"] = _normalize_text(normalized["body_type"])
    normalized["seller_type"] = _normalize_text(normalized["seller_type"])
    normalized["location"] = _normalize_text(normalized["location"])
    normalized["variant"] = _normalize_text(normalized["variant"])

    normalized["year"] = pd.to_numeric(normalized["year"], errors="coerce")
    normalized["price_gbp"] = _parse_numeric_series(normalized["price_gbp"])
    normalized["mileage_miles"] = _parse_numeric_series(normalized["mileage_miles"])
    normalized["engine_size_l"] = _parse_numeric_series(normalized["engine_size_l"])
    normalized["listing_id"] = normalized["listing_id"].fillna(normalized["source_url"])

    normalized = normalized.dropna(subset=["make", "model", "year", "price_gbp"])
    normalized = normalized[normalized["price_gbp"] > 0]
    normalized = normalized[(normalized["year"] >= 1990) & (normalized["year"] <= 2035)]
    normalized["year"] = normalized["year"].astype(int)

    return normalized.reset_index(drop=True)


def _derive_market_features(frame: pd.DataFrame) -> pd.DataFrame:
    market = frame.copy()
    current_year = pd.Timestamp.utcnow().year
    market["age_years"] = (current_year - market["year"]).clip(lower=0)
    market["price_per_mile"] = market["price_gbp"] / market["mileage_miles"].replace({0: pd.NA})

    expected_price = pd.Series(pd.NA, index=market.index, dtype="Float64")
    strategy = pd.Series(pd.NA, index=market.index, dtype="object")
    comparable_count = pd.Series(0, index=market.index, dtype="int64")

    for grouping in GROUPINGS:
        medians = market.groupby(grouping)["price_gbp"].median()
        counts = market.groupby(grouping)["price_gbp"].transform("count")
        candidate = market[grouping].apply(lambda row: medians.get(tuple(row)), axis=1)
        missing = expected_price.isna() & candidate.notna()

        expected_price.loc[missing] = candidate.loc[missing]
        strategy.loc[missing] = "+".join(grouping)
        comparable_count.loc[missing] = counts.loc[missing]

    if expected_price.isna().any():
        corpus_median = float(market["price_gbp"].median())
        expected_price = expected_price.fillna(corpus_median)
        strategy = strategy.fillna("corpus")
        comparable_count.loc[comparable_count == 0] = len(market)

    market["pricing_strategy"] = strategy
    market["comparable_count"] = comparable_count
    market["expected_price_gbp"] = expected_price.round().astype(int)
    market["price_gap_gbp"] = (market["price_gbp"] - market["expected_price_gbp"]).astype(int)
    market["price_gap_pct"] = (
        (market["price_gbp"] - market["expected_price_gbp"]) / market["expected_price_gbp"]
    ).round(4)
    market["is_overpriced"] = (market["price_gap_pct"] >= 0.1).astype(int)
    market["investment_score"] = market.apply(_investment_score, axis=1)
    market["investment_signal"] = market["investment_score"].apply(_investment_signal)
    return market


def _investment_score(row: pd.Series) -> int:
    margin_score = max(-40.0, min(40.0, float(-row["price_gap_pct"]) * 100))
    age_penalty = min(20.0, float(row["age_years"]) * 1.5)
    mileage = row.get("mileage_miles")
    mileage_penalty = 0.0 if pd.isna(mileage) else min(20.0, float(mileage) / 10_000)
    seller_type = row.get("seller_type")
    dealer_bonus = 5.0 if not pd.isna(seller_type) and seller_type == "dealer" else 0.0

    score = 50.0 + margin_score - age_penalty - mileage_penalty + dealer_bonus
    return max(0, min(100, int(round(score))))


def _investment_signal(score: int) -> str:
    if score >= 70:
        return "strong_buy"
    if score >= 55:
        return "watchlist"
    if score >= 40:
        return "neutral"
    return "avoid"


def _canonical_name(column: str) -> str:
    lowered = column.strip().lower().replace("-", "_")
    for canonical, aliases in EXPECTED_COLUMNS.items():
        if lowered == canonical or lowered in aliases:
            return canonical
    return lowered.replace(" ", "_")


def _normalize_text(series: pd.Series) -> pd.Series:
    cleaned = series.astype("string").str.strip().str.lower()
    return cleaned.replace({"<na>": pd.NA, "nan": pd.NA, "none": pd.NA, "": pd.NA})


def _parse_numeric_series(series: pd.Series) -> pd.Series:
    cleaned = (
        series.astype("string")
        .str.replace(",", "", regex=False)
        .str.replace("£", "", regex=False)
        .str.replace(" miles", "", regex=False)
        .str.extract(r"([-+]?\d*\.?\d+)")[0]
    )
    return pd.to_numeric(cleaned, errors="coerce")
