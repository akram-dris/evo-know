import hashlib
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.auth import create_api_token, get_current_user, require_role
from shared.database.postgres import get_db, User

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str  # "Reader" or "Expert"

class ProfileUpdateRequest(BaseModel):
    email: str
    password: Optional[str] = None

def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    calc_hash = get_password_hash(plain_password)
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

    if user.status != "approved":
        status_fr = "en attente d'approbation" if user.status == "pending" else "rejeté"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"L'accès à votre compte est {status_fr}. Veuillez contacter l'administrateur."
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

@router.post("/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user.
    - Readers get approved automatically.
    - Experts are set to pending and require Admin approval.
    """
    # Normalize and validate roles
    role = request.role
    if role not in ["Reader", "Expert"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seuls les rôles 'Reader' et 'Expert' sont autorisés à l'inscription."
        )
        
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce nom d'utilisateur est déjà pris."
        )
        
    # Create new user
    status_val = "approved" if role == "Reader" else "pending"
    
    new_user = User(
        username=request.username,
        email=request.email,
        password_hash=get_password_hash(request.password),
        role=role,
        status=status_val
    )
    db.add(new_user)
    db.commit()
    
    msg = "Inscription réussie ! Vous pouvez vous connecter immédiatement." if status_val == "approved" else "Inscription soumise ! Votre compte est en attente d'approbation par l'administrateur."
    
    return {
        "status": "success",
        "message": msg,
        "user_status": status_val
    }

@router.get("/users")
async def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["Admin"]))
):
    """
    Admin only: List all users in the system.
    """
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [
        {
            "id": str(u.id),
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "status": u.status,
            "created_at": u.created_at.strftime("%Y-%m-%d %H:%M") if u.created_at else None
        } for u in users
    ]

@router.post("/users/{username}/approve")
async def approve_user(
    username: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["Admin"]))
):
    """
    Admin only: Approve a pending expert user registration.
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
    user.status = "approved"
    db.commit()
    return {"status": "success", "message": f"Le compte de {username} a été approuvé avec succès."}

@router.post("/users/{username}/reject")
async def reject_user(
    username: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["Admin"]))
):
    """
    Admin only: Reject a pending user registration.
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
    user.status = "rejected"
    db.commit()
    return {"status": "success", "message": f"Le compte de {username} a été rejeté."}

@router.delete("/users/{username}")
async def delete_user(
    username: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["Admin"]))
):
    """
    Admin only: Delete a user account from the system.
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
    if user.username == admin.username:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas supprimer votre propre compte administrateur.")
        
    db.delete(user)
    db.commit()
    return {"status": "success", "message": f"Le compte de {username} a été supprimé."}

@router.put("/profile")
async def update_profile(
    request: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update profile details for the currently logged in user.
    """
    current_user.email = request.email
    if request.password:
        current_user.password_hash = get_password_hash(request.password)
    db.commit()
    
    return {
        "status": "success",
        "message": "Profil mis à jour avec succès.",
        "user": {
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role
        }
    }


