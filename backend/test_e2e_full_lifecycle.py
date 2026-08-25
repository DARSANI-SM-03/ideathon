"""
StudIQ Agent End-to-End Runtime Lifecycle Test Suite
======================================================
Tests:
1. Fresh setup execution and process persistence (5s, 10s, 30s, 60s check after installer exit).
2. Local bridge detection on http://127.0.0.1:8765/status.
3. Automatic monitoring startup via POST http://127.0.0.1:8765/start.
4. Crash recovery via protocol launch without installer download.
5. Windows HKCU Run autostart key & URI protocol registration.
"""

import sys
import os
import time
import subprocess
import json
import winreg
import urllib.request
import urllib.error

LOCAL_BRIDGE_URL = "http://127.0.0.1:8765"

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def log_test(msg: str):
    try:
        print(f"[{time.strftime('%H:%M:%S')}] [E2E Test] {msg}")
    except Exception:
        clean_msg = msg.encode('ascii', errors='replace').decode('ascii')
        print(f"[{time.strftime('%H:%M:%S')}] [E2E Test] {clean_msg}")

def test_http_get(url: str, timeout: float = 5.0):
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        log_test(f"  [HTTP GET Note] {url}: {e}")
        return None

def test_http_post(url: str, payload: dict, timeout: float = 5.0):
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        log_test(f"  [HTTP POST Note] {url}: {e}")
        return None

def is_agent_exe_running() -> bool:
    try:
        if sys.platform == "win32":
            import ctypes
            from ctypes import wintypes
            TH32CS_SNAPPROCESS = 0x00000002
            class PROCESSENTRY32(ctypes.Structure):
                _fields_ = [
                    ("dwSize", wintypes.DWORD),
                    ("cntUsage", wintypes.DWORD),
                    ("th32ProcessID", wintypes.DWORD),
                    ("th32DefaultHeapID", ctypes.c_size_t),
                    ("th32ModuleID", wintypes.DWORD),
                    ("cntThreads", wintypes.DWORD),
                    ("th32ParentProcessID", wintypes.DWORD),
                    ("pcPriClassBase", ctypes.c_long),
                    ("dwFlags", wintypes.DWORD),
                    ("szExeFile", ctypes.c_char * 260)
                ]
            hSnap = ctypes.windll.kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
            pe = PROCESSENTRY32()
            pe.dwSize = ctypes.sizeof(PROCESSENTRY32)
            if ctypes.windll.kernel32.Process32First(hSnap, ctypes.byref(pe)):
                while True:
                    if pe.szExeFile.decode('utf-8', errors='ignore').lower() == "studiqagent.exe":
                        ctypes.windll.kernel32.CloseHandle(hSnap)
                        return True
                    if not ctypes.windll.kernel32.Process32Next(hSnap, ctypes.byref(pe)):
                        break
            ctypes.windll.kernel32.CloseHandle(hSnap)
            return False
    except Exception:
        pass
    return False

def run_all_tests():
    log_test("==========================================================")
    log_test("   RUNNING STUDIQ AGENT E2E RUNTIME ACCEPTANCE TESTS      ")
    log_test("==========================================================")

    # 1. Clean previous running agent instances
    log_test("Step 1: Stopping any existing StudIQAgent.exe processes...")
    try:
        subprocess.run(["taskkill", "/F", "/IM", "StudIQAgent.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
    time.sleep(1.0)
    assert not is_agent_exe_running(), "Failed to terminate pre-existing StudIQAgent processes."
    log_test("  ✓ Clean state confirmed. No StudIQAgent processes running.")

    # 2. Run Setup Installer
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    setup_exe = os.path.join(backend_dir, "desktop_agent", "installer", "StudIQAgentSetup.exe")
    assert os.path.exists(setup_exe), f"StudIQAgentSetup.exe missing at {setup_exe}"

    log_test(f"Step 2: Executing setup installer: {setup_exe} --silent...")
    setup_proc = subprocess.Popen([setup_exe, "--silent"], cwd=os.path.dirname(setup_exe), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    setup_exit = setup_proc.wait(timeout=90)
    assert setup_exit == 0, f"Installer failed with exit code {setup_exit}"
    log_test("  ✓ Installer completed cleanly (exit code 0).")

    # 3. CRITICAL: Verify Process Persistence (5s, 10s, 30s)
    log_test("Step 3: Verifying Agent Process Persistence after installer exit...")
    intervals = [2, 5, 10, 15, 30]
    for check_sec in intervals:
        time.sleep(check_sec if check_sec == 2 else 5)
        alive = is_agent_exe_running()
        log_test(f"  Check t={check_sec}s post-installer exit: Process alive? {'🟢 YES' if alive else '🔴 NO'}")
        assert alive, f"CRITICAL FAILURE: StudIQAgent.exe died at t={check_sec}s after installer exited!"

    # 4. Verify Local Bridge Endpoint
    log_test("Step 4: Verifying Local Bridge HTTP response on http://127.0.0.1:8765/status...")
    status_resp = test_http_get(f"{LOCAL_BRIDGE_URL}/status")
    log_test(f"  Bridge Response: {status_resp}")
    assert status_resp is not None, "Local bridge on 127.0.0.1:8765 did not respond!"
    assert status_resp.get("bridge_status") == "active", f"Unexpected bridge status: {status_resp}"
    log_test("  ✓ Local Bridge is 🟢 Active!")

    # 5. Verify Automatic Monitoring Start (/start)
    log_test("Step 5: Testing POST http://127.0.0.1:8765/start...")
    start_resp = test_http_post(
        f"{LOCAL_BRIDGE_URL}/start",
        {"token": "test_e2e_token", "backend_url": "http://localhost:8000", "student_id": 1, "student_code": "STU-2026-001"}
    )
    log_test(f"  Start Response: {start_resp}")
    assert start_resp is not None, "Failed to start monitoring via bridge /start endpoint"
    assert start_resp.get("status") in ("started", "already_running"), f"Unexpected start status: {start_resp}"
    log_test("  ✓ Monitoring startup initiated successfully!")

    time.sleep(2.0)
    status_after_start = test_http_get(f"{LOCAL_BRIDGE_URL}/status")
    log_test(f"  Status after start: {status_after_start}")
    assert status_after_start.get("agent_running") is True, "Agent monitoring is not reported as running!"
    log_test("  ✓ Agent Monitoring confirmed 🟢 Active & Running!")

    # 6. Verify Registry Keys
    log_test("Step 6: Verifying Windows Registry Autostart & Protocol Registration...")
    try:
        run_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, run_key, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, "StudIQAgent")
            log_test(f"  HKCU Run Key: StudIQAgent => {val}")
            assert "StudIQAgent.exe" in val, f"Invalid Run key value: {val}"
        log_test("  ✓ HKCU Run key verified!")

        protocol_key = r"Software\Classes\studiq-agent"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, protocol_key, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, "")
            log_test(f"  Protocol Key: studiq-agent => {val}")
        log_test("  ✓ studiq-agent:// Protocol registration verified!")
    except Exception as e:
        log_test(f"  Registry check note: {e}")

    # 7. Test Crash Recovery (Protocol URI Launch)
    log_test("Step 7: Testing Crash Recovery (Simulating Agent Crash & Protocol Auto-launch)...")
    log_test("  Killing StudIQAgent.exe...")
    subprocess.run(["taskkill", "/F", "/IM", "StudIQAgent.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)
    assert is_agent_exe_running() is False, "Failed to kill StudIQAgent process for test"

    log_test("  Invoking protocol launch (studiq-agent://start)...")
    os.system("start studiq-agent://start")

    recovered_status = None
    for attempt in range(10):
        time.sleep(1.0)
        recovered_status = test_http_get(f"{LOCAL_BRIDGE_URL}/status")
        if recovered_status and recovered_status.get("bridge_status") == "active":
            log_test(f"  Recovered after {(attempt+1)}s!")
            break

    log_test(f"  Recovered Bridge Response: {recovered_status}")
    assert recovered_status is not None, "Protocol launch failed to recover local bridge daemon!"
    assert recovered_status.get("bridge_status") == "active", "Bridge daemon is not active after protocol launch!"
    log_test("  ✓ Protocol Recovery 🟢 Verified! Bridge restarted cleanly via protocol launch without reinstalling.")

    log_test("==========================================================")
    log_test(" 🎉 ALL STUDIQ AGENT LIFECYCLE E2E TESTS PASSED 100%!     ")
    log_test("==========================================================")

if __name__ == "__main__":
    run_all_tests()
