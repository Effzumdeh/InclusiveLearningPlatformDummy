"""
Definition der Datenbankmodelle für Kurse, Lernpfade, Nutzungsstatistiken und Benutzereinstellungen.
"""
from sqlalchemy import Column, Integer, String, Table, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base

# Assoziationstabelle für die m:n-Beziehung zwischen Lernpfaden und Kursen
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
    description = Column(String)

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

class UserSetting(Base):
    __tablename__ = "user_settings"
    id = Column(Integer, primary_key=True, index=True)
    daily_target = Column(Integer, default=60)
