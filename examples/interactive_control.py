import asyncio
import os
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from src.communication.thymio_controller import ThymioController

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu():
    print("\n=== Contrôle Thymio ===")
    print("1. Avancer")
    print("2. Reculer")
    print("3. Tourner à gauche")
    print("4. Tourner à droite")
    print("5. Arrêter")
    print("6. LED Rouge")
    print("7. LED Vert")
    print("8. LED Bleu")
    print("9. Éteindre LED")
    print("0. Quitter")
    print("=====================")

async def main():
    # Initialisation du contrôleur
    controller = ThymioController()
    
    # Tentative de connexion
    print("Tentative de connexion au Thymio...")
    if not await controller.connect():
        print("Erreur: Impossible de se connecter au Thymio")
        return
        
    print("Connexion réussie!")
    
    running = True
    while running:
        clear_screen()
        print_menu()
        
        choice = input("\nVotre choix: ")
        
        if choice == "1":
            await controller.execute_command("avancer")
        elif choice == "2":
            await controller.execute_command("reculer")
        elif choice == "3":
            await controller.execute_command("tourner_gauche")
        elif choice == "4":
            await controller.execute_command("tourner_droite")
        elif choice == "5":
            await controller.execute_command("arreter")
        elif choice == "6":
            await controller.execute_command("led_rouge")
        elif choice == "7":
            await controller.execute_command("led_vert")
        elif choice == "8":
            await controller.execute_command("led_bleu")
        elif choice == "9":
            await controller.execute_command("led_eteindre")
        elif choice == "0":
            running = False
        else:
            print("Choix invalide!")
            
        # if choice != "0":
        #     input("\nAppuyez sur Entrée pour continuer...")
    
    # Déconnexion propre
    await controller.disconnect()
    print("Déconnexion du Thymio...")

if __name__ == "__main__":
    asyncio.run(main()) 