# backend/routes/courses.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db
from schemas import CourseCreate, CourseResponse
from models import Course

router = APIRouter(prefix="/api/courses", tags=["courses"])

@router.get("", response_model=list)
def read_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).all()
    return [
        {"id": course.id, "title": course.title, "short_description": course.short_description}
        for course in courses
    ]

@router.get("/{course_id}")
def read_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Kurs nicht gefunden")
    return {
        "id": course.id,
        "title": course.title,
        "short_description": course.short_description,
        "course_content": course.course_content
    }

@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    existing_course = db.query(Course).filter(Course.title == course.title).first()
    if existing_course:
        raise HTTPException(
            status_code=409,
            detail="Kurs mit diesem Titel existiert bereits."
        )
    new_course = Course(
        title=course.title,
        short_description=course.short_description,
        course_content=course.course_content
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    feedback = {}
    if course.didactic_simulation:
        feedback = {
            "UDL": "Die Inhalte sollten in alternativen Formaten vorliegen.",
            "LearningFirstPrinciples": "Die Grundlagen sollten stärker strukturiert sein.",
            "ARCS": "Mehr interaktive Elemente zur Steigerung der Aufmerksamkeit einfügen."
        }
    return {
        "course_id": new_course.id,
        "title": new_course.title,
        "status": "erstellt",
        "didactic_feedback": feedback
    }

@router.put("/{course_id}", response_model=CourseResponse)
def update_course(course_id: int, course: CourseCreate, db: Session = Depends(get_db)):
    existing_course = db.query(Course).filter(Course.id == course_id).first()
    if not existing_course:
        raise HTTPException(status_code=404, detail="Kurs nicht gefunden")
    if existing_course.title != course.title:
        other = db.query(Course).filter(Course.title == course.title).first()
        if other:
            raise HTTPException(status_code=409, detail="Kurs mit diesem Titel existiert bereits.")
    existing_course.title = course.title
    existing_course.short_description = course.short_description
    existing_course.course_content = course.course_content
    db.commit()
    db.refresh(existing_course)

    feedback = {}
    if course.didactic_simulation:
        feedback = {
            "UDL": "Die Inhalte sollten in alternativen Formaten vorliegen.",
            "LearningFirstPrinciples": "Die Grundlagen sollten stärker strukturiert sein.",
            "ARCS": "Mehr interaktive Elemente zur Steigerung der Aufmerksamkeit einfügen."
        }
    return {
        "course_id": existing_course.id,
        "title": existing_course.title,
        "status": "aktualisiert",
        "didactic_feedback": feedback
    }

@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Kurs nicht gefunden")
    db.delete(course)
    db.commit()
    return