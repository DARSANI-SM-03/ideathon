"""
Real Application Capture Test
Monitors Windows foreground applications for 15 seconds to verify window title detection.
"""

import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collector import SystemActivityCollector

def test_real_capture():
    collector = SystemActivityCollector()
    print("==========================================================")
    print("   TESTING REAL WINDOWS FOREGROUND APPLICATION CAPTURE")
    print("   Switch between Chrome, VS Code, Notepad, File Explorer...")
    print("==========================================================")
    
    for i in range(5):
        snap = collector.collect_telemetry_snapshot()
        print(f"[{i+1}/5] Captured: App='{snap['appName']}' | Title='{snap['windowTitle']}' | Idle={snap['idleSeconds']}s")
        time.sleep(2)

if __name__ == "__main__":
    test_real_capture()
