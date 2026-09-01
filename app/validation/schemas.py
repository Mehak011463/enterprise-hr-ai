from pydantic import BaseModel, Field, ConfigDict
from typing import Any

class SkillGapRequest(BaseModel):
    current_skills: list[str] = Field(min_length=0, max_length=100)
    target_onet_code: str = Field(min_length=3, max_length=30)

class RecommendationRequest(BaseModel):
    missing_skills: list[str] = Field(max_length=100)
    limit: int = Field(default=5, ge=1, le=20)

class PolicyQuery(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    top_k: int = Field(default=3, ge=1, le=10)

class AttritionRequest(BaseModel):
    features: dict[str, Any]
