"""
FastAPI-Backend für die Lernplattform.
Dieses Backend stellt eine API zur Verfügung und integriert eine SQLite-Datenbank,
in der Lernkurse, Lernpfade, Nutzungsstatistiken und Benutzereinstellungen gespeichert werden.
Beim Startup werden Demo-Daten (Kurse, Lernpfade, fiktive Nutzungsstatistiken der letzten 7 Tage
sowie ein Standard-Tagesziel) generiert.
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import date, timedelta
from database import engine, SessionLocal, Base
from models import Course, LearningPath, UserStatistic, UserSetting, Comment

# Erstelle alle Datenbanktabellen, falls sie noch nicht existieren
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Lernplattform API",
    description="Backend-API zur Unterstützung der nutzungsfreundlichen Lernplattform.",
    version="1.0.0"
)

# Erlaube CORS-Anfragen vom Frontend
origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    """
    Abhängigkeitsfunktion zur Bereitstellung einer Datenbanksession.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event() -> None:
    """
    Beim Starten der Anwendung werden Demo-Daten generiert:
    - Demo-Kurse und ein Demo-Lernpfad, sofern noch nicht vorhanden.
    - Fiktive Nutzungsstatistiken (Lernminuten pro Tag) für die letzten 7 Tage.
    - Ein Standard-Tagesziel (falls noch nicht vorhanden).
    """
    db: Session = SessionLocal()
    # Demo-Kurse generieren
    if db.query(Course).first() is None:
        course1 = Course(title="Digitale Diversität", description="Platzhalterinhalte zur digitalen Diversität. Inhalt folgt bald.")
        course2 = Course(title="Fortgeschrittene Python-Techniken", description="Vertiefung in fortgeschrittene Python-Konzepte.")
        course3 = Course(title="Datenbanken und SQL", description="Einführung in relationale Datenbanken und SQL.")
        db.add_all([course1, course2, course3])
        db.commit()
    # Demo-Lernpfad generieren, der alle vorhandenen Kurse enthält
    if db.query(LearningPath).first() is None:
        courses = db.query(Course).all()
        learning_path = LearningPath(name="Demo Lernpfad", courses=courses)
        db.add(learning_path)
        db.commit()
    # Fiktive Nutzungsstatistiken für die letzten 7 Tage generieren
    today = date.today()
    for i in range(7):
        stat_date = today - timedelta(days=i)
        if not db.query(UserStatistic).filter(UserStatistic.date == stat_date).first():
            minutes = 30 + i * 10  # Beispielwerte
            user_stat = UserStatistic(date=stat_date, minutes=minutes)
            db.add(user_stat)
    # Standard-Tagesziel generieren (sofern noch nicht vorhanden)
    if not db.query(UserSetting).first():
        setting = UserSetting(daily_target=60)
        db.add(setting)
    db.commit()
    db.close()

@app.get("/api")
def read_api() -> dict:
    """
    Ein einfacher Endpunkt, der eine JSON-Antwort liefert.
    """
    return {"message": "Hello from FastAPI with Database, Usage Stats and User Settings!"}

@app.get("/api/courses")
def get_courses(db: Session = Depends(get_db)) -> list:
    """
    Endpunkt zum Abrufen aller Kurse.
    """
    courses = db.query(Course).all()
    return [{"id": course.id, "title": course.title, "description": course.description} for course in courses]

@app.get("/api/courses/{course_id}")
def get_course(course_id: int, db: Session = Depends(get_db)) -> dict:
    """
    Endpunkt zum Abrufen der Details eines einzelnen Kurses.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Kurs nicht gefunden")
    return {"id": course.id, "title": course.title, "description": course.description}

@app.get("/api/learning-paths")
def get_learning_paths(db: Session = Depends(get_db)) -> list:
    """
    Endpunkt zum Abrufen aller Lernpfade inklusive der enthaltenen Kurse.
    """
    learning_paths = db.query(LearningPath).all()
    result = []
    for lp in learning_paths:
        result.append({
            "id": lp.id,
            "name": lp.name,
            "courses": [{"id": course.id, "title": course.title, "description": course.description} for course in lp.courses]
        })
    return result

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)) -> list:
    """
    Endpunkt zum Abrufen der Nutzungsstatistiken (Lernminuten pro Tag) der letzten 7 Tage.
    """
    stats = db.query(UserStatistic).order_by(UserStatistic.date).all()
    result = [{"date": stat.date.isoformat(), "minutes": stat.minutes} for stat in stats]
    return result

@app.get("/api/settings")
def get_settings(db: Session = Depends(get_db)) -> dict:
    """
    Endpunkt zum Abrufen der Benutzereinstellungen (tägliches Lernziel).
    """
    setting = db.query(UserSetting).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Einstellung nicht gefunden")
    return {"daily_target": setting.daily_target}

@app.put("/api/settings")
def update_settings(new_setting: dict, db: Session = Depends(get_db)) -> dict:
    """
    Endpunkt zum Aktualisieren des täglichen Lernziels.
    Erwartet ein JSON-Objekt mit dem Schlüssel 'daily_target'.
    """
    setting = db.query(UserSetting).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Einstellung nicht gefunden")
    try:
        new_target = int(new_setting.get("daily_target"))
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Ungültiger Wert für daily_target")
    setting.daily_target = new_target
    db.commit()
    return {"daily_target": setting.daily_target}

@app.get("/api/comments/{course_id}")
def get_comments(course_id: int, db: Session = Depends(get_db)) -> list:
    """
    Endpunkt zum Abrufen aller Kommentare eines Kurses.
    """
    comments = db.query(Comment).filter(Comment.course_id == course_id).order_by(Comment.timestamp).all()
    return [
        {
            "id": comment.id,
            "course_id": comment.course_id,
            "content": comment.content,
            "timestamp": comment.timestamp.isoformat()
        }
        for comment in comments
    ]

@app.post("/api/comments/{course_id}")
def post_comment(course_id: int, new_comment: dict, db: Session = Depends(get_db)) -> dict:
    """
    Endpunkt zum Erstellen eines neuen Kommentars für einen Kurs.
    Erwartet ein JSON-Objekt mit dem Schlüssel 'content'.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Kurs nicht gefunden")
    content = new_comment.get("content")
    if not content:
        raise HTTPException(status_code=400, detail="Kommentarinhalt darf nicht leer sein")
    comment = Comment(course_id=course_id, content=content)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {
        "id": comment.id,
        "course_id": comment.course_id,
        "content": comment.content,
        "timestamp": comment.timestamp.isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)