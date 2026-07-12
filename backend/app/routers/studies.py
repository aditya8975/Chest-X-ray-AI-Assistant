from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models import Study
from app.schemas import StudyOut
from app.utils.image_utils import unique_stem, save_raw_upload, save_display_image
from app.services.pipeline import run_pipeline

router = APIRouter(prefix="/studies", tags=["studies"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".dcm"}


@router.post("/upload", response_model=StudyOut)
async def upload_study(
    file: UploadFile = File(...),
    patient_ref: str | None = Form(None),
    modality_note: str | None = Form(None),
    db: Session = Depends(get_db),
):
    filename = file.filename or "upload.png"
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type '{ext}'. Use JPEG, PNG, or DICOM (.dcm).")

    raw = await file.read()
    stem = unique_stem(filename)

    try:
        original_path = save_raw_upload(raw, filename, stem)
        pipeline_result = run_pipeline(raw, filename, stem, patient_ref)
    except Exception as e:
        raise HTTPException(422, f"Could not process this image: {e}")

    display_path = save_display_image(pipeline_result["display_image"], stem)

    study = Study(
        filename=filename,
        original_path=original_path,
        display_path=display_path,
        patient_ref=patient_ref,
        modality_note=modality_note,
        findings=pipeline_result["findings"],
        positive_findings=pipeline_result["positive_findings"],
        borderline_findings=pipeline_result["borderline_findings"],
        heatmaps=pipeline_result["heatmaps"],
        report_text=pipeline_result["report_text"],
        model_version=pipeline_result["model_version"],
        overall_confidence=pipeline_result["overall_confidence"],
    )
    db.add(study)
    db.commit()
    db.refresh(study)
    return study.to_dict()


@router.get("", response_model=list[StudyOut])
def list_studies(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    studies = db.query(Study).order_by(desc(Study.created_at)).offset(skip).limit(limit).all()
    return [s.to_dict() for s in studies]


@router.get("/{study_id}", response_model=StudyOut)
def get_study(study_id: int, db: Session = Depends(get_db)):
    study = db.query(Study).filter(Study.id == study_id).first()
    if not study:
        raise HTTPException(404, "Study not found")
    return study.to_dict()


@router.delete("/{study_id}")
def delete_study(study_id: int, db: Session = Depends(get_db)):
    study = db.query(Study).filter(Study.id == study_id).first()
    if not study:
        raise HTTPException(404, "Study not found")
    db.delete(study)
    db.commit()
    return {"status": "deleted", "id": study_id}
