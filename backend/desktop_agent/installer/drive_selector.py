"""
StudIQ Windows Dynamic Drive & Path Resolution Module
======================================================
Resolves the Windows per-user installation directory (%LOCALAPPDATA%\StudIQ\Agent)
and verifies disk space availability without hardcoded drive letters.
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
    Dynamically resolves the Windows per-user installation directory (%LOCALAPPDATA%\StudIQ\Agent).
    Selection Rules:
      1. Default to %LOCALAPPDATA%\StudIQ\Agent if LocalAppData drive has free space >= required_bytes.
      2. If LocalAppData drive has insufficient space, fall back to any available fixed drive.
      3. Return None if no drive has sufficient space.
    """
    local_app_data = os.getenv("LOCALAPPDATA")
    if not local_app_data:
        user_profile = os.getenv("USERPROFILE", os.path.expanduser("~"))
        local_app_data = os.path.join(user_profile, "AppData", "Local")

    fixed_drives = get_windows_fixed_drives()

    app_data_drive = "C:\\"
    if len(local_app_data) >= 3 and local_app_data[1:3] == ":\\":
        app_data_drive = local_app_data[:3].upper()

    diagnostics = {
        "local_app_data": local_app_data,
        "app_data_drive": app_data_drive,
        "fixed_drives_found": fixed_drives,
        "drive_space_map": {}
    }

    for d in fixed_drives:
        free_bytes = get_drive_free_space(d)
        diagnostics["drive_space_map"][d] = free_bytes

    # Rule 1: Check LocalAppData drive
    app_data_free = get_drive_free_space(app_data_drive)
    if app_data_free >= required_bytes:
        install_path = os.path.join(local_app_data, "StudIQ", "Agent")
        return install_path, app_data_drive, diagnostics

    # Rule 2: Fallback to any fixed drive with space
    for d in fixed_drives:
        if get_drive_free_space(d) >= required_bytes:
            install_path = os.path.join(d, "StudIQ", "Agent")
            return install_path, d, diagnostics

    # Rule 3: Insufficient space across all drives
    return None, None, diagnostics

def simulate_drive_selection(mock_drives_space: Dict[str, int], required_bytes: int = REQUIRED_FREE_SPACE_BYTES) -> Optional[str]:
    """
    Simulation helper to verify per-user drive selection logic across arbitrary drive configurations.
    """
    local_app_data = os.getenv("LOCALAPPDATA")
    if not local_app_data:
        user_profile = os.getenv("USERPROFILE", os.path.expanduser("~"))
        local_app_data = os.path.join(user_profile, "AppData", "Local")

    app_data_drive = "C:\\"
    if len(local_app_data) >= 3 and local_app_data[1:3] == ":\\":
        app_data_drive = local_app_data[:3].upper()

    if app_data_drive in mock_drives_space and mock_drives_space[app_data_drive] >= required_bytes:
        return os.path.join(local_app_data, "StudIQ", "Agent")

    for d, free_b in mock_drives_space.items():
        if free_b >= required_bytes:
            return os.path.join(d, "StudIQ", "Agent")

    return None
