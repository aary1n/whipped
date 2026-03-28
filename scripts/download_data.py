"""Download and extract the Kaggle used-car dataset.

Usage:
    KAGGLE_API_TOKEN=<your_token> python scripts/download_data.py

Get your token:
    kaggle.com → Account → Settings → "Create New API Token" → copy the token string
"""
from __future__ import annotations

import glob
import os
import subprocess
import sys
import zipfile
from pathlib import Path

DATASET = "adityadesai13/used-car-dataset-ford-and-mercedes"
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
EXTRACT_DIR = RAW_DIR / "used-cars-100k"
ZIP_PATH = RAW_DIR / "used-car-dataset-ford-and-mercedes.zip"


def main() -> None:
    if EXTRACT_DIR.exists() and any(EXTRACT_DIR.glob("*.csv")):
        print(f"Data already present at {EXTRACT_DIR} — nothing to do.")
        return

    token = os.environ.get("KAGGLE_API_TOKEN")
    if not token:
        print(
            "KAGGLE_API_TOKEN is not set.\n\n"
            "  1. Go to kaggle.com > Account > Settings > 'Create New API Token'\n"
            "  2. Copy the token string (starts with KGAT_...)\n"
            "  3. Re-run with:\n\n"
            "       KAGGLE_API_TOKEN=<your_token> python scripts/download_data.py\n"
        )
        sys.exit(1)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {DATASET} ...")
    _kaggle("datasets", "download", DATASET, "--path", str(RAW_DIR), token=token)

    print(f"Extracting to {EXTRACT_DIR} ...")
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        zf.extractall(EXTRACT_DIR)

    n = len(list(EXTRACT_DIR.glob("*.csv")))
    print(f"Done. {n} CSV files ready in {EXTRACT_DIR.relative_to(Path.cwd())}")


def _kaggle(*args: str, token: str) -> None:
    env = {**os.environ, "KAGGLE_API_TOKEN": token}
    result = subprocess.run([_find_kaggle(), *args], env=env, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr.strip() or result.stdout.strip())
        sys.exit(1)
    if result.stdout.strip():
        print(result.stdout.strip())


def _find_kaggle() -> str:
    patterns = [
        str(Path.home() / "AppData" / "Roaming" / "Python" / "Python*" / "Scripts" / "kaggle.exe"),
        str(Path.home() / "AppData" / "Local" / "Programs" / "Python" / "Python*" / "Scripts" / "kaggle.exe"),
    ]
    for pattern in patterns:
        matches = glob.glob(pattern)
        if matches:
            return matches[0]
    return "kaggle"


if __name__ == "__main__":
    main()
