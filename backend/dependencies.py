from database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from models import User
from auth_utils import SECRET_KEY, ALGORITHM
from typing import Optional

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
         raise HTTPException(status_code=404, detail="User not found")
    return user

def get_optional_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[User]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            return None
    except JWTError:
        return None
    user = db.query(User).filter(User.id == user_id).first()
    return user