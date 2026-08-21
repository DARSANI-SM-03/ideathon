from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    user_identifier: str  # College ID / Student ID / Admin Username
    password: str
    role: str = "student"  # student, admin, parent, mentor
    remember_me: bool = False

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    user_identifier: str
    name: str

class StudentRegisterRequest(BaseModel):
    full_name: str
    student_id: str
    email: str
    college_name: Optional[str] = "Global Institute of Technology"
    department: str
    semester: int = 1
    year: Optional[int] = 1
    password: str
    parent_name: Optional[str] = None
    parent_email: str
    parent_phone: Optional[str] = None


class ParentRegisterRequest(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    password: str

class AdminRegisterRequest(BaseModel):
    college_name: str
    institution_type: Optional[str] = "college"
    full_name: str
    email: str
    password: str

class MentorRegisterRequest(BaseModel):
    full_name: str
    employee_id: str
    email: str
    department: str
    password: str

class UserProfile(BaseModel):
    id: int
    user_identifier: str
    name: str
    email: str
    role: str
    department: Optional[str] = None
    onboarding_completed: Optional[bool] = True

