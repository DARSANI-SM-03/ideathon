"""
Unit Test Suite for Dynamic Windows Per-User Path Resolution Algorithm
========================================================================
Tests drive_selector logic against all real-world machine scenarios:
  1. Default %LOCALAPPDATA%\StudIQ\Agent when user drive has space
  2. LocalAppData drive full, fallback drive available
  3. Insufficient space across all drives
"""

import sys
import os

backend_path = os.path.dirname(os.path.abspath(__file__))
agent_installer_path = os.path.join(backend_path, "desktop_agent", "installer")
if agent_installer_path not in sys.path:
    sys.path.insert(0, agent_installer_path)

from desktop_agent.installer.drive_selector import (
    select_optimal_installation_path,
    simulate_drive_selection,
    get_windows_fixed_drives,
    get_drive_free_space,
    REQUIRED_FREE_SPACE_BYTES
)

def test_drive_selection_scenarios():
    print("==========================================================")
    print("   TESTING DYNAMIC WINDOWS PATH SELECTION ALGORITHM       ")
    print("==========================================================")

    # 1. Real System Execution Check
    path, drive, diag = select_optimal_installation_path()
    print(f"[Real System Test] LocalAppData Path : {diag['local_app_data']}")
    print(f"[Real System Test] Fixed Drives Found: {diag['fixed_drives_found']}")
    print(f"[Real System Test] Drive Space Map   : {diag['drive_space_map']}")
    print(f"[Real System Test] Selected Path     : {path}")
    print(f"[Real System Test] Selected Drive    : {drive}\n")

    assert path is not None, "Real system path selection should return a valid install path"
    assert drive is not None, "Real system path selection should return a valid drive"
    assert "StudIQ\\Agent" in path, "Selected path must end with StudIQ\\Agent"

    # 2. Simulated Machine Scenarios
    print("--- SIMULATING OTHER WINDOWS LAPTOP CONFIGURATIONS ---")

    local_app_data = os.getenv("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
    app_data_drive = local_app_data[:3].upper() if len(local_app_data) >= 3 and local_app_data[1:3] == ":\\" else "C:\\"

    # Scenario A: LocalAppData drive has space
    res_a = simulate_drive_selection({app_data_drive: 500 * 1024 * 1024, "D:\\": 200 * 1024 * 1024})
    print(f"Scenario A (AppData drive {app_data_drive} 500MB) -> Selected: {res_a}")
    assert res_a == os.path.join(local_app_data, "StudIQ", "Agent")

    # Scenario B: LocalAppData drive low space (10MB), fallback drive available (500MB)
    fallback_drive = "D:\\" if app_data_drive != "D:\\" else "E:\\"
    res_b = simulate_drive_selection({app_data_drive: 10 * 1024 * 1024, fallback_drive: 500 * 1024 * 1024})
    print(f"Scenario B (AppData drive low space, fallback {fallback_drive}) -> Selected: {res_b}")
    assert res_b == os.path.join(fallback_drive, "StudIQ", "Agent")

    # Scenario C: Insufficient space across all drives
    res_c = simulate_drive_selection({"C:\\": 10 * 1024 * 1024, "D:\\": 20 * 1024 * 1024})
    print(f"Scenario C (All drives < 150MB) -> Selected: {res_c} (Expected: None)")
    assert res_c is None

    print("\n==========================================================")
    print(" SUCCESS: All Path Selection Machine Scenarios Verified!   ")
    print("==========================================================")

if __name__ == "__main__":
    test_drive_selection_scenarios()
