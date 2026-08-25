"""
StudIQ Desktop Agent Setup Installer Builder
=============================================
Compiles setup_entry.py and bundles dist/StudIQAgent into a single standalone installer
executable: StudIQAgentSetup.exe using PyInstaller.
"""

import sys
import os
import subprocess
import shutil

def build_setup_installer():
    agent_dir = os.path.dirname(os.path.abspath(__file__))
    setup_entry = os.path.join(agent_dir, "installer", "setup_entry.py")
    agent_dist_dir = os.path.join(agent_dir, "dist", "StudIQAgent")
    installer_output_dir = os.path.join(agent_dir, "installer")

    # 1. Check if dist/StudIQAgent exists, build if missing
    if not os.path.exists(os.path.join(agent_dist_dir, "StudIQAgent.exe")):
        print("[Build Setup] Building StudIQAgent executable first...")
        import build_agent_exe
        build_agent_exe.build()

    print("==========================================================")
    print("   BUILDING STUDIQ AGENT SETUP STANDALONE INSTALLER EXE   ")
    print("==========================================================")
    print(f"Setup Entry : {setup_entry}")
    print(f"Payload Dir : {agent_dist_dir}")

    # Separator for PyInstaller --add-data (Windows uses ;)
    sep = ";" if sys.platform == "win32" else ":"
    add_data_arg = f"{agent_dist_dir}{sep}payload"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name=StudIQAgentSetup",
        f"--add-data={add_data_arg}",
        "--exclude-module=unittest",
        "--exclude-module=pydoc",
        f"--distpath={installer_output_dir}",
        f"--workpath={os.path.join(agent_dir, 'build_installer_work')}",
        setup_entry
    ]

    try:
        res = subprocess.run(cmd, cwd=agent_dir, check=True)
        exe_output = os.path.join(installer_output_dir, "StudIQAgentSetup.exe")
        print("\n==========================================================")
        print(" SUCCESS: StudIQAgentSetup.exe built successfully!")
        print(f" Location: {exe_output}")
        print(f" Size    : {os.path.getsize(exe_output)} bytes")
        print("==========================================================")
    except subprocess.CalledProcessError as e:
        print(f"\n[Build Error] PyInstaller installer compilation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_setup_installer()
