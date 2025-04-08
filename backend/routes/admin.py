from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import User, UserStatistic
from database import SessionLocal
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from schemas_auth import TokenData
from dependencies import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

router = APIRouter(prefix="/api/admin", tags=["admin"])

def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, "your_secret_key_here", algorithms=["HS256"])
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")
        if user_id is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.role != "Admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return user

@router.get("/users")
def read_users(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "daily_target": user.daily_target
        } for user in users
    ]

@router.get("/aggregated-stats")
def aggregated_stats(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    stats = db.query(UserStatistic).all()
    total = sum(s.minutes for s in stats)
    count = len(stats) if stats else 1
    average = total / count
    return {"total_minutes": total, "average_minutes": average}