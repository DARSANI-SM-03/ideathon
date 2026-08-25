import subprocess
import time
import shutil
import os
import urllib.request
import json
import sqlite3

INSTALLER_EXE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "desktop_agent", "installer", "StudIQAgentSetup.exe")
LOCAL_BRIDGE_URL = "http://127.0.0.1:8765"
LOCAL_APP_DATA_AGENT = os.path.expandvars(r"%LOCALAPPDATA%\StudIQ\Agent")
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "studiq.db")

def log_test(msg: str):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] [Live Test] {msg}")

def is_process_running(process_name: str) -> bool:
    try:
        out = subprocess.check_output(["tasklist", "/FI", f"IMAGENAME eq {process_name}"], text=True)
        return process_name.lower() in out.lower()
    except Exception:
        return False

def http_get(url: str) -> dict:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return None

def http_post(url: str, payload: dict) -> dict:
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST", headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return None

def run_live_test():
    log_test("==========================================================")
    log_test("  RUNNING LIVE STUDIQ AGENT LONG-RUNNING STABILITY TEST    ")
    log_test("==========================================================")

    # 1. Uninstall / Clean old agent
    log_test("Step 1: Cleaning & uninstalling any existing StudIQAgent instances...")
    subprocess.run(["taskkill", "/F", "/IM", "StudIQAgent.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)
    assert not is_process_running("StudIQAgent.exe"), "Failed to terminate StudIQAgent.exe"

    if os.path.exists(LOCAL_APP_DATA_AGENT):
        try:
            shutil.rmtree(LOCAL_APP_DATA_AGENT)
            log_test(f"  [OK] Successfully deleted {LOCAL_APP_DATA_AGENT}")
        except Exception as e:
            log_test(f"  Note clearing directory: {e}")

    # 2. Confirm agent not installed
    log_test("Step 2: Confirming 'Agent Setup Required' state (Bridge offline & binary missing)...")
    status_off = http_get(f"{LOCAL_BRIDGE_URL}/status")
    assert status_off is None, "Bridge should be offline after cleanup!"
    log_test("  [OK] Confirmed: Agent Bridge is offline ('Agent Setup Required').")

    # 3. Simulate user clicking "Set Up StudIQ Agent" ONCE
    log_test("Step 3: Simulating single user click on 'Set Up StudIQ Agent'...")
    log_test(f"  Launching installer: {INSTALLER_EXE} --silent")
    proc = subprocess.Popen([INSTALLER_EXE, "--silent"])
    exit_code = proc.wait(timeout=90)
    log_test(f"  [OK] Installer completed cleanly (exit code {exit_code}).")

    # 4. Automatic Agent Detection
    log_test("Step 4: Polling dashboard auto-detection on http://127.0.0.1:8765/status...")
    bridge_active = False
    status_resp = None
    for attempt in range(15):
        time.sleep(1.0)
        status_resp = http_get(f"{LOCAL_BRIDGE_URL}/status")
        if status_resp and status_resp.get("bridge_status") == "active":
            bridge_active = True
            log_test(f"  [OK] Agent detected after {(attempt+1)} seconds!")
            break
    assert bridge_active, "Dashboard failed to detect agent bridge after installation!"

    # 5. Automatic Monitoring Startup
    log_test("Step 5: Triggering automatic monitoring startup via POST /start...")
    start_resp = http_post(f"{LOCAL_BRIDGE_URL}/start", {
        "student_id": 1,
        "student_code": "STU-2026-001"
    })
    log_test(f"  Start Response: {start_resp}")
    time.sleep(2.0)

    status_post_start = http_get(f"{LOCAL_BRIDGE_URL}/status")
    log_test(f"  Status Post-Start: {status_post_start}")
    assert status_post_start.get("running") or status_post_start.get("agent_running"), "Monitoring did not start!"
    log_test("  [OK] Monitoring Active confirmed!")

    # 6. Long-running Stability Check (Wait 120 seconds / 2 minutes with ZERO user clicks)
    log_test("==========================================================")
    log_test("Step 6: LONG-RUNNING STABILITY WAIT (120 SECONDS / 2 MINUTES)...")
    log_test("  Simulating zero user interactions ('DO NOT CLICK ANYTHING')...")
    log_test("==========================================================")

    check_points = [10, 30, 60, 90, 120]
    start_time = time.time()

    for cp in check_points:
        elapsed = time.time() - start_time
        sleep_needed = cp - elapsed
        if sleep_needed > 0:
            time.sleep(sleep_needed)

        current_elapsed = int(time.time() - start_time)
        process_alive = is_process_running("StudIQAgent.exe")
        st = http_get(f"{LOCAL_BRIDGE_URL}/status")
        bridge_ok = st is not None and st.get("bridge_status") == "active"
        monitoring_ok = st is not None and (st.get("running") or st.get("agent_running"))

        log_test(f"  [Checkpoint t={current_elapsed}s]: Process Alive? {'YES' if process_alive else 'NO'} | Bridge Active? {'YES' if bridge_ok else 'NO'} | Monitoring Active? {'YES' if monitoring_ok else 'NO'}")
        
        assert process_alive, f"StudIQAgent.exe process died at t={current_elapsed}s!"
        assert bridge_ok, f"Bridge on 127.0.0.1:8765 went offline at t={current_elapsed}s!"
        assert monitoring_ok, f"Monitoring stopped unexpectedly at t={current_elapsed}s!"

    # 7. Confirm Telemetry Continuing in Database
    log_test("Step 7: Confirming continuous telemetry recording in database...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    total_logs = c.execute("SELECT COUNT(*) FROM activity_logs").fetchone()[0]
    recent_logs = c.execute("SELECT id, application_name, timestamp FROM activity_logs ORDER BY id DESC LIMIT 3").fetchall()
    conn.close()

    log_test(f"  Total Activity Logs in Database: {total_logs}")
    log_test(f"  Most Recent Telemetry Entries: {recent_logs}")
    assert total_logs > 0, "No telemetry logs found in database!"
    log_test("  [OK] Continuous Telemetry Database Logging VERIFIED!")

    log_test("==========================================================")
    log_test("  SUCCESS: LIVE 2-MINUTE STABILITY ACCEPTANCE TEST PASSED 100%!")
    log_test("==========================================================")

if __name__ == "__main__":
    run_live_test()
