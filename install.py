"""
Script d'installation et de configuration pour VoxThymio Intelligence
Installe les dépendances et configure l'environnement.

Développé par Espérance AYIWAHOUN pour AI4Innov
"""

import subprocess
import sys
import os
from pathlib import Path
import json

def run_command(command, description):
    """Exécute une commande avec gestion d'erreur."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} réussi")
            return True
        else:
            print(f"❌ Erreur: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        return False

def install_dependencies():
    """Installe les dépendances Python."""
    print("📦 INSTALLATION DES DÉPENDANCES")
    print("=" * 50)
    
    # Mise à jour de pip
    run_command(f"{sys.executable} -m pip install --upgrade pip", "Mise à jour de pip")
    
    # Installation des requirements
    requirements_file = Path(__file__).parent / "requirements.txt"
    if requirements_file.exists():
        run_command(f"{sys.executable} -m pip install -r {requirements_file}", "Installation des dépendances")
    else:
        print("❌ Fichier requirements.txt non trouvé")
        return False
    
    return True

def check_python_version():
    """Vérifie la version de Python."""
    print("🐍 VÉRIFICATION DE PYTHON")
    print("=" * 50)
    
    version = sys.version_info
    print(f"Version Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ requis")
        return False
    
    print("✅ Version Python compatible")
    return True

def create_directories():
    """Crée les répertoires nécessaires."""
    print("📁 CRÉATION DES RÉPERTOIRES")
    print("=" * 50)
    
    directories = [
        "vector_db",
        "logs",
        "exports"
    ]
    
    for directory in directories:
        dir_path = Path(__file__).parent / directory
        dir_path.mkdir(exist_ok=True)
        print(f"✅ Répertoire créé: {directory}")
    
    return True

def check_dependencies():
    """Vérifie les dépendances critiques."""
    print("🔍 VÉRIFICATION DES DÉPENDANCES")
    print("=" * 50)
    
    critical_packages = [
        "transformers",
        "torch",
        "chromadb",
        "numpy",
        "tkinter"
    ]
    
    missing_packages = []
    
    for package in critical_packages:
        try:
            if package == "tkinter":
                import tkinter
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} manquant")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Packages manquants: {', '.join(missing_packages)}")
        return False
    
    print("✅ Toutes les dépendances sont installées")
    return True

def test_bert_model():
    """Teste le chargement du modèle BERT."""
    print("🧠 TEST DU MODÈLE BERT")
    print("=" * 50)
    
    try:
        from transformers import AutoTokenizer, AutoModel
        print("📥 Téléchargement du modèle BERT français...")
        
        # Test avec un modèle léger
        model_name = "camembert-base"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name)
        
        print("✅ Modèle BERT chargé avec succès")
        
        # Test d'encoding simple
        text = "test de fonctionnement"
        tokens = tokenizer(text, return_tensors='pt')
        print("✅ Tokenisation fonctionnelle")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test BERT: {e}")
        return False

def create_config_file():
    """Crée un fichier de configuration par défaut."""
    print("⚙️ CRÉATION DE LA CONFIGURATION")
    print("=" * 50)
    
    config = {
        "embedding_model": "camembert-base",
        "vector_db_path": "./vector_db",
        "thresholds": {
            "execution": 0.6,
            "learning": 0.85
        },
        "ui_settings": {
            "theme": "modern_dark",
            "auto_connect": False,
            "show_similarity_scores": True
        },
        "logging": {
            "level": "INFO",
            "file": "./logs/voxthymio.log"
        }
    }
    
    config_file = Path(__file__).parent / "config.json"
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print("✅ Fichier de configuration créé")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création de config.json: {e}")
        return False

def display_summary():
    """Affiche un résumé de l'installation."""
    print("\n" + "=" * 60)
    print("🎉 INSTALLATION TERMINÉE")
    print("=" * 60)
    print()
    print("📋 FICHIERS PRINCIPAUX:")
    print("• main.py              - Interface console complète")
    print("• launch_gui.py        - Lanceur interface graphique")
    print("• requirements.txt     - Dépendances Python")
    print("• config.json          - Configuration système")
    print()
    print("📁 RÉPERTOIRES:")
    print("• src/                 - Code source du système")
    print("• gui/                 - Interface graphique")
    print("• vector_db/           - Base vectorielle ChromaDB")
    print("• logs/                - Fichiers de log")
    print("• exports/             - Exportations de données")
    print()
    print("🚀 POUR DÉMARRER:")
    print("• Mode console: python main.py")
    print("• Mode graphique: python launch_gui.py")
    print()
    print("📚 COMMANDES PRINCIPALES:")
    print("• 'avancer' - faire avancer le robot")
    print("• 'tourner à gauche' - tourner vers la gauche")
    print("• 'LED rouge' - allumer la LED en rouge")
    print("• 'arrêter' - arrêter le robot")
    print()
    print("💡 Le système apprend automatiquement de nouvelles commandes !")
    print("   Seuil d'exécution: 0.6 | Seuil d'apprentissage: 0.85")

def main():
    """Fonction principale d'installation."""
    print("🤖 VoxThymio - Installation du Système Intelligent")
    print("Développé par Espérance AYIWAHOUN pour AI4Innov")
    print("=" * 60)
    print()
    
    # Étapes d'installation
    steps = [
        ("Vérification Python", check_python_version),
        ("Création des répertoires", create_directories),
        ("Installation des dépendances", install_dependencies),
        ("Vérification des packages", check_dependencies),
        ("Test du modèle BERT", test_bert_model),
        ("Configuration système", create_config_file)
    ]
    
    failed_steps = []
    
    for step_name, step_function in steps:
        print(f"\n📋 ÉTAPE: {step_name}")
        print("-" * 40)
        
        if not step_function():
            failed_steps.append(step_name)
            print(f"❌ Échec de l'étape: {step_name}")
        else:
            print(f"✅ Étape réussie: {step_name}")
    
    print("\n" + "=" * 60)
    
    if failed_steps:
        print("⚠️ INSTALLATION INCOMPLÈTE")
        print(f"Étapes échouées: {', '.join(failed_steps)}")
        print("Veuillez corriger les erreurs et relancer l'installation.")
    else:
        print("🎉 INSTALLATION RÉUSSIE !")
        display_summary()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Installation interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
    finally:
        input("\nAppuyez sur Entrée pour quitter...")
