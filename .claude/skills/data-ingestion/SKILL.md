Read this when: working with datasets, sample data, parsing listings, or `ingest/` and `features/` modules.

## Dataset assumptions
- Primary source: Kaggle UK used-car CSVs (100k+ rows typical)
- Expected columns: make, model, year, mileage, fuel_type, transmission, engine_size, price
- Raw CSVs go in `data/raw/` (gitignored); samples in `data/sample/` (committed)
- Sample data: ~100 rows, representative distribution, no PII

## Sample data workflow
- `scripts/prepare_sample_data.py` reads raw CSV → writes `data/sample/sample.csv`
- Sample must be loadable without any raw data present
- Keep sample small enough to commit

## Ingestion conventions
- `ingest/listings.py` — parse unstructured listing text into `Listing` dataclass
- `ingest/datasets.py` — load CSV datasets into list of `Listing`
- Always validate and coerce types at ingestion boundary
- Missing fields → `None`, never invented defaults
- Mileage in miles, prices in GBP integers

## Feature extraction
- `features/extract.py` — `Listing` → `FeatureVector`
- Normalize: age from year, mileage bands, categorical encoding
- Keep features flat (dict or dataclass), no nested structures
