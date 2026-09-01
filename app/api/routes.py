from fastapi import APIRouter, Depends, HTTPException
from app.auth import require_api_key
from app.validation.schemas import SkillGapRequest, RecommendationRequest, PolicyQuery, AttritionRequest
from app.ml.predictor import AttritionPredictor
from app.services.skill_service import SkillService
from app.services.recommendation_service import RecommendationService
from app.services.analytics_service import AnalyticsService
from app.services.policy_service import PolicyService
from app.services.agent_service import HRAgentOrchestrator

router=APIRouter(prefix="/api/v1",dependencies=[Depends(require_api_key)])
predictor=AttritionPredictor(); skills=SkillService(); recs=RecommendationService()
analytics=AnalyticsService(); policy=PolicyService()
agent=HRAgentOrchestrator(analytics,skills,recs)

@router.post("/predict/attrition")
def predict(req: AttritionRequest):
    try: return predictor.predict(req.features)
    except ValueError as e: raise HTTPException(422,str(e))

@router.post("/skills/gap-analysis")
def gap(req: SkillGapRequest):
    try: return skills.get_skill_gap(req.current_skills,req.target_onet_code)
    except ValueError as e: raise HTTPException(404,str(e))

@router.post("/recommendations")
def recommend(req: RecommendationRequest):
    return {"recommendations":recs.recommend(req.missing_skills,req.limit)}

@router.post("/policy/search")
def policy_search(req: PolicyQuery):
    return {"results":policy.search(req.query,req.top_k)}

@router.get("/dashboard/summary")
def summary(): return analytics.summary()

@router.get("/dashboard/attrition-by-department")
def by_dept(): return {"data":analytics.attrition_by_department()}

@router.get("/dashboard/skill-gaps")
def skill_gaps(): return {"data":analytics.skill_gaps()}

@router.get("/dashboard/recommendations")
def recommendations(): return {"data":analytics.recommendations()}

@router.get("/employees/{employee_id}")
def employee(employee_id:int):
    try:return analytics.employee(employee_id)
    except ValueError as e: raise HTTPException(404,str(e))

@router.get("/agents/employee/{employee_id}/plan")
def employee_plan(employee_id:int):
    try:return agent.employee_plan(employee_id)
    except ValueError as e: raise HTTPException(404,str(e))
