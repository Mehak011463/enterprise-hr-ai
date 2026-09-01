import pandas as pd
from app.config import PROCESSED_DIR

class AnalyticsService:
    def __init__(self):
        self.emp=pd.read_csv(PROCESSED_DIR/"workforce_intelligence_final.csv")
        self.eng=pd.read_csv(PROCESSED_DIR/"engagement_processed.csv")
    def summary(self):
        return {"total_employees":int(len(self.emp)),
                "high_risk_employees":int((self.emp.Attrition_Risk_Score>=.7).sum()),
                "medium_risk_employees":int(((self.emp.Attrition_Risk_Score>=.4)&(self.emp.Attrition_Risk_Score<.7)).sum()),
                "low_risk_employees":int((self.emp.Attrition_Risk_Score<.4).sum()),
                "average_satisfaction":round(float(self.emp.Overall_Satisfaction.mean()),2)}
    def attrition_by_department(self):
        return self.emp.groupby("Department",as_index=False)["Attrition_Risk_Score"].mean().round(4).to_dict("records")
    def skill_gaps(self):
        rows=[]
        for s in self.emp.Skill_Gap.fillna(""):
            for skill in [x.strip() for x in s.split(",") if x.strip()]:
                rows.append(skill)
        if not rows: return []
        return pd.Series(rows).value_counts().rename_axis("skill").reset_index(name="employees_missing").to_dict("records")
    def recommendations(self):
        cols=["EmployeeID","JobRole","Attrition_Risk_Score","Risk_Category","Skill_Gap","Recommendation","Automated_HR_Action"]
        return self.emp[cols].sort_values("Attrition_Risk_Score",ascending=False).head(100).to_dict("records")
    def employee(self, employee_id):
        rows=self.emp[self.emp.EmployeeID==employee_id]
        if rows.empty: raise ValueError("Employee not found")
        r=rows.iloc[0].replace({pd.NA:None}).to_dict()
        return r
