from __future__ import annotations

from pathlib import Path

from whipped.domain.models import DriverProfile, Listing
from whipped.insurance.model import load_insurance_model, train_insurance_model


def test_train_and_load_insurance_model(tmp_path: Path) -> None:
    csv_path = tmp_path / "quotes.csv"
    csv_path.write_text(
        "\n".join(
                [
                    "annual_premium_gbp,driver_age,years_licensed,no_claims_years,claims_last_5y,convictions_last_5y,annual_mileage,vehicle_year,vehicle_price_gbp,vehicle_mileage_miles,engine_size_l,sex,make,model,fuel_type,transmission,body_type,postcode_area,parking,cover_type",
                "820,42,20,10,0,0,8000,2020,9000,30000,1.0,female,ford,fiesta,petrol,manual,hatchback,ba,garage,comprehensive",
                "910,37,15,8,0,0,10000,2020,9500,35000,1.0,female,ford,fiesta,petrol,manual,hatchback,ba,driveway,comprehensive",
                "1940,20,2,0,1,0,14000,2020,9000,28000,1.0,male,ford,fiesta,petrol,manual,hatchback,e,street,comprehensive",
                "2260,19,1,0,1,1,16000,2020,9200,29000,1.0,male,ford,fiesta,petrol,manual,hatchback,e,street,comprehensive",
                "1120,31,10,5,0,0,9000,2019,11000,40000,1.6,female,bmw,3series,diesel,automatic,saloon,sw,driveway,comprehensive",
                "1380,29,8,3,0,0,12000,2019,11000,42000,1.6,male,bmw,3series,diesel,automatic,saloon,sw,street,comprehensive",
            ]
        ),
        encoding="utf-8",
    )
    model_path = tmp_path / "insurance_model.npz"

    model = train_insurance_model([csv_path], model_path, epochs=250, learning_rate=0.005)
    reloaded = load_insurance_model(model_path)

    assert reloaded is not None
    assert model.training_rows == 6

    safer = reloaded.predict_annual_premium(
        Listing(make="ford", model="fiesta", year=2020, price_gbp=9_000, mileage_miles=30_000, fuel_type="petrol", transmission="manual", body_type="hatchback", engine_size_l=1.0),
        DriverProfile(age=40, sex="female", years_licensed=18, no_claims_years=10, claims_last_5y=0, convictions_last_5y=0, annual_mileage=8_000, postcode_area="ba", parking="garage", cover_type="comprehensive"),
    )
    riskier = reloaded.predict_annual_premium(
        Listing(make="ford", model="fiesta", year=2020, price_gbp=9_000, mileage_miles=30_000, fuel_type="petrol", transmission="manual", body_type="hatchback", engine_size_l=1.0),
        DriverProfile(age=20, sex="male", years_licensed=1, no_claims_years=0, claims_last_5y=1, convictions_last_5y=1, annual_mileage=15_000, postcode_area="e", parking="street", cover_type="comprehensive"),
    )

    assert safer > 0
    assert riskier > safer
