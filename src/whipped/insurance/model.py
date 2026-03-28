"""Train and run a lightweight insurance premium model from real quote CSVs."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from whipped.domain.models import DriverProfile, Listing

NUMERIC_FIELDS = [
    "driver_age",
    "years_licensed",
    "no_claims_years",
    "claims_last_5y",
    "convictions_last_5y",
    "annual_mileage",
    "vehicle_year",
    "vehicle_age",
    "vehicle_price_gbp",
    "vehicle_mileage_miles",
    "engine_size_l",
]

CATEGORICAL_FIELDS = [
    "make",
    "model",
    "fuel_type",
    "transmission",
    "body_type",
    "postcode_area",
    "parking",
    "cover_type",
]

REQUIRED_TARGET = "annual_premium_gbp"

ALIASES = {
    "annual_premium_gbp": ["annual_premium_gbp", "annual_premium", "premium", "quote_price", "price"],
    "driver_age": ["driver_age", "age"],
    "years_licensed": ["years_licensed", "license_years", "driving_years"],
    "no_claims_years": ["no_claims_years", "ncb_years", "no_claims_bonus_years"],
    "claims_last_5y": ["claims_last_5y", "claims", "claims_5y"],
    "convictions_last_5y": ["convictions_last_5y", "convictions", "motoring_convictions"],
    "annual_mileage": ["annual_mileage", "mileage_per_year"],
    "vehicle_year": ["vehicle_year", "year", "car_year"],
    "vehicle_price_gbp": ["vehicle_price_gbp", "price_gbp", "car_price"],
    "vehicle_mileage_miles": ["vehicle_mileage_miles", "mileage_miles", "mileage"],
    "engine_size_l": ["engine_size_l", "engine_size", "engine"],
    "make": ["make"],
    "model": ["model"],
    "fuel_type": ["fuel_type", "fuel"],
    "transmission": ["transmission"],
    "body_type": ["body_type", "body"],
    "postcode_area": ["postcode_area", "postcode_prefix", "area"],
    "parking": ["parking", "overnight_parking"],
    "cover_type": ["cover_type", "cover"],
}


@dataclass
class InsuranceModel:
    numeric_fields: list[str]
    categorical_fields: list[str]
    categories: dict[str, list[str]]
    numeric_mean: np.ndarray
    numeric_std: np.ndarray
    hidden_weights: np.ndarray
    hidden_bias: np.ndarray
    output_weights: np.ndarray
    output_bias: float
    training_rows: int
    target_mean: float
    target_std: float

    def predict_annual_premium(self, listing: Listing, driver: DriverProfile) -> int:
        row = _record_from_inputs(listing, driver)
        features = _encode_frame(
            pd.DataFrame([row]),
            numeric_fields=self.numeric_fields,
            categorical_fields=self.categorical_fields,
            categories=self.categories,
            numeric_mean=self.numeric_mean,
            numeric_std=self.numeric_std,
        )
        hidden = np.maximum(0.0, features @ self.hidden_weights + self.hidden_bias)
        prediction_norm = hidden @ self.output_weights + self.output_bias
        prediction = prediction_norm * self.target_std + self.target_mean
        return max(250, int(round(float(prediction[0]))))


def train_insurance_model(csv_paths: list[Path], output_path: Path, epochs: int = 800, learning_rate: float = 0.01) -> InsuranceModel:
    if not csv_paths:
        raise ValueError("At least one insurance CSV is required.")

    frames = [_load_quote_export(path) for path in csv_paths]
    data = pd.concat(frames, ignore_index=True)
    data = data.dropna(subset=[REQUIRED_TARGET, "driver_age", "vehicle_year", "vehicle_price_gbp"])
    data["vehicle_age"] = pd.Timestamp.utcnow().year - data["vehicle_year"]
    data["vehicle_age"] = data["vehicle_age"].clip(lower=0)

    numeric_mean = data[NUMERIC_FIELDS].mean().to_numpy(dtype=float)
    numeric_std = data[NUMERIC_FIELDS].std().replace(0, 1).fillna(1).to_numpy(dtype=float)
    categories = {
        field: sorted(data[field].fillna("unknown").astype(str).str.lower().unique().tolist())
        for field in CATEGORICAL_FIELDS
    }

    x = _encode_frame(
        data,
        numeric_fields=NUMERIC_FIELDS,
        categorical_fields=CATEGORICAL_FIELDS,
        categories=categories,
        numeric_mean=numeric_mean,
        numeric_std=numeric_std,
    )
    y_raw = data[REQUIRED_TARGET].to_numpy(dtype=float).reshape(-1, 1)
    target_mean = float(y_raw.mean())
    target_std = float(y_raw.std()) or 1.0
    y = (y_raw - target_mean) / target_std

    hidden_size = min(32, max(8, x.shape[1] // 2))
    rng = np.random.default_rng(42)
    w1 = rng.normal(0.0, 0.15, size=(x.shape[1], hidden_size))
    b1 = np.zeros((1, hidden_size))
    w2 = rng.normal(0.0, 0.15, size=(hidden_size, 1))
    b2 = np.array([[float(y.mean())]])

    for _ in range(epochs):
        z1 = x @ w1 + b1
        a1 = np.maximum(0.0, z1)
        y_hat = a1 @ w2 + b2
        error = y_hat - y

        batch = len(x)
        d_y = (2.0 / batch) * error
        d_w2 = a1.T @ d_y
        d_b2 = d_y.sum(axis=0, keepdims=True)
        d_a1 = d_y @ w2.T
        d_z1 = d_a1 * (z1 > 0)
        d_w1 = x.T @ d_z1
        d_b1 = d_z1.sum(axis=0, keepdims=True)

        w2 -= learning_rate * d_w2
        b2 -= learning_rate * d_b2
        w1 -= learning_rate * d_w1
        b1 -= learning_rate * d_b1

    model = InsuranceModel(
        numeric_fields=NUMERIC_FIELDS,
        categorical_fields=CATEGORICAL_FIELDS,
        categories=categories,
        numeric_mean=numeric_mean,
        numeric_std=numeric_std,
        hidden_weights=w1,
        hidden_bias=b1[0],
        output_weights=w2[:, 0],
        output_bias=float(b2[0, 0]),
        training_rows=int(len(data)),
        target_mean=target_mean,
        target_std=target_std,
    )
    save_insurance_model(model, output_path)
    return model


def save_insurance_model(model: InsuranceModel, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        path,
        numeric_fields=np.array(model.numeric_fields, dtype=object),
        categorical_fields=np.array(model.categorical_fields, dtype=object),
        category_json=np.array(json.dumps(model.categories), dtype=object),
        numeric_mean=model.numeric_mean,
        numeric_std=model.numeric_std,
        hidden_weights=model.hidden_weights,
        hidden_bias=model.hidden_bias,
        output_weights=model.output_weights,
        output_bias=np.array([model.output_bias]),
        training_rows=np.array([model.training_rows]),
        target_mean=np.array([model.target_mean]),
        target_std=np.array([model.target_std]),
    )


def load_insurance_model(path: Path) -> InsuranceModel | None:
    if not path.exists():
        return None

    payload = np.load(path, allow_pickle=True)
    return InsuranceModel(
        numeric_fields=[str(x) for x in payload["numeric_fields"].tolist()],
        categorical_fields=[str(x) for x in payload["categorical_fields"].tolist()],
        categories={k: list(v) for k, v in json.loads(str(payload["category_json"].item())).items()},
        numeric_mean=payload["numeric_mean"].astype(float),
        numeric_std=payload["numeric_std"].astype(float),
        hidden_weights=payload["hidden_weights"].astype(float),
        hidden_bias=payload["hidden_bias"].astype(float),
        output_weights=payload["output_weights"].astype(float),
        output_bias=float(payload["output_bias"][0]),
        training_rows=int(payload["training_rows"][0]),
        target_mean=float(payload["target_mean"][0]),
        target_std=float(payload["target_std"][0]),
    )


def _load_quote_export(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    renamed = frame.rename(columns={column: _canonical_name(column) for column in frame.columns})
    normalized = pd.DataFrame()

    for target in set(NUMERIC_FIELDS + CATEGORICAL_FIELDS + [REQUIRED_TARGET]):
        normalized[target] = renamed[target] if target in renamed.columns else None

    for column in NUMERIC_FIELDS + [REQUIRED_TARGET]:
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce")

    for column in CATEGORICAL_FIELDS:
        normalized[column] = normalized[column].astype("string").str.strip().str.lower().fillna("unknown")

    return normalized


def _canonical_name(name: str) -> str:
    lowered = name.strip().lower().replace("-", "_").replace(" ", "_")
    for canonical, aliases in ALIASES.items():
        if lowered == canonical or lowered in aliases:
            return canonical
    return lowered


def _encode_frame(
    frame: pd.DataFrame,
    *,
    numeric_fields: list[str],
    categorical_fields: list[str],
    categories: dict[str, list[str]],
    numeric_mean: np.ndarray,
    numeric_std: np.ndarray,
) -> np.ndarray:
    numeric = frame.reindex(columns=numeric_fields).copy()
    numeric = numeric.fillna(pd.Series(numeric_mean, index=numeric_fields))
    numeric_values = numeric.to_numpy(dtype=float)
    numeric_values = (numeric_values - numeric_mean) / numeric_std

    encoded: list[np.ndarray] = [numeric_values]
    for field in categorical_fields:
        values = frame.get(field, pd.Series(["unknown"] * len(frame))).fillna("unknown").astype(str).str.lower()
        field_categories = categories[field]
        arr = np.zeros((len(frame), len(field_categories)), dtype=float)
        index = {category: i for i, category in enumerate(field_categories)}
        unknown_slot = index.get("unknown")
        for row_idx, value in enumerate(values):
            col_idx = index.get(value, unknown_slot)
            if col_idx is not None:
                arr[row_idx, col_idx] = 1.0
        encoded.append(arr)

    return np.concatenate(encoded, axis=1)


def _record_from_inputs(listing: Listing, driver: DriverProfile) -> dict[str, Any]:
    current_year = pd.Timestamp.utcnow().year
    return {
        "driver_age": driver.age,
        "years_licensed": driver.years_licensed,
        "no_claims_years": driver.no_claims_years,
        "claims_last_5y": driver.claims_last_5y,
        "convictions_last_5y": driver.convictions_last_5y,
        "annual_mileage": driver.annual_mileage,
        "vehicle_year": listing.year,
        "vehicle_age": max(0, current_year - listing.year),
        "vehicle_price_gbp": listing.price_gbp,
        "vehicle_mileage_miles": listing.mileage_miles,
        "engine_size_l": listing.engine_size_l,
        "make": (listing.make or "unknown").lower(),
        "model": (listing.model or "unknown").lower(),
        "fuel_type": (listing.fuel_type or "unknown").lower(),
        "transmission": (listing.transmission or "unknown").lower(),
        "body_type": (listing.body_type or "unknown").lower(),
        "postcode_area": (driver.postcode_area or "unknown").lower(),
        "parking": (driver.parking or "unknown").lower(),
        "cover_type": (driver.cover_type or "unknown").lower(),
    }
