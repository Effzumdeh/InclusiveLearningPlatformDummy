from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db, get_current_user
from models import User, Course, UserStatistic, CourseOpenEvent, QuizQuestion, QuizResponse
from auth_utils import get_password_hash
from datetime import date, timedelta

router = APIRouter(prefix="/api/guardian", tags=["guardian"])

def ensure_parent(current_user: User):
    if current_user.is_child_account:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

@router.get("/children", response_model=list)
def list_children(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    List child-accounts created by the current user, plus today's and 7-day average stats.
    """
    ensure_parent(current_user)
    children = db.query(User).filter(User.parent_user_id == current_user.id).all()
    result = []
    today = date.today()
    week_ago = today - timedelta(days=6)
    for ch in children:
        stat_today = db.query(UserStatistic).filter_by(user_id=ch.id, date=today).first()
        m_today = stat_today.minutes if stat_today else 0
        stats_week = db.query(UserStatistic).filter(
            UserStatistic.user_id == ch.id,
            UserStatistic.date >= week_ago
        ).all()
        avg = sum(s.minutes for s in stats_week) / len(stats_week) if stats_week else 0
        result.append({
            "id": ch.id,
            "username": ch.username,
            "minutes_today": m_today,
            "average_last_7_days": round(avg, 2)
        })
    return result

@router.post("/children", status_code=status.HTTP_201_CREATED)
def create_child(data: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Create a new child-account under this parent.
    """
    ensure_parent(current_user)
    uname = data.get("username")
    pwd = data.get("password")
    if not uname or not pwd:
        raise HTTPException(status_code=400, detail="username and password required")
    if db.query(User).filter(User.username == uname).first():
        raise HTTPException(status_code=409, detail="Username already exists")
    hashed = get_password_hash(pwd)
    child = User(
        username=uname,
        password_hash=hashed,
        role="User",
        is_child_account=True,
        parent_user_id=current_user.id
    )
    db.add(child)
    db.commit()
    db.refresh(child)
    return {"id": child.id, "username": child.username}

@router.post("/children/{child_id}/convert")
def convert_child(child_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Convert a child-account into a regular account (irreversible).
    """
    ensure_parent(current_user)
    child = db.query(User).filter(
        User.id == child_id,
        User.parent_user_id == current_user.id,
        User.is_child_account == True
    ).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found or not yours")
    child.is_child_account = False
    child.parent_user_id = None
    db.commit()
    return {"message": "converted"}

@router.get("/children/{child_id}/courses", response_model=list)
def list_child_courses(child_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get a child's enrolled courses plus progress metrics.
    """
    ensure_parent(current_user)
    child = db.query(User).filter(User.id == child_id, User.parent_user_id == current_user.id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found or not yours")
    courses = []
    for c in child.courses:
        opened = db.query(CourseOpenEvent).filter_by(user_id=child.id, course_id=c.id).first() is not None
        total_q = len(c.quiz_questions)
        answered = db.query(QuizResponse.user_id).join(QuizQuestion).filter(
            QuizQuestion.course_id == c.id,
            QuizResponse.user_id == child.id
        ).count()
        completed = (answered >= total_q) and total_q > 0
        courses.append({
            "course_id": c.id,
            "title": c.title,
            "opened": opened,
            "answered_count": answered,
            "total_questions": total_q,
            "completed": completed
        })
    return courses

@router.post("/children/{child_id}/courses/{course_id}", status_code=status.HTTP_201_CREATED)
def enroll_child_course(child_id: int, course_id: int,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    """
    Enroll a child into a course.
    """
    ensure_parent(current_user)
    child = db.query(User).filter(User.id == child_id, User.parent_user_id == current_user.id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found or not yours")
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course in child.courses:
        raise HTTPException(status_code=409, detail="Already enrolled")
    child.courses.append(course)
    db.commit()
    return {"message": "enrolled"}

@router.delete("/children/{child_id}/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def unenroll_child_course(child_id: int, course_id: int,
                          db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    """
    Unenroll a child from a course.
    """
    ensure_parent(current_user)
    child = db.query(User).filter(User.id == child_id, User.parent_user_id == current_user.id).first()
    course = db.query(Course).filter(Course.id == course_id).first()
    if not child or not course or course not in child.courses:
        raise HTTPException(status_code=404, detail="Not enrolled")
    child.courses.remove(course)
    db.commit()
    return

@router.get("/children/{child_id}/settings")
def get_child_settings(child_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieve a child's display settings.
    """
    ensure_parent(current_user)
    child = db.query(User).filter(User.id == child_id, User.parent_user_id == current_user.id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found or not yours")
    return {
        "show_chat": child.show_chat,
        "show_stats": child.show_stats,
        "show_comments": child.show_comments
    }

@router.put("/children/{child_id}/settings")
def update_child_settings(child_id: int, settings: dict,
                          db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    """
    Update a child's display settings.
    """
    ensure_parent(current_user)
    child = db.query(User).filter(User.id == child_id, User.parent_user_id == current_user.id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found or not yours")
    if "show_chat" in settings:
        child.show_chat = bool(settings["show_chat"])
    if "show_stats" in settings:
        child.show_stats = bool(settings["show_stats"])
    if "show_comments" in settings:
        child.show_comments = bool(settings["show_comments"])
    db.commit()
    return {"message": "settings updated"}