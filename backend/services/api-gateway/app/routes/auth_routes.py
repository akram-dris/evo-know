import hashlib
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.auth import create_api_token
from shared.database.postgres import get_db, User

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str

def verify_password(plain_password: str, hashed_password: str) -> bool:
    calc_hash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
    return calc_hash == hashed_password

@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate a human user and return a session token and their role.
    """
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
        
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
        
    # Generate token with user role scope
    token = create_api_token(user.username, [user.role])
    
    return {
        "token": token,
        "user": {
            "username": user.username,
            "email": user.email,
            "role": user.role
        },
        "role": user.role
    }
