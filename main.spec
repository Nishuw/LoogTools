# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py', 'navigation.py', 'observacao.py', 'telefonia.py', 'utils.py', 'fechamento.py', 'codigos_sip.py', 'calculadora_subrede.py', 'coleta_logs_telefonia.py', 'tab_navigation.py', 'troubleshooting.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\\\LoogTools\\\\codigos_sip.txt', '.'), ('C:\\\\LoogTools\\\\processos\\\\imagens', 'processos\\\\imagens'), ('C:\\\\LoogTools\\\\processos', 'processos'), ('C:\\\\LoogTools\\\\scriptss', 'scriptss')],
    hiddenimports=[],
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
    name='main',
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
