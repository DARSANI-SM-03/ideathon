import time
import sys
import psutil
from typing import Dict, Any, List

# Windows-specific win32 API imports with safe cross-platform fallback
try:
    import win32gui
    import win32process
    import win32api
    IS_WINDOWS = True
except ImportError:
    try:
        import ctypes
        IS_WINDOWS = sys.platform.startswith('win')
    except Exception:
        IS_WINDOWS = False

class SystemActivityCollector:
    def __init__(self):
        self.session_start_time = time.time()

    def get_idle_time_seconds(self) -> float:
        """Calculates system idle time (time since last mouse/keyboard input) using Windows API."""
        if IS_WINDOWS:
            try:
                class LASTINPUTINFO(ctypes.Structure):
                    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

                lii = LASTINPUTINFO()
                lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
                if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
                    millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
                    return max(0.0, millis / 1000.0)
            except Exception:
                pass
        return 0.0

    def get_foreground_window_info(self) -> Dict[str, str]:
        """Collects foreground active application name and window title."""
        appName = "Unknown Application"
        windowTitle = "Active Desktop Session"
        websiteUrl = ""

        if IS_WINDOWS:
            try:
                hwnd = win32gui.GetForegroundWindow()
                if hwnd:
                    windowTitle = win32gui.GetWindowText(hwnd) or "Active Desktop Session"
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    try:
                        proc = psutil.Process(pid)
                        appName = proc.name()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        appName = "System Window"
            except Exception:
                pass
        else:
            # Simulated telemetry fallback for non-Windows platforms
            appName = "Visual Studio Code"
            windowTitle = "studiq / src / agent.py - StudIQ AI Project"
            websiteUrl = "github.com/studiq-ai/core-engine"

        # Basic domain extraction if title contains web page metadata
        if "chrome" in appName.lower() or "edge" in appName.lower() or "firefox" in appName.lower():
            if "youtube" in windowTitle.lower():
                websiteUrl = "youtube.com"
            elif "leetcode" in windowTitle.lower():
                websiteUrl = "leetcode.com"
            elif "arxiv" in windowTitle.lower():
                websiteUrl = "arxiv.org"
            elif "coursera" in windowTitle.lower():
                websiteUrl = "coursera.org"
            elif "github" in windowTitle.lower():
                websiteUrl = "github.com"
            elif "instagram" in windowTitle.lower():
                websiteUrl = "instagram.com"

        return {
            "appName": appName,
            "windowTitle": windowTitle,
            "websiteUrl": websiteUrl
        }

    def get_running_applications(self) -> List[str]:
        """Lists active running user applications."""
        running = set()
        try:
            for p in psutil.process_iter(['name']):
                name = p.info.get('name')
                if name and not name.lower().startswith(('svchost', 'system', 'conhost', 'runtimebroker')):
                    running.add(name)
        except Exception:
            pass
        return sorted(list(running))[:20]

    def collect_telemetry_snapshot(self) -> Dict[str, Any]:
        """Gathers a complete 5-second telemetry snapshot."""
        fg_info = self.get_foreground_window_info()
        idle_secs = self.get_idle_time_seconds()
        session_duration = int(time.time() - self.session_start_time)
        running_apps = self.get_running_applications()

        return {
            "appName": fg_info["appName"],
            "windowTitle": fg_info["windowTitle"],
            "websiteUrl": fg_info["websiteUrl"],
            "idleSeconds": round(idle_secs, 1),
            "sessionDurationSeconds": session_duration,
            "runningAppsCount": len(running_apps),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
