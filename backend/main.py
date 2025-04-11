from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
from datetime import date, timedelta
from database import engine, SessionLocal, Base
from models import Course, LearningPath, UserStatistic, Comment, User
from dependencies import get_db, get_current_user
from auth_utils import get_password_hash

# Erstelle alle Tabellen, falls sie noch nicht existieren.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Lernplattform API",
    description="Backend-API zur Unterstützung der Lernplattform.",
    version="1.0.0"
)

# Binde den Ordner "uploads" als statische Dateien ein, damit Profilbilder verfügbar sind.
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

origins = ["http://localhost", "http://localhost:8080"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event() -> None:
    # Stelle sicher, dass alle Tabellen existieren (falls die DB neu ist oder gelöscht wurde)
    Base.metadata.create_all(bind=engine)
    
    inspector = inspect(engine)
    # Migrate courses table: add missing columns if needed.
    if inspector.has_table("courses"):
        course_columns = [col["name"] for col in inspector.get_columns("courses")]
        with engine.begin() as connection:
            if "short_description" not in course_columns:
                connection.execute(text("ALTER TABLE courses ADD COLUMN short_description VARCHAR"))
                print("Spalte 'short_description' zu Tabelle courses hinzugefügt.")
            if "course_content" not in course_columns:
                connection.execute(text("ALTER TABLE courses ADD COLUMN course_content VARCHAR"))
                print("Spalte 'course_content' zu Tabelle courses hinzugefügt.")
                if "detailed_description" in course_columns:
                    connection.execute(text("UPDATE courses SET course_content = detailed_description"))
                    print("Werte von 'detailed_description' in 'course_content' kopiert.")
    # Migrate comments table: add missing column "parent_id"
    if inspector.has_table("comments"):
        comment_columns = [col["name"] for col in inspector.get_columns("comments")]
        with engine.begin() as connection:
            if "parent_id" not in comment_columns:
                connection.execute(text("ALTER TABLE comments ADD COLUMN parent_id INTEGER"))
                print("Spalte 'parent_id' zu Tabelle comments hinzugefügt.")
    
    db: Session = SessionLocal()
    if db.query(Course).first() is None:
        course1 = Course(
            title="Digitale Diversität",
            short_description="Platzhalterinhalte zur digitalen Diversität.",
            course_content=""
        )
        course2 = Course(
            title="Fortgeschrittene Python-Techniken",
            short_description="Vertiefung in fortgeschrittene Python-Konzepte.",
            course_content=""
        )
        course3 = Course(
            title="Datenbanken und SQL",
            short_description="Einführung in relationale Datenbanken und SQL.",
            course_content=""
        )
        db.add_all([course1, course2, course3])
        db.commit()
    if db.query(LearningPath).first() is None:
        courses = db.query(Course).all()
        learning_path = LearningPath(name="Demo Lernpfad", courses=courses)
        db.add(learning_path)
        db.commit()
    today = date.today()
    for i in range(7):
        stat_date = today - timedelta(days=i)
        if not db.query(UserStatistic).filter(UserStatistic.date == stat_date).first():
            minutes = 30 + i * 10
            user_stat = UserStatistic(date=stat_date, minutes=minutes)
            db.add(user_stat)
    if not db.query(User).filter(User.username == "admin").first():
        admin_user = User(
            username="admin",
            password_hash=get_password_hash("admin"),
            role="Admin"
        )
        db.add(admin_user)
    db.commit()
    db.close()

@app.get("/api")
def read_api() -> dict:
    return {"message": "Hello from FastAPI with Database, Usage Stats and User Settings!"}

@app.get("/api/learning-paths")
def get_learning_paths(db: Session = Depends(get_db)) -> list:
    learning_paths = db.query(LearningPath).all()
    result = []
    for lp in learning_paths:
        result.append({
            "id": lp.id,
            "name": lp.name,
            "courses": [{"id": course.id, "title": course.title, "short_description": course.short_description} for course in lp.courses]
        })
    return result

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)) -> list:
    stats = db.query(UserStatistic).order_by(UserStatistic.date).all()
    result = [{"date": stat.date.isoformat(), "minutes": stat.minutes} for stat in stats]
    return result

@app.get("/api/comments/{course_id}")
def get_comments(course_id: int, db: Session = Depends(get_db)) -> list:
    comments = db.query(Comment).filter(Comment.course_id == course_id).order_by(Comment.timestamp).all()
    comment_dict = {}
    for comment in comments:
        comment_dict[comment.id] = {
            "id": comment.id,
            "course_id": comment.course_id,
            "content": comment.content,
            "timestamp": comment.timestamp.isoformat(),
            "username": comment.user.username if comment.user else "",
            "user_id": comment.user.id if comment.user else None,
            "parent_id": comment.parent_id,
            "replies": []
        }
    root_comments = []
    for c in comment_dict.values():
        if c["parent_id"]:
            parent = comment_dict.get(c["parent_id"])
            if parent:
                parent["replies"].append(c)
            else:
                root_comments.append(c)
        else:
            root_comments.append(c)
    return root_comments

from dependencies import get_current_user
@app.post("/api/comments/{course_id}")
def post_comment(course_id: int, new_comment: dict, db: Session = Depends(get_db), current_user = Depends(get_current_user)) -> dict:
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Kurs nicht gefunden")
    content = new_comment.get("content")
    if not content:
        raise HTTPException(status_code=400, detail="Kommentarinhalt darf nicht leer sein")
    parent_id = new_comment.get("parent_id")
    if parent_id:
        parent_comment = db.query(Comment).filter(Comment.id == parent_id, Comment.course_id == course_id).first()
        if not parent_comment:
            raise HTTPException(status_code=400, detail="Ungültiger parent_id")
    comment = Comment(course_id=course_id, content=content, user_id=current_user.id, parent_id=parent_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {
        "id": comment.id,
        "course_id": comment.course_id,
        "content": comment.content,
        "timestamp": comment.timestamp.isoformat(),
        "username": current_user.username,
        "user_id": current_user.id,
        "parent_id": comment.parent_id,
        "replies": []
    }

from routes import courses, auth, admin, user, quiz
app.include_router(courses.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(user.router)
app.include_router(quiz.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)