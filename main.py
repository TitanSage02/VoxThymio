"""
Interface ultra-simple de contrôle vocal pour le robot Thymio.
Version qui fonctionne garantie !
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
    """Interface ultra-simple qui fonctionne."""
    
    def __init__(self):
        self.controller = None
        self.voice_controller = None
        self.running = False
        self.voice_mode = False
    
    def clear_screen(self):
        """Efface l'écran."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_menu(self):
        """Affiche le menu et les informations."""
        self.clear_screen()
        print("🤖 CONTRÔLE THYMIO VOCAL")
        print("=" * 30)
        print("MODE ACTUEL:", "🎤 VOCAL" if self.voice_mode else "⌨️ MANUEL")
        print("=" * 30)
        
        if self.voice_mode:
            print("🎤 MODE VOCAL ACTIF")
            print("Parlez maintenant !")
            print("Commandes: avancer, reculer, gauche, droite, stop, rouge, vert, bleu, éteindre")
            print("\nPour revenir au menu: attendez le timeout ou dites 'quitter'")
        else:
            print("⌨️ MODE MANUEL")
            print("1= Faire avancer\n2= Reculer\n3= Tourner à gauche\n4= Tourner à droite\n5= Stop")
            print("6= Allumer led rouge\n7= Allumer led verte\n8= Allumer led bleue\n9= Éteindre led")
            print("=============================")
            print("v= Passer en mode Vocal\n0= Quitter")

    async def voice_session(self):
        """Une session d'écoute vocale."""
        print("\n🎤 SESSION VOCALE DÉMARRÉE")
        print("Parlez maintenant...")
        
        while self.voice_mode:
            try:
                print(f"\n🎤 Écoute ...")
                
                command = self.voice_controller.listen_for_command()
                
                if command.status == VoiceCommandStatus.SUCCESS:
                    print(f"✅ COMMANDE RECONNUE: '{command.text}'")
                    
                    if command.command_key == "quitter":
                        print("👋 Arrêt demandé")
                        self.voice_mode = False
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
                    print("Essayez: avancer, reculer, gauche, droite, stop, rouge, vert, bleu, éteindre")
                
                elif command.status == VoiceCommandStatus.TIMEOUT:
                    print("⏱️ Timeout - pas de parole détectée")
                
                elif command.status == VoiceCommandStatus.NO_SPEECH:
                    print("🔇 Aucune parole claire détectée")
                
                else:
                    print("❌ Erreur de reconnaissance")
                
                # Petite pause entre les tentatives
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Erreur: {e}")
                await asyncio.sleep(1)

        print(f"\n Session vocale arretée")
        self.voice_mode = False
    
    async def run(self):
        """Fonction principale simplifiée."""
        print("🚀 Démarrage de VoxThymio...")
        
        # Connexion au Thymio
        self.controller = ThymioController()
        if not await self.controller.connect():
            print("❌ ERREUR: Impossible de se connecter au Thymio")
            print("Vérifiez que Thymio Suite est lancé et le robot connecté")
            input("Appuyez sur Entrée pour quitter...")
            return
        
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
                        choice = input("\n👉 Votre choix: ").strip()
                        
                        if choice == "0":
                            self.running = False
                            
                        elif choice.lower() == "v":
                            if self.voice_controller.is_microphone_available():
                                self.voice_mode = True
                                print("🎤 Mode vocal activé !")
                            else:
                                print("❌ Microphone non disponible")
                                input("Appuyez sur Entrée...")
                        
                        elif choice in "123456789":
                            commands = {
                                "1": "avancer", "2": "reculer", "3": "tourner_gauche", 
                                "4": "tourner_droite", "5": "arreter", "6": "led_rouge",
                                "7": "led_vert", "8": "led_bleu", "9": "led_eteindre"
                            }
                            cmd = commands[choice]
                            print(f"🤖 Exécution: {cmd}")
                            result = await self.controller.execute_command(cmd)
                            if result:
                                print(f"✅ '{cmd}' exécutée avec succès !")
                            else:
                                print(f"❌ Échec de '{cmd}'")
                            input("Appuyez sur Entrée...")
                        
                        else:
                            print("❌ Choix invalide")
                            input("Appuyez sur Entrée...")
                            
                    except KeyboardInterrupt:
                        self.running = False
                
        except Exception as e:
            print(f"❌ Erreur critique: {e}")
            
        finally:
            await self.controller.disconnect()
            print("👋 VoxThymio arrêté")


async def main():
    """Point d'entrée principal."""
    interface = ThymioVoiceInterface()
    await interface.run()


if __name__ == "__main__":
    print("🎤 VoxThymio - Contrôle Vocal")
    print("=======================================")

    try:
        asyncio.run(main())
    
    except KeyboardInterrupt:
        print("\n👋 Programme interrompu par l'utilisateur")
    
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        input("Appuyez sur Entrée pour quitter...")
