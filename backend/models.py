from sqlalchemy import Column, Integer, String, Table, ForeignKey, Date, DateTime, Boolean
from sqlalchemy.orm import relationship, backref
from datetime import datetime
from database import Base
from encryption_utils import EncryptedType

# Association table for many-to-many relationship between learning paths and courses
learningpath_course_association = Table(
    "learningpath_course",
    Base.metadata,
    Column("learningpath_id", Integer, ForeignKey("learning_paths.id")),
    Column("course_id", Integer, ForeignKey("courses.id"))
)

# Association table for many-to-many relationship between users and courses (enrollment)
user_course_association = Table(
    "user_course",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("course_id", Integer, ForeignKey("courses.id"))
)

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    short_description = Column(String)
    course_content = Column(String)
    comments = relationship("Comment", back_populates="course", cascade="all, delete")
    quiz_questions = relationship("QuizQuestion", back_populates="course", cascade="all, delete")
    open_events = relationship("CourseOpenEvent", back_populates="course", cascade="all, delete")
    users = relationship("User", secondary=user_course_association, back_populates="courses")

class LearningPath(Base):
    __tablename__ = "learning_paths"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    courses = relationship(
        "Course",
        secondary=learningpath_course_association,
        backref="learning_paths"
    )

class UserStatistic(Base):
    __tablename__ = "user_statistics"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=False, index=True)
    minutes = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="statistics")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    replies = relationship(
        "Comment",
        backref=backref("parent", remote_side=[id])
    )
    course = relationship("Course", back_populates="comments")
    user = relationship("User")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(EncryptedType(256), unique=True, index=True, nullable=True)
    phone = Column(EncryptedType(64), unique=True, index=True, nullable=True)
    password_hash = Column(String)
    role = Column(String, default="User")
    daily_target = Column(Integer, default=60)
    points = Column(Integer, default=0)
    full_name = Column(EncryptedType(128), nullable=True)
    age = Column(Integer, default=0)
    birth_date = Column(Date, nullable=True)
    short_description = Column(EncryptedType(1024), nullable=True)
    profile_picture = Column(EncryptedType(256), nullable=True)
    is_full_name_public = Column(Boolean, default=True)
    is_age_public = Column(Boolean, default=True)
    is_description_public = Column(Boolean, default=True)
    is_profile_picture_public = Column(Boolean, default=True)
    show_chat = Column(Boolean, default=True)
    show_stats = Column(Boolean, default=True)
    show_comments = Column(Boolean, default=True)
    theme_preference = Column(String, default="system")

    # child-account flag and parent linkage
    is_child_account = Column(Boolean, default=False)
    parent_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    children = relationship(
        "User",
        backref=backref("parent", remote_side=[id])
    )

    courses = relationship("Course", secondary=user_course_association, back_populates="users")

    statistics = relationship("UserStatistic", back_populates="user", cascade="all, delete")

    course_open_events = relationship(
        "CourseOpenEvent",
        back_populates="user",
        cascade="all, delete"
    )

class TutorialStatus(Base):
    __tablename__ = "tutorial_statuses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    user = relationship("User", backref=backref("tutorial_status", uselist=False))

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    question_text = Column(String, nullable=False)
    option1 = Column(String, nullable=False)
    option2 = Column(String, nullable=False)
    option3 = Column(String, nullable=False)
    option4 = Column(String, nullable=False)
    correct_option = Column(Integer, nullable=False)
    course = relationship("Course", back_populates="quiz_questions")

class QuizResponse(Base):
    __tablename__ = "quiz_responses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("quiz_questions.id"), nullable=False)
    is_correct = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", backref="quiz_responses")
    question = relationship("QuizQuestion", backref="responses")

class CourseOpenEvent(Base):
    __tablename__ = "course_open_events"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="course_open_events")
    course = relationship("Course", back_populates="open_events")