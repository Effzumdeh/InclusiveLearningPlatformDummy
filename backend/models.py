from sqlalchemy import Column, Integer, String, Table, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship, backref
from datetime import datetime
from database import Base

# Association table for many-to-many relationship between learning paths and courses
learningpath_course_association = Table(
    "learningpath_course",
    Base.metadata,
    Column("learningpath_id", Integer, ForeignKey("learning_paths.id")),
    Column("course_id", Integer, ForeignKey("courses.id"))
)

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    short_description = Column(String)
    course_content = Column(String)  # renamed from detailed_description
    comments = relationship("Comment", back_populates="course", cascade="all, delete")

class LearningPath(Base):
    __tablename__ = "learning_paths"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    courses = relationship("Course", secondary=learningpath_course_association, backref="learning_paths")

class UserStatistic(Base):
    __tablename__ = "user_statistics"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True)
    minutes = Column(Integer)

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    replies = relationship("Comment", backref=backref("parent", remote_side=[id]))
    course = relationship("Course", back_populates="comments")
    user = relationship("User")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String)
    role = Column(String, default="User")  # Possible roles: "User", "Teacher", "Admin"
    daily_target = Column(Integer, default=60)  # Individual daily learning goal