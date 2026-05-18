from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from shared.database.postgres import get_db

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint verifying PostgreSQL connectivity."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {e}"
        
    return {
        "status": "online",
        "service": "api-gateway",
        "database": db_status
    }
