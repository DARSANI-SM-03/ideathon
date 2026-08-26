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
    IS_WINDOWS = sys.platform.startswith('win')

if IS_WINDOWS:
    import ctypes
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

class SystemActivityCollector:
    def __init__(self):
        self.session_start_time = time.time()

    def get_idle_time_seconds(self) -> float:
        """Calculates system idle time (time since last mouse/keyboard input) using Windows API."""
        if IS_WINDOWS:
            try:
                lii = LASTINPUTINFO()
                lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
                if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
                    millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
                    return max(0.0, millis / 1000.0)
            except Exception:
                pass
        return 0.0

    def sanitize_and_abstract_window_title(self, app_name: str, raw_title: str) -> tuple:
        """
        Privacy-by-Design: Evaluates raw window title locally on the device to extract
        domain/category signals, but NEVER exposes or transmits PII or raw sensitive titles.
        Returns (privacy_safe_title, website_url).
        """
        appName_lower = (app_name or "").lower()
        title_lower = (raw_title or "").lower()
        website_url = ""

        # Extract domain locally from browser title
        if any(b in appName_lower for b in ["chrome", "edge", "firefox", "brave", "opera"]):
            domain_map = [
                ("youtube", "youtube.com"),
                ("youtu.be", "youtube.com"),
                ("github", "github.com"),
                ("leetcode", "leetcode.com"),
                ("hackerrank", "hackerrank.com"),
                ("coursera", "coursera.org"),
                ("udemy", "udemy.com"),
                ("edx", "edx.org"),
                ("khan academy", "khanacademy.org"),
                ("khanacademy", "khanacademy.org"),
                ("geeksforgeeks", "geeksforgeeks.org"),
                ("w3schools", "w3schools.com"),
                ("nptel", "nptel.ac.in"),
                ("stackoverflow", "stackoverflow.com"),
                ("stack overflow", "stackoverflow.com"),
                ("wikipedia", "wikipedia.org"),
                ("arxiv", "arxiv.org"),
                ("instagram", "instagram.com"),
                ("facebook", "facebook.com"),
                ("reddit", "reddit.com"),
                ("twitter", "twitter.com"),
                ("x.com", "x.com"),
                ("linkedin", "linkedin.com"),
                ("netflix", "netflix.com"),
                ("spotify", "spotify.com"),
                ("twitch", "twitch.tv"),
                ("amazon", "amazon.com"),
                ("flipkart", "flipkart.com"),
                ("google", "google.com"),
                ("bing", "bing.com"),
                ("duckduckgo", "duckduckgo.com"),
            ]

            for key, dom in domain_map:
                if key in title_lower:
                    if dom != "google.com":
                        website_url = dom
                    break

            if website_url:
                anonymized_title = f"Web Activity ({website_url})"
            else:
                anonymized_title = "Active Web Session"

        elif "code" in appName_lower or "devenv" in appName_lower or "idea" in appName_lower or "pycharm" in appName_lower or "eclipse" in appName_lower:
            anonymized_title = "Active IDE / Coding Work"
        elif "word" in appName_lower or "excel" in appName_lower or "powerpnt" in appName_lower or "onenote" in appName_lower or "notepad" in appName_lower:
            anonymized_title = "Document Editing"
        elif "teams" in appName_lower or "slack" in appName_lower or "zoom" in appName_lower or "discord" in appName_lower or "outlook" in appName_lower:
            anonymized_title = "Communication & Collaboration"
        elif "cmd" in appName_lower or "powershell" in appName_lower or "terminal" in appName_lower:
            if any(t in title_lower for t in ["python", "node", "git", "npm", "docker", "studiq"]):
                anonymized_title = "Development Terminal Work"
            else:
                anonymized_title = "System Command Prompt"
        elif "explorer" in appName_lower or "taskmgr" in appName_lower or "settings" in appName_lower:
            anonymized_title = f"System {app_name} Work"
        else:
            anonymized_title = f"Active {app_name} Session"

        return anonymized_title, website_url

    def get_foreground_window_info(self) -> Dict[str, str]:
        """Collects foreground active application name and privacy-sanitized activity label."""
        import os
        appName = "Unknown Application"
        rawWindowTitle = ""

        if IS_WINDOWS:
            try:
                hwnd = win32gui.GetForegroundWindow()
                if hwnd:
                    rawWindowTitle = win32gui.GetWindowText(hwnd) or ""
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    if pid > 0:
                        try:
                            import win32process, win32api
                            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
                            handle = win32api.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
                            if handle:
                                try:
                                    exe_path = win32process.GetQueryFullProcessImageName(handle, 0)
                                    appName = os.path.basename(exe_path)
                                except Exception:
                                    try:
                                        exe_path = win32process.GetModuleFileNameEx(handle, 0)
                                        appName = os.path.basename(exe_path)
                                    except Exception:
                                        pass
                                win32api.CloseHandle(handle)
                        except Exception:
                            pass

                        if appName == "Unknown Application":
                            try:
                                proc = psutil.Process(pid)
                                appName = proc.name()
                            except Exception:
                                pass

            except Exception:
                pass

            # Fallback 1: EnumWindows visible window search if GetForegroundWindow returned 0 or Unknown Application
            if appName == "Unknown Application":
                try:
                    import win32gui, win32process
                    def _enum_cb(h, acc):
                        try:
                            if win32gui.IsWindowVisible(h):
                                t = win32gui.GetWindowText(h)
                                if t and len(t) > 2 and not t.startswith(('Program Manager', 'Settings', 'Calculator', 'Default IME', 'MSCTFIME')):
                                    _, p = win32process.GetWindowThreadProcessId(h)
                                    try:
                                        pr = psutil.Process(p)
                                        pname = pr.name()
                                        if pname and not pname.lower().startswith(('svchost', 'system', 'conhost', 'cmd', 'powershell', 'python')):
                                            acc.append((pname, t))
                                    except Exception:
                                        pass
                        except Exception:
                            pass
                        return True
                    visible_windows = []
                    try:
                        win32gui.EnumWindows(_enum_cb, visible_windows)
                    except Exception:
                        pass
                    if visible_windows:
                        appName, rawWindowTitle = visible_windows[0]
                except Exception:
                    pass

            # Fallback 2: Scan active user processes via psutil
            if appName == "Unknown Application":
                target_apps = ["chrome.exe", "code.exe", "notepad.exe", "devenv.exe", "idea64.exe", "msedge.exe", "firefox.exe", "brave.exe", "excel.exe", "winword.exe"]
                try:
                    for proc in psutil.process_iter(['name']):
                        pname = (proc.info['name'] or '').lower()
                        if pname in target_apps:
                            appName = proc.info['name']
                            rawWindowTitle = f"Active {appName} Session"
                            break
                except Exception:
                    pass
        else:
            appName = "code.exe"
            rawWindowTitle = "studiq - Visual Studio Code"

        anonymizedTitle, websiteUrl = self.sanitize_and_abstract_window_title(appName, rawWindowTitle)

        return {
            "appName": appName,
            "windowTitle": anonymizedTitle,
            "websiteUrl": websiteUrl
        }

    def get_running_applications(self) -> List[str]:
        """Lists active running top-level user applications (<1ms using EnumWindows)."""
        running = set()
        if IS_WINDOWS:
            try:
                import win32gui, win32process, win32api, win32con, os
                def enum_windows_callback(hwnd, extra):
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if title and len(title) > 2:
                            _, pid = win32process.GetWindowThreadProcessId(hwnd)
                            try:
                                handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
                                if handle:
                                    exe_path = win32process.GetModuleFileNameEx(handle, 0)
                                    appName = os.path.basename(exe_path)
                                    if appName and not appName.lower().startswith(('svchost', 'system', 'conhost', 'explorer')):
                                        running.add(appName)
                                    win32api.CloseHandle(handle)
                            except Exception:
                                pass
                    return True
                win32gui.EnumWindows(enum_windows_callback, None)
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
