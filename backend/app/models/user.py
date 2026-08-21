from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base


class Institution(Base):
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, default="college")  # school/college/coaching
    address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    students = relationship("Student", back_populates="institution")

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)

class ParentConsent(Base):
    __tablename__ = "parent_consents"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    parent_email = Column(String, nullable=False)
    parent_phone = Column(String, nullable=True)
    status = Column(String, default="Pending")  # Pending, Approved, Rejected
    requested_permissions = Column(String, default="App & Web Monitoring, Focus Analysis, Burnout Risk Alerts")
    monitoring_scope = Column(String, default="Desktop Application Window Titles, Academic Browsing URLs")
    rejection_reason = Column(String, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class MentorAssignment(Base):
    __tablename__ = "mentor_assignments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    mentor_id = Column(Integer, ForeignKey("mentors.id"), nullable=False)
    assigned_by_admin_id = Column(Integer, nullable=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    name = Column(String, nullable=False)  # Alias for backward compatibility
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    department = Column(String, nullable=False)
    semester = Column(Integer, default=1)
    cgpa = Column(Float, default=0.0)
    attendance = Column(Float, default=0.0)
    focus_score = Column(Float, default=80.0)
    burnout_score = Column(Float, default=20.0)
    role = Column(String, default="student")

    # Workflow & Approval Fields
    status = Column(String, default="Pending Approval")  # Pending Approval, Active, Blocked, Deactivated
    monitoring_authorized = Column(Boolean, default=False)
    onboarding_completed = Column(Boolean, default=False)
    parent_email = Column(String, nullable=True)
    parent_phone = Column(String, nullable=True)

    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id"), nullable=True)
    parent_id = Column(Integer, ForeignKey("parents.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    institution = relationship("Institution", back_populates="students")
    mentor = relationship("Mentor", back_populates="students")
    parents = relationship("Parent", back_populates="student", foreign_keys="Parent.student_id")

    activities = relationship("Activity", back_populates="student", cascade="all, delete-orphan")
    attendance_records = relationship("AttendanceRecord", back_populates="student", cascade="all, delete-orphan")
    quiz_scores = relationship("QuizScore", back_populates="student", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="student", cascade="all, delete-orphan")
    semester_results = relationship("SemesterResult", back_populates="student", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="student", cascade="all, delete-orphan")
    teacher_feedbacks = relationship("TeacherFeedback", back_populates="student", cascade="all, delete-orphan")
    warnings = relationship("Warning", back_populates="student", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="student", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="student", cascade="all, delete-orphan")


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    department = Column(String, nullable=False)
    role = Column(String, default="teacher")
    password_hash = Column(String, nullable=False)

class Mentor(Base):
    __tablename__ = "mentors"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, index=True, nullable=False)
    mentor_id = Column(String, nullable=False)  # Alias for compatibility
    full_name = Column(String, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    department = Column(String, nullable=False)
    student_capacity = Column(Integer, default=15)
    role = Column(String, default="mentor")
    password_hash = Column(String, nullable=False)

    students = relationship("Student", back_populates="mentor")

class Parent(Base):
    __tablename__ = "parents"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(String, unique=True, index=True, nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    full_name = Column(String, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=True)
    role = Column(String, default="parent")
    password_hash = Column(String, nullable=False)

    student = relationship("Student", back_populates="parents", foreign_keys=[student_id])

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, default="admin")
    password_hash = Column(String, nullable=False)

class ParentApprovalRequest(Base):
    __tablename__ = "parent_approval_requests"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    student_name = Column(String, nullable=False)
    student_code = Column(String, nullable=False)
    college_name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    parent_email = Column(String, nullable=False)
    parent_phone = Column(String, nullable=True)
    status = Column(String, default="Pending")  # Pending, Approved, Rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    device_id = Column(String, nullable=False, index=True)
    device_name = Column(String, nullable=False)
    os_name = Column(String, nullable=False)
    agent_version = Column(String, default="v2.4")
    is_trusted = Column(Boolean, default=True)
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

