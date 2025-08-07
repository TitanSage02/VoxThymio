"""
Script de test pour VoxThymio Intelligence
Teste les composants principaux sans nécessiter de connexion Thymio.

Développé par Espérance AYIWAHOUN pour AI4Innov
"""

import sys
import os
from pathlib import Path

# Ajout du chemin racine
sys.path.append(str(Path(__file__).parent))

def test_embedding_manager():
    """Teste le gestionnaire d'embeddings."""
    print("🧠 Test du gestionnaire d'embeddings...")
    try:
        from src.embedding_manager import EmbeddingManager
        
        embedding_mgr = EmbeddingManager()
        
        # Test de génération d'embedding
        text = "faire avancer le robot"
        embedding = embedding_mgr.generate_embedding(text)
        
        print(f"✅ Embedding généré: dimension {len(embedding)}")
        
        # Test de similarité
        text2 = "avancer rapidement"
        embedding2 = embedding_mgr.generate_embedding(text2)
        
        similarity = embedding_mgr.calculate_similarity(embedding, embedding2)
        print(f"✅ Similarité calculée: {similarity:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_vector_database():
    """Teste la base vectorielle."""
    print("\n🗄️ Test de la base vectorielle...")
    try:
        from src.command_manager import VectorDatabase
        from src.embedding_manager import EmbeddingManager
        
        vector_db = VectorDatabase()
        embedding_mgr = EmbeddingManager()
        
        # Test d'ajout d'une commande
        test_id = "test_avancer"
        test_desc = "faire avancer le robot de test"
        test_code = "motor.left.target = 200\nmotor.right.target = 200"
        test_embedding = embedding_mgr.generate_embedding(test_desc)
        
        result = vector_db.add_command(test_id, test_desc, test_code, test_embedding, "test")
        print(f"✅ Ajout de commande: {result}")
        
        # Test de recherche
        query_embedding = embedding_mgr.generate_embedding("avancer vers l'avant")
        similar_commands = vector_db.search_similar_commands(query_embedding, n_results=1)
        
        if similar_commands:
            cmd = similar_commands[0]
            print(f"✅ Commande trouvée: {cmd['command_id']} (similarité: {cmd['similarity']:.3f})")
        
        # Nettoyage
        vector_db.delete_command(test_id)
        print("✅ Commande de test supprimée")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_smart_voice_controller():
    """Teste le contrôleur vocal intelligent (sans Thymio)."""
    print("\n🎤 Test du contrôleur vocal intelligent...")
    try:
        # Import fictif pour le test
        class MockThymioController:
            async def execute_code(self, code):
                return True
        
        from src.smart_voice_controller import SmartVoiceController
        
        mock_controller = MockThymioController()
        voice_controller = SmartVoiceController(mock_controller)
        
        # Test de statistiques
        stats = voice_controller.get_system_stats()
        print(f"✅ Statistiques récupérées: {stats['database']['total_commands']} commandes")
        
        # Test d'ajout de commande
        result = voice_controller.add_new_command(
            "test_led",
            "allumer la LED de test",
            "call leds.top(32,0,0)",
            "test"
        )
        print(f"✅ Ajout de commande: {result['status']}")
        
        # Test de suppression
        if result['status'] == 'success':
            delete_result = voice_controller.delete_command("test_led")
            print(f"✅ Suppression: {delete_result['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_gui_imports():
    """Teste les imports de l'interface graphique."""
    print("\n🖥️ Test des imports GUI...")
    try:
        import tkinter as tk
        print("✅ Tkinter disponible")
        
        # Test d'import de notre GUI (sans l'exécuter)
        from gui.modern_voxthymio_gui import ModernVoxThymioGUI
        print("✅ Interface graphique importable")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Fonction principale de test."""
    print("🧪 VoxThymio - Tests des Composants")
    print("=" * 50)
    
    tests = [
        ("Gestionnaire d'embeddings", test_embedding_manager),
        ("Base vectorielle", test_vector_database),
        ("Contrôleur vocal intelligent", test_smart_voice_controller),
        ("Interface graphique", test_gui_imports)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 TEST: {test_name}")
        print("-" * 40)
        
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Erreur critique: {e}")
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests réussis")
    
    if passed == len(results):
        print("🎉 TOUS LES TESTS SONT PASSÉS !")
        print("Le système VoxThymio Intelligence est prêt à l'utilisation.")
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
    
    return passed == len(results)

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n💡 Pour tester avec Thymio:")
            print("   python main.py")
            print("   python launch_gui.py")
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
    finally:
        input("\nAppuyez sur Entrée pour quitter...")
