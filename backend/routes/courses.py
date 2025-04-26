from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db, get_optional_user, get_current_user
from models import Course, CourseOpenEvent, QuizQuestion, QuizResponse, User, user_course_association
from typing import Dict, List, Optional
import requests
import re
from sqlalchemy import func

router = APIRouter(prefix="/api/courses", tags=["courses"])

def check_links(html: str) -> List[str]:
    urls = re.findall(r'href="(https?://[^"]+)"', html or "")
    broken = []
    for url in set(urls):
        try:
            resp = requests.head(url, timeout=5)
            if resp.status_code >= 400:
                broken.append(url)
        except Exception:
            broken.append(url)
    return broken

@router.get("", response_model=list)
def read_courses(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Return all courses with an 'enrolled' flag for the logged-in user.
    """
    courses = db.query(Course).all()
    result = []
    for c in courses:
        enrolled = False
        if current_user:
            enrolled = db.query(user_course_association).filter_by(
                user_id=current_user.id,
                course_id=c.id
            ).first() is not None
        result.append({
            "id": c.id,
            "title": c.title,
            "short_description": c.short_description,
            "enrolled": enrolled
        })
    return result

@router.get("/{course_id}")
def read_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Kurs nicht gefunden")
    # Log open event
    if current_user:
        evt = CourseOpenEvent(user_id=current_user.id, course_id=course_id)
        db.add(evt)
        db.commit()
    return {
        "id": course.id,
        "title": course.title,
        "short_description": course.short_description,
        "course_content": course.course_content
    }

@router.post("", response_model=Dict, status_code=status.HTTP_201_CREATED)
def create_or_update_course(
    course: Dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["Teacher", "Admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    existing = db.query(Course).filter(Course.title == course["title"]).first()
    feedback = {}
    if existing:
        existing.short_description = course.get("short_description")
        existing.course_content = course.get("course_content")
        db.commit()
        db.refresh(existing)
        status_text = "aktualisiert"
    else:
        existing = Course(
            title=course.get("title"),
            short_description=course.get("short_description"),
            course_content=course.get("course_content")
        )
        db.add(existing)
        db.commit()
        db.refresh(existing)
        status_text = "erstellt"
    if course.get("didactic_simulation"):
        feedback = {
            "UDL": "Die Inhalte sollten in alternativen Formaten vorliegen.",
            "LearningFirstPrinciples": "Die Grundlagen sollten stärker strukturiert sein.",
            "ARCS": "Mehr interaktive Elemente zur Steigerung der Aufmerksamkeit einfügen."
        }
    broken = check_links(course.get("course_content"))
    return {
        "course_id": existing.id,
        "title": existing.title,
        "status": status_text,
        "didactic_feedback": feedback,
        "broken_links": broken
    }

@router.put("/{course_id}", response_model=Dict)
def update_course(
    course_id: int,
    course: Dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["Teacher", "Admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    existing = db.query(Course).filter(Course.id == course_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Kurs nicht gefunden")
    if existing.title != course.get("title"):
        other = db.query(Course).filter(Course.title == course.get("title")).first()
        if other:
            raise HTTPException(status_code=409, detail="Ein Kurs mit diesem Titel existiert bereits.")
    existing.title = course.get("title")
    existing.short_description = course.get("short_description")
    existing.course_content = course.get("course_content")
    db.commit()
    db.refresh(existing)
    feedback = {}
    if course.get("didactic_simulation"):
        feedback = {
            "UDL": "Die Inhalte sollten in alternativen Formaten vorliegen.",
            "LearningFirstPrinciples": "Die Grundlagen sollten stärker strukturiert sein.",
            "ARCS": "Mehr interaktive Elemente zur Steigerung der Aufmerksamkeit einfügen."
        }
    broken = check_links(course.get("course_content"))
    return {
        "course_id": existing.id,
        "title": existing.title,
        "status": "aktualisiert",
        "didactic_feedback": feedback,
        "broken_links": broken
    }

@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["Teacher", "Admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    c = db.query(Course).filter(Course.id == course_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Kurs nicht gefunden")
    db.delete(c)
    db.commit()
    return

@router.get("/{course_id}/analytics")
def course_analytics(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["Teacher", "Admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Kurs nicht gefunden")
    unique_openers = db.query(CourseOpenEvent.user_id).filter(
        CourseOpenEvent.course_id == course_id
    ).distinct().count()
    total_q = len(course.quiz_questions)
    unique_quiz = db.query(QuizResponse.user_id).join(QuizQuestion).filter(
        QuizQuestion.course_id == course_id
    ).distinct().count()
    sub = db.query(
        QuizResponse.user_id,
        func.count(QuizResponse.id).label("cnt")
    ).join(QuizQuestion).filter(
        QuizQuestion.course_id == course_id
    ).group_by(QuizResponse.user_id).subquery()
    avg_ans = db.query(func.avg(sub.c.cnt)).scalar() or 0
    completed_users = db.query(sub.c.user_id).filter(sub.c.cnt >= total_q).count()
    percent_completed = (completed_users / unique_openers * 100) if unique_openers else 0
    return {
        "unique_openers": unique_openers,
        "unique_quiz_participants": unique_quiz,
        "avg_questions_answered": avg_ans,
        "percent_completed": percent_completed
    }

@router.get("/{course_id}/link-report")
def link_report(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["Teacher", "Admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Kurs nicht gefunden")
    broken = check_links(course.course_content)
    distinct = len(set(re.findall(r'href="(https?://[^"]+)"', course.course_content or "")))
    return {
        "total_checked": distinct,
        "broken_count": len(broken),
        "broken_links": broken
    }