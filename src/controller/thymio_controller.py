"""
Contrôleur pour le robot Thymio - Version 2
Support amélioré pour les commandes définies dans commands.json
"""
from tdmclient import ClientAsync
from typing import Dict, List
import warnings
import asyncio

class ThymioController:
    """Contrôleur pour le robot Thymio avec support pour les commandes JSON."""
    
    def __init__(self):
        """Initialise le contrôleur Thymio."""
        self.client = ClientAsync()
        self.node = None
        self.connected = False
        self.commands = self._load_default_commands()

    def _load_default_commands(self) -> Dict[str, str]:
        """Charge les commandes depuis le fichier JSON."""
       
        # Commandes supportées par défaut
        return { 
            "avancer": "motor.left.target = 200\nmotor.right.target = 200",
            "reculer": "motor.left.target = -200\nmotor.right.target = -200",
            "arreter": "motor.left.target = 0\nmotor.right.target = 0",
            "tourner_gauche": "motor.left.target = -100\nmotor.right.target = 100",
            "tourner_droite": "motor.left.target = 100\nmotor.right.target = -100"
        }

    async def connect(self) -> bool:
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
        
    async def execute_command(self, command: str) -> bool:
        """Exécute une commande sur le robot Thymio."""
        if not self.connected or not self.node:
            print("❌ Robot non connecté")
            return False
        
        if command not in self.commands:
            print(f"❌ Commande inconnue: {command}")
            return False
            
        try:
            # Récupère le code Aseba associé à la commande
            aseba_code = self.commands[command]
            
            # Exécute le code
            await self.node.compile(aseba_code)
            await self.node.run()
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'exécution de '{command}': {e}")
            return False

    async def execute_code(self, code: str) -> bool:
        """Exécute directement du code Aseba sur le robot."""
        if not self.connected or not self.node:
            print("❌ Robot non connecté")
            return False
            
        try:
            await self.node.compile(code)
            await self.node.run()
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'exécution du code: {e}")
            return False

    async def disconnect(self) -> None:
        """Déconnecte le robot Thymio."""
        if self.connected:
            try:
                # Arrête le robot et éteint les LEDs
                await self.execute_command("arreter")
                
                # Ferme la connexion
                self.client.close()
                self.connected = False
                
                print("👋 Thymio déconnecté")
            except Exception as e:
                print(f"❌ Erreur lors de la déconnexion: {e}")
                
    def is_connected(self) -> bool:
        """Vérifie si le robot est connecté."""
        return self.connected and self.node is not None
    
    def get_available_commands(self) -> List[str]:
        """Retourne la liste des commandes disponibles."""
        return list(self.commands.keys())
    
            
if __name__ == "__main__":
    """Point d'entrée pour tester le contrôleur."""
    async def main():
        controller = ThymioController()
        
        # Affiche les commandes disponibles
        commands = controller.get_available_commands()
        print(f"Commandes disponibles ({len(commands)}):")
        for i, cmd in enumerate(commands):
            if i > 0 and i % 5 == 0:
                print()  # Nouvelle ligne tous les 5 éléments
            print(f"{i+1}. {cmd}", end="\t")
        print("\n")
        
        # Connecte au robot
        if await controller.connect():
            print("\nRobot connecté!")
            try:
                while True:
                    try:
                        # Menu simple pour tester
                        cmd_idx = input("\nEntrez le numéro de la commande (0 pour quitter): ")
                        
                        if cmd_idx == "0":
                            break
                            
                        try:
                            idx = int(cmd_idx) - 1
                            if 0 <= idx < len(commands):
                                cmd = commands[idx]
                                print(f"Exécution de: {cmd}")
                                await controller.execute_command(cmd)
                            else:
                                print("❌ Numéro de commande invalide")
                        except ValueError:
                            print("❌ Veuillez entrer un nombre valide")
                            
                    except KeyboardInterrupt:
                        print("\n Interruption...")
                        break
                        
            finally:
                print("\nDéconnexion du robot...")
                await controller.disconnect()
    
    asyncio.run(main())
