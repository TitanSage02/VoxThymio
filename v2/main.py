"""
VoxThymio - Interface de contrôle pour le robot Thymio.
Supporte deux modes de contrôle : clavier (manuel) et vocal (avec IA).

Développé par Espérance AYIWAHOUN pour AI4Innov
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
    """Interface unifiée de contrôle pour Thymio avec support vocal et clavier."""
    
    def __init__(self):
        """Initialise l'interface de contrôle."""
        self.controller = None          # Contrôleur de communication avec Thymio
        self.voice_controller = None    # Contrôleur de commandes vocales
        self.running = False            # État de l'application
        self.voice_mode = False         # Mode de contrôle actif (vocal ou clavier)
        self.available_commands = []    # Liste des commandes disponibles
        self.show_command_details = False  # Affichage détaillé des commandes
    
    def clear_screen(self):
        """Efface l'écran du terminal."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_menu(self):
        """Affiche le menu principal adapté au mode actuel."""
        self.clear_screen()
        print("🤖 VoxThymio - CONTRÔLE INTELLIGENT")
        print("=" * 50)
        print("MODE ACTUEL:", "🎤 VOCAL (IA)" if self.voice_mode else "⌨️ MANUEL (Clavier)")
        print("=" * 50)
        
        # Affiche le menu approprié selon le mode actif
        if self.voice_mode:
            self._show_voice_mode_menu()
        else:
            self._show_manual_mode_menu()
    
    def _show_voice_mode_menu(self):
        """Affiche le menu spécifique au mode vocal."""
        print("\n🎤 MODE VOCAL ACTIF")
        print("Pipeline: Audio → Transcription → Classification BERT → Commande")
        print("Parlez distinctement après le signal d'écoute\n")
        
        # Affiche un résumé des commandes vocales par catégorie
        if self.voice_controller:
            categories = self.voice_controller.get_available_commands_by_category()
            
            for category, commands in categories.items():
                if commands:
                    print(f"\n{category}:")
                    command_text = ", ".join([cmd for cmd in commands[:6]])
                    if len(commands) > 6:
                        command_text += ", ..."
                    print(f"  {command_text}")
            
        print("\nPour revenir au menu: attendez le timeout ou dites 'quitter'")
    
    def _show_manual_mode_menu(self):
        """Affiche le menu spécifique au mode manuel (clavier)."""
        print("\n⌨️ MODE MANUEL (CLAVIER)")
        
        # Options de base
        print("\nCONTRÔLES:")
        print("v = Passer en mode vocal (IA)")
        print("l = Lister toutes les commandes")
        print("0 = Quitter")
        print("-" * 50)
        
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
        """Exécute une session d'écoute vocale complète.
        
        Pipeline complet:
        1. Capture audio via microphone
        2. Transcription via Google Speech Recognition
        3. Classification d'intention via modèle BERT
        4. Exécution de la commande sur Thymio
        """
        print("\n🎤 SESSION VOCALE DÉMARRÉE")
        print("Parlez maintenant...")
        
        while self.voice_mode and self.running:
            try:
                print(f"\n🎤 Écoute en cours...")
                
                # 1-3. Capture audio, transcription et classification (via voice_controller)
                command = self.voice_controller.listen_for_command()
                
                # 4. Traitement du résultat et exécution sur Thymio
                if command.status == VoiceCommandStatus.SUCCESS:
                    print(f"🤖 INTENTION DÉTECTÉE: '{command.command_key}'")
                    
                    if command.command_key == "quitter":
                        print("👋 Retour au menu principal")
                        self.voice_mode = False
                        await asyncio.sleep(1)
                        break
                    
                    if self.controller.is_connected():
                        print(f"🔄 Exécution de la commande: {command.command_key}")
                        result = await self.controller.execute_command(command.command_key)
                        # if result:
                        #     print(f"✅ '{command.command_key}' exécutée avec succès!")
                        # else:
                        #     print(f"❌ Échec de '{command.command_key}'")
                    else:
                        print("❌ Robot non connecté")
                
                elif command.status == VoiceCommandStatus.UNKNOWN_COMMAND:
                    print(f"❓ Intention non reconnue: '{command.text}'")
                    print("💡 Essayez une commande comme: avancer, reculer, arrêter, tourner...")
                
                elif command.status == VoiceCommandStatus.TIMEOUT:
                    print("⏱️ Timeout - pas de parole détectée")
                    
                    # Option pour revenir au menu après timeout
                    choice = input("Revenir au menu principal? (o/n): ").lower()
                    if choice in ['o', 'oui']:
                        self.voice_mode = False
                        break
                
                elif command.status == VoiceCommandStatus.NO_SPEECH:
                    print("🔇 Aucune parole claire détectée")
                
                else:
                    print("❌ Erreur de reconnaissance vocale")
                
                # Petite pause entre les tentatives
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Erreur: {e}")
                await asyncio.sleep(1)

        print(f"\nSession vocale terminée")
        self.voice_mode = False
        await asyncio.sleep(1)
    
    async def run(self):
        """Fonction principale de l'application."""
        print("🚀 Démarrage de VoxThymio V2...")
        
        # Étape 1: Connexion au Thymio
        print("\n⏳ Connexion au robot Thymio...")
        self.controller = ThymioController()
        if not await self.controller.connect():
            print("❌ ERREUR: Impossible de se connecter au Thymio")
            print("⚠️ Vérifiez que Thymio Suite est lancé et qu'un robot est connecté")
            input("Appuyez sur Entrée pour quitter...")
            return
        
        # Étape 2: Chargement des commandes disponibles
        self.available_commands = self.controller.get_available_commands()
        print(f"✅ {len(self.available_commands)} commandes disponibles")
        
        # Étape 3: Initialisation du contrôleur vocal
        print("\n⏳ Initialisation du moteur vocal et IA...")
        self.voice_controller = VoiceController(intent_model_path="./models")
        
        if not self.voice_controller.is_microphone_available():
            print("⚠️ ATTENTION: Microphone non disponible")
            print("⚠️ Seul le mode manuel (clavier) sera possible")
        else:
            print("✅ Microphone et modèle d'IA prêts")
        
        print("\n✅ Système prêt ! Démarrage de l'interface...")
        
        # Boucle principale
        self.running = True
        
        try:
            while self.running:
                self.show_menu()
                
                if self.voice_mode:
                    # Mode vocal: exécuter une session d'écoute
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
                                input("Appuyez sur Entrée pour continuer...")
                        
                        elif choice == "l":
                            # Bascule l'affichage détaillé des commandes
                            self.show_command_details = not self.show_command_details
                        
                        elif choice.isdigit():
                            # Exécuter une commande par son numéro
                            cmd_idx = int(choice) - 1
                            if 0 <= cmd_idx < len(self.available_commands):
                                cmd = self.available_commands[cmd_idx]
                                print(f"🤖 Exécution: {cmd}")
                                result = await self.controller.execute_command(cmd)
                                # if result:
                                #     print(f"✅ '{cmd}' exécutée avec succès !")
                                # else:
                                #     print(f"❌ Échec de '{cmd}'")
                                input("Appuyez sur Entrée pour continuer...")
                            else:
                                print(f"❌ Choix invalide: {choice}")
                                input("Appuyez sur Entrée pour continuer...")
                        
                        else:
                            print(f"❌ Choix invalide: {choice}")
                            input("Appuyez sur Entrée pour continuer...")
                            
                    except KeyboardInterrupt:
                        self.running = False
                
        except Exception as e:
            print(f"❌ Erreur critique: {e}")
            
        finally:
            # Nettoyage et déconnexion
            print("\n⏳ Fermeture de l'application...")
            await self.controller.disconnect()
            print("👋 VoxThymio V2 arrêté")


async def main():
    """Point d'entrée principal de l'application."""
    interface = ThymioVoiceInterface()
    await interface.run()


if __name__ == "__main__":
    print("🎤 VoxThymio - Contrôle intelligent du robot Thymio")
    print("=" * 50)
    print("Développé par AI4Innov")
    print("=" * 50)

    try:
        asyncio.run(main())
    
    except KeyboardInterrupt:
        print("\n👋 Programme interrompu par l'utilisateur")
    
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        input("Appuyez sur Entrée pour quitter...")
