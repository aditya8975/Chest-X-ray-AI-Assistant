"""
Central configuration for the Chest X-ray AI Assistant.

Defaults to local SQLite so the API runs with zero external setup;
docker-compose overrides DATABASE_URL to point at Postgres.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "Chest X-ray AI Assistant"
    api_prefix: str = "/api"

    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'app.db'}")

    upload_dir: Path = BASE_DIR / "data" / "uploads"
    heatmap_dir: Path = BASE_DIR / "data" / "heatmaps"

    cors_origins: list[str] = ["http://localhost:3000", "*"]

    # torchxrayvision pretrained weight set. "densenet121-res224-all" is
    # trained jointly across NIH ChestX-ray14, CheXpert, MIMIC-CXR and
    # PadChest, giving broad (if noisier) coverage across 18 pathologies.
    xrv_weights: str = os.getenv("XRV_WEIGHTS", "densenet121-res224-all")
    image_size: int = 224

    # A finding is only surfaced in the report / heatmap set if its
    # predicted probability clears this bar.
    finding_threshold: float = float(os.getenv("FINDING_THRESHOLD", "0.5"))
    # Findings between borderline_threshold and finding_threshold are shown
    # in the full results table but flagged as "borderline" rather than
    # a positive finding in the draft report.
    borderline_threshold: float = float(os.getenv("BORDERLINE_THRESHOLD", "0.3"))

    max_heatmaps_per_study: int = 6  # cap Grad-CAM computation cost per upload

    force_cpu: bool = os.getenv("FORCE_CPU", "false").lower() == "true"

    class Config:
        env_file = ".env"


settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.heatmap_dir.mkdir(parents=True, exist_ok=True)
if settings.database_url.startswith("sqlite"):
    (BASE_DIR / "data").mkdir(parents=True, exist_ok=True)
