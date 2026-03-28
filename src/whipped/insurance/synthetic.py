"""Generate synthetic insurance quotes for local model training."""
from __future__ import annotations

from pathlib import Path
import random

import pandas as pd

from whipped.config import INSURANCE_SYNTHETIC_CSV

MAKES = {
    "ford": [("fiesta", "hatchback", 1.0), ("focus", "hatchback", 1.5), ("kuga", "suv", 2.0)],
    "vauxhall": [("corsa", "hatchback", 1.2), ("astra", "hatchback", 1.4), ("mokka", "suv", 1.6)],
    "toyota": [("yaris", "hatchback", 1.3), ("corolla", "saloon", 1.8), ("rav4", "suv", 2.0)],
    "bmw": [("1series", "hatchback", 1.5), ("3series", "saloon", 2.0), ("x1", "suv", 2.0)],
    "audi": [("a1", "hatchback", 1.4), ("a3", "saloon", 1.6), ("q3", "suv", 2.0)],
    "vw": [("polo", "hatchback", 1.0), ("golf", "hatchback", 1.5), ("tiguan", "suv", 2.0)],
    "mercedes": [("aclass", "hatchback", 1.5), ("cclass", "saloon", 2.0), ("gla", "suv", 2.0)],
}

FUELS = ["petrol", "diesel", "hybrid", "electric"]
TRANSMISSIONS = ["manual", "automatic"]
SEXES = ["female", "male"]
POSTCODE_AREAS = [
    "AB", "BA", "B", "BH", "BN", "BS", "CB", "CF", "CM", "CR",
    "CV", "E", "EC", "EH", "G", "GU", "IP", "KT", "L", "LE",
    "LS", "M", "MK", "N", "NE", "NG", "NW", "OX", "PE", "PL",
    "PO", "RG", "S", "SE", "SL", "SO", "SW", "TN", "W", "WA",
    "WD", "YO",
]
PARKING = ["garage", "driveway", "street", "car_park"]
COVER_TYPES = ["comprehensive", "third_party_fire_theft", "third_party"]


def generate_synthetic_insurance_dataset(
    output_path: Path = INSURANCE_SYNTHETIC_CSV,
    *,
    rows: int = 6000,
    seed: int = 42,
) -> pd.DataFrame:
    random.seed(seed)
    records: list[dict[str, object]] = []
    current_year = 2026

    for _ in range(rows):
        make = random.choice(list(MAKES))
        model, body_type, engine_seed = random.choice(MAKES[make])
        fuel_type = random.choices(FUELS, weights=[0.48, 0.18, 0.22, 0.12])[0]
        transmission = random.choices(TRANSMISSIONS, weights=[0.58, 0.42])[0]
        vehicle_year = random.randint(2009, 2025)
        vehicle_age = current_year - vehicle_year
        annual_mileage = random.randint(5_000, 20_000)
        vehicle_mileage = max(3_000, int(random.gauss((vehicle_age + 1) * annual_mileage, 12_000)))
        vehicle_price = max(2_000, int(25_000 - vehicle_age * 1_150 - vehicle_mileage * 0.03 + random.gauss(0, 1_500)))
        engine_size = round(max(0.9, min(3.2, engine_seed + random.uniform(-0.3, 0.7))), 1)
        driver_age = random.randint(18, 78)
        sex = random.choices(SEXES, weights=[0.49, 0.51])[0]
        years_licensed = min(driver_age - 17, max(0, int(random.gauss((driver_age - 17) * 0.65, 4))))
        no_claims_years = max(0, min(years_licensed, int(random.gauss(max(0, years_licensed - 2), 2))))
        claims_last_5y = random.choices([0, 1, 2, 3], weights=[0.72, 0.19, 0.07, 0.02])[0]
        convictions_last_5y = random.choices([0, 1, 2], weights=[0.9, 0.08, 0.02])[0]
        postcode_area = random.choice(POSTCODE_AREAS)
        parking = random.choices(PARKING, weights=[0.25, 0.35, 0.28, 0.12])[0]
        cover_type = random.choices(COVER_TYPES, weights=[0.74, 0.18, 0.08])[0]
        condition_score = _condition_score(vehicle_age, vehicle_mileage)

        premium = _annual_premium(
            driver_age=driver_age,
            sex=sex,
            years_licensed=years_licensed,
            no_claims_years=no_claims_years,
            claims_last_5y=claims_last_5y,
            convictions_last_5y=convictions_last_5y,
            annual_mileage=annual_mileage,
            vehicle_year=vehicle_year,
            vehicle_price_gbp=vehicle_price,
            vehicle_mileage_miles=vehicle_mileage,
            engine_size_l=engine_size,
            condition_score=condition_score,
            make=make,
            model=model,
            fuel_type=fuel_type,
            transmission=transmission,
            body_type=body_type,
            postcode_area=postcode_area,
            parking=parking,
            cover_type=cover_type,
        )

        records.append(
            {
                "annual_premium_gbp": premium,
                "driver_age": driver_age,
                "sex": sex,
                "years_licensed": years_licensed,
                "no_claims_years": no_claims_years,
                "claims_last_5y": claims_last_5y,
                "convictions_last_5y": convictions_last_5y,
                "annual_mileage": annual_mileage,
                "vehicle_year": vehicle_year,
                "vehicle_price_gbp": vehicle_price,
                "vehicle_mileage_miles": vehicle_mileage,
                "engine_size_l": engine_size,
                "condition_score": condition_score,
                "make": make,
                "model": model,
                "fuel_type": fuel_type,
                "transmission": transmission,
                "body_type": body_type,
                "postcode_area": postcode_area,
                "parking": parking,
                "cover_type": cover_type,
            }
        )

    frame = pd.DataFrame.from_records(records)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False)
    return frame


def _condition_score(vehicle_age: int, vehicle_mileage: int) -> int:
    score = 96.0
    score -= vehicle_age * 2.6
    score -= min(38.0, vehicle_mileage / 5_500)
    return int(max(18, min(99, round(score))))


def _annual_premium(**row: object) -> int:
    driver_age = int(row["driver_age"])
    sex = str(row["sex"])
    years_licensed = int(row["years_licensed"])
    no_claims_years = int(row["no_claims_years"])
    claims_last_5y = int(row["claims_last_5y"])
    convictions_last_5y = int(row["convictions_last_5y"])
    annual_mileage = int(row["annual_mileage"])
    vehicle_year = int(row["vehicle_year"])
    vehicle_price = int(row["vehicle_price_gbp"])
    vehicle_mileage = int(row["vehicle_mileage_miles"])
    engine_size = float(row["engine_size_l"])
    condition_score = int(row["condition_score"])
    fuel_type = str(row["fuel_type"])
    transmission = str(row["transmission"])
    body_type = str(row["body_type"])
    postcode_area = str(row["postcode_area"])
    parking = str(row["parking"])
    cover_type = str(row["cover_type"])

    vehicle_age = 2026 - vehicle_year
    premium = 420.0
    premium += max(0, 27 - driver_age) * 48
    premium += 220 if driver_age < 21 else 0
    premium += max(0, 4 - years_licensed) * 60
    premium -= min(250, no_claims_years * 24)
    premium += claims_last_5y * 210
    premium += convictions_last_5y * 280
    premium += max(0, annual_mileage - 8_000) * 0.018
    premium += vehicle_age * 15
    premium += vehicle_price * 0.02
    premium += vehicle_mileage * 0.003
    premium += max(0.0, engine_size - 1.4) * 140
    premium += {"petrol": 30, "diesel": 70, "hybrid": 55, "electric": 110}[fuel_type]
    premium += {"manual": 0, "automatic": 60}[transmission]
    premium += {"hatchback": 0, "saloon": 35, "suv": 140}[body_type]
    premium += _postcode_load(postcode_area)
    premium += {"garage": -80, "driveway": -35, "street": 95, "car_park": 25}[parking]
    premium += {"comprehensive": 0, "third_party_fire_theft": -45, "third_party": -105}[cover_type]
    premium += {"female": -25, "male": 15}.get(sex, 0)
    premium += max(0, 72 - condition_score) * 7
    premium += random.gauss(0, 65)
    return max(280, int(round(premium)))


def _postcode_load(postcode_area: str) -> int:
    area_loads = {
        "AB": 10, "BA": 0, "B": 45, "BH": 18, "BN": 30, "BS": 28, "CB": 8, "CF": 26, "CM": 40, "CR": 95,
        "CV": 36, "E": 190, "EC": 170, "EH": 12, "G": 30, "GU": 20, "IP": 14, "KT": 42, "L": 65, "LE": 38,
        "LS": 44, "M": 55, "MK": 18, "N": 165, "NE": 20, "NG": 34, "NW": 135, "OX": 10, "PE": 16, "PL": 8,
        "PO": 22, "RG": 16, "S": 24, "SE": 145, "SL": 34, "SO": 18, "SW": 125, "TN": 14, "W": 150, "WA": 26,
        "WD": 35, "YO": 12,
    }
    return area_loads.get(postcode_area, 25)
