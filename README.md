# StudIQ — AI-Powered Digital Academic Intelligence Platform

StudIQ is an AI-powered Digital Academic Intelligence Platform designed to help students reduce digital distractions, optimize study productivity, and predict burnout before academic performance declines.

Unlike traditional screen-time applications, StudIQ combines academic records (attendance, quiz marks, assignments, CGPA) with digital behavior tracking (application usage, active window titles, 5-category behavior classification) to generate explainable Focus Scores, Burnout Risk predictions, and personalized recommendations.

---

## 📁 Project Structure

The project is organized into **ONLY TWO** main directories:

```
studiq-main/
│
├── frontend/                  # React + TypeScript + Vite + Tailwind UI SaaS Portal (Website)
│   ├── src/                   # React components, pages, charts, contexts, and API services
│   ├── public/                # Static web assets
│   ├── package.json           # Frontend dependencies
│   ├── package-lock.json
│   ├── vite.config.ts         # Vite dev server configuration (Port 3000)
│   ├── tsconfig.json          # TypeScript configuration
│   ├── tailwind.config.js     # Tailwind CSS design system configuration
│   └── postcss.config.js
│
├── backend/                   # FastAPI Server + SQLite DB + AI Engines + Desktop Agent
│   ├── app/                   # FastAPI application (routers, services, AI engines, models, auth)
│   ├── desktop_agent/         # Windows 11 Desktop Monitoring Daemon
│   │   ├── agent.py           # Main monitoring agent loop
│   │   ├── classifier.py      # Rule-based & keyword activity classifier
│   │   ├── collector.py       # Active window title & process telemetry collector
│   │   ├── config.py          # Agent configuration & backend API URLs
│   │   ├── sender.py          # HTTP telemetry dispatcher & popup controller
│   │   ├── requirements.txt   # Desktop agent dependencies (psutil, pywin32, pygetwindow)
│   │   └── README.md
│   │
│   ├── requirements.txt       # Backend dependencies (FastAPI, SQLAlchemy, uvicorn, scikit-learn)
│   ├── seed.py                # Database seeder script
│   ├── check_openapi.py       # OpenAPI verification script
│   ├── check_tables.py        # Database schema integrity checker
│   ├── studiq.db              # SQLite Database (populated with 200+ students, 3000+ activities)
│   └── README.md
│
└── README.md                  # Main project documentation
```

### Component Roles
- **Frontend**: Web SaaS portal interface for Students, Mentors, Parents, and Administrators.
- **Backend**: Core API server, SQLite database, Explainable AI engines, and the Desktop Monitoring Agent.

---

## ⚡ Quick Start & Running Commands

### 1. FRONTEND (Website)
```bash
cd frontend
npm run dev
```
- **Access URL**: `http://localhost:3000/`

### 2. BACKEND (API & Database)
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
- **Server URL**: `http://localhost:8000/`
- **Interactive Swagger Documentation**: `http://localhost:8000/docs`

### 3. DESKTOP AGENT (Windows Desktop Monitoring Daemon)
```bash
cd backend\desktop_agent
python agent.py
```
- Sends real-time telemetry to: `http://localhost:8000/api/v1/monitoring/update`

---

## 🔐 Preset Demo Credentials

| Role | Identifier / Email | Password | Access View |
| :--- | :--- | :--- | :--- |
| **Student** | `STU-2026-001` | `student123` | Student Focus & Burnout Dashboard |
| **Admin** | `admin` | `admin123` | Institutional Control & High Risk Roster |
| **Mentor** | `vance@studiq.edu` | `password123` | Mentor Weekly Intelligence Digest |
| **Parent** | `parent.mercer@gmail.com` | `parent123` | Parent Monitoring & Alert Center |

---

## 🧪 Testing

Run the full master production test suite:
```bash
cd backend
python test_production_master_suite.py
```
Verification covers:
1. Telemetry Classification Engine
2. AI Behavior Intelligence Engine
3. Intelligent Monitoring Rule Engine
4. Interlinked Role Workflow & Consent Approvals
5. Production Live Dashboards & Export APIs
6. AI Risk Prediction & Recommendation Engine
