"""Download and extract the Kaggle used-car dataset.

Usage:
    python scripts/download_data.py

Auth (pick one):
    1. Set KAGGLE_API_TOKEN env var (your token from kaggle.com/settings/account)
    2. Place kaggle.json in ~/.kaggle/kaggle.json  (downloaded from same page)
"""
from __future__ import annotations

import os
import subprocess
import sys
import zipfile
from pathlib import Path

DATASET = "adityadesai13/used-car-dataset-ford-and-mercedes"
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
EXTRACT_DIR = RAW_DIR / "used-cars-100k"
ZIP_PATH = RAW_DIR / "used-car-dataset-ford-and-mercedes.zip"

def _find_kaggle() -> str:
    """Return kaggle executable path, searching common Windows user-install locations."""
    import glob
    patterns = [
        str(Path.home() / "AppData" / "Roaming" / "Python" / "Python*" / "Scripts" / "kaggle.exe"),
        str(Path.home() / "AppData" / "Local" / "Programs" / "Python" / "Python*" / "Scripts" / "kaggle.exe"),
    ]
    for pattern in patterns:
        matches = glob.glob(pattern)
        if matches:
            return matches[0]
    return "kaggle"  # hope it's on PATH


def _kaggle(*args: str) -> None:
    exe = _find_kaggle()
    result = subprocess.run([exe, *args], capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr.strip())
        sys.exit(1)
    print(result.stdout.strip())


def main() -> None:
    if EXTRACT_DIR.exists() and any(EXTRACT_DIR.glob("*.csv")):
        print(f"Data already present at {EXTRACT_DIR} — nothing to do.")
        return

    if not os.environ.get("KAGGLE_API_TOKEN") and not (Path.home() / ".kaggle" / "kaggle.json").exists():
        print(
            "No Kaggle auth found.\n"
            "  Option 1: export KAGGLE_API_TOKEN=<your_token>  (from kaggle.com/settings/account)\n"
            "  Option 2: download kaggle.json from the same page and place it at ~/.kaggle/kaggle.json"
        )
        sys.exit(1)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {DATASET} ...")
    _kaggle("datasets", "download", DATASET, "--path", str(RAW_DIR))

    print(f"Extracting to {EXTRACT_DIR} ...")
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        zf.extractall(EXTRACT_DIR)

    print(f"Done. {len(list(EXTRACT_DIR.glob('*.csv')))} CSV files in {EXTRACT_DIR}")


if __name__ == "__main__":
    main()
