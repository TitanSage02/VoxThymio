"""
Script de création d'exécutable VoxThymio
Développé par Espérance AYIWAHOUN pour AI4Innov
"""

import subprocess
import sys
import os
from pathlib import Path

def install_pyinstaller():
    """Installe PyInstaller si nécessaire."""
    try:
        import PyInstaller
        print("✅ PyInstaller déjà installé")
    except ImportError:
        print("📦 Installation de PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def create_executable():
    """Crée l'exécutable VoxThymio."""
    print("🚀 Création de l'exécutable VoxThymio...")
    
    # Commande PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",                    # Un seul fichier
        "--windowed",                   # Sans console (GUI)
        "--name=VoxThymio",             # Nom de l'exécutable
        "--icon=robot.ico",             # Icône 
        "--add-data=src;src",           # Inclure le dossier src
        "--hidden-import=tdmclient",    # Import caché
        "--hidden-import=speech_recognition",
        "--hidden-import=pyaudio",
        "--clean",                      # Nettoyer avant de construire
        "voxthymio_gui.py"              # Fichier principal
    ]
    
    try:
        subprocess.check_call(cmd)
        print("✅ Exécutable créé avec succès!")
        print("📁 Fichier disponible dans: dist/VoxThymio.exe")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la création: {e}")
        return False
    
    return True

def create_spec_file():
    """Crée un fichier .spec personnalisé pour plus de contrôle."""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['voxthymio_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('src', 'src')],
    hiddenimports=['tdmclient', 'speech_recognition', 'pyaudio'],
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
    name='VoxThymio',
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
    icon='robot.ico',
    version='version.txt'
)
'''
    
    with open("VoxThymio.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print("📝 Fichier VoxThymio.spec créé")

def create_version_file():
    """Crée un fichier de version pour Windows."""
    version_content = '''# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'AI4Innov'),
        StringStruct(u'FileDescription', u'VoxThymio - Contrôle Vocal pour Robot Thymio'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'VoxThymio'),
        StringStruct(u'LegalCopyright', u'© 2024 Espérance AYIWAHOUN pour AI4Innov'),
        StringStruct(u'OriginalFilename', u'VoxThymio.exe'),
        StringStruct(u'ProductName', u'VoxThymio'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    with open("version.txt", "w", encoding="utf-8") as f:
        f.write(version_content)
    
    print("📝 Fichier version.txt créé")

def main():
    """Fonction principale."""
    print("🤖 VoxThymio - Générateur d'Exécutable")
    print("Développé par Espérance AYIWAHOUN pour AI4Innov")
    print("=" * 50)
    
    # Vérifier que nous sommes dans le bon dossier
    if not Path("voxthymio_gui.py").exists():
        print("❌ Erreur: voxthymio_gui.py non trouvé")
        print("Assurez-vous d'être dans le dossier VoxThymio")
        return
    
    # Installer PyInstaller
    install_pyinstaller()
    
    # Créer les fichiers de support
    create_version_file()
    create_spec_file()
    
    # Créer l'exécutable
    if create_executable():
        print("\n🎉 SUCCESS!")
        print("Votre exécutable VoxThymio est prêt à être utilisé.")
        print("📁 Localisation: dist/VoxThymio.exe")
        print("\n💡 Instructions:")
        print("1. Copiez VoxThymio.exe où vous voulez")
        print("2. Connectez votre robot Thymio")
        print("3. Lancez VoxThymio.exe")
        print("4. Profitez du contrôle vocal!")
    else:
        print("\n❌ Échec de la création de l'exécutable")
        print("Vérifiez les erreurs ci-dessus")

if __name__ == "__main__":
    main()
