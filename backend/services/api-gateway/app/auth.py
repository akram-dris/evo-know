import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "secure_default_jwt_secret_key_2026_evo_know")
ALGORITHM = "HS256"

security = HTTPBearer()

def create_api_token(client_name: str, scopes: list[str] = []) -> str:
    payload = {
        "sub": client_name,
        "scopes": scopes,
        "exp": datetime.utcnow() + timedelta(days=365)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

from sqlalchemy.orm import Session
from shared.database.postgres import get_db, User

def get_current_user(
    payload: dict = Depends(verify_token),
    db: Session = Depends(get_db)
) -> User:
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing subject"
        )
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user not found"
        )
    if user.status != "approved":
        status_fr = "en attente d'approbation" if user.status == "pending" else "rejeté"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"L'accès à votre compte est {status_fr}."
        )
    return user

def require_role(allowed_roles: list[str]):
    def dependency(user: User = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous n'avez pas l'autorisation d'effectuer cette action."
            )
        return user
    return dependency
