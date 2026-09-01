from app.services.skill_service import SkillService
from app.services.recommendation_service import RecommendationService
from app.services.policy_service import PolicyService
from app.services.analytics_service import AnalyticsService

def test_skill_gap():
    s=SkillService()
    out=s.get_skill_gap(["Python","SQL"], "15-1252.00")
    assert 0 <= out["match_score_pct"] <= 100
    assert out["target_title"]

def test_recommendations():
    r=RecommendationService().recommend(["MLOps","Docker"])
    assert len(r) > 0

def test_policy_search():
    out=PolicyService().search("training budget")
    assert out and out[0]["policy_id"]

def test_summary():
    out=AnalyticsService().summary()
    assert out["total_employees"] == 1470
    assert out["high_risk_employees"] >= 0
