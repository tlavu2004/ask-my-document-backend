# app/config.py
import os
from pathlib import Path

APP_ENV = os.environ.get("APP_ENV", "prod")  # 'prod' | 'test'

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / ("data_test" if APP_ENV == "test" else "data")

UPLOAD_DIR = DATA_DIR / "uploads"
INDEX_DIR = DATA_DIR / "index"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
INDEX_DIR.mkdir(parents=True, exist_ok=True)
