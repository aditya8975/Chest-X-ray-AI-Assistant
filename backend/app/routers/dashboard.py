from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Study

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

HIGH_RISK_THRESHOLD = 0.85


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    studies = db.query(Study).all()
    total = len(studies)

    if total == 0:
        return {
            "total_studies": 0,
            "avg_positive_findings": 0,
            "pathology_frequency": {},
            "avg_confidence": 0,
            "studies_flagged_high_risk": 0,
            "studies_by_day": {},
        }

    avg_positive = round(sum(len(s.positive_findings) for s in studies) / total, 2)
    avg_confidence = round(sum(s.overall_confidence for s in studies) / total, 3)

    pathology_counter = Counter()
    for s in studies:
        pathology_counter.update(s.positive_findings.keys())

    high_risk = sum(1 for s in studies if s.overall_confidence >= HIGH_RISK_THRESHOLD)

    studies_by_day: dict[str, int] = {}
    for s in studies:
        if s.created_at:
            day = s.created_at.strftime("%Y-%m-%d")
            studies_by_day[day] = studies_by_day.get(day, 0) + 1

    return {
        "total_studies": total,
        "avg_positive_findings": avg_positive,
        "pathology_frequency": dict(pathology_counter.most_common()),
        "avg_confidence": avg_confidence,
        "studies_flagged_high_risk": high_risk,
        "studies_by_day": dict(sorted(studies_by_day.items())),
    }
