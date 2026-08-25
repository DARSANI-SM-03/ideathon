"""
StudIQ Local Desktop Agent Bridge v1.0
Lightweight, secure Windows local HTTP daemon running on 127.0.0.1:8765.
Enables the StudIQ Web Dashboard to securely check status, start, and stop the local Windows monitoring agent.
"""

import sys
import os

class NullWriter:
    def write(self, s):
        pass
    def flush(self):
        pass

if sys.stdout is None:
    sys.stdout = NullWriter()
if sys.stderr is None:
    sys.stderr = NullWriter()

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
agent_process_lock = threading.Lock()

def get_script_dir() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def log_debug(msg: str):
    try:
        appdata = os.getenv("LOCALAPPDATA", get_script_dir())
        log_dir = os.path.join(appdata, "StudIQ")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "agent_debug.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [Bridge] {msg}\n")
    except Exception:
        pass

def is_agent_running() -> bool:
    global agent_process
    with agent_process_lock:
        if agent_process is None:
            return False
        poll = agent_process.poll()
        if poll is None:
            return True
        else:
            agent_process = None
            return False

def stop_agent_process() -> bool:
    global agent_process
    with agent_process_lock:
        if agent_process is None:
            return True
        try:
            poll = agent_process.poll()
            if poll is None:
                agent_process.terminate()
                try:
                    agent_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    agent_process.kill()
            agent_process = None
            return True
        except Exception as e:
            print(f"[Bridge Error] Failed to stop agent process: {e}")
            agent_process = None
            return False

def start_agent_process(backend_url: str = "", token: str = "", student_id: int = 1, student_code: str = "STU-2026-001") -> Dict[str, Any]:
    global agent_process
    with agent_process_lock:
        if is_agent_running():
            return {"status": "already_running", "pid": agent_process.pid}

        if getattr(sys, 'frozen', False):
            cmd = [sys.executable, "--run-agent"]
        else:
            agent_py = os.path.join(get_script_dir(), "agent.py")
            if not os.path.exists(agent_py):
                return {"status": "error", "message": f"agent.py not found at {agent_py}"}
            cmd = [sys.executable, agent_py]

        if backend_url:
            cmd.extend(["--backend-url", backend_url])
        if token:
            cmd.extend(["--token", token])
        if student_id:
            cmd.extend(["--student-id", str(student_id)])
        if student_code:
            cmd.extend(["--student-code", str(student_code)])

        env = os.environ.copy()
        if backend_url:
            env["STUDIQ_BACKEND_URL"] = backend_url
        if token:
            env["STUDIQ_AGENT_TOKEN"] = token
        if student_id:
            env["STUDIQ_STUDENT_ID"] = str(student_id)
        if student_code:
            env["STUDIQ_STUDENT_CODE"] = str(student_code)

        log_debug(f"Spawning agent process: cmd={cmd}, cwd={get_script_dir()}")
        try:
            CREATE_NO_WINDOW = 0x08000000
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            flags = (CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP) if sys.platform == "win32" else 0

            agent_process = subprocess.Popen(
                cmd,
                cwd=get_script_dir(),
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=flags,
                close_fds=True
            )
            log_debug(f"[Bridge] Started agent process with PID {agent_process.pid}")
            return {"status": "started", "pid": agent_process.pid}
        except Exception as e:
            log_debug(f"[Bridge Error] Failed to launch agent process: {e}")
            return {"status": "error", "message": str(e)}

class BridgeRequestHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        origin = self.headers.get("Origin", "")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
        else:
            # For local dev ease fallback to origin if present
            self.send_header("Access-Control-Allow-Origin", origin if origin else "http://localhost:3000")
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
        else:
            self._send_json_response(404, {"error": "Endpoint not found"})

    def do_POST(self):
        path = self.path.split("?")[0]
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

            if is_agent_running():
                self._send_json_response(200, {"status": "already_running", "message": "Agent process is already active."})
            else:
                t = threading.Thread(
                    target=start_agent_process,
                    kwargs={
                        "backend_url": backend_url,
                        "token": token,
                        "student_id": student_id,
                        "student_code": student_code
                    },
                    daemon=True
                )
                t.start()
                self._send_json_response(200, {"status": "started", "message": "Monitoring agent startup initiated."})

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
    try:
        server = ReusableThreadingHTTPServer((HOST, PORT), BridgeRequestHandler)
        server.serve_forever()
    except OSError as e:
        log_debug(f"[Bridge Single Instance] Port {PORT} is already bound. Bridge daemon is already active: {e}")
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n[Bridge Shutting Down] Stopping bridge and active agent...")
        stop_agent_process()
    except Exception as e:
        log_debug(f"[Bridge Crash Error] {e}")

if __name__ == "__main__":
    main()
