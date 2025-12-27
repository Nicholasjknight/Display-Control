# PyInstaller spec file for Display Control+
# Generates a single-file Windows executable

block_cipher = None

from PyInstaller.utils.hooks import collect_data_files

a = Analysis([
    '../overlay.py',
],
    pathex=['..'],
    binaries=[],
    datas=collect_data_files('PIL') + [('../config.json', '.'), ('../assets', 'assets'), ('../Display Control+ Logo.ico', '.'), ('../overlay_bg.py', '.'), ('../monitor_activity.py', '.'), ('../monitor_control.py', '.'), ('../log_config.py', '.')],
    hiddenimports=['tkinter', 'PIL', 'monitor_control', 'overlay', 'tray'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DisplayControlPlus',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='../Display Control+ Logo.ico'
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DisplayControlPlus'
)
