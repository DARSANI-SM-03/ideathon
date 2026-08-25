"""
StudIQ Windows Dynamic Drive Selection Module
==============================================
Discovers available Windows local fixed drives, checks disk space,
and dynamically calculates the optimal installation directory for StudIQ Agent.
Zero hardcoded drive letters (e.g. E:, C:, D:).
"""

import os
import sys
import shutil
import ctypes
from typing import List, Optional, Tuple, Dict, Any

REQUIRED_FREE_SPACE_BYTES = 150 * 1024 * 1024  # 150 MB required

def get_windows_fixed_drives() -> List[str]:
    """Returns a list of all local fixed drives (e.g. ['C:\\', 'D:\\', 'E:\\'])."""
    drives = []
    if sys.platform != 'win32':
        return drives

    try:
        kernel32 = ctypes.windll.kernel32
        bitmask = kernel32.GetLogicalDrives()
        for letter_code in range(26):
            if bitmask & (1 << letter_code):
                drive_letter = f"{chr(65 + letter_code)}:\\"
                # DRIVE_FIXED = 3
                if kernel32.GetDriveTypeW(drive_letter) == 3:
                    drives.append(drive_letter)
    except Exception:
        # Fallback to checking standard drive letters
        for letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
            path = f"{letter}:\\"
            if os.path.exists(path):
                drives.append(path)

    return drives

def get_drive_free_space(drive_path: str) -> int:
    """Returns available free disk space in bytes for a given drive path."""
    try:
        usage = shutil.disk_usage(drive_path)
        return usage.free
    except Exception:
        return 0

def select_optimal_installation_path(required_bytes: int = REQUIRED_FREE_SPACE_BYTES) -> Tuple[Optional[str], Optional[str], Dict[str, Any]]:
    """
    Dynamically selects the optimal Windows installation directory.
    Selection Rules:
      1. Prefer drive containing %LOCALAPPDATA% if free space >= required_bytes.
      2. Prefer fixed non-system drives (e.g. E:\\, D:\\) with free space >= required_bytes.
      3. Fall back to system drive (C:\\) if free space >= required_bytes.
      4. Return None if no drive has sufficient space.
    """
    fixed_drives = get_windows_fixed_drives()
    local_app_data = os.getenv("LOCALAPPDATA", "")
    system_drive = os.getenv("SystemDrive", "C:").upper().rstrip("\\") + "\\"

    app_data_drive = None
    if local_app_data and len(local_app_data) >= 3 and local_app_data[1:3] == ":\\":
        app_data_drive = local_app_data[:3].upper()

    diagnostics = {
        "fixed_drives_found": fixed_drives,
        "system_drive": system_drive,
        "app_data_drive": app_data_drive,
        "drive_space_map": {}
    }

    for d in fixed_drives:
        free_bytes = get_drive_free_space(d)
        diagnostics["drive_space_map"][d] = free_bytes

    # Rule 1: Check AppData drive
    if app_data_drive and app_data_drive in fixed_drives:
        if get_drive_free_space(app_data_drive) >= required_bytes:
            install_path = os.path.join(local_app_data, "StudIQ", "Agent")
            return install_path, app_data_drive, diagnostics

    # Rule 2: Prefer non-system fixed drives (e.g. E:\, D:\)
    non_system_drives = [d for d in fixed_drives if d.upper() != system_drive]
    for d in non_system_drives:
        if get_drive_free_space(d) >= required_bytes:
            install_path = os.path.join(d, "StudIQ", "Agent")
            return install_path, d, diagnostics

    # Rule 3: Fall back to system drive (C:\)
    if system_drive in fixed_drives and get_drive_free_space(system_drive) >= required_bytes:
        install_path = os.path.join(system_drive, "StudIQ", "Agent")
        return install_path, system_drive, diagnostics

    # Rule 4: Insufficient space across all drives
    return None, None, diagnostics

def simulate_drive_selection(mock_drives_space: Dict[str, int], required_bytes: int = REQUIRED_FREE_SPACE_BYTES) -> Optional[str]:
    """
    Simulation helper to verify drive selection logic across arbitrary drive configurations.
    Example mock input: {'E:\\': 500000000, 'C:\\': 50000000}
    """
    system_drive = "C:\\"

    # 1. Non-system fixed drives
    for d, free_b in mock_drives_space.items():
        if d.upper() != system_drive and free_b >= required_bytes:
            return os.path.join(d, "StudIQ", "Agent")

    # 2. System drive
    if system_drive in mock_drives_space and mock_drives_space[system_drive] >= required_bytes:
        return os.path.join(system_drive, "StudIQ", "Agent")

    return None
