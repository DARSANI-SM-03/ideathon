"""
StudIQ Desktop Agent Setup Installer Builder
=============================================
1. Packages dist/StudIQAgent into a lightweight zip archive (StudIQAgent.zip).
2. Compiles setup_entry.py + drive_selector.py + StudIQAgent.zip into StudIQAgentSetup.exe using PyInstaller.
"""

import sys
import os
import subprocess
import shutil
import zipfile

def create_payload_zip(source_dir: str, output_zip_path: str):
    print(f"[Build Setup] Zipping payload directory '{source_dir}' -> '{output_zip_path}'...")
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, source_dir)
                zipf.write(abs_path, rel_path)
    zip_size = os.path.getsize(output_zip_path)
    print(f"[Build Setup] Payload ZIP created successfully ({zip_size} bytes / {zip_size / (1024*1024):.2f} MB).")

def build_setup_installer():
    agent_dir = os.path.dirname(os.path.abspath(__file__))
    setup_entry = os.path.join(agent_dir, "installer", "setup_entry.py")
    drive_selector = os.path.join(agent_dir, "installer", "drive_selector.py")
    agent_dist_dir = os.path.join(agent_dir, "dist", "StudIQAgent")
    installer_dir = os.path.join(agent_dir, "installer")
    payload_zip = os.path.join(installer_dir, "StudIQAgent.zip")

    # 1. Build StudIQAgent executable first to include all latest code edits
    print("[Build Setup] Building fresh StudIQAgent executable...")
    import build_agent_exe
    build_agent_exe.build()

    # 2. Package dist/StudIQAgent into StudIQAgent.zip
    create_payload_zip(agent_dist_dir, payload_zip)

    print("==========================================================")
    print("   BUILDING STUDIQ AGENT SETUP STANDALONE INSTALLER EXE   ")
    print("==========================================================")
    print(f"Setup Entry    : {setup_entry}")
    print(f"Drive Selector : {drive_selector}")
    print(f"Payload Archive: {payload_zip}")

    sep = ";" if sys.platform == "win32" else ":"
    add_zip_arg = f"{payload_zip}{sep}."
    add_selector_arg = f"{drive_selector}{sep}."

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name=StudIQAgentSetup",
        f"--add-data={add_zip_arg}",
        f"--add-data={add_selector_arg}",
        "--exclude-module=unittest",
        "--exclude-module=pydoc",
        f"--distpath={installer_dir}",
        f"--workpath={os.path.join(agent_dir, 'build_installer_work')}",
        setup_entry
    ]

    try:
        res = subprocess.run(cmd, cwd=agent_dir, check=True)
        exe_output = os.path.join(installer_dir, "StudIQAgentSetup.exe")
        exe_size = os.path.getsize(exe_output)
        print("\n==========================================================")
        print(" SUCCESS: StudIQAgentSetup.exe built successfully!")
        print(f" Location: {exe_output}")
        print(f" Size    : {exe_size} bytes ({exe_size / (1024*1024):.2f} MB)")
        print("==========================================================")
    except subprocess.CalledProcessError as e:
        print(f"\n[Build Error] PyInstaller installer compilation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_setup_installer()
