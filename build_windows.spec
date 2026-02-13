# -*- mode: python ; coding: utf-8 -*-
# TMA Magic Black Box - PyInstaller Spec File
"""
Build Configuration for Windows Executable.

Usage:
    pyinstaller build_windows.spec

Output:
    dist/TMA Magic Black Box/
"""

import sys
from pathlib import Path

block_cipher = None

# Get the directory containing this spec file
SPEC_DIR = Path(SPECPATH)

# Collect all Python files
a = Analysis(
    ['app.py'],
    pathex=[str(SPEC_DIR)],
    binaries=[],
    datas=[
        # Include all engine and utility modules
        ('engines', 'engines'),
        ('utils', 'utils'),
        ('config.py', '.'),
        ('backend_processor.py', '.'),
    ],
    hiddenimports=[
        # Streamlit internals
        'streamlit',
        'streamlit.web.cli',
        'streamlit.runtime.scriptrunner',
        
        # Data processing
        'pandas',
        'pandas._libs',
        'pandas._libs.tslibs',
        
        # PDF processing
        'pypdf',
        'pdf2image',
        
        # Excel
        'openpyxl',
        
        # OpenAI
        'openai',
        
        # Our modules
        'engines',
        'engines.regex_engine',
        'engines.ai_engine',
        'utils',
        'utils.pdf_parser',
        'config',
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
    [],
    exclude_binaries=True,
    name='TMA Magic Black Box',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if desired
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TMA Magic Black Box',
)
