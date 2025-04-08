from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import get_db, get_current_user
from models import User

router = APIRouter(prefix="/api/user", tags=["user"])

@router.get("/settings")
def get_user_settings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {"daily_target": current_user.daily_target}

@router.put("/settings")
def update_user_settings(new_setting: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        new_target = int(new_setting.get("daily_target"))
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Ungültiger Wert für daily_target")
    current_user.daily_target = new_target
    db.commit()
    return {"daily_target": current_user.daily_target}