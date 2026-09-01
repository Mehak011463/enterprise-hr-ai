# Enterprise HR AI — Workforce Intelligence Platform

A working MVP for workforce intelligence: attrition prediction, engagement analytics, semantic-ish skill-gap analysis, learning recommendations, HR policy retrieval, governed employee plans, FastAPI APIs and a Streamlit dashboard.

## Important data-integrity decision
The supplied performance dataset contains 5,000 records with IDs that do **not overlap** the 1,470 EmployeeNumber values in the attrition dataset. The original project arbitrarily mapped the first performance IDs to attrition IDs; that is not a defensible join. The completed pipeline therefore keeps the two datasets separate. Attrition modeling uses the attrition dataset only, while performance/engagement remains an independent analytics source.

The source data also has no employee-level current-skills table. `data/processed/employee_skills_demo.csv` is explicitly controlled synthetic/demo data generated from O*NET role requirements with a fixed seed. Do not use it for real HR decisions.

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
In another terminal:
```bash
streamlit run app/streamlit_app.py
```
API docs: `http://127.0.0.1:8000/docs`

For production-like authentication:
```bash
set HR_ENVIRONMENT=production
set HR_API_KEY=<strong-secret>
```
and provide `X-API-Key` to protected API calls.

## Core endpoints
- `GET /health`
- `POST /api/v1/predict/attrition`
- `GET /api/v1/dashboard/summary`
- `GET /api/v1/dashboard/attrition-by-department`
- `GET /api/v1/dashboard/skill-gaps`
- `GET /api/v1/dashboard/recommendations`
- `GET /api/v1/employees/{employee_id}`
- `POST /api/v1/skills/gap-analysis`
- `POST /api/v1/recommendations`
- `POST /api/v1/policy/search`
- `GET /api/v1/agents/employee/{employee_id}/plan`

## Tests
```bash
pytest -q
```

## Architecture
Streamlit → FastAPI → governed services → model / skill engine / recommendation engine / policy retrieval → processed data + model registry.

The agent layer in this MVP is deterministic orchestration. It demonstrates tool boundaries and workflow composition without granting an LLM direct authority over HR data or actions. A production LLM/LangGraph layer can be added behind the same governed service interfaces.

## Security notes
- Raw data is never exposed directly through an API.
- API input is validated with Pydantic.
- Production mode requires an API key.
- CORS is restricted to the local dashboard origins.
- Employee actions are recommendations only; human HR review is required.
- Sensitive attributes should be excluded from production training after a formal fairness/legal review.
