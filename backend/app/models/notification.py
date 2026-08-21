from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base

class Warning(Base):
    __tablename__ = "warnings"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String, default="Medium")  # Low, Medium, High, Critical
    trigger_source = Column(String, default="Burnout Engine")
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved = Column(Boolean, default=False)

    student = relationship("Student", back_populates="warnings")

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    report_type = Column(String, default="Weekly Intelligence")
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    focus_score_avg = Column(Float, default=0.0)
    burnout_risk_level = Column(String, default="Low")
    summary_text = Column(Text, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="reports")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    parent_id = Column(Integer, ForeignKey("parents.id"), nullable=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id"), nullable=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    body = Column(Text, nullable=True)  # Alias for compatibility
    status = Column(String, default="unread")
    read = Column(Boolean, default=False)  # Alias for compatibility
    created_at = Column(DateTime, default=datetime.utcnow)
    timestamp = Column(DateTime, default=datetime.utcnow)  # Alias for compatibility

    student = relationship("Student", back_populates="notifications")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(String, nullable=False)
    receiver_id = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    read = Column(Boolean, default=False)
