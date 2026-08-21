# StudIQ — Windows Desktop Monitoring Agent v1.0

The **StudIQ Windows Desktop Monitoring Agent** is a lightweight, background daemon that runs on Windows 11 devices to collect active foreground application titles and telemetry metadata.

---

## 🏗️ Architecture Overview

```
+--------------------------+
|  Windows 11 OS Telemetry |
|  (Process & Window Title)|
+--------------------------+
             │
             ▼
+--------------------------+
|   collector.py           |  <-- Collects process name, window title, idle seconds
+--------------------------+
             │
             ▼
+--------------------------+
|   classifier.py          |  <-- Classifies into Educational/Productive/Entertainment/Gaming/Utilities
+--------------------------+
             │
             ▼
+--------------------------+
|   sender.py              |  <-- Dispatches JSON payloads to FastAPI Backend
+--------------------------+
             │
             ▼
+--------------------------+
|  FastAPI Backend Server  |  <-- http://localhost:8000/api/v1/monitoring/update
+--------------------------+
```

---

## 🚀 Installation & Running

1. **Navigate to the agent directory**:
   ```bash
   cd backend/desktop_agent
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Monitoring Agent**:
   ```bash
   python agent.py
   ```

---

## 🔒 Privacy Guarantee

The StudIQ Desktop Agent **NEVER** accesses:
- ❌ Photo Gallery & Images
- ❌ Banking & Financial Applications
- ❌ Passwords & Keylogging
- ❌ Private Files & Documents
- ❌ Personal Messages & Chats
- ❌ Clipboard Contents

Only process names, active window titles, and duration metadata are captured to calculate Focus Score and predict academic burnout.
