"""
VoxThymio V2 - Interface de contrôle vocal pour le robot Thymio.
"""

import asyncio
import os
import sys
from pathlib import Path

# Ajout du chemin racine pour les imports
sys.path.append(str(Path(__file__).parent))

from src.communication.thymio_controller import ThymioController
from src.voice_controller import VoiceController, VoiceCommandStatus


class ThymioVoiceInterface:
    """Interface de contrôle vocal pour Thymio."""
    
    def __init__(self):
        self.controller = None
        self.voice_controller = None
        self.running = False
        self.voice_mode = False
        self.available_commands = []
        self.show_command_details = False
    
    def clear_screen(self):
        """Efface l'écran."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_menu(self):
        """Affiche le menu principal et les informations."""
        self.clear_screen()
        print("🤖 VoxThymio V2 - CONTRÔLE VOCAL")
        print("=" * 40)
        print("MODE ACTUEL:", "🎤 VOCAL" if self.voice_mode else "⌨️ MANUEL")
        print("=" * 40)
        
        if self.voice_mode:
            self._show_voice_mode_menu()
        else:
            self._show_manual_mode_menu()
    
    def _show_voice_mode_menu(self):
        """Affiche le menu du mode vocal."""
        print("🎤 MODE VOCAL ACTIF")
        print("Parlez distinctement après le signal d'écoute")
        
        # Affiche un résumé des commandes vocales par catégorie
        if self.voice_controller:
            categories = self.voice_controller.get_available_commands_by_category()
            
            for category, commands in categories.items():
                if commands:
                    print(f"\n{category}:")
                    command_text = ", ".join([cmd[0] for cmd in commands[:6]])
                    if len(commands) > 6:
                        command_text += ", ..."
                    print(f"  {command_text}")
            
        print("\nPour revenir au menu: attendez le timeout ou dites 'quitter'")
    
    def _show_manual_mode_menu(self):
        """Affiche le menu du mode manuel."""
        print("⌨️ MODE MANUEL")
        
        # Options de base
        print("v = Passer en mode vocal")
        print("l = Lister toutes les commandes")
        print("0 = Quitter")
        print("-" * 40)
        
        # Si les commandes sont chargées, montrer un sous-ensemble
        if self.available_commands:
            if self.show_command_details:
                # Afficher toutes les commandes avec leur numéro
                print("COMMANDES DISPONIBLES:")
                for i, cmd in enumerate(self.available_commands):
                    print(f"{i+1:2d}. {cmd}")
            else:
                # Afficher un résumé des commandes disponibles
                print("COMMANDES PRINCIPALES:")
                categories = {
                    "Mouvement": ["avancer", "reculer", "arreter", "tourner_gauche", "tourner_droite"],
                    "LEDs": ["led_rouge", "led_vert", "led_bleu", "led_eteindre"],
                    "Sons": ["son_heureux", "son_triste", "son_silence", "volume_moyen"]
                }
                
                for category, cmds in categories.items():
                    print(f"{category}:")
                    for cmd in cmds:
                        if cmd in self.available_commands:
                            idx = self.available_commands.index(cmd) + 1
                            print(f"  {idx:2d}. {cmd}")
                
                print("\nTapez 'l' pour voir toutes les commandes")
    
    async def voice_session(self):
        """Une session d'écoute vocale."""
        print("\n🎤 SESSION VOCALE DÉMARRÉE")
        print("Parlez maintenant...")
        
        while self.voice_mode and self.running:
            try:
                print(f"\n🎤 Écoute en cours...")
                
                command = self.voice_controller.listen_for_command()
                
                if command.status == VoiceCommandStatus.SUCCESS:
                    print(f"✅ COMMANDE RECONNUE: '{command.text}'")
                    
                    if command.command_key == "quitter":
                        print("👋 Retour au menu principal")
                        self.voice_mode = False
                        await asyncio.sleep(1)
                        break
                    
                    if self.controller.is_connected():
                        print(f"🤖 Exécution de: {command.command_key}")
                        result = await self.controller.execute_command(command.command_key)
                        if result:
                            print(f"✅ '{command.command_key}' RÉUSSIE !")
                        else:
                            print(f"❌ Échec de '{command.command_key}'")
                    else:
                        print("❌ Robot non connecté")
                
                elif command.status == VoiceCommandStatus.UNKNOWN_COMMAND:
                    print(f"❓ Commande inconnue: '{command.text}'")
                    print("Essayez une commande comme: avancer, reculer, arrêter, tourner...")
                
                elif command.status == VoiceCommandStatus.TIMEOUT:
                    print("⏱️ Timeout - pas de parole détectée")
                    
                    # Option pour revenir au menu après plusieurs timeouts
                    choice = input("Revenir au menu principal? (o/n): ").lower()
                    if choice == 'o' or choice == 'oui':
                        self.voice_mode = False
                        break
                
                elif command.status == VoiceCommandStatus.NO_SPEECH:
                    print("🔇 Aucune parole claire détectée")
                
                else:
                    print("❌ Erreur de reconnaissance")
                
                # Petite pause entre les tentatives
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Erreur: {e}")
                await asyncio.sleep(1)

        print(f"\nSession vocale arrêtée")
        self.voice_mode = False
        await asyncio.sleep(1)
    
    async def run(self):
        """Fonction principale."""
        print("🚀 Démarrage de VoxThymio V2...")
        
        # Connexion au Thymio
        self.controller = ThymioController()
        if not await self.controller.connect():
            print("❌ ERREUR: Impossible de se connecter au Thymio")
            print("Vérifiez que Thymio Suite est lancé et le robot connecté")
            input("Appuyez sur Entrée pour quitter...")
            return
        
        # Récupération des commandes disponibles
        self.available_commands = self.controller.get_available_commands()
        print(f"✅ {len(self.available_commands)} commandes disponibles")
        
        # Initialisation du contrôleur vocal
        self.voice_controller = VoiceController()
        if not self.voice_controller.is_microphone_available():
            print("⚠️ ATTENTION: Microphone non disponible")
            print("Seul le mode manuel sera possible")
        
        print("✅ Système prêt !")
        
        # Boucle principale
        self.running = True
        
        try:
            while self.running:
                self.show_menu()
                
                if self.voice_mode:
                    # Mode vocal: faire une session d'écoute
                    await self.voice_session()
                else:
                    # Mode manuel: attendre une commande clavier
                    try:
                        choice = input("\n👉 Votre choix: ").strip().lower()
                        
                        if choice == "0":
                            self.running = False
                            
                        elif choice == "v":
                            if self.voice_controller.is_microphone_available():
                                self.voice_mode = True
                                print("🎤 Mode vocal activé !")
                                await asyncio.sleep(0.5)
                            else:
                                print("❌ Microphone non disponible")
                                input("Appuyez sur Entrée...")
                        
                        elif choice == "l":
                            # Bascule l'affichage des détails
                            self.show_command_details = not self.show_command_details
                        
                        elif choice.isdigit():
                            # Exécuter une commande par son numéro
                            cmd_idx = int(choice) - 1
                            if 0 <= cmd_idx < len(self.available_commands):
                                cmd = self.available_commands[cmd_idx]
                                print(f"🤖 Exécution: {cmd}")
                                result = await self.controller.execute_command(cmd)
                                if result:
                                    print(f"✅ '{cmd}' exécutée avec succès !")
                                else:
                                    print(f"❌ Échec de '{cmd}'")
                                input("Appuyez sur Entrée pour continuer...")
                            else:
                                print(f"❌ Choix invalide: {choice}")
                                input("Appuyez sur Entrée...")
                        
                        else:
                            print(f"❌ Choix invalide: {choice}")
                            input("Appuyez sur Entrée...")
                            
                    except KeyboardInterrupt:
                        self.running = False
                
        except Exception as e:
            print(f"❌ Erreur critique: {e}")
            
        finally:
            await self.controller.disconnect()
            print("👋 VoxThymio V2 arrêté")


async def main():
    """Point d'entrée principal."""
    interface = ThymioVoiceInterface()
    await interface.run()


if __name__ == "__main__":
    print("🎤 VoxThymio V2 - Contrôle Vocal Avancé")
    print("=========================================")

    try:
        asyncio.run(main())
    
    except KeyboardInterrupt:
        print("\n👋 Programme interrompu par l'utilisateur")
    
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        input("Appuyez sur Entrée pour quitter...")
