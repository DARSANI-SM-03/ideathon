from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base

class Activity(Base):
    __tablename__ = "activities"

    activity_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    application_name = Column(String, nullable=False)
    window_title = Column(String, nullable=True)
    website = Column(String, nullable=True)
    category = Column(String, nullable=False, default="Study")  # Study, Coding, Research, Entertainment, Social Media, Gaming, Utility
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, default=datetime.utcnow)
    duration = Column(Integer, default=0)  # in seconds

    student = relationship("Student", back_populates="activities")
