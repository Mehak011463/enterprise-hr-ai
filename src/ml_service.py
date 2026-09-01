import joblib
import pandas as pd
import os

MODEL_PATH = "models/attrition_pipeline.joblib"

class MLService:
    def __init__(self):
        if os.path.exists(MODEL_PATH):
            self.model = joblib.load(MODEL_PATH)
        else:
            self.model = None

    def predict_attrition(self, input_features: dict):
        if not self.model:
            return {"error": "Model binary not found."}
        
        df = pd.DataFrame([input_features])
        prob = float(self.model.predict_proba(df)[:, 1][0])
        pred = int(self.model.predict(df)[0])
        
        return {
            "attrition_prediction": "Yes" if pred == 1 else "No",
            "attrition_probability": round(prob, 4),
            "risk_level": "High Risk" if prob >= 0.7 else ("Medium Risk" if prob >= 0.4 else "Low Risk")
        }