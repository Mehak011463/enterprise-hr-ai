import pandas as pd
from app.config import PROCESSED_DIR

def data_drift_snapshot():
    df=pd.read_csv(PROCESSED_DIR/"employee_attrition_processed.csv")
    numeric=df.select_dtypes(include="number")
    return {"rows":len(df),"numeric_means":numeric.mean().round(3).to_dict(),
            "numeric_missing_pct":(numeric.isna().mean()*100).round(3).to_dict()}
