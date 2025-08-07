#!/usr/bin/env python3
"""
Lanceur rapide pour l'interface graphique moderne de VoxThymio
Développé par Espérance AYIWAHOUN pour AI4Innov
"""

import sys
from pathlib import Path

# Ajout du chemin racine
sys.path.append(str(Path(__file__).parent))

try:
    from gui.modern_voxthymio_gui import ModernVoxThymioGUI
    
    def main():
        """Lance directement l'interface graphique."""
        print("🚀 VoxThymio - Interface Graphique Intelligente")
        print("Chargement en cours...")
        
        app = ModernVoxThymioGUI()
        app.run()

    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("Assurez-vous que toutes les dépendances sont installées.")
    print("Exécutez: pip install -r requirements.txt")
    input("Appuyez sur Entrée pour quitter...")
except Exception as e:
    print(f"❌ Erreur: {e}")
    input("Appuyez sur Entrée pour quitter...")
