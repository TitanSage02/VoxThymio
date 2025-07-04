"""
Contrôleur pour le robot Thymio

Ce module fournit une interface de haut niveau pour contrôler les robots Thymio
via la librairie tdmclient. Il permet d'établir une connexion au robot,
d'exécuter diverses commandes de mouvement et de contrôle des LEDs, 
et de gérer proprement la déconnexion.
"""
from tdmclient import ClientAsync, Node
import asyncio
import warnings
import time
from typing import Dict, Callable, Optional, Any

class ThymioController:
    """
    Classe pour contrôler le robot Thymio
    
    Cette classe gère l'interface avec le robot Thymio en utilisant l'API tdmclient.
    Elle permet d'exécuter des commandes simples comme avancer, reculer, tourner,
    et contrôler les LEDs du robot.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialise le contrôleur Thymio
        
        Args:
            config: Configuration du contrôleur (debug, motor_speed, led_intensity)
        """
        self.config = config or {}
        self.client = ClientAsync(debug=self.config.get('debug', False))
        self.node = None
        self.motor_speed = self.config.get('motor_speed', 200)
        self.led_intensity = self.config.get('led_intensity', 32)
        self.debug = self.config.get('debug', False)
        self.connected = False

        # Commandes disponibles
        self.commands: Dict[str, str] = { 
            # Commandes de mouvement
            "avancer": "motor.left.target = 200\nmotor.right.target = 200",
                        
            "reculer": "motor.left.target = -200\nmotor.right.target = -200",

            "arreter": "motor.left.target = 0\nmotor.right.target = 0",

            "tourner_gauche": "motor.left.target = -100\nmotor.right.target = 100",

            "tourner_droite": "motor.left.target = 100\nmotor.right.target = -100",

            # Commandes de contrôle des LEDs en haut
            "led_rouge": "call leds.top(32,0,0)",
            
            "led_vert": "call leds.top(0,32,0)",
            
            "led_bleu": "call leds.top(0,0,32)",    
            
            "led_eteindre": "call leds.top(0,0,0)",

            "pass": ""
        }

    async def connect(self):
        """
        Établit une connexion avec un robot Thymio
        
        Returns:
            bool: True si la connexion a réussi, False sinon
        """
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                print("Recherche d'un robot Thymio...")
                await self.client.wait_for_status(self.client.NODE_STATUS_AVAILABLE)
                self.node = self.client.first_node()
                
                if self.node:
                    await self.node.lock_node()
                    await self.client.wait_for_status(self.client.NODE_STATUS_READY)
                    
                    self.connected = True
                    print(f"Connecté au robot Thymio (ID: {self.node.id_str})")
                    
                    return True
                else:
                    print("Aucun robot Thymio détecté")
                    return False
        
        except Exception as e:
            print(f"Erreur lors de la connexion: {e}")
            if self.client:
                self.client.close()
                self.client = None
            self.node = None
            self.connected = False
            return False
        
    async def execute_command(self, command: str):
        """
        Exécute une commande sur le robot Thymio
        
        Args:
            command (str): Nom de la commande à exécuter
            
        Returns:
            bool: True si la commande a été exécutée avec succès, False sinon
        """
        if not self.connected or not self.node:
            print("❌ Robot non connecté - impossible d'exécuter la commande")
            return False
        
        if command in self.commands:
            if command == "pass":
                for _ in range(3):
                    asyncio.run(self.execute_command("led_rouge"))
                    time.sleep(2)
                    asyncio.run(self.execute_command("led_eteindre"))
                    time.sleep(2)
                return True
            
            try:
                print(f"Compilation de la commande '{command}'...")
                print(f"Code Thymio: {repr(self.commands[command])}")
                
                error = await self.node.compile(self.commands[command])
                if error is not None:
                    print(f"❌ Erreur de compilation pour '{command}': {error}")
                    return False
                
                print(f"▶️ Exécution de la commande '{command}'...")
                error = await self.node.run()
                if error is not None:
                    print(f"❌ Erreur d'exécution pour '{command}': {error}")
                    return False
                
                print(f"✅ Commande '{command}' exécutée avec succès")
                return True
            
            except Exception as e:
                print(f"❌ Exception lors de l'exécution de '{command}': {e}")
                return False
        else:
            print(f"❌ Commande inconnue: '{command}'")
            print(f"   Commandes disponibles: {list(self.commands.keys())}")
            return False

    async def disconnect(self):
        """
        Déconnecte le robot Thymio
        """
        if self.connected and self.node:
            try:
                await self.execute_command("arreter")
                await self.execute_command("led_eteindre")
                self.client.close()
                self.connected = False
                self.node = None
                self.client = None
                print("Déconnecté du robot Thymio")
            except Exception as e:
                print(f"Erreur lors de la déconnexion: {e}")
                self.connected = False
                self.node = None
                self.client = None
    
    def __del__(self):
        """
        Destructeur de classe - assure la déconnexion propre
        """
        if self.connected and self.client:
            loop = asyncio.get_event_loop_policy().get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.disconnect())
            else:
                asyncio.run(self.disconnect())
                
    def get_connection_status(self) -> dict:
        """
        Retourne l'état de la connexion avec des détails.
        
        Returns:
            dict: Informations sur l'état de la connexion
        """
        return {
            "connected": self.connected,
            "node_available": self.node is not None,
            "client_active": self.client is not None,
            "node_status": getattr(self.node, 'status', 'N/A') if self.node else 'N/A'
        }