"""
Unit Test Suite for Dynamic Windows Drive Selection Algorithm
===============================================================
Tests drive_selector logic against all real-world machine scenarios:
  1. E: drive available with space
  2. E: drive unavailable, D: drive available with space
  3. Only C: drive available with space
  4. Preferred drive out of space, fallback drive available
  5. Insufficient space across all drives
"""

import sys
import os

backend_path = os.path.dirname(os.path.abspath(__file__))
agent_installer_path = os.path.join(backend_path, "desktop_agent", "installer")
if agent_installer_path not in sys.path:
    sys.path.insert(0, agent_installer_path)

from drive_selector import (
    select_optimal_installation_path,
    simulate_drive_selection,
    get_windows_fixed_drives,
    get_drive_free_space,
    REQUIRED_FREE_SPACE_BYTES
)

def test_drive_selection_scenarios():
    print("==========================================================")
    print("   TESTING DYNAMIC WINDOWS DRIVE SELECTION ALGORITHM       ")
    print("==========================================================")

    # 1. Real System Execution Check
    path, drive, diag = select_optimal_installation_path()
    print(f"[Real System Test] Fixed Drives Found: {diag['fixed_drives_found']}")
    print(f"[Real System Test] Drive Space Map   : {diag['drive_space_map']}")
    print(f"[Real System Test] Selected Path     : {path}")
    print(f"[Real System Test] Selected Drive    : {drive}\n")

    assert path is not None, "Real system drive selection should return a valid install path"
    assert drive is not None, "Real system drive selection should return a valid drive"
    assert not path.startswith("E:") or os.path.exists("E:\\"), "Selected drive must exist"

    # 2. Simulated Machine Scenarios (Item 14 Requirement)
    print("--- SIMULATING OTHER WINDOWS LAPTOP CONFIGURATIONS ---")

    # Scenario A: E: available with space
    res_a = simulate_drive_selection({"E:\\": 500 * 1024 * 1024, "C:\\": 200 * 1024 * 1024})
    print(f"Scenario A (E: 500MB, C: 200MB) -> Selected: {res_a}")
    assert res_a == os.path.join("E:\\", "StudIQ", "Agent")

    # Scenario B: E: unavailable, D: available
    res_b = simulate_drive_selection({"D:\\": 300 * 1024 * 1024, "C:\\": 200 * 1024 * 1024})
    print(f"Scenario B (D: 300MB, C: 200MB) -> Selected: {res_b}")
    assert res_b == os.path.join("D:\\", "StudIQ", "Agent")

    # Scenario C: Only C: available
    res_c = simulate_drive_selection({"C:\\": 500 * 1024 * 1024})
    print(f"Scenario C (Only C: 500MB)      -> Selected: {res_c}")
    assert res_c == os.path.join("C:\\", "StudIQ", "Agent")

    # Scenario D: E: space insufficient (50MB), C: has space (200MB)
    res_d = simulate_drive_selection({"E:\\": 50 * 1024 * 1024, "C:\\": 200 * 1024 * 1024})
    print(f"Scenario D (E: 50MB, C: 200MB)  -> Selected: {res_d}")
    assert res_d == os.path.join("C:\\", "StudIQ", "Agent")

    # Scenario E: Insufficient space across all drives
    res_e = simulate_drive_selection({"E:\\": 10 * 1024 * 1024, "C:\\": 20 * 1024 * 1024})
    print(f"Scenario E (E: 10MB, C: 20MB)   -> Selected: {res_e} (Expected: None)")
    assert res_e is None

    print("\n==========================================================")
    print(" SUCCESS: All Drive Selection Machine Scenarios Verified!  ")
    print("==========================================================")

if __name__ == "__main__":
    test_drive_selection_scenarios()
