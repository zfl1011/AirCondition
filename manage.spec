# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['manage.py'],
             pathex=['D:\\AirCondition'],
             binaries=[],
             datas=[],
             hiddenimports=['django.contrib.admin',
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.messages',
                'django.contrib.staticfiles',
                'django.contrib.admin.apps','django.contrib.auth.apps','django.contrib.contenttypes.apps',
	            'django.contrib.sessions.apps', 'django.contrib.messages.apps', 'django.contrib.staticfiles.apps',
                'openpyxl',
                'inspector','inspector.model','inspector.url','inspector.app'
                'user','user.model','user.url','user.app'
                'manager','manager.model','manager.url','manager.app'
                'reception','manager.model','manager.url','manager.app'],
             hookspath=[

             ],
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
          name='manage',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='manage')
