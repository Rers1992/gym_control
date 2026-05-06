# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

sys.setrecursionlimit(5000)

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
datas=[
    ('firebase_credentials.json', '.'),
    ('charly_photo.jpg', '.'),
],
    hiddenimports=[
        'firebase_admin',
        'firebase_admin.credentials',
        'firebase_admin.firestore',
        'flet',
        'flet.page',
        'flet.controls',
        'flet_core',
        'google.cloud.firestore',
        'google.cloud',
        'grpc',
        'grpc._cython.cygrpc',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GymControl',
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
    icon=None,
)
