import sys
import time
import threading
from datetime import datetime
from typing import Optional, Dict, Any

try:
    import psutil
except ImportError:
    psutil = None

try:
    import win32gui
    import win32process
except ImportError:
    win32gui = None
    win32process = None

from app.database.session import SessionLocal
from app.models.monitoring import MonitoringLog
from app.models.activity import Activity
from app.ai.behavior_engine import behavior_engine
from app.ai.focus_engine import focus_engine

class WindowsMonitorService:
    """
    Thread-safe Windows 11 background monitoring daemon.
    Captures foreground window title, process name, application name, start time,
    and continuous session duration every 3 seconds. Automatically runs AI classification.
    """

    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self.current_session: Dict[str, Any] = {
            "application_name": "VS Code",
            "window_title": "main.py - StudIQ AI Engine",
            "process_name": "Code.exe",
            "category": "Educational",
            "start_time": datetime.utcnow(),
            "duration": 0
        }

    def get_active_window_info(self) -> Dict[str, str]:
        """
        Retrieves active window title and process name using win32gui and psutil.
        """
        window_title = "StudIQ Active Session"
        process_name = "python.exe"
        app_name = "Python IDE"

        if sys.platform == "win32" and win32gui and psutil:
            try:
                hwnd = win32gui.GetForegroundWindow()
                if hwnd:
                    window_title = win32gui.GetWindowText(hwnd) or "System Workspace"
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    proc = psutil.Process(pid)
                    process_name = proc.name()
                    app_name = process_name.replace(".exe", "").capitalize()
            except Exception:
                pass

        return {
            "application_name": app_name,
            "window_title": window_title,
            "process_name": process_name
        }

    def _monitor_loop(self, student_id: int = 1):
        last_app = ""
        last_title = ""
        session_duration = 0

        while self._running:
            try:
                info = self.get_active_window_info()
                app_name = info["application_name"]
                title = info["window_title"]
                proc_name = info["process_name"]

                # 5-Category AI Classification
                category = behavior_engine.classify_activity(app_name, title)

                with self._lock:
                    if app_name == last_app and title == last_title:
                        session_duration += 3
                    else:
                        session_duration = 3
                        last_app = app_name
                        last_title = title

                    self.current_session = {
                        "application_name": app_name,
                        "window_title": title,
                        "process_name": proc_name,
                        "category": category,
                        "duration": session_duration,
                        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                    }

                # Store activity log in SQLite database every cycle
                db = SessionLocal()
                try:
                    m_log = MonitoringLog(
                        student_id=student_id,
                        process_name=proc_name,
                        application_name=app_name,
                        window_title=title,
                        category=category,
                        duration=3,
                        session_time=session_duration
                    )
                    db.add(m_log)

                    act = Activity(
                        student_id=student_id,
                        application_name=app_name,
                        window_title=title,
                        category=category,
                        duration=3
                    )
                    db.add(act)
                    db.commit()
                except Exception:
                    db.rollback()
                finally:
                    db.close()

            except Exception as e:
                print(f"[WindowsMonitorService Error]: {e}")

            time.sleep(3)

    def start(self, student_id: int = 1):
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._monitor_loop, args=(student_id,), daemon=True)
            self._thread.start()
            print("[WindowsMonitorService]: Started background telemetry daemon.")

    def stop(self):
        if self._running:
            self._running = False
            if self._thread:
                self._thread.join(timeout=2.0)
            print("[WindowsMonitorService]: Stopped background telemetry daemon.")

    def get_current_activity(self) -> Dict[str, Any]:
        with self._lock:
            return self.current_session.copy()

windows_monitor = WindowsMonitorService()
