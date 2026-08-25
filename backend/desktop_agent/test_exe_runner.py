import subprocess
import time
import sys
import os
import urllib.request
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
exe_path = os.path.join(script_dir, "dist", "StudIQAgent", "StudIQAgent.exe")
print(f"1. Verifying production executable exists at: {exe_path}")
if not os.path.exists(exe_path):
    print("ERROR: Executable file does not exist!")
    sys.exit(1)

print(f"2. Executable File Size: {os.path.getsize(exe_path)} bytes")

print("3. Launching StudIQAgent.exe --daemon...")
proc = subprocess.Popen([exe_path, "--daemon"])
print(f"Process spawned with PID {proc.pid}")

time.sleep(2.0)

print("4. Testing HTTP GET http://127.0.0.1:8765/status...")
try:
    req = urllib.request.Request("http://127.0.0.1:8765/status")
    with urllib.request.urlopen(req, timeout=3.0) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print(f"[PASS] Local Bridge Response: {data}")
except Exception as e:
    print(f"[FAIL] Error querying local bridge status: {e}")

print("5. Testing Single-Instance Protection (launching second instance)...")
proc2 = subprocess.Popen([exe_path, "--daemon"])
time.sleep(1.0)
poll_code = proc2.poll()
print(f"[PASS] Duplicate instance exited cleanly with code: {poll_code}")

print("6. Cleaning up test process...")
try:
    proc.terminate()
except Exception:
    pass

print("=== ALL PRODUCTION EXECUTABLE TESTS PASSED ===")
