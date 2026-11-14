from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.getenv("OMNIPOST_DATA_DIR", BASE_DIR / "data"))
UPLOAD_DIR = Path(os.getenv("OMNIPOST_UPLOAD_DIR", DATA_DIR / "uploads"))
DATABASE_PATH = Path(os.getenv("OMNIPOST_DATABASE_PATH", DATA_DIR / "omnipost.db"))
MAX_UPLOAD_BYTES = int(os.getenv("OMNIPOST_MAX_UPLOAD_BYTES", 200 * 1024 * 1024))
ALLOWED_ORIGINS = os.getenv("OMNIPOST_ALLOWED_ORIGINS", "http://localhost:3000").split(",")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

