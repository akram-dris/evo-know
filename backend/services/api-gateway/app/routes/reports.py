from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from shared.database.postgres import get_db, UpdateReport

router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])

@router.get("")
async def get_update_reports(limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    """
    Retrieves all update reports from the database, ordered by generation time descending.
    """
    query = db.query(UpdateReport).order_by(UpdateReport.generated_at.desc())
    total = query.count()
    reports = query.offset(offset).limit(limit).all()
    return {
        "total": total,
        "items": reports
    }
