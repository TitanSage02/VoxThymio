"""
Contrôleur simplifié pour le robot Thymio
"""
from tdmclient import ClientAsync
import asyncio
import warnings
from typing import Dict, Optional, Any
import os 

class ThymioController:
    """Contrôleur simplifié pour le robot Thymio."""
    
    def __init__(self):
        """Initialise le contrôleur Thymio."""
        self.client = ClientAsync()
        self.node = None
        self.connected = False

        # Commandes disponibles
        self.commands: Dict[str, str] = { 
            "avancer": "motor.left.target = 200\nmotor.right.target = 200",
            "reculer": "motor.left.target = -200\nmotor.right.target = -200",
            "arreter": "motor.left.target = 0\nmotor.right.target = 0",
            "tourner_gauche": "motor.left.target = -100\nmotor.right.target = 100",
            "tourner_droite": "motor.left.target = 100\nmotor.right.target = -100",
            "led_rouge": "call leds.top(32,0,0)",
            "led_vert": "call leds.top(0,32,0)",
            "led_bleu": "call leds.top(0,0,32)",
            "led_eteindre": "call leds.top(0,0,0)"
        }

    async def connect(self):
        """Établit une connexion avec un robot Thymio."""
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                await self.client.wait_for_status(self.client.NODE_STATUS_AVAILABLE)
                self.node = self.client.first_node()
                
                if self.node:
                    await self.node.lock_node()
                    await self.client.wait_for_status(self.client.NODE_STATUS_READY)
                    self.connected = True
                    print(f"✅ Connecté au Thymio (ID: {self.node.id_str})")
                    return True
                else:
                    print("❌ Aucun robot Thymio détecté")
                    return False
        
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            self.connected = False
            return False
        
    async def execute_command(self, command: str):
        """Exécute une commande sur le robot Thymio."""
        if not self.connected or not self.node:
            print("❌ Robot non connecté")
            return False
        
        if command not in self.commands:
            print(f"❌ Commande inconnue: {command}")
            return False
            
        try:
            await self.node.compile(self.commands[command])
            await self.node.run()
            print(f"✅ Commande '{command}' exécutée")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'exécution de '{command}': {e}")
            return False

    async def disconnect(self):
        """Déconnecte le robot Thymio."""
        if self.connected:
            try:
                await self.execute_command("arreter")
                await self.execute_command("led_eteindre")
                self.client.close()
                self.connected = False
                print("👋 Thymio déconnecté")
            except:
                pass
                
    def is_connected(self) -> bool:
        """Vérifie si le robot est connecté."""
        return self.connected and self.node is not None
    
if __name__ == "__main__":
    """Point d'entrée pour tester le contrôleur."""
    async def main():
        controller = ThymioController()
        if await controller.connect():
            while True:
                try : 
                    print("Commandes disponibles:")
                    print("1. avancer\n2. reculer\n3. tourner_gauche\n4. tourner_droite\n5. arreter\n6. led_rouge\n7. led_vert\n8. led_bleu\n9. led_eteindre")
                    command = input("Entrez une commande (1-9): ")
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
                    if command in command_map:
                        await controller.execute_command(command_map[command])
                        os.system("clear")
                    else:
                        print("❌ Commande invalide")
                except KeyboardInterrupt:
                    print("\n👋 Déconnexion...")
                    break
                finally:
                    if not controller.is_connected():
                        print("❌ Déconnexion du robot Thymio")
                        break

    asyncio.run(main())