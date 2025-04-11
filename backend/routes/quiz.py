from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import get_db, get_current_user
from models import Course, QuizQuestion, QuizResponse, User
from datetime import datetime
from fastapi.responses import StreamingResponse
from io import BytesIO

router = APIRouter(tags=["quiz"])

# Endpoint for students to get quiz questions that are not yet correctly answered
@router.get("/api/courses/{course_id}/quiz-questions")
def get_quiz_questions(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Kurs nicht gefunden")
    questions = course.quiz_questions
    unanswered = []
    for q in questions:
        correct_response = db.query(QuizResponse).filter(
            QuizResponse.user_id == current_user.id,
            QuizResponse.question_id == q.id,
            QuizResponse.is_correct == True
        ).first()
        if not correct_response:
            unanswered.append({
                "id": q.id,
                "question_text": q.question_text,
                "option1": q.option1,
                "option2": q.option2,
                "option3": q.option3,
                "option4": q.option4
            })
    return unanswered

# Neuer Endpunkt für Lehrer/Dozenten: Alle Quizfragen eines Kurses abrufen
@router.get("/api/courses/{course_id}/quiz-questions/all")
def get_all_quiz_questions(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["Teacher", "Admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Kurs nicht gefunden")
    questions = course.quiz_questions
    return [{
         "id": q.id,
         "question_text": q.question_text,
         "option1": q.option1,
         "option2": q.option2,
         "option3": q.option3,
         "option4": q.option4,
         "correct_option": q.correct_option
    } for q in questions]

# Teacher endpoints for managing quiz questions
@router.post("/api/courses/{course_id}/quiz-questions")
def create_quiz_question(course_id: int, question: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["Teacher", "Admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Kurs nicht gefunden")
    try:
        new_question = QuizQuestion(
            course_id=course_id,
            question_text=question.get("question_text"),
            option1=question.get("option1"),
            option2=question.get("option2"),
            option3=question.get("option3"),
            option4=question.get("option4"),
            correct_option=question.get("correct_option")
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid question format")
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return {"id": new_question.id, "message": "Frage erstellt"}

@router.put("/api/quiz-questions/{question_id}")
def update_quiz_question(question_id: int, question: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["Teacher", "Admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    q = db.query(QuizQuestion).filter(QuizQuestion.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Frage nicht gefunden")
    q.question_text = question.get("question_text", q.question_text)
    q.option1 = question.get("option1", q.option1)
    q.option2 = question.get("option2", q.option2)
    q.option3 = question.get("option3", q.option3)
    q.option4 = question.get("option4", q.option4)
    q.correct_option = question.get("correct_option", q.correct_option)
    db.commit()
    return {"id": q.id, "message": "Frage aktualisiert"}

@router.delete("/api/quiz-questions/{question_id}")
def delete_quiz_question(question_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["Teacher", "Admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    q = db.query(QuizQuestion).filter(QuizQuestion.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Frage nicht gefunden")
    db.delete(q)
    db.commit()
    return {"message": "Frage gelöscht"}

# Endpoint for submitting quiz responses
@router.post("/api/courses/{course_id}/quiz/{question_id}/response")
def submit_quiz_response(course_id: int, question_id: int, response: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(QuizQuestion).filter(QuizQuestion.id == question_id, QuizQuestion.course_id == course_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Frage nicht gefunden")
    selected_option = response.get("selected_option")
    if selected_option not in [1, 2, 3, 4]:
        raise HTTPException(status_code=400, detail="Ungültige Auswahl")
    is_correct = (selected_option == q.correct_option)
    quiz_response = QuizResponse(
        user_id=current_user.id,
        question_id=q.id,
        is_correct=is_correct,
        timestamp=datetime.utcnow()
    )
    db.add(quiz_response)
    if is_correct:
        current_user.points += 25
    db.commit()
    return {"correct": is_correct, "points": current_user.points}

# Endpoint for certificate generation
@router.get("/api/courses/{course_id}/certificate")
def generate_certificate(course_id: int, name: str = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Kurs nicht gefunden")
    questions = course.quiz_questions
    for q in questions:
        correct_response = db.query(QuizResponse).filter(
            QuizResponse.user_id == current_user.id,
            QuizResponse.question_id == q.id,
            QuizResponse.is_correct == True
        ).first()
        if not correct_response:
            raise HTTPException(status_code=400, detail="Nicht alle Quizfragen wurden korrekt beantwortet.")
    participant_name = name if name else (current_user.full_name if current_user.full_name else current_user.username)
    completion_date = datetime.utcnow().date().isoformat()
    course_title = course.title

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ImportError:
        raise HTTPException(status_code=500, detail="ReportLab nicht installiert.")
    
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 100, "Zertifikat")
    
    c.setFont("Helvetica", 16)
    text = f"Hiermit wird bestätigt, dass {participant_name}"
    c.drawCentredString(width/2, height - 150, text)
    
    text = f"den Kurs '{course_title}' erfolgreich abgeschlossen hat."
    c.drawCentredString(width/2, height - 180, text)
    
    text = f"Abschlussdatum: {completion_date}"
    c.drawCentredString(width/2, height - 210, text)
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=Zertifikat_{course_id}.pdf"})