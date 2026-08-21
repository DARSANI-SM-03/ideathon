# StudIQ Backend API

StudIQ is an AI-powered Digital Academic Intelligence Platform backend built with FastAPI, SQLite, SQLAlchemy, and Scikit-Learn / Pandas.

## Features
- **JWT Role-Based Authentication**: Student, Parent, Mentor, Admin.
- **Modular AI Engines**:
  - `FocusEngine`: Calculates focus score from application activity logs.
  - `BehaviorEngine`: Application window title and URL classifier.
  - `BurnoutEngine`: Predicts student burnout risk and fatigue levels.
  - `RecommendationEngine`: Generates actionable study & wellbeing recommendations.
- **Monitoring Service**: Real-time app usage telemetry ingestion endpoint (`/api/v1/monitoring/telemetry`).
- **REST APIs**: Full CRUD and dashboard analytics for Students, Admin, Activities, Attendance, Quizzes, Assignments, Warnings, Notifications.

## Setup & Running Instructions

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Seed Database
Generates 200 Students, 20 Teachers, 20 Mentors, 200 Parents, 5000+ Activity Logs, and Academic Records:
```bash
python seed.py
```

### 3. Run FastAPI Backend Server
```bash
python app/main.py
```
Or using uvicorn directly:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive API documentation available at `http://localhost:8000/docs`.
