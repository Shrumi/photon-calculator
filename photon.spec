# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec: ФОТОН демо (onefile, windowed)

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[('photon/static', 'photon/static')],
    hiddenimports=['uvicorn.logging', 'uvicorn.loops', 'uvicorn.protocols',
                   'uvicorn.protocols.http', 'uvicorn.protocols.http.auto',
                   'uvicorn.protocols.websockets', 'uvicorn.protocols.websockets.auto',
                   'uvicorn.lifespan', 'uvicorn.lifespan.on'],
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas', 'PIL'],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PhotonCalcDemo',
    debug=False,
    strip=False,
    upx=False,
    console=False,
    icon=None,
)
