from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
SAMPLE_DIR = DATA_DIR / "sample"
SAMPLE_CSV = SAMPLE_DIR / "sample.csv"
MARKET_DIR = DATA_DIR / "market"
MARKET_DB = MARKET_DIR / "autotrader_listings.sqlite"
INSURANCE_DIR = DATA_DIR / "insurance"
INSURANCE_MODEL = INSURANCE_DIR / "insurance_model.npz"
