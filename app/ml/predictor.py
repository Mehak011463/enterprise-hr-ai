import json
import joblib
import pandas as pd
from app.config import MODEL_PATH, MODEL_METADATA_PATH

class AttritionPredictor:
    def __init__(self):
        self.model = joblib.load(MODEL_PATH)
        self.metadata = json.loads(MODEL_METADATA_PATH.read_text()) if MODEL_METADATA_PATH.exists() else {}

    def predict(self, features: dict) -> dict:
        frame = pd.DataFrame([features])
        expected = list(self.model.feature_names_in_)
        missing = [c for c in expected if c not in frame.columns]
        if missing:
            raise ValueError(f"Missing model features: {missing[:10]}")
        frame = frame[expected]
        probability = float(self.model.predict_proba(frame)[:, 1][0])
        label = "Yes" if probability >= 0.5 else "No"
        risk = "High Risk" if probability >= 0.70 else ("Medium Risk" if probability >= 0.40 else "Low Risk")
        return {"attrition_prediction": label, "attrition_probability": round(probability, 4),
                "risk_level": risk, "model_version": self.metadata.get("version", "unknown")}
