from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
SAMPLE_DIR = DATA_DIR / "sample"
SAMPLE_CSV = SAMPLE_DIR / "sample.csv"
<<<<<<< HEAD
MARKET_DIR = DATA_DIR / "market"
MARKET_DB = MARKET_DIR / "autotrader_listings.sqlite"
INSURANCE_DIR = DATA_DIR / "insurance"
INSURANCE_MODEL = INSURANCE_DIR / "insurance_model.npz"
=======
RAW_DIR = DATA_DIR / "raw"
KAGGLE_RAW_DIR = RAW_DIR / "used-cars-100k"
>>>>>>> e17d8da (refactor: remove .json requirement for kaggle verif)
