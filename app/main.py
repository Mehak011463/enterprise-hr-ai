from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.api.admin_routes import router as admin_router


app = FastAPI(
    title="Enterprise HR Intelligence API",
    version="2.0.0",
    description=(
        "Governed workforce intelligence API: "
        "attrition prediction, skills, recommendations, "
        "HR policy retrieval and administration."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)

# Normal application APIs
app.include_router(router)

# Admin APIs
app.include_router(admin_router)


@app.get("/health", tags=["System"])
def health():
    return {
        "status": "ok",
        "service": "enterprise-hr-ai",
        "version": "2.0.0",
    }