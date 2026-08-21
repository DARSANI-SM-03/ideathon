from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ActivityBase(BaseModel):
    application_name: str
    window_title: Optional[str] = None
    website: Optional[str] = None
    category: str = "Study"
    duration: int = 0  # seconds

class ActivityCreate(ActivityBase):
    student_id: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class ActivityOut(ActivityBase):
    activity_id: int
    student_id: int
    start_time: datetime
    end_time: datetime

    class Config:
        from_attributes = True

class TelemetryPayload(BaseModel):
    student_id: int
    application_name: str
    window_title: Optional[str] = None
    website: Optional[str] = None
    duration: int = 10
    category: Optional[str] = None
