"""
StudIQ Windows Desktop Agent Executable Builder
==============================================
Compiles agent.py, bridge.py, and protocol_handler.py into a single, standalone
Windows executable (StudIQAgent.exe) using PyInstaller.
"""

import sys
import os
import subprocess
import shutil

def build():
    agent_dir = os.path.dirname(os.path.abspath(__file__))
    entry_point = os.path.join(agent_dir, "protocol_handler.py")
    
    # Incremental build using cached PYZ analysis
        
    print("==========================================================")
    print("   BUILDING STUDIQ DESKTOP AGENT STANDALONE EXECUTABLE   ")
    print("==========================================================")
    print(f"Entrypoint : {entry_point}")
    print(f"Target Dir : {agent_dir}")
    
    # 1. Terminate any running agent instances to prevent DLL file lock errors during PyInstaller rebuild
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/IM", "StudIQAgent.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
    
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name=StudIQAgent",
        "--exclude-module=tkinter",
        "--exclude-module=_tkinter",
        "--exclude-module=unittest",
        "--exclude-module=pydoc",
        f"--distpath={os.path.join(agent_dir, 'dist')}",
        f"--workpath={os.path.join(agent_dir, 'build')}",
        entry_point
    ]
    
    try:
        res = subprocess.run(cmd, cwd=agent_dir, check=True)
        print("\n==========================================================")
        print(" SUCCESS: StudIQAgent.exe compiled successfully!")
        print(f" Location: {os.path.join(agent_dir, 'dist', 'StudIQAgent', 'StudIQAgent.exe')}")
        print("==========================================================")
    except subprocess.CalledProcessError as e:
        print(f"\n[Build Error] PyInstaller compilation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build()
