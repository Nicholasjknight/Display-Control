# PyInstaller spec file for Display Control+ (Fixed Single-File Build)
# Addresses multiprocessing issues with embedded Python interpreter

import multiprocessing
multiprocessing.freeze_support()

block_cipher = None

from PyInstaller.utils.hooks import collect_data_files

a = Analysis([
    '../overlay.py',
],
    pathex=['..'],
    binaries=[],
    datas=collect_data_files('PIL') + [
        ('../config.json', '.'),
        ('../assets', 'assets'),
        ('../Display Control+ Logo.ico', '.')
    ],
    hiddenimports=[
        'tkinter', 'PIL', 'PIL.Image', 'PIL.ImageTk',
        'monitor_control', 'monitor_activity', 'overlay', 'overlay_bg',
        'multiprocessing', 'multiprocessing.spawn'
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'scipy', 'pandas', 'pytest', 'jupyter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

# Trim unnecessary data from bundled libs to keep the one-file exe smaller
a.datas = [x for x in a.datas if not x[0].startswith('matplotlib')]
a.datas = [x for x in a.datas if not x[0].startswith('numpy')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# One-file GUI build with embedded assets/config
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DisplayControlPlus',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='../Display Control+ Logo.ico'
)
