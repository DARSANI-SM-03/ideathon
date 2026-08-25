# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['E:/ideathon/studiq-main/studiq-main/backend/desktop_agent/installer/setup_entry.py'],
    pathex=[],
    binaries=[],
    datas=[('E:/ideathon/studiq-main/studiq-main/backend/desktop_agent/dist/StudIQAgent', 'payload')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['unittest', 'pydoc'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='StudIQAgentSetup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
