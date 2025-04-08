from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from schemas_auth import UserRegister, UserLogin, Token
from models import User
from dependencies import get_db
from auth_utils import get_password_hash, verify_password, create_access_token
from datetime import timedelta

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=409, detail="Ein Nutzer mit diesem Namen existiert bereits.")
    hashed_pw = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        password_hash=hashed_pw,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token = create_access_token(
        data={"user_id": new_user.id, "role": new_user.role},
        expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user.identifier).first()
    if not existing:
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten.")
    if not verify_password(user.password, existing.password_hash):
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten.")
    access_token = create_access_token(data={"user_id": existing.id, "role": existing.role})
    return {"access_token": access_token, "token_type": "bearer"}