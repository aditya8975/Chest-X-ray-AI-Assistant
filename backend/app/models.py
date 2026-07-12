from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class Study(Base):
    """
    One uploaded chest X-ray plus everything the pipeline produces for it:
    per-pathology probabilities, Grad-CAM heatmap paths for the surfaced
    findings, and the generated draft report.
    """
    __tablename__ = "studies"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_path = Column(String, nullable=False)
    display_path = Column(String, nullable=False)  # normalized 8-bit PNG used for viewing/overlay

    patient_ref = Column(String, nullable=True)  # free-text label the user supplies, e.g. "Case 12" — no PHI is parsed or required
    modality_note = Column(String, nullable=True)  # e.g. "PA", "AP", "Lateral" if the user tags it

    # Model output: {pathology: probability} for all 18 labels
    findings = Column(JSON, nullable=False)
    # Subset of `findings` that cleared finding_threshold
    positive_findings = Column(JSON, nullable=False)
    # Subset that cleared borderline_threshold but not finding_threshold
    borderline_findings = Column(JSON, nullable=False)

    # {pathology: heatmap_image_path} for the top findings a Grad-CAM was computed for
    heatmaps = Column(JSON, nullable=True)

    report_text = Column(Text, nullable=False)
    model_version = Column(String, nullable=False)
    overall_confidence = Column(Float, nullable=False)  # max probability across all pathologies

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "original_path": self.original_path,
            "display_path": self.display_path,
            "patient_ref": self.patient_ref,
            "modality_note": self.modality_note,
            "findings": self.findings,
            "positive_findings": self.positive_findings,
            "borderline_findings": self.borderline_findings,
            "heatmaps": self.heatmaps,
            "report_text": self.report_text,
            "model_version": self.model_version,
            "overall_confidence": self.overall_confidence,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
