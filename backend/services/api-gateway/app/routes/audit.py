from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from shared.database.postgres import get_db, AuditLog

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("")
async def get_audit_logs(db: Session = Depends(get_db)):
    """
    Retrieves all audit logs from the database, ordered by creation time descending.
    """
    logs = db.query(AuditLog).order_by(AuditLog.performed_at.desc()).all()
    return logs
