from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from shared.database.postgres import get_db, UpdateReport

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("")
async def get_update_reports(db: Session = Depends(get_db)):
    """
    Retrieves all update reports from the database, ordered by generation time descending.
    """
    reports = db.query(UpdateReport).order_by(UpdateReport.generated_at.desc()).all()
    return reports
