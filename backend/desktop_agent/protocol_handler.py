"""
StudIQ Windows Custom Protocol URI & Daemon Entrypoint (studiq-agent://)
========================================================================
Parses custom Windows URI protocol calls (e.g., studiq-agent://start, studiq-agent://stop)
and manages the background local bridge daemon on 127.0.0.1:8765.
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

import re
import time
import subprocess
import urllib.request
import urllib.parse
import urllib.error
import json
from typing import Dict, Any, Optional

# Top-level imports for PyInstaller executable bundling
import bridge
import agent
import collector
import config

LOCAL_BRIDGE_URL = "http://127.0.0.1:8765"
ALLOWED_ACTIONS = {"start", "stop", "status", "health", "daemon"}

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
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass

def parse_protocol_uri(raw_uri: str) -> Dict[str, Any]:
    """
    Parses and strictly sanitizes studiq-agent:// URI calls.
    Example URIs:
      - studiq-agent://start
      - studiq-agent://stop
      - studiq-agent://status
      - studiq-agent://start?token=...&backend_url=...
    """
    clean_str = raw_uri.replace("studiq-agent://", "").replace("studiq-agent:", "").strip("/")
    
    parts = clean_str.split("?", 1)
    action = parts[0].strip().lower()
    action = re.sub(r"[^a-z0-9_\-]", "", action)
    
    params = {}
    if len(parts) > 1:
        query_str = parts[1]
        for pair in query_str.split("&"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                params[k.strip()] = urllib.parse.unquote(v.strip())
                
    if action not in ALLOWED_ACTIONS:
        print(f"[Security Warning] Action '{action}' is not in allowed list {ALLOWED_ACTIONS}. Defaulting to status.")
        action = "status"
        
    return {"action": action, "params": params}

def is_bridge_running() -> bool:
    try:
        req = urllib.request.Request(f"{LOCAL_BRIDGE_URL}/status", method="GET")
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("bridge_status") == "active"
    except Exception:
        pass
    return False

def ensure_bridge_running():
    if is_bridge_running():
        log_debug("ensure_bridge_running: bridge is already running.")
        return True
    
    log_debug("[Protocol Handler] Local bridge on 127.0.0.1:8765 is not running. Launching background bridge daemon...")
    
    try:
        if getattr(sys, 'frozen', False):
            cmd = [sys.executable, "--daemon"]
        else:
            bridge_py = os.path.join(get_script_dir(), "bridge.py")
            cmd = [sys.executable, bridge_py]

        CREATE_NO_WINDOW = 0x08000000
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        DETACHED_PROCESS = 0x00000008
        CREATE_BREAKAWAY_FROM_JOB = 0x01000000
        flags = (CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS | CREATE_BREAKAWAY_FROM_JOB) if sys.platform == "win32" else 0

        proc = subprocess.Popen(
            cmd,
            cwd=get_script_dir(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=flags,
            close_fds=True
        )
        log_debug(f"Daemon process launched with PID {proc.pid}")
        for i in range(40):
            time.sleep(0.2)
            if is_bridge_running():
                log_debug(f"[Protocol Handler] Local bridge started successfully after {(i+1)*0.2:.1f}s.")
                return True
        log_debug(f"[Protocol Handler] Timed out waiting for bridge daemon. proc.poll()={proc.poll()}")
    except Exception as e:
        log_debug(f"[Protocol Handler Error] Failed to start local bridge daemon: {e}")
        
    return False

def show_status_popup(status_text: str):
    """Spawns a native Tkinter popup to display protocol handler status."""
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showinfo("StudIQ Desktop Agent", status_text)
        root.destroy()
    except Exception as e:
        log_debug(f"[Status Popup Error] {e}")

def dispatch_action(action: str, params: Dict[str, Any]):
    log_debug(f"dispatch_action called with action='{action}', params={params}")
    if action == "start":
        ensure_bridge_running()
        student_id_raw = params.get("student_id", params.get("studentId", 1))
        try:
            student_id = int(student_id_raw)
        except Exception:
            student_id = 1

        payload = {
            "token": params.get("token", ""),
            "backend_url": params.get("backend_url", params.get("backendUrl", "")),
            "student_id": student_id,
            "student_code": params.get("student_code", params.get("studentCode", "STU-2026-001"))
        }
        log_debug(f"Sending POST /start to local bridge: {payload}")
        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                f"{LOCAL_BRIDGE_URL}/start",
                data=req_data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                log_debug(f"[Protocol Handler] Start Agent Result: {result}")
        except Exception as e:
            log_debug(f"[Protocol Handler Error] Failed to send start command to local bridge: {e}")

    elif action == "stop":
        if is_bridge_running():
            try:
                req = urllib.request.Request(f"{LOCAL_BRIDGE_URL}/stop", method="POST", data=b"{}")
                with urllib.request.urlopen(req, timeout=3.0) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                    log_debug(f"[Protocol Handler] Stop Agent Result: {result}")
            except Exception as e:
                log_debug(f"[Protocol Handler Error] Failed to send stop command to local bridge: {e}")
        else:
            log_debug("[Protocol Handler] Local bridge is not running.")

    elif action in ("status", "health"):
        ensure_bridge_running()
        running = is_bridge_running()
        msg = f"StudIQ Desktop Agent Status\n--------------------------------\nLocal Bridge (127.0.0.1:8765): {'🟢 Active' if running else '🔴 Inactive'}"
        if running:
            try:
                req = urllib.request.Request(f"{LOCAL_BRIDGE_URL}/status", method="GET")
                with urllib.request.urlopen(req, timeout=2.0) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    agent_run = data.get("agent_running", False)
                    pid = data.get("agent_pid", "N/A")
                    msg += f"\nMonitoring Service: {'🟢 Active (PID: ' + str(pid) + ')' if agent_run else '🔴 Ready / Stopped'}"
            except Exception as e:
                log_debug(f"Failed to query bridge status: {e}")
        show_status_popup(msg)

def main():
    log_debug(f"protocol_handler main() started with sys.argv={sys.argv}")
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg.startswith("studiq-agent://") or arg.startswith("studiq-agent:"):
            parsed = parse_protocol_uri(arg)
            dispatch_action(parsed["action"], parsed["params"])
        elif arg in ("--start", "-start", "start"):
            dispatch_action("start", {})
        elif arg in ("--stop", "-stop", "stop"):
            dispatch_action("stop", {})
        elif arg in ("--status", "-status", "status"):
            dispatch_action("status", {})
        elif arg in ("--daemon", "daemon"):
            log_debug("Executing --daemon: importing bridge and running bridge.main()")
            import bridge
            bridge.main()
        elif arg in ("--run-agent", "run-agent"):
            log_debug("Executing --run-agent: importing agent and running agent.main()")
            import agent
            agent.main()
        else:
            parsed = parse_protocol_uri(arg)
            dispatch_action(parsed["action"], parsed["params"])
    else:
        log_debug("No arguments passed. Executing default behavior: bridge.main()")
        import bridge
        bridge.main()

if __name__ == "__main__":
    main()
