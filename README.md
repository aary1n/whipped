# whipped

UK used-car pricing intelligence engine. Paste a listing, get a fair price band, ripoff index, hidden-risk score, and suggested counteroffer.

## Quickstart

```bash
pip install -e ".[dev]"
python scripts/prepare_sample_data.py
python scripts/run_demo.py
```

To run a localhost website for manual testing:

```bash
PYTHONPATH=src python scripts/run_web.py --host 127.0.0.1 --port 8000
```

Then open `http://127.0.0.1:8000`.

## Train A Real Insurance Model

If you have real insurance quote data in CSV form, you can train the app to predict annual premiums from that data:

```bash
PYTHONPATH=src python scripts/train_insurance_model.py quotes/batch_01.csv quotes/batch_02.csv
```

Expected columns can use these names or close aliases:

- `annual_premium_gbp`
- `driver_age`
- `years_licensed`
- `no_claims_years`
- `claims_last_5y`
- `convictions_last_5y`
- `annual_mileage`
- `vehicle_year`
- `vehicle_price_gbp`
- `vehicle_mileage_miles`
- `engine_size_l`
- `make`
- `model`
- `fuel_type`
- `transmission`
- `body_type`
- `postcode_area`
- `parking`
- `cover_type`

When `data/insurance/insurance_model.npz` exists, the ownership forecast automatically uses that trained model for insurance instead of the fallback heuristic.

## Build A Market Database

If you export listing data from Auto Trader or another marketplace into CSV files, you can turn them into a local SQLite training set:

```bash
python scripts/build_market_database.py exports/autotrader_batch_01.csv exports/autotrader_batch_02.csv
```

This writes `data/market/autotrader_listings.sqlite` with a `market_listings` table containing:

- normalized listing fields like `make`, `model`, `year`, `price_gbp`, `mileage_miles`
- a derived `expected_price_gbp`
- a binary `is_overpriced` label where the ask is at least 10% above expected price
- an `investment_score` and `investment_signal` for shortlist ranking

This repo currently supports importing CSV exports, not direct scraping. That keeps the pipeline safer and lets you iterate on the ML side first.

## Flow

```
listing text → parsed listing → feature extraction → fair price range
                                                   → risk score
                                                   → ripoff index
                                                   → explanation + counteroffer
```

## Layout

| Path | Owner | Purpose |
|------|-------|---------|
| `src/whipped/domain/` | shared | Data models |
| `src/whipped/ingest/` | data team | Parsing & dataset loading |
| `src/whipped/features/` | data team | Feature extraction |
| `src/whipped/pricing/` | pricing team | Fair price range estimation |
| `src/whipped/scoring/` | scoring team | Ripoff index, risk score, explanations |
| `src/whipped/app.py` | app team | Demo entrypoint |
