from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)

def test_health():
    r=client.get("/health")
    assert r.status_code==200
    assert r.json()["status"]=="ok"

def test_skill_gap_api():
    r=client.post("/api/v1/skills/gap-analysis",json={"current_skills":["Python","SQL"],"target_onet_code":"15-1252.00"})
    assert r.status_code==200
    assert "missing_skills" in r.json()

def test_unknown_employee():
    r=client.get("/api/v1/employees/999999")
    assert r.status_code==404
