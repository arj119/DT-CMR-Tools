# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['DiffusionParameterResultsViewer.py'],
             pathex=['/Users/arjunbanerjee/Desktop/DT-CMR/DT-CMR-Tools'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Diffusion Parameter Results Viewer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='rbht_nhs_logo.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Diffusion Parameter Results Viewer')
app = BUNDLE(coll,
             name='Diffusion Parameter Results Viewer.app',
             icon='rbht_nhs_logo.ico',
             bundle_identifier=None,
             info_plist={
                'NSHighResolutionCapable': 'True'
                },
             )
