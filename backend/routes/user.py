from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from dependencies import get_db, get_current_user
from models import User, UserStatistic, Course
from datetime import datetime, date
import os

router = APIRouter(prefix="/api/user", tags=["user"])

@router.get("/settings")
def get_user_settings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {
        "daily_target": current_user.daily_target,
        "is_full_name_public": current_user.is_full_name_public,
        "is_age_public": current_user.is_age_public,
        "is_description_public": current_user.is_description_public,
        "is_profile_picture_public": current_user.is_profile_picture_public,
        "show_chat": current_user.show_chat,
        "show_stats": current_user.show_stats,
        "show_comments": current_user.show_comments,
        "theme_preference": current_user.theme_preference
    }

@router.put("/settings")
def update_user_settings(new_setting: dict,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    try:
        new_target = int(new_setting.get("daily_target"))
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Ungültiger Wert für daily_target")
    current_user.daily_target = new_target
    db.commit()
    return {"daily_target": current_user.daily_target}

@router.get("/tutorial-status")
def get_tutorial_status(db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    from models import TutorialStatus
    status_record = db.query(TutorialStatus).filter(TutorialStatus.user_id == current_user.id).first()
    if status_record:
        return {"completed": status_record.completed, "completed_at": status_record.completed_at}
    else:
        return {"completed": False, "completed_at": None}

@router.post("/tutorial-status")
def set_tutorial_status(status: dict,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    from models import TutorialStatus
    completed = status.get("completed", False)
    status_record = db.query(TutorialStatus).filter(TutorialStatus.user_id == current_user.id).first()
    if status_record:
        status_record.completed = completed
        if completed:
            status_record.completed_at = datetime.utcnow()
    else:
        status_record = TutorialStatus(
            user_id=current_user.id,
            completed=completed,
            completed_at=datetime.utcnow() if completed else None
        )
        db.add(status_record)
    db.commit()
    return {"completed": status_record.completed, "completed_at": status_record.completed_at}

@router.get("/profile")
def get_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "full_name": current_user.full_name,
        "birth_date": current_user.birth_date.isoformat() if current_user.birth_date else None,
        "short_description": current_user.short_description,
        "profile_picture": current_user.profile_picture,
        "points": current_user.points,
        "is_full_name_public": current_user.is_full_name_public,
        "is_age_public": current_user.is_age_public,
        "is_description_public": current_user.is_description_public,
        "is_profile_picture_public": current_user.is_profile_picture_public,
        "show_chat": current_user.show_chat,
        "show_stats": current_user.show_stats,
        "show_comments": current_user.show_comments,
        "theme_preference": current_user.theme_preference,
        "is_child_account": current_user.is_child_account,
        "parent_user_id": current_user.parent_user_id
    }

@router.put("/profile")
def update_profile(
    full_name: str = Form(None),
    birth_date: str = Form(None),
    short_description: str = Form(None),
    profile_picture: UploadFile = File(None),
    is_full_name_public: str = Form("true"),
    is_age_public: str = Form("true"),
    is_description_public: str = Form("true"),
    is_profile_picture_public: str = Form("true"),
    show_chat: str = Form("true"),
    show_stats: str = Form("true"),
    show_comments: str = Form("true"),
    theme_preference: str = Form("system"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if full_name is not None:
        current_user.full_name = full_name
    if birth_date:
        try:
            bd = datetime.strptime(birth_date, "%Y-%m-%d").date()
            current_user.birth_date = bd
            today = date.today()
            current_user.age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid birth_date format. Expected YYYY-MM-DD.")
    if short_description is not None:
        current_user.short_description = short_description
    if profile_picture is not None:
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_location = os.path.join(upload_dir, profile_picture.filename).replace("\\", "/")
        with open(file_location, "wb") as f:
            f.write(profile_picture.file.read())
        current_user.profile_picture = file_location
    current_user.is_full_name_public = (is_full_name_public.lower() == "true")
    current_user.is_age_public = (is_age_public.lower() == "true")
    current_user.is_description_public = (is_description_public.lower() == "true")
    current_user.is_profile_picture_public = (is_profile_picture_public.lower() == "true")
    current_user.show_chat = (show_chat.lower() == "true")
    current_user.show_stats = (show_stats.lower() == "true")
    current_user.show_comments = (show_comments.lower() == "true")
    current_user.theme_preference = theme_preference
    db.commit()
    return {
        "username": current_user.username,
        "full_name": current_user.full_name,
        "birth_date": current_user.birth_date.isoformat() if current_user.birth_date else None,
        "short_description": current_user.short_description,
        "profile_picture": current_user.profile_picture,
        "points": current_user.points,
        "is_full_name_public": current_user.is_full_name_public,
        "is_age_public": current_user.is_age_public,
        "is_description_public": current_user.is_description_public,
        "is_profile_picture_public": current_user.is_profile_picture_public,
        "show_chat": current_user.show_chat,
        "show_stats": current_user.show_stats,
        "show_comments": current_user.show_comments,
        "theme_preference": current_user.theme_preference
    }

@router.get("/{user_id}/public-profile")
def get_public_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Nutzer nicht gefunden")
    computed_age = None
    if user.birth_date and user.is_age_public:
        today = date.today()
        computed_age = today.year - user.birth_date.year - ((today.month, today.day) < (user.birth_date.month, user.birth_date.day))
    return {
        "username": user.username,
        "full_name": user.full_name if user.is_full_name_public else None,
        "age": computed_age,
        "short_description": user.short_description if user.is_description_public else None,
        "profile_picture": user.profile_picture if user.is_profile_picture_public else None,
        "points": user.points
    }

# NEW: Heartbeat endpoint using SQLite UPSERT
@router.post("/heartbeat", status_code=status.HTTP_200_OK)
def heartbeat(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Increments today's learning-minutes for the current user by one,
    using SQLite UPSERT with correct ON CONFLICT clause on (date, user_id).
    """
    today_str = date.today().isoformat()
    sql = text("""
        INSERT INTO user_statistics(date, user_id, minutes)
        VALUES(:d, :uid, 1)
        ON CONFLICT(date, user_id) DO UPDATE
          SET minutes = user_statistics.minutes + 1
    """)
    db.execute(sql, {"d": today_str, "uid": current_user.id})
    db.commit()
    stat = db.query(UserStatistic).filter_by(date=date.fromisoformat(today_str), user_id=current_user.id).first()
    return {"date": today_str, "minutes": stat.minutes}


# NEW: Self-enrollment endpoints
@router.get("/courses", response_model=list)
def get_enrolled_courses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return [
        {
            "id": c.id,
            "title": c.title,
            "short_description": c.short_description
        } for c in current_user.courses
    ]

@router.post("/courses/{course_id}", status_code=status.HTTP_201_CREATED)
def enroll_course(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Kurs nicht gefunden")
    if course in current_user.courses:
        raise HTTPException(status_code=409, detail="Bereits eingeschrieben")
    current_user.courses.append(course)
    db.commit()
    return {"message": "eingeschrieben", "course_id": course_id}

@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def unenroll_course(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course or course not in current_user.courses:
        raise HTTPException(status_code=404, detail="Nicht eingeschrieben")
    current_user.courses.remove(course)
    db.commit()
    return