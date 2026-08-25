"""
StudIQ Local Desktop Agent Bridge v1.0
Lightweight, secure Windows local HTTP daemon running on 127.0.0.1:8765.
Enables the StudIQ Web Dashboard to securely check status, start, and stop the local Windows monitoring agent.
"""

import sys
import os

class DummyStream:
    encoding = "utf-8"
    errors = "ignore"
    buffer = None
    def write(self, s): pass
    def flush(self): pass
    def writable(self): return True
    def isatty(self): return False

if sys.stdout is None or not hasattr(sys.stdout, "write"):
    sys.stdout = DummyStream()
if sys.stderr is None or not hasattr(sys.stderr, "write"):
    sys.stderr = DummyStream()

import json
import subprocess
import signal
import time
import threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing import Optional, Dict, Any

class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True

HOST = "127.0.0.1"
PORT = 8765

ALLOWED_ORIGINS = {
    "https://studiq-frontend.onrender.com",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173"
}

# Global Process Handle for spawned agent.py
agent_process: Optional[subprocess.Popen] = None
agent_process_lock = threading.RLock()

def get_script_dir() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def log_debug(msg: str):
    try:
        appdata = os.getenv("LOCALAPPDATA", get_script_dir())
        log_dir = os.path.join(appdata, "StudIQ")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "agent_execution.log")
        with open(log_file, "a", encoding="utf-8", errors="ignore") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [Bridge] {msg}\n")
            f.flush()
    except Exception:
        pass

def is_agent_lock_held() -> bool:
    """Checks whether %LOCALAPPDATA%\\StudIQ\\agent.lock is currently locked by a running agent process."""
    global agent_thread_running
    if agent_thread_running:
        return True
    try:
        appdata = os.getenv("LOCALAPPDATA", get_script_dir())
        lock_file = os.path.join(appdata, "StudIQ", "agent.lock")
        if not os.path.exists(lock_file):
            return False
        try:
            with open(lock_file, "r+") as f:
                if sys.platform == "win32":
                    import msvcrt
                    try:
                        msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                        return False
                    except (IOError, OSError, PermissionError):
                        return True
        except (PermissionError, IOError, OSError):
            return True
    except Exception:
        pass
    return False

agent_thread = None
agent_thread_running = False

def run_agent_worker(token="", backend_url="", student_id=0, student_code=""):
    global agent_thread_running
    agent_thread_running = True
    log_debug(f"run_agent_worker thread started: student_id={student_id}, student_code={student_code}")
    try:
        if token:
            os.environ["STUDIQ_AGENT_TOKEN"] = token
        if backend_url:
            os.environ["STUDIQ_BACKEND_URL"] = backend_url
        if student_id:
            os.environ["STUDIQ_STUDENT_ID"] = str(student_id)
        if student_code:
            os.environ["STUDIQ_STUDENT_CODE"] = str(student_code)

        import agent
        log_debug("Calling agent.main() from worker thread...")
        agent.main()
        log_debug("agent.main() finished execution.")
    except Exception as e:
        log_debug(f"[Agent Worker Exception] {e}")
    finally:
        agent_thread_running = False
        log_debug("run_agent_worker thread exiting (agent_thread_running=False).")

def is_agent_running() -> bool:
    global agent_process, agent_thread, agent_thread_running
    if agent_thread_running or (agent_thread and agent_thread.is_alive()):
        return True
    with agent_process_lock:
        if agent_process is not None and agent_process.poll() is None:
            return True
    return is_agent_lock_held()

def stop_agent_process() -> bool:
    global agent_process, agent_thread_running
    agent_thread_running = False
    with agent_process_lock:
        if agent_process is not None:
            try:
                poll = agent_process.poll()
                if poll is None:
                    agent_process.terminate()
                    try:
                        agent_process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        agent_process.kill()
                agent_process = None
            except Exception as e:
                log_debug(f"[Bridge Error] Failed to stop agent process handle: {e}")
                agent_process = None
        return True

def start_agent_process(backend_url: str = "", token: str = "", student_id: int = 1, student_code: str = "STU-2026-001") -> Dict[str, Any]:
    global agent_process, agent_thread, agent_thread_running
    with agent_process_lock:
        if is_agent_running():
            pid = agent_process.pid if agent_process else os.getpid()
            log_debug("start_agent_process called but agent is already running.")
            return {"status": "already_running", "pid": pid}

        agent_thread = threading.Thread(
            target=run_agent_worker,
            kwargs={
                "token": token,
                "backend_url": backend_url,
                "student_id": student_id,
                "student_code": student_code
            },
            daemon=True
        )
        agent_thread.start()
        log_debug("Agent monitoring worker thread launched successfully.")
        return {"status": "started", "message": "Monitoring agent startup initiated.", "pid": os.getpid()}

class BridgeRequestHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        origin = self.headers.get("Origin", "")
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
        else:
            self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def _send_json_response(self, code: int, data: Dict[str, Any]):
        self.send_response(code)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]
        log_debug(f"HTTP GET {path}")
        if path in ("/status", "/health", "/"):
            running = is_agent_running()
            pid = agent_process.pid if (running and agent_process) else None
            self._send_json_response(200, {
                "bridge_status": "active",
                "bridge_version": "1.0.0",
                "running": running,
                "agent_running": running,
                "agent_pid": pid,
                "platform": sys.platform
            })
            log_debug(f"HTTP GET {path} response sent (running={running})")
        else:
            self._send_json_response(404, {"error": "Endpoint not found"})

    def do_POST(self):
        path = self.path.split("?")[0]
        log_debug(f"HTTP POST {path}")
        content_length = int(self.headers.get("Content-Length", 0))
        body_data = {}
        if content_length > 0:
            try:
                body_bytes = self.rfile.read(content_length)
                body_data = json.loads(body_bytes.decode("utf-8"))
            except Exception:
                body_data = {}

        if path == "/start":
            backend_url = body_data.get("backend_url", body_data.get("backendUrl", ""))
            token = body_data.get("token", "")
            student_id = body_data.get("student_id", body_data.get("studentId", 1))
            student_code = body_data.get("student_code", body_data.get("studentCode", "STU-2026-001"))

            log_debug(f"Handling POST /start: token={token[:10]}..., backend_url={backend_url}, student_id={student_id}, student_code={student_code}")
            res = start_agent_process(
                backend_url=backend_url,
                token=token,
                student_id=student_id,
                student_code=student_code
            )
            log_debug(f"POST /start result: {res}")
            self._send_json_response(200, res)

        elif path == "/stop":
            success = stop_agent_process()
            self._send_json_response(200, {
                "status": "stopped" if success else "error",
                "message": "Desktop agent process terminated."
            })
        else:
            self._send_json_response(404, {"error": "Endpoint not found"})

    def log_message(self, format, *args):
        # Suppress verbose default HTTP logging
        pass

def main():
    print("==========================================================")
    print("   STUDIQ LOCAL WINDOWS DESKTOP AGENT BRIDGE v1.0")
    print(f"   Listening on http://{HOST}:{PORT} (Localhost Only)")
    print("==========================================================")
    server = None
    for attempt in range(10):
        try:
            server = ReusableThreadingHTTPServer((HOST, PORT), BridgeRequestHandler)
            log_debug(f"Bridge HTTP server successfully initialized on http://{HOST}:{PORT}")
            break
        except OSError as e:
            if attempt < 9:
                log_debug(f"[Bridge Bind Retry {attempt+1}/10] Port {PORT} busy/release pending: {e}")
                time.sleep(0.5)
            else:
                log_debug(f"[Bridge Single Instance] Port {PORT} is bound by active bridge daemon: {e}")
                sys.exit(0)

    if server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n[Bridge Shutting Down] Stopping bridge and active agent...")
            stop_agent_process()
        except Exception as e:
            log_debug(f"[Bridge Crash Error] {e}")

if __name__ == "__main__":
    main()
