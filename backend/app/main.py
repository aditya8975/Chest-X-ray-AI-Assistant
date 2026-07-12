from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, engine
from app.routers import studies, dashboard

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description=(
        "Research/educational chest X-ray triage assistant: pathology "
        "classification, Grad-CAM explainability, and draft report "
        "generation. NOT a diagnostic device — see /api/health for the "
        "standing disclaimer."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/media/uploads", StaticFiles(directory=str(settings.upload_dir)), name="uploads")
app.mount("/media/heatmaps", StaticFiles(directory=str(settings.heatmap_dir)), name="heatmaps")

app.include_router(studies.router, prefix=settings.api_prefix)
app.include_router(dashboard.router, prefix=settings.api_prefix)


@app.get("/api/health")
def health_check():
    from app.services.model_registry import get_device
    return {
        "status": "ok",
        "device": get_device(),
        "disclaimer": (
            "This system is a research/educational demo. It is not an FDA-cleared medical "
            "device and must not be used for real clinical diagnosis or patient care."
        ),
    }


@app.get("/")
def root():
    return {"name": settings.app_name, "docs": "/docs", "health": "/api/health"}
