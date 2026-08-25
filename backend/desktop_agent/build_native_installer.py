"""
StudIQ Windows Desktop Agent Setup Builder
============================================
Delegates setup installer compilation to build_setup_installer.py,
producing the standalone windowed executable StudIQAgentSetup.exe.
"""

import sys
import os

agent_dir = os.path.dirname(os.path.abspath(__file__))
if agent_dir not in sys.path:
    sys.path.insert(0, agent_dir)

from build_setup_installer import build_setup_installer

def build():
    build_setup_installer()

if __name__ == "__main__":
    build()
