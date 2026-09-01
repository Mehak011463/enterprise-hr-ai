"""Reproducible attrition training pipeline."""
from pathlib import Path
import json, joblib, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score
from xgboost import XGBClassifier

ROOT=Path(__file__).resolve().parents[1]
df=pd.read_csv(ROOT/"data/raw/employee_attrition.csv")
y=df["Attrition"].map({"Yes":1,"No":0})
X=df.drop(columns=["Attrition","EmployeeNumber","EmployeeCount","Over18","StandardHours"],errors="ignore")
cat=X.select_dtypes(include="object").columns.tolist(); num=[c for c in X.columns if c not in cat]
pre=ColumnTransformer([("num",SimpleImputer(strategy="median"),num),
 ("cat",Pipeline([("impute",SimpleImputer(strategy="most_frequent")),("onehot",OneHotEncoder(handle_unknown="ignore"))]),cat)])
neg,pos=(y==0).sum(),(y==1).sum()
model=XGBClassifier(n_estimators=250,max_depth=4,learning_rate=.04,subsample=.85,colsample_bytree=.85,
 random_state=42,eval_metric="logloss",scale_pos_weight=neg/pos,n_jobs=2)
pipe=Pipeline([("preprocessor",pre),("model",model)])
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.2,stratify=y,random_state=42)
pipe.fit(Xtr,ytr); p=pipe.predict_proba(Xte)[:,1]; pred=(p>=.5).astype(int)
m={"roc_auc":roc_auc_score(yte,p),"precision":precision_score(yte,p),"recall":recall_score(yte,p),"f1":f1_score(yte,p)}
(ROOT/"models").mkdir(exist_ok=True); joblib.dump(pipe,ROOT/"models/attrition_pipeline.joblib")
(ROOT/"models/model_metadata.json").write_text(json.dumps({"version":"v2.0","algorithm":"XGBoost + preprocessing","training_date":"2026-09-01",**m},indent=2))
print(m)
