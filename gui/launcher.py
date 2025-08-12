"""
Script de lancement pour VoxThymio GUI
Développé par Espérance AYIWAHOUN pour AI4Innov

Ce script lance l'interface graphique VoxThymio avec la gestion appropriée des chemins.
"""

import sys
import os
from pathlib import Path

# Ajouter les répertoires nécessaires au PATH
current_dir = Path(__file__).parent
project_root = current_dir.parent
src_dir = project_root / "src"

# Ajouter les chemins pour les imports
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(current_dir))

def main():
    """Lance l'application VoxThymio GUI."""
    try:
        # Vérifier que les modules nécessaires sont disponibles
        required_modules = [
            "smart_voice_controller",
            "controller.thymio_controller",
            "speech_recognizer",
            "embedding_generator",
            "embedding_manager"
        ]
        
        missing_modules = []
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)
        
        if missing_modules:
            print("❌ Modules manquants:")
            for module in missing_modules:
                print(f"   - {module}")
            print("\nAssurez-vous que tous les fichiers sont présents dans le répertoire src/")
            return
        
        # Importer et lancer l'interface
        from voxthymio_modern_gui import VoxThymioGUI
        
        print("🚀 Lancement de VoxThymio Interface Moderne")
        print("   Développé par Espérance AYIWAHOUN")
        print("   Projet TechEduc - AI4Innov")
        print("=" * 50)
        
        app = VoxThymioGUI()
        app.run()
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("Vérifiez que tous les modules sont installés (pip install -r requirements.txt)")
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
