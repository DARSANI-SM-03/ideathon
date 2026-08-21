from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date, Text
from sqlalchemy.orm import relationship
from datetime import datetime, date
from app.database.base import Base

class AttendanceRecord(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    date = Column(Date, default=date.today)
    subject = Column(String, default="General")
    status = Column(String, nullable=False, default="Present")  # Present, Absent, Late

    student = relationship("Student", back_populates="attendance_records")

class QuizScore(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject = Column(String, nullable=False)
    quiz_name = Column(String, default="Quiz 1")
    score = Column(Float, nullable=False)
    max_score = Column(Float, default=100.0)
    date = Column(Date, default=date.today)

    student = relationship("Student", back_populates="quiz_scores")

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject = Column(String, nullable=False)
    title = Column(String, default="Assignment 1")
    due_date = Column(DateTime, default=datetime.utcnow)
    submission_date = Column(DateTime, default=datetime.utcnow)
    score = Column(Float, default=85.0)
    status = Column(String, default="Pending")  # Completed, Pending, Late
    grade = Column(String, nullable=True)

    student = relationship("Student", back_populates="assignments")

class SemesterResult(Base):
    __tablename__ = "semester_results"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    semester = Column(Integer, nullable=False)
    sgpa = Column(Float, nullable=False)
    total_credits = Column(Integer, default=24)
    backlog_count = Column(Integer, default=0)

    student = relationship("Student", back_populates="semester_results")

class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    semester = Column(Integer, nullable=False)
    percentage = Column(Float, nullable=False)

    student = relationship("Student", back_populates="exams")

class TeacherFeedback(Base):
    __tablename__ = "teacher_feedback"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    teacher_name = Column(String, nullable=False)
    feedback = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="teacher_feedbacks")
