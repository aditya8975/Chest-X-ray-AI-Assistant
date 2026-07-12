from pydantic import BaseModel
from typing import Optional, Any


class StudyOut(BaseModel):
    id: int
    filename: str
    original_path: str
    display_path: str
    patient_ref: Optional[str] = None
    modality_note: Optional[str] = None
    findings: dict[str, float]
    positive_findings: dict[str, float]
    borderline_findings: dict[str, float]
    heatmaps: Optional[dict[str, str]] = None
    report_text: str
    model_version: str
    overall_confidence: float
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_studies: int
    avg_positive_findings: float
    pathology_frequency: dict[str, int]
    avg_confidence: float
    studies_flagged_high_risk: int
    studies_by_day: dict[str, int]
