"""
VoxThymio - Interface de contrôle intelligent pour le robot Thymio.
"""

import asyncio
import os
import sys
from pathlib import Path

# Ajout du chemin racine pour les imports
sys.path.append(str(Path(__file__).parent))

from src.controller.thymio_controller import ThymioController
from src.smart_voice_controller import SmartVoiceController


class VoxThymio:
    """Interface  de contrôle pour Thymio."""
    
    def __init__(self):
        """Initialise l'interface de contrôle."""
        self.controller = None              # Contrôleur de communication avec Thymio
        self.smart_voice_controller = None  # Contrôleur vocal
        self.running = False                # État de l'application
        self.connected = False              # État de connexion
    
    def clear_screen(self):
        """Efface l'écran du terminal."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_main_menu(self):
        """Affiche le menu principal de l'application."""
        self.clear_screen()
        print("🤖 VoxThymio")
        print("=" * 50)
        print(f"État: {'🟢 Connecté' if self.connected else '🔴 Déconnecté'}")
        print("=" * 50)
        print()
        print("MODES DISPONIBLES:")
        print("1. 🎤 Mode vocal")
        print("2. ⚙️ Gestion des commandes")
        print("3. 🧠 Interface graphique complète")
        print("4. 📊 Statistiques du système")
        print("5. 🎙️ Statistiques vocales")
        print("6. 🔧 Configuration")
        print()
        print("0. ❌ Quitter")
        print("=" * 50)
    
    async def connect_thymio(self):
        """Connecte à Thymio et initialise le système."""
        if self.connected:
            print("✅ Déjà connecté à Thymio.")
            return True
        
        try:
            print("🔗 Connexion à Thymio en cours...")
            self.controller = ThymioController()
            await self.controller.connect()

            print("🧠 Initialisation du système...")
            self.smart_voice_controller = SmartVoiceController(self.controller)
            
            self.connected = True
            print("✅ Connexion établie et système activé !")
            return True
            
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    async def disconnect_thymio(self):
        """Déconnecte de Thymio."""
        if not self.connected:
            return
        
        try:
            if self.controller:
                await self.controller.disconnect()

            self.controller = None
            self.smart_voice_controller = None
            self.connected = False
            print("🔌 Déconnecté de Thymio.")
        
        except Exception as e:
            print(f"❌ Erreur lors de la déconnexion: {e}")
    
    async def voice_mode(self):
        """Mode de contrôle vocal intelligent."""
        if not self.connected:
            if not await self.connect_thymio():
                return
        
        self.clear_screen()
        print("🎤 MODE VOCAL INTELLIGENT")
        print("=" * 50)
        print("• Tapez vos commandes en langage naturel")
        print("• Le système utilise l'IA pour comprendre vos intentions")
        print("• Tapez 'voix' pour activer/désactiver la reconnaissance vocale")
        print("• Tapez 'calibrer' pour calibrer le microphone")
        print("• Tapez 'quitter' pour revenir au menu principal")
        print("• Tapez 'aide' pour voir les commandes disponibles")
        print("=" * 50)
        print()
        
        # État de la reconnaissance vocale
        voice_active = False
        
        while True:
            try:
                # Affichage de l'état du microphone
                mic_status = "🎤 ON" if voice_active else "🎤 OFF"
                user_input = input(f"{mic_status} Votre commande: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quitter', 'exit', 'quit']:
                    # Arrêter la reconnaissance vocale si active
                    if voice_active:
                        result = self.smart_voice_controller.stop_voice_recognition()
                        print(result['message'])
                    break
                
                if user_input.lower() in ['aide', 'help']:
                    self.show_available_commands()
                    continue
                
                if user_input.lower() in ['voix', 'voice', 'microphone', 'micro']:
                    if voice_active:
                        result = self.smart_voice_controller.stop_voice_recognition()
                        voice_active = False
                    else:
                        result = self.smart_voice_controller.start_voice_recognition()
                        voice_active = result['status'] == 'success'
                    print(result['message'])
                    continue
                
                if user_input.lower() in ['calibrer', 'calibrate']:
                    # Arrêter temporairement la reconnaissance vocale pour la calibration
                    was_active = voice_active
                    if voice_active:
                        self.smart_voice_controller.stop_voice_recognition()
                        voice_active = False
                    
                    print("🎤 Calibration du microphone...")
                    result = self.smart_voice_controller.calibrate_microphone(duration=2.0)
                    print(result['message'])
                    
                    # Réactiver si c'était actif avant
                    if was_active:
                        result = self.smart_voice_controller.start_voice_recognition()
                        voice_active = result['status'] == 'success'
                    
                    continue
                
                # Traitement normal des commandes textuelles
                print(f"🔍 Traitement de: '{user_input}'")
                result = await self.smart_voice_controller.process_command(user_input)
                
                self.display_command_result(result)
                print()
                
            except KeyboardInterrupt:
                # Arrêter la reconnaissance vocale si active
                if voice_active:
                    self.smart_voice_controller.stop_voice_recognition()
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")
    
    def show_available_commands(self):
        """Affiche les commandes disponibles."""
        if not self.smart_voice_controller:
            print("❌ Système intelligent non initialisé.")
            return
        
        commands = self.smart_voice_controller.get_all_commands()
        
        print("\n📋 COMMANDES DISPONIBLES:")
        print("=" * 50)
        
        categories = {}
        for cmd in commands:
            category = cmd.get('category', 'unknown')
            if category not in categories:
                categories[category] = []
            categories[category].append(cmd)
        
        for category, cmds in categories.items():
            print(f"\n🏷️ {category.upper()}")
            print("-" * 30)
            for cmd in cmds[:5]:  # Limiter à 5 par catégorie pour l'affichage
                print(f"  • {cmd['description']}")
            if len(cmds) > 5:
                print(f"  ... et {len(cmds) - 5} autres")
        
        print(f"\n📊 Total: {len(commands)} commandes disponibles")
        input("\nAppuyez sur Entrée pour continuer...")
    
    async def command_management_mode(self):
        """Mode de gestion des commandes."""
        if not self.connected:
            if not await self.connect_thymio():
                return
        
        while True:
            self.clear_screen()
            print("⚙️ GESTION DES COMMANDES")
            print("=" * 50)
            print("1. ➕ Ajouter une nouvelle commande")
            print("2. 📋 Lister toutes les commandes")
            print("3. 🗑️ Supprimer une commande")
            print("4. 🧪 Tester une commande")
            print("5. 📊 Statistiques détaillées")
            print("0. ↩️ Retour au menu principal")
            print("=" * 50)
            
            choice = input("Votre choix: ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                await self.add_new_command()
            elif choice == '2':
                self.list_all_commands()
            elif choice == '3':
                self.delete_command()
            elif choice == '4':
                await self.test_command()
            elif choice == '5':
                self.show_detailed_stats()
            else:
                print("❌ Choix invalide.")
                input("Appuyez sur Entrée pour continuer...")
    
    async def add_new_command(self):
        """Ajoute une nouvelle commande."""
        self.clear_screen()
        print("➕ AJOUTER UNE NOUVELLE COMMANDE")
        print("=" * 50)
        
        try:
            cmd_id = input("ID de la commande (unique): ").strip()
            if not cmd_id:
                print("❌ L'ID ne peut pas être vide.")
                input("Appuyez sur Entrée pour continuer...")
                return
            
            description = input("Description en langage naturel: ").strip()
            if not description:
                print("❌ La description ne peut pas être vide.")
                input("Appuyez sur Entrée pour continuer...")
                return
            
            print("\nCode Thymio (tapez 'FIN' sur une ligne seule pour terminer):")
            code_lines = []
            while True:
                line = input(">>> ")
                if line.strip() == 'FIN':
                    break
                code_lines.append(line)
            
            code = '\n'.join(code_lines).strip()
            if not code:
                print("❌ Le code ne peut pas être vide.")
                input("Appuyez sur Entrée pour continuer...")
                return
            
            categories = ["custom", "movement", "lights", "sounds", "advanced"]
            print(f"\nCatégories disponibles: {', '.join(categories)}")
            category = input("Catégorie (défaut: custom): ").strip() or "custom"
            
            print(f"\n🔍 Ajout de la commande '{cmd_id}'...")
            result = self.smart_voice_controller.add_new_command(cmd_id, description, code, category)
            
            self.display_command_result(result)
            
        except KeyboardInterrupt:
            print("\n❌ Ajout annulé.")
        
        input("\nAppuyez sur Entrée pour continuer...")
    
    def list_all_commands(self):
        """Liste toutes les commandes."""
        self.clear_screen()
        print("📋 TOUTES LES COMMANDES")
        print("=" * 70)
        
        commands = self.smart_voice_controller.get_all_commands()
        
        if not commands:
            print("Aucune commande trouvée.")
        else:
            for i, cmd in enumerate(commands, 1):
                print(f"{i:2d}. {cmd['command_id']} ({cmd['category']})")
                print(f"    📝 {cmd['description']}")
                print(f"    💻 {cmd['code'][:50]}{'...' if len(cmd['code']) > 50 else ''}")
                print()
        
        print(f"📊 Total: {len(commands)} commandes")
        input("\nAppuyez sur Entrée pour continuer...")
    
    def delete_command(self):
        """Supprime une commande."""
        self.clear_screen()
        print("🗑️ SUPPRIMER UNE COMMANDE")
        print("=" * 50)
        
        commands = self.smart_voice_controller.get_all_commands()
        
        if not commands:
            print("Aucune commande à supprimer.")
            input("Appuyez sur Entrée pour continuer...")
            return
        
        print("Commandes disponibles:")
        for i, cmd in enumerate(commands, 1):
            print(f"{i:2d}. {cmd['command_id']} - {cmd['description'][:40]}...")
        
        try:
            choice = input("\nNuméro de la commande à supprimer (0 pour annuler): ").strip()
            if choice == '0':
                return
            
            index = int(choice) - 1
            if 0 <= index < len(commands):
                cmd_to_delete = commands[index]
                confirm = input(f"Êtes-vous sûr de vouloir supprimer '{cmd_to_delete['command_id']}' ? (oui/non): ")
                
                if confirm.lower() in ['oui', 'yes', 'o', 'y']:
                    result = self.smart_voice_controller.delete_command(cmd_to_delete['command_id'])
                    self.display_command_result(result)
                else:
                    print("❌ Suppression annulée.")
            else:
                print("❌ Numéro invalide.")
        
        except ValueError:
            print("❌ Veuillez entrer un numéro valide.")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        input("\nAppuyez sur Entrée pour continuer...")
    
    async def test_command(self):
        """Teste une commande."""
        self.clear_screen()
        print("🧪 TESTER UNE COMMANDE")
        print("=" * 50)
        
        test_input = input("Tapez une phrase à tester: ").strip()
        if not test_input:
            return
        
        print(f"\n🔍 Test de: '{test_input}'")
        result = await self.smart_voice_controller.process_command(test_input)
        
        self.display_command_result(result)
        input("\nAppuyez sur Entrée pour continuer...")
    
    def show_detailed_stats(self):
        """Affiche les statistiques détaillées."""
        if not self.connected:
            print("❌ Veuillez d'abord vous connecter à Thymio.")
            input("Appuyez sur Entrée pour continuer...")
            return
            
        self.clear_screen()
        print("📊 STATISTIQUES DÉTAILLÉES")
        print("=" * 60)
        
        stats = self.smart_voice_controller.get_system_stats()
        
        # Statistiques de la base
        db_stats = stats.get('database', {})
        print("🗄️ BASE VECTORIELLE:")
        print(f"   Total commandes: {db_stats.get('total_commands', 0)}")
        
        categories = db_stats.get('categories', {})
        if categories:
            print("   Répartition par catégorie:")
            for cat, count in categories.items():
                print(f"     - {cat}: {count}")
        
        print(f"   Chemin: {db_stats.get('db_path', 'N/A')}")
        
        # Statistiques du modèle
        model_stats = stats.get('embedding_model', {})
        print(f"\n🧠 MODÈLE D'EMBEDDING:")
        print(f"   Modèle: {model_stats.get('model_name', 'N/A')}")
        print(f"   Dimension: {model_stats.get('embedding_dim', 'N/A')}")
        print(f"   Périphérique: {model_stats.get('device', 'N/A')}")
        print(f"   Taille vocabulaire: {model_stats.get('vocab_size', 'N/A')}")
        
        # Configuration actuelle
        thresholds = stats.get('thresholds', {})
        print(f"\n⚙️ CONFIGURATION:")
        print(f"   Seuil d'exécution: {thresholds.get('execution', 'N/A')}")
        print(f"   Seuil d'apprentissage: {thresholds.get('learning', 'N/A')}")
        
        input("\nAppuyez sur Entrée pour continuer...")
    
    def launch_gui(self):
        """Lance l'interface graphique complète."""
        try:
            from gui.voxthymio_gui import VoxThymioIntelligentGUI
            print("🚀 Lancement de l'interface graphique...")
            gui = VoxThymioIntelligentGUI()
            gui.run()
        except ImportError as e:
            print(f"❌ Erreur lors du chargement de l'interface graphique: {e}")
            print("Assurez-vous que tkinter est installé.")
            input("Appuyez sur Entrée pour continuer...")
        except Exception as e:
            print(f"❌ Erreur: {e}")
            input("Appuyez sur Entrée pour continuer...")
    
    def display_command_result(self, result):
        """Affiche le résultat d'une commande."""
        status = result.get('status', 'unknown')
        message = result.get('message', 'Pas de message')
        
        if status == 'success':
            print(f"✅ {message}")
            if 'similarity' in result:
                print(f"   📊 Similarité: {result['similarity']:.3f}")
        elif status == 'unknown':
            print(f"❓ {message}")
            suggestions = result.get('suggestions', [])
            if suggestions:
                print("   💡 Suggestions:")
                for suggestion in suggestions[:3]:
                    print(f"     - {suggestion}")
        elif status == 'error':
            print(f"❌ {message}")
        elif status == 'warning':
            print(f"⚠️ {message}")
        else:
            print(f"ℹ️ {message}")
    
    def show_voice_stats(self):
        """Affiche les statistiques de reconnaissance vocale."""
        if not self.connected or not self.smart_voice_controller:
            print("❌ Système non connecté.")
            return
            
        try:
            result = self.smart_voice_controller.get_voice_recognition_stats()
            
            if result['status'] != 'success':
                print(f"❌ {result['message']}")
                return
                
            stats = result['stats']
            is_active = result['is_active']
            
            self.clear_screen()
            print("🎤 STATISTIQUES DE RECONNAISSANCE VOCALE")
            print("=" * 50)
            print(f"État: {'🟢 Actif' if is_active else '🔴 Inactif'}")
            print("=" * 50)
            
            print(f"\n📊 PERFORMANCE:")
            print(f"  • Tentatives totales: {stats['total_attempts']}")
            print(f"  • Reconnaissances réussies: {stats['successful_recognitions']}")
            print(f"  • Échecs de reconnaissance: {stats['failed_recognitions']}")
            
            if stats['total_attempts'] > 0:
                print(f"  • Taux de réussite: {stats['success_rate']:.1f}%")
            
            print(f"\n⚙️ CONFIGURATION:")
            print(f"  • Langue: {stats['language']}")
            print(f"  • Seuil d'énergie: {stats['energy_threshold']}")
            print(f"  • Seuil de pause: {stats['pause_threshold']}")
            
            if stats['last_error']:
                print(f"\n❌ Dernière erreur: {stats['last_error']}")
                
            input("\nAppuyez sur Entrée pour continuer...")
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des statistiques: {e}")
            input("Appuyez sur Entrée pour continuer...")
            
    async def configuration_mode(self):
        """Mode de configuration du système."""
        while True:
            self.clear_screen()
            print("🔧 CONFIGURATION DU SYSTÈME")
            print("=" * 50)
            print("1. ⚙️ Ajuster les seuils de similarité")
            print("2. 🔄 Réinitialiser la base vectorielle")
            print("3. 📤 Exporter les commandes")
            print("4. 📥 Importer des commandes")
            print("0. ↩️ Retour au menu principal")
            print("=" * 50)
            
            choice = input("Votre choix: ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                await self.adjust_thresholds()
            elif choice == '2':
                await self.reset_database()
            elif choice == '3':
                self.export_commands()
            elif choice == '4':
                self.import_commands()
            else:
                print("❌ Choix invalide.")
                input("Appuyez sur Entrée pour continuer...")
    
    async def adjust_thresholds(self):
        """Ajuste les seuils de similarité."""
        if not self.connected:
            if not await self.connect_thymio():
                return
        
        self.clear_screen()
        print("⚙️ AJUSTEMENT DES SEUILS")
        print("=" * 50)
        
        current_stats = self.smart_voice_controller.get_system_stats()
        current_thresholds = current_stats.get('thresholds', {})
        
        print(f"Seuil d'exécution actuel: {current_thresholds.get('execution', 0.6)}")
        print(f"Seuil d'apprentissage actuel: {current_thresholds.get('learning', 0.85)}")
        print()
        
        try:
            exec_input = input("Nouveau seuil d'exécution (0.1-1.0, Entrée pour garder): ").strip()
            learn_input = input("Nouveau seuil d'apprentissage (0.1-1.0, Entrée pour garder): ").strip()
            
            exec_threshold = float(exec_input) if exec_input else None
            learn_threshold = float(learn_input) if learn_input else None
            
            result = self.smart_voice_controller.update_thresholds(exec_threshold, learn_threshold)
            self.display_command_result(result)
            
        except ValueError:
            print("❌ Valeurs invalides. Les seuils doivent être des nombres entre 0.1 et 1.0.")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        input("\nAppuyez sur Entrée pour continuer...")
    
    async def reset_database(self):
        """Remet à zéro la base vectorielle."""
        if not self.connected:
            if not await self.connect_thymio():
                return
        
        self.clear_screen()
        print("🔄 RÉINITIALISATION DE LA BASE")
        print("=" * 50)
        print("⚠️ ATTENTION: Cette action supprimera TOUTES les commandes personnalisées !")
        print("Les commandes par défaut seront rechargées.")
        print()
        
        confirm = input("Êtes-vous absolument sûr ? (tapez 'RESET' pour confirmer): ")
        
        if confirm == 'RESET':
            try:
                if self.smart_voice_controller.vector_db.reset_database():
                    print("✅ Base vectorielle réinitialisée.")
                    print("🔄 Rechargement des commandes par défaut...")
                    self.smart_voice_controller._load_commands()
                    print("✅ Commandes par défaut rechargées.")
                else:
                    print("❌ Échec de la réinitialisation.")
            except Exception as e:
                print(f"❌ Erreur: {e}")
        else:
            print("❌ Réinitialisation annulée.")
        
        input("\nAppuyez sur Entrée pour continuer...")
    
    def export_commands(self):
        """Exporte les commandes."""
        # Implémentation simplifiée pour le mode console
        print("📤 Fonctionnalité d'export disponible dans l'interface graphique.")
        input("Appuyez sur Entrée pour continuer...")
    
    def import_commands(self):
        """Importe des commandes."""
        # Implémentation simplifiée pour le mode console
        print("📥 Fonctionnalité d'import disponible dans l'interface graphique.")
        input("Appuyez sur Entrée pour continuer...")
    
    async def run(self):
        """Lance l'application principale."""
        self.running = True
        
        try:
            while self.running:
                self.show_main_menu()
                choice = input("Votre choix: ").strip()
                
                if choice == '0':
                    self.running = False
                elif choice == '1':
                    await self.voice_mode()
                elif choice == '2':
                    await self.command_management_mode()
                elif choice == '3':
                    self.launch_gui()
                elif choice == '4':
                    self.show_detailed_stats()
                elif choice == '5':
                    self.show_voice_stats()
                elif choice == '6':
                    await self.configuration_mode()
                else:
                    print("❌ Choix invalide.")
                    input("Appuyez sur Entrée pour continuer...")
        
        except KeyboardInterrupt:
            print("\n👋 Arrêt de l'application...")
        
        finally:
            await self.disconnect_thymio()


async def main():
    """Point d'entrée principal."""
    print("🤖 VoxThymio")
    print("Initialisation du système...")
    
    app = VoxThymio()
    await app.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Au revoir !")
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        input("Appuyez sur Entrée pour quitter...")
