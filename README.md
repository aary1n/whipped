# Whipped

UK used-car pricing intelligence engine. Enter a listing, get a statistical fair price band, hidden-risk flags, brand-tax analysis, and a 5-year ownership forecast including insurance, depreciation, and repair costs.

Built for the 2026 Quant hackathon.

## Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- **Kaggle account** (free) for the dataset download

## Setup (from scratch)

### 1. Clone and install Python dependencies

```bash
git clone <repo-url> && cd whipped
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -e ".[dev]"
```

### 2. Download the Kaggle dataset

Go to [kaggle.com](https://www.kaggle.com/) → Account → Settings → **Create New API Token**. This gives you a `kaggle.json` with your token.

```bash
KAGGLE_API_TOKEN=<your_token> python scripts/download_data.py
```

Downloads 9 CSV files (~98k UK used-car listings) to `data/raw/used-cars-100k/`.

Dataset: [`adityadesai13/used-car-dataset-ford-and-mercedes`](https://www.kaggle.com/datasets/adityadesai13/used-car-dataset-ford-and-mercedes)

### 3. Prepare sample data

```bash
python scripts/prepare_sample_data.py
```

Samples the Kaggle CSVs into `data/sample/sample.csv` (capped at 20 rows per make/model for fast lookups). Falls back to a synthetic 150-row generator if the Kaggle data is missing.

### 4. Generate synthetic insurance quotes

```bash
PYTHONPATH=src python scripts/prepare_synthetic_insurance_data.py --rows 6000 --seed 42
```

Writes `data/insurance/synthetic_insurance_quotes.csv` — 6,000 realistic UK insurance quotes with driver profiles, vehicle specs, and annual premiums.

### 5. Train the insurance model

```bash
PYTHONPATH=src python scripts/train_insurance_model.py data/insurance/synthetic_insurance_quotes.csv
```

Trains a 2-layer neural network on the synthetic data and saves weights to `data/insurance/insurance_model.npz`. When this file exists, the ownership forecast uses the trained model instead of a heuristic fallback.

### 6. Start the backend

```bash
PYTHONPATH=src python scripts/run_web.py --host 127.0.0.1 --port 8000
```

Starts a WSGI server on `http://127.0.0.1:8000` serving the `/api/evaluate` endpoint.

### 7. Start the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Opens `http://localhost:3000`. The Next.js dev server proxies `/api/*` requests to the backend on port 8000.

## Quick reference

| Command | What it does |
|---------|-------------|
| `python scripts/download_data.py` | Download Kaggle CSVs |
| `python scripts/prepare_sample_data.py` | Build sample dataset |
| `PYTHONPATH=src python scripts/prepare_synthetic_insurance_data.py` | Generate insurance training data |
| `PYTHONPATH=src python scripts/train_insurance_model.py <csv>` | Train insurance neural net |
| `PYTHONPATH=src python scripts/run_web.py` | Start backend API |
| `cd frontend && npm run dev` | Start frontend dev server |
| `python scripts/run_demo.py` | Run mocked demo (no data needed) |

## How it works

```
listing + driver profile
  → ingest/       parse & validate
  → features/     extract feature vector (age, mileage band, fuel, etc.)
  → pricing/      4-tier cascade → fair price range + confidence
  → scoring/      ripoff index, risk flags, counteroffer, explanation
  → insurance/    trained neural net → annual premium estimate
  → ownership/    5-year forecast (depreciation + repairs + insurance)
  → brand_tax/    KNN cross-make analysis → brand premium & recommendations
```

### Pricing cascade

The fair-range estimator tries progressively broader filters until it finds enough comparables:

1. Exact match: same make, model, year, fuel type, transmission
2. Relaxed: same make, model, year
3. Broad: same make, model (any year)
4. Fallback: corpus median

### Brand tax model

A KNN model with a 6-feature vector (engine size, mileage, year delta, fuel/transmission/body match) finds "mechanical twins" — cars with similar specs but different badges. The price difference is the brand tax: how much extra (or less) you pay for the badge.

### Insurance model

A 2-layer neural network trained on synthetic UK quote data. Features include driver profile (age, sex, license years, claims history, no-claims bonus), vehicle profile (price, age, engine size, fuel type), and location (postcode area, parking type). Falls back to a rule-based heuristic if no trained model is available.

## Project layout

```
whipped/
├── src/whipped/
│   ├── domain/models.py      Shared data models (Listing, Verdict, etc.)
│   ├── ingest/               CSV loading & validation
│   ├── features/             Feature extraction
│   ├── pricing/              Fair price range, brand tax KNN
│   ├── scoring/              Ripoff index, risk flags, explanations, ownership
│   ├── insurance/            Synthetic data generator, neural net model
│   ├── app.py                Core evaluation pipeline
│   └── webapp.py             WSGI API server
├── scripts/                  CLI entry points (download, prepare, train, run)
├── frontend/                 Next.js 15 + React 19 + Tailwind CSS
│   ├── app/
│   │   ├── page.tsx          Home / landing page
│   │   ├── analyze/          Main analysis form + results
│   │   ├── ownership/        5-year cost forecast
│   │   ├── market/           Comparables table + brand tax
│   │   └── lib/              Shared types, context, helpers
│   └── next.config.ts        API proxy config
├── data/                     Datasets & trained models (gitignored)
└── pyproject.toml            Python dependencies (pandas + numpy)
```

## Tech stack

- **Backend:** Python 3.11, pandas, numpy, stdlib WSGI server
- **Frontend:** Next.js 15, React 19, TypeScript, Tailwind CSS
- **ML:** Custom 2-layer neural net (numpy only, no PyTorch/sklearn)
- **Data:** Kaggle UK used-car dataset (98k+ listings) + synthetic insurance quotes
