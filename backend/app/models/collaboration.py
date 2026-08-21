from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    parent_id = Column(Integer, ForeignKey("parents.id"), nullable=True)
    meeting_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    scheduled_at = Column(DateTime, nullable=True)  # Alias for compatibility
    purpose = Column(String, nullable=False)
    type = Column(String, default="student")  # student, parent, joint
    location = Column(String, default="Office / Online")
    is_online = Column(Boolean, default=True)
    meeting_link = Column(String, nullable=True)
    status = Column(String, default="scheduled")  # scheduled, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)

class ParentConsent(Base):
    __tablename__ = "parent_consent"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("parents.id"), nullable=True)
    consent_given = Column(Boolean, default=True)
    consent_date = Column(DateTime, default=datetime.utcnow)

class CounselingSession(Base):
    __tablename__ = "counseling_sessions"

    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    priority = Column(String, default="medium")  # urgent, high, medium, low
    reason = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    status = Column(String, default="scheduled")  # pending, scheduled, completed
    created_at = Column(DateTime, default=datetime.utcnow)
