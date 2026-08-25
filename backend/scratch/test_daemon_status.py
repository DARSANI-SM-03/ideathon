import subprocess
import time
import urllib.request
import json
import os
import sys

def main():
    exe_path = r"C:\Users\25032\AppData\Local\StudIQ\Agent\StudIQAgent.exe"
    print(f"Launching {exe_path} --daemon...")
    proc = subprocess.Popen([exe_path, "--daemon"])
    time.sleep(2)

    try:
        req = urllib.request.Request("http://127.0.0.1:8765/status", method="GET")
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            print("Initial GET /status:", resp.read().decode("utf-8"))

        start_payload = json.dumps({"student_id": 1, "student_code": "STU-2026-001"}).encode("utf-8")
        start_req = urllib.request.Request("http://127.0.0.1:8765/start", data=start_payload, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(start_req, timeout=2.0) as resp:
            print("POST /start response:", resp.read().decode("utf-8"))

        for i in range(5):
            time.sleep(2)
            try:
                status_req = urllib.request.Request("http://127.0.0.1:8765/status", method="GET")
                with urllib.request.urlopen(status_req, timeout=2.0) as resp:
                    print(f"t={(i+1)*2}s GET /status:", resp.read().decode("utf-8"))
            except Exception as e:
                print(f"t={(i+1)*2}s GET /status ERROR: {e}")

    finally:
        print("Terminating test daemon...")
        proc.terminate()

if __name__ == "__main__":
    main()
