"""
Contrôle principal du robot Thymio avec commandes vocales et interface utilisateur.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional
import threading
import time
import queue
from concurrent.futures import ThreadPoolExecutor

root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from src.communication.thymio_controller import ThymioController
from src.voice_controller import VoiceController, VoiceCommandStatus


class ThymioVoiceInterface:
    """Interface de contrôle vocal pour le robot Thymio."""
    
    def __init__(self):
        self.controller: Optional[ThymioController] = None
        self.voice_controller: Optional[VoiceController] = None
        self.running = False
        self.voice_mode = False
        self.voice_thread: Optional[threading.Thread] = None
        self.voice_active = False
        self.command_queue = queue.Queue()
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    def clear_screen(self):
        """Efface l'écran de la console."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_menu(self):
        """Affiche le menu principal."""
        print("\n" + "="*50)
        print("         CONTRÔLE THYMIO VOCAL")
        print("="*50)
        print("COMMANDES MANUELLES:")
        print("1. Avancer")
        print("2. Reculer") 
        print("3. Tourner à gauche")
        print("4. Tourner à droite")
        print("5. Arrêter")
        print("6. LED Rouge")
        print("7. LED Vert")
        print("8. LED Bleu")
        print("9. Éteindre LED")
        print("-" * 30)
        print("CONTRÔLE VOCAL:")
        print("v. Activer/Désactiver le contrôle vocal")
        print("c. Afficher les commandes vocales")
        print("t. Tester le microphone")
        print("-" * 30)
        print("DIAGNOSTIC:")
        print("d. Diagnostic de connexion")
        print("-" * 30)
        print("0. Quitter")
        print("="*50)
        
        # Affichage du statut
        if self.voice_mode:
            print("🎤 CONTRÔLE VOCAL ACTIF")
            print("Parlez maintenant ou utilisez les commandes manuelles")
        else:
            print("⌨️  CONTRÔLE MANUEL ACTIF")
        
        print("="*50)
    
    def print_voice_commands(self):
        """Affiche la liste des commandes vocales disponibles."""
        print("\n" + "="*50)
        print("        COMMANDES VOCALES DISPONIBLES")
        print("="*50)
        
        commands = self.voice_controller.list_commands()
        
        # Groupement par catégorie
        movement_commands = {}
        led_commands = {}
        system_commands = {}
        
        for voice_phrase, command_key in commands.items():
            if command_key in ["avancer", "reculer", "tourner_gauche", "tourner_droite", "arreter"]:
                movement_commands[voice_phrase] = command_key
            elif command_key.startswith("led_"):
                led_commands[voice_phrase] = command_key
            else:
                system_commands[voice_phrase] = command_key
        
        print("MOUVEMENTS:")
        for phrase, cmd in movement_commands.items():
            print(f"  • \"{phrase}\" -> {cmd}")
        
        print("\nLED:")
        for phrase, cmd in led_commands.items():
            print(f"  • \"{phrase}\" -> {cmd}")
        
        print("\nSYSTÈME:")
        for phrase, cmd in system_commands.items():
            print(f"  • \"{phrase}\" -> {cmd}")
        
        print("="*50)
    
    def print_connection_diagnostic(self):
        """Affiche le diagnostic de connexion."""
        print("\n" + "="*50)
        print("        DIAGNOSTIC DE CONNEXION")
        print("="*50)
        
        if self.controller:
            status = self.controller.get_connection_status()
            print(f"État de connexion: {'🟢 Connecté' if status['connected'] else '🔴 Déconnecté'}")
            print(f"Nœud disponible: {'✅ Oui' if status['node_available'] else '❌ Non'}")
            print(f"Client actif: {'✅ Oui' if status['client_active'] else '❌ Non'}")
            print(f"Statut du nœud: {status['node_status']}")
            
            if status['connected']:
                print("\n✅ Le robot devrait pouvoir exécuter les commandes")
            else:
                print("\n❌ Le robot ne peut pas exécuter les commandes")
                print("   Vérifiez que le robot Thymio est allumé et connecté")
        else:
            print("❌ Aucun contrôleur initialisé")
        
        print("="*50)
    
    def voice_listener(self):
        """Thread d'écoute des commandes vocales."""
        while self.voice_active:
            try:
                if self.voice_mode:
                    print("\n🎤 Parlez maintenant...")
                    command = self.voice_controller.listen_for_command()
                    
                    if command.status == VoiceCommandStatus.SUCCESS:
                        print(f"✅ Commande reconnue: '{command.text}'")
                        # Exécution de la commande de manière asynchrone
                        if command.command_key == "quitter":
                            self.running = False
                            self.voice_mode = False
                            break
                        else:
                            # Ajouter la commande à la queue pour exécution
                            self.command_queue.put(command.command_key)
                            print(f"🤖 Commande '{command.command_key}' ajoutée à la queue")
                    
                    elif command.status == VoiceCommandStatus.UNKNOWN_COMMAND:
                        print(f"❓ Commande non reconnue: '{command.text}'")
                        print("Tapez 'c' pour voir les commandes disponibles")
                    
                    elif command.status == VoiceCommandStatus.NO_SPEECH:
                        print("🔇 Aucune parole détectée")
                    
                    elif command.status == VoiceCommandStatus.TIMEOUT:
                        print("⏱️ Timeout d'écoute")
                    
                    elif command.status == VoiceCommandStatus.ERROR:
                        print("❌ Erreur de reconnaissance vocale")
                    
                    time.sleep(0.1)  # Petite pause pour éviter la surcharge
                else:
                    time.sleep(0.5)  # Pause plus longue quand le mode vocal est désactivé
                    
            except Exception as e:
                print(f"Erreur dans le thread vocal: {e}")
                time.sleep(1)
    
    def toggle_voice_mode(self):
        """Active/désactive le mode de contrôle vocal."""
        if not self.voice_controller or not self.voice_controller.is_microphone_available():
            print("❌ Contrôle vocal non disponible - microphone non détecté")
            return
            
        self.voice_mode = not self.voice_mode
        if self.voice_mode:
            print("🎤 Contrôle vocal activé")
            if not self.voice_controller.test_microphone():
                print("⚠️  Problème avec le microphone détecté")
                self.voice_mode = False
        else:
            print("⌨️  Contrôle vocal désactivé")
    
    async def process_manual_command(self, choice: str):
        """Traite les commandes manuelles."""
        command_map = {
            "1": "avancer",
            "2": "reculer", 
            "3": "tourner_gauche",
            "4": "tourner_droite",
            "5": "arreter",
            "6": "led_rouge",
            "7": "led_vert",
            "8": "led_bleu",
            "9": "led_eteindre"
        }
        
        if choice in command_map:
            await self.controller.execute_command(command_map[choice])
            return True
        return False
    
    async def process_command_queue(self):
        """Traite les commandes en attente dans la queue."""
        while self.running:
            try:
                # Vérifier s'il y a des commandes en attente (non-bloquant)
                try:
                    command = self.command_queue.get_nowait()
                    print(f"🔄 Traitement de la commande: {command}")
                    
                    # Vérification de la connexion
                    if not self.controller.connected:
                        print("❌ Robot non connecté - commande ignorée")
                        continue
                    
                    # Exécution de la commande
                    try:
                        result = await self.controller.execute_command(command)
                        if result:
                            print(f"✅ Commande '{command}' exécutée avec succès")
                        else:
                            print(f"❌ Échec de l'exécution de la commande '{command}'")
                    except Exception as e:
                        print(f"❌ Erreur lors de l'exécution de '{command}': {e}")
                        
                except queue.Empty:
                    # Pas de commande en attente, courte pause
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                print(f"❌ Erreur dans le traitement de la queue: {e}")
                await asyncio.sleep(1)
    
    async def run(self):
        """Fonction principale d'exécution."""
        # Initialisation du contrôleur Thymio
        self.controller = ThymioController()
        
        # Tentative de connexion
        print("Tentative de connexion au Thymio...")
        if not await self.controller.connect():
            print("❌ Erreur: Impossible de se connecter au Thymio")
            return
        
        print("✅ Connexion au Thymio réussie!")
        
        # Initialisation du contrôleur vocal
        try:
            print("Initialisation du contrôleur vocal...")
            self.voice_controller = VoiceController()
            
            if self.voice_controller.is_microphone_available():
                print("✅ Contrôleur vocal initialisé avec succès")
            else:
                print("⚠️  Contrôleur vocal initialisé mais microphone non disponible")
                print("   Vérifiez que votre microphone est connecté et accessible")
                
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation du contrôleur vocal: {e}")
            print("Le programme continuera sans le contrôle vocal")
            self.voice_controller = None
        
        # Démarrage du thread vocal
        if self.voice_controller and self.voice_controller.is_microphone_available():
            self.voice_active = True
            self.voice_thread = threading.Thread(target=self.voice_listener, daemon=True)
            self.voice_thread.start()
        else:
            print("⚠️  Thread vocal non démarré - microphone non disponible")
        
        # Démarrage du traitement des commandes en arrière-plan
        command_processor_task = asyncio.create_task(self.process_command_queue())
        
        # Boucle principale avec gestion des entrées non-bloquantes
        self.running = True
        try:
            await self._run_main_loop()
        finally:
            # Nettoyage
            command_processor_task.cancel()
            try:
                await command_processor_task
            except asyncio.CancelledError:
                pass
    
    async def _run_main_loop(self):
        """Boucle principale avec interface utilisateur."""
        while self.running:
            self.clear_screen()
            self.print_menu()
            
            try:
                # Utilisation d'un executor pour rendre input() non-bloquant
                choice = await asyncio.get_event_loop().run_in_executor(
                    self.executor, input, "\nVotre choix: "
                )
                choice = choice.strip().lower()
                
                if choice == "0":
                    self.running = False
                    
                elif choice == "v" and self.voice_controller:
                    self.toggle_voice_mode()
                    await asyncio.get_event_loop().run_in_executor(
                        self.executor, input, "\nAppuyez sur Entrée pour continuer..."
                    )
                    
                elif choice == "c" and self.voice_controller:
                    self.print_voice_commands()
                    await asyncio.get_event_loop().run_in_executor(
                        self.executor, input, "\nAppuyez sur Entrée pour continuer..."
                    )
                    
                elif choice == "t" and self.voice_controller:
                    print("\nTest du microphone...")
                    if self.voice_controller.test_microphone():
                        print("✅ Microphone fonctionnel")
                    else:
                        print("❌ Problème avec le microphone")
                    await asyncio.get_event_loop().run_in_executor(
                        self.executor, input, "\nAppuyez sur Entrée pour continuer..."
                    )
                    
                elif choice == "d" and self.controller:
                    self.print_connection_diagnostic()
                    await asyncio.get_event_loop().run_in_executor(
                        self.executor, input, "\nAppuyez sur Entrée pour continuer..."
                    )
                    
                elif choice == "v" and not self.voice_controller:
                    print("❌ Contrôle vocal non disponible")
                    await asyncio.get_event_loop().run_in_executor(
                        self.executor, input, "\nAppuyez sur Entrée pour continuer..."
                    )
                    
                elif not await self.process_manual_command(choice):
                    if choice not in ["c", "t", "d"] or not self.voice_controller:
                        print("❌ Choix invalide!")
                        await asyncio.get_event_loop().run_in_executor(
                            self.executor, input, "\nAppuyez sur Entrée pour continuer..."
                        )
                
            except KeyboardInterrupt:
                print("\n\nInterruption détectée...")
                self.running = False
            except Exception as e:
                print(f"❌ Erreur: {e}")
                await asyncio.get_event_loop().run_in_executor(
                    self.executor, input, "\nAppuyez sur Entrée pour continuer..."
                )
        
        # Nettoyage
        self.voice_active = False
        if self.voice_thread:
            self.voice_thread.join(timeout=2)
        
        # Fermeture de l'executor
        self.executor.shutdown(wait=False)
        
        # Déconnexion propre
        await self.controller.disconnect()
        print("👋 Déconnexion du Thymio terminée")


async def main():
    """Point d'entrée principal du programme."""
    interface = ThymioVoiceInterface()
    await interface.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Programme interrompu par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")