class HRAgentOrchestrator:
    """Deterministic, governed orchestration MVP. No LLM is granted direct database/tool authority."""
    def __init__(self, analytics, skills, recommendations):
        self.analytics=analytics; self.skills=skills; self.recommendations=recommendations
    def employee_plan(self, employee_id):
        employee=self.analytics.employee(employee_id)
        gap=self.skills.employee_gap(employee_id)
        courses=self.recommendations.recommend(gap.get("missing_skills",[]))
        return {"employee_id":employee_id,"risk_level":employee["Risk_Category"],
                "attrition_probability":employee["Attrition_Risk_Score"],
                "skill_gap":gap,"recommended_courses":courses,
                "next_action":employee["Automated_HR_Action"]}
