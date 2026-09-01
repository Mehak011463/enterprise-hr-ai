import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
MODEL_PATH = BASE_DIR / "models" / "attrition_pipeline.joblib"
MODEL_METADATA_PATH = BASE_DIR / "models" / "model_metadata.json"
API_KEY = os.getenv("HR_API_KEY", "")
ENVIRONMENT = os.getenv("HR_ENVIRONMENT", "development")
