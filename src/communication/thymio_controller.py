"""
Contrôleur simplifié pour le robot Thymio
"""
from tdmclient import ClientAsync
import asyncio
import warnings
from typing import Dict, Optional, Any

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