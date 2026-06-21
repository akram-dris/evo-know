from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from shared.database.postgres import get_db, AuditLog

router = APIRouter(prefix="/api/v1/audit", tags=["Audit"])

@router.get("")
async def get_audit_logs(limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    """
    Retrieves all audit logs from the database, ordered by creation time descending.
    """
    query = db.query(AuditLog).order_by(AuditLog.performed_at.desc())
    total = query.count()
    logs = query.offset(offset).limit(limit).all()
    return {
        "total": total,
        "items": logs
    }
