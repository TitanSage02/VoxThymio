"""
VoxThymio - Script de lancement principal
Développé par Espérance AYIWAHOUN pour AI4Innov

Ce script lance l'interface graphique VoxThymio avec toutes les vérifications nécessaires.
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Vérifie la version de Python."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 ou supérieur requis")
        print(f"   Version actuelle: {sys.version}")
        return False
    return True

def check_requirements():
    """Vérifie que les dépendances sont installées."""
    required_packages = [
        "tkinter",
        "asyncio",
        "threading",
        "json",
        "pathlib"
    ]
    
    optional_packages = [
        "tdmclient",
        "SpeechRecognition", 
        "transformers",
        "sentence_transformers",
        "chromadb",
        "torch",
        "numpy"
    ]
    
    missing_required = []
    missing_optional = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_required.append(package)
    
    for package in optional_packages:
        try:
            __import__(package)
        except ImportError:
            missing_optional.append(package)
    
    if missing_required:
        print("❌ Packages requis manquants:")
        for pkg in missing_required:
            print(f"   - {pkg}")
        return False
    
    if missing_optional:
        print("⚠️ Packages optionnels manquants (fonctionnalités limitées):")
        for pkg in missing_optional:
            print(f"   - {pkg}")
        print("   Installez avec: pip install -r requirements.txt")
    
    return True

def main():
    """Point d'entrée principal."""
    print("🤖 VoxThymio v1.0 - Système de contrôle vocal pour Thymio")
    print("   Développé par Espérance AYIWAHOUN (AI4Innov)")
    print("=" * 60)
    
    # Vérifications préliminaires
    if not check_python_version():
        sys.exit(1)
    
    if not check_requirements():
        print("\n⚠️ Certaines dépendances sont manquantes.")
        response = input("Continuer quand même ? (y/N): ").lower()
        if response != 'y':
            print("Installation annulée.")
            print("Installez les dépendances avec: pip install -r requirements.txt")
            sys.exit(1)
    
    # Lancement de l'interface
    try:
        gui_dir = Path(__file__).parent / "gui"
        launcher_path = gui_dir / "launcher.py"
        
        if not launcher_path.exists():
            print(f"❌ Fichier launcher non trouvé: {launcher_path}")
            sys.exit(1)
        
        print("\n🚀 Lancement de l'interface graphique...")
        
        # Lancer le script GUI
        os.chdir(gui_dir)
        subprocess.run([sys.executable, "launcher.py"], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du lancement: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
