# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['F:\\road_defect_detection\\road_defect_detection\\yolo\\app\\app.py'],
    pathex=['F:\\py_YOLOv5\\YOLO\\yolov8'],
    binaries=[],
    datas=[('F:\\road_defect_detection\\road_defect_detection\\yolo\\app*', '.')],
    hiddenimports=['ultralytics', 'ultralytics.yolo', 'ultralytics.nn', 'ultralytics.data', 'view_frame_manager', 'analyze_gemini'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='app',
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
