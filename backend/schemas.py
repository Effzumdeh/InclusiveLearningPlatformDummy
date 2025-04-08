# backend/schemas.py
from pydantic import BaseModel
from typing import Optional

class CourseCreate(BaseModel):
    title: str
    short_description: str
    course_content: str
    didactic_simulation: bool = False

class CourseResponse(BaseModel):
    course_id: int
    title: str
    status: str
    didactic_feedback: Optional[dict] = None