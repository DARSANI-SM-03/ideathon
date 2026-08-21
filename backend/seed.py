import random
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from app.database.session import SessionLocal, engine
from app.database.base import Base
from app.models.user import Student, Teacher, Mentor, Parent, Admin, Institution
from app.models.activity import Activity
from app.models.academic import AttendanceRecord, QuizScore, Assignment, SemesterResult, Exam, TeacherFeedback
from app.models.monitoring import ActivityLog, FocusScore, BurnoutPrediction, MonitoringLog
from app.models.collaboration import Meeting, ParentConsent, CounselingSession
from app.models.notification import Warning, Report, Notification, Message
from app.auth.security import get_password_hash

FIRST_NAMES = [
    "Alex", "Sophia", "Liam", "Emma", "Noah", "Ava", "Ethan", "Isabella", "Mason", "Mia",
    "Lucas", "Harper", "Oliver", "Evelyn", "Elijah", "Abigail", "James", "Emily", "Benjamin", "Ella",
    "Aarav", "Ananya", "Rohan", "Priya", "Vikram", "Neha", "Arjun", "Diya", "Kabir", "Aditi",
    "Marcus", "Elena", "Daniel", "Chloe", "Samuel", "Grace", "David", "Zoe", "Joseph", "Nora"
]

LAST_NAMES = [
    "Mercer", "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez",
    "Sharma", "Verma", "Patel", "Rao", "Gupta", "Nair", "Singh", "Mukherjee", "Reddy", "Joshi",
    "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Clark", "Lewis", "Walker"
]

DEPARTMENTS = [
    "Computer Science", "Electronics & Comm", "Mechanical Eng", "Electrical Eng", "Civil Eng",
    "Information Tech", "Biomedical Eng", "Aerospace Eng", "Chemical Eng", "Data Science"
]

APPLICATIONS = [
    ("VS Code", "Coding", "main.py - StudIQ Project"),
    ("PyCharm", "Coding", "script.py - Data Processing"),
    ("Google Chrome", "Research", "arXiv: AI in Higher Education PDF"),
    ("Google Chrome", "Study", "Canvas LMS - CS101 Course Materials"),
    ("Google Chrome", "Social Media", "Reddit - r/programming"),
    ("YouTube", "Entertainment", "Lo-Fi Beats / Gaming Streams"),
    ("Spotify", "Utility", "Study Focus Playlist"),
    ("Discord", "Social Media", "Study Group Chat"),
    ("Steam", "Gaming", "Valorant / Counter-Strike"),
    ("Terminal", "Coding", "bash - npm run dev"),
    ("Notion", "Study", "Exam Preparation Notes & Schedule"),
    ("Zoom", "Study", "Interactive Lecture Session")
]

def seed_database():
    print("Resetting database tables...")
    with engine.connect() as conn:
        conn.exec_driver_sql("PRAGMA foreign_keys = OFF;")
        Base.metadata.drop_all(bind=conn)
        Base.metadata.create_all(bind=conn)
        conn.exec_driver_sql("PRAGMA foreign_keys = ON;")

    db: Session = SessionLocal()
    try:
        print("1/16 Seeding Institutions...")
        inst1 = Institution(
            name="StudIQ Institute of Engineering & Technology",
            type="college",
            address="Innovation Park, Silicon Valley, CA",
            created_at=datetime.utcnow() - timedelta(days=365)
        )
        inst2 = Institution(
            name="StudIQ Academy of Advanced Computing",
            type="school",
            address="Academic Ridge, Cambridge, MA",
            created_at=datetime.utcnow() - timedelta(days=180)
        )
        db.add_all([inst1, inst2])
        db.commit()

        print("2/16 Seeding Admins...")
        admin = Admin(
            username="admin",
            full_name="Dr. Arthur Pendelton",
            name="Dr. Arthur Pendelton",
            email="admin@studiq.edu",
            role="admin",
            password_hash=get_password_hash("admin123")
        )
        db.add(admin)

        print("3/16 Seeding Teachers...")
        teachers = []
        for i in range(1, 21):
            fname = random.choice(FIRST_NAMES)
            lname = random.choice(LAST_NAMES)
            t = Teacher(
                teacher_id=f"TCH-2026-{i:03d}",
                full_name=f"Prof. {fname} {lname}",
                name=f"Prof. {fname} {lname}",
                email=f"prof.teacher{i}@studiq.edu",
                department=random.choice(DEPARTMENTS),
                role="teacher",
                password_hash=get_password_hash("password123")
            )
            teachers.append(t)
            db.add(t)

        print("4/16 Seeding Mentors...")
        mentors = []
        for i in range(1, 21):
            fname = random.choice(FIRST_NAMES)
            lname = random.choice(LAST_NAMES)
            m = Mentor(
                employee_id=f"EMP-2026-{i:03d}",
                mentor_id=f"EMP-2026-{i:03d}",
                full_name=f"Dr. {fname} {lname}",
                name=f"Dr. {fname} {lname}",
                email=f"mentor{i}@studiq.edu",
                department=random.choice(DEPARTMENTS),
                student_capacity=15,
                role="mentor",
                password_hash=get_password_hash("password123")
            )
            mentors.append(m)
            db.add(m)

        db.commit()

        print("5/16 Seeding Students...")
        students = []
        # Student 1: Alex Mercer (STU-2026-001) for default login
        s1 = Student(
            student_id="STU-2026-001",
            full_name="Alex Mercer",
            name="Alex Mercer",
            email="alex.mercer@studiq.edu",
            department="Computer Science",
            semester=6,
            cgpa=3.85,
            attendance=94.0,
            focus_score=88.5,
            burnout_score=22.0,
            role="student",
            institution_id=inst1.id,
            mentor_id=mentors[0].id,
            password_hash=get_password_hash("student123")
        )
        students.append(s1)
        db.add(s1)

        for i in range(2, 201):
            fname = random.choice(FIRST_NAMES)
            lname = random.choice(LAST_NAMES)
            cgpa = round(random.uniform(2.5, 4.0), 2)
            attendance = round(random.uniform(65.0, 99.0), 1)
            f_score = round(random.uniform(40.0, 95.0), 1)
            b_score = round(random.uniform(15.0, 85.0), 1)

            st = Student(
                student_id=f"STU-2026-{i:03d}",
                full_name=f"{fname} {lname}",
                name=f"{fname} {lname}",
                email=f"{fname.lower()}.{lname.lower()}{i}@studiq.edu",
                department=random.choice(DEPARTMENTS),
                semester=random.randint(1, 8),
                cgpa=cgpa,
                attendance=attendance,
                focus_score=f_score,
                burnout_score=b_score,
                role="student",
                institution_id=inst1.id if i % 2 == 0 else inst2.id,
                mentor_id=mentors[i % len(mentors)].id,
                password_hash=get_password_hash("student123")
            )
            students.append(st)
            db.add(st)

        db.commit()

        print("6/16 Seeding Parents & Linking Foreign Keys...")
        parents = []
        for i, st in enumerate(students):
            parent = Parent(
                parent_id=f"PAR-2026-{i+1:03d}",
                student_id=st.id,
                full_name=f"Mr/Ms {st.full_name.split()[-1]}",
                name=f"Mr/Ms {st.full_name.split()[-1]}",
                email=f"parent.{st.student_id.lower()}@gmail.com",
                phone=f"+1-555-01{i+10:02d}",
                role="parent",
                password_hash=get_password_hash("parent123")
            )
            parents.append(parent)
            db.add(parent)

        db.commit()

        # Update parent_id on students
        for i, st in enumerate(students):
            st.parent_id = parents[i].id
        db.commit()

        print("7/16 Seeding Parent Consent...")
        for i, st in enumerate(students):
            pc = ParentConsent(
                student_id=st.id,
                parent_id=parents[i].id,
                consent_given=True,
                consent_date=datetime.utcnow() - timedelta(days=random.randint(1, 60))
            )
            db.add(pc)

        print("8/16 Seeding Activity Logs...")
        now = datetime.utcnow()
        for st in students:
            for _ in range(15):
                app, cat, window = random.choice(APPLICATIONS)
                duration = random.randint(300, 3600)
                offset_mins = random.randint(0, 10080)
                start_t = now - timedelta(minutes=offset_mins)

                act_log = ActivityLog(
                    student_id=st.id,
                    application_name=app,
                    window_title=f"{window} ({st.department})",
                    website_url="https://studiq.edu" if cat in ["Study", "Research"] else "https://web.app",
                    category=cat,
                    duration=duration,
                    timestamp=start_t
                )
                db.add(act_log)

                act_legacy = Activity(
                    student_id=st.id,
                    application_name=app,
                    window_title=f"{window} ({st.department})",
                    website="https://studiq.edu" if cat in ["Study", "Research"] else "https://web.app",
                    category=cat,
                    start_time=start_t,
                    end_time=start_t + timedelta(seconds=duration),
                    duration=duration
                )
                db.add(act_legacy)

        print("9/16 Seeding Focus Scores & 10/16 Burnout Predictions...")
        for st in students:
            for day_offset in range(7):
                f_score = FocusScore(
                    student_id=st.id,
                    score=round(max(30.0, min(100.0, st.focus_score + random.uniform(-10, 10))), 1),
                    calculated_at=now - timedelta(days=day_offset)
                )
                db.add(f_score)

                risk_lvl = "Low"
                if st.burnout_score > 75:
                    risk_lvl = "Critical"
                elif st.burnout_score > 55:
                    risk_lvl = "High"
                elif st.burnout_score > 35:
                    risk_lvl = "Medium"

                bp = BurnoutPrediction(
                    student_id=st.id,
                    risk_level=risk_lvl,
                    confidence=round(random.uniform(88.0, 99.0), 1),
                    recommendation="Schedule 10-minute break interval after continuous 45-minute focus session.",
                    created_at=now - timedelta(days=day_offset)
                )
                db.add(bp)

        print("11/16 Seeding Attendance Records...")
        subjects = ["Algorithms", "Machine Learning", "Database Systems", "Operating Systems", "Computer Networks"]
        for st in students:
            for sub in subjects:
                for d in range(1, 5):
                    att = AttendanceRecord(
                        student_id=st.id,
                        date=date.today() - timedelta(days=d * 7),
                        subject=sub,
                        status="Present" if random.random() > 0.1 else "Absent"
                    )
                    db.add(att)

        print("12/16 Seeding Assignments & 13/16 Quizzes...")
        for st in students:
            for sub in subjects[:3]:
                asgn = Assignment(
                    student_id=st.id,
                    subject=sub,
                    title=f"Lab Assignment #{random.randint(1, 5)}",
                    due_date=now + timedelta(days=random.randint(1, 10)),
                    submission_date=now - timedelta(days=random.randint(1, 5)),
                    score=round(random.uniform(70.0, 98.0), 1),
                    status="Completed" if random.random() > 0.2 else "Pending",
                    grade="A" if random.random() > 0.4 else "B"
                )
                db.add(asgn)

                q = QuizScore(
                    student_id=st.id,
                    subject=sub,
                    quiz_name=f"Quiz #{random.randint(1, 3)}",
                    score=round(random.uniform(60.0, 99.0), 1),
                    max_score=100.0,
                    date=date.today() - timedelta(days=random.randint(5, 30))
                )
                db.add(q)

        print("14/16 Seeding Exams & Teacher Feedback...")
        for st in students:
            ex = Exam(
                student_id=st.id,
                semester=st.semester,
                percentage=round(random.uniform(65.0, 98.0), 1)
            )
            db.add(ex)

            res = SemesterResult(
                student_id=st.id,
                semester=max(1, st.semester - 1),
                sgpa=round(random.uniform(2.8, 3.95), 2),
                total_credits=24,
                backlog_count=0 if random.random() > 0.1 else 1
            )
            db.add(res)

            tf = TeacherFeedback(
                student_id=st.id,
                teacher_name=teachers[random.randint(0, len(teachers) - 1)].full_name,
                feedback="Demonstrates outstanding engagement during practical lab sessions. Recommended for advanced project track.",
                created_at=now - timedelta(days=random.randint(1, 15))
            )
            db.add(tf)

        print("15/16 Seeding Meetings & 16/16 Notifications...")
        for st in students[:50]:
            mtg = Meeting(
                mentor_id=st.mentor_id or mentors[0].id,
                student_id=st.id,
                parent_id=st.parent_id,
                meeting_date=now + timedelta(days=random.randint(1, 7)),
                scheduled_at=now + timedelta(days=random.randint(1, 7)),
                purpose="Academic Performance & Digital Wellbeing Review",
                type="joint",
                location="Office / Virtual Room",
                status="scheduled"
            )
            db.add(mtg)

        for st in students:
            notif = Notification(
                student_id=st.id,
                parent_id=st.parent_id,
                mentor_id=st.mentor_id,
                title="Weekly Focus Digest",
                message=f"Your Focus Score this week reached {st.focus_score}/100. Keep up the high study consistency!",
                body=f"Your Focus Score this week reached {st.focus_score}/100. Keep up the high study consistency!",
                status="unread",
                read=False,
                created_at=now - timedelta(days=random.randint(0, 3))
            )
            db.add(notif)

            if st.burnout_score > 60.0:
                w = Warning(
                    student_id=st.id,
                    title="High Burnout Risk Alert",
                    message="Excessive late night digital activity detected combined with declining quiz performance.",
                    severity="High" if st.burnout_score < 80.0 else "Critical",
                    trigger_source="StudIQ Burnout Engine",
                    resolved=False
                )
                db.add(w)

        db.commit()
        print("Database Seed Completed Successfully across ALL 16 Tables!")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
