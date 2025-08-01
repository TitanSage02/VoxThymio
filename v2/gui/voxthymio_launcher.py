"""
VoxThymio - Splash Screen et Démarrage
Interface de démarrage moderne avec branding AI4Innov

Développé par Espérance AYIWAHOUN pour AI4Innov
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import sys
from pathlib import Path

class SplashScreen:
    """Écran de démarrage moderne pour VoxThymio."""
    
    def __init__(self):
        self.splash = tk.Tk()
        self.setup_splash()
        self.progress_var = tk.DoubleVar()
        self.setup_widgets()
    
    def setup_splash(self):
        """Configure la fenêtre de splash."""
        self.splash.title("VoxThymio")
        self.splash.geometry("500x300")
        self.splash.configure(bg="#1e1e1e")
        self.splash.resizable(False, False)
        
        # Centrer la fenêtre
        self.splash.update_idletasks()
        x = (self.splash.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.splash.winfo_screenheight() // 2) - (300 // 2)
        self.splash.geometry(f"500x300+{x}+{y}")
        
        # Supprimer la barre de titre
        self.splash.overrideredirect(True)
        
        # Toujours au premier plan
        self.splash.attributes('-topmost', True)
        
        try:
            self.splash.iconbitmap("robot.ico")
        except:
            pass
    
    def setup_widgets(self):
        """Crée les widgets du splash screen."""
        # Frame principal
        main_frame = tk.Frame(self.splash, bg="#1e1e1e")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Logo/Titre
        title_frame = tk.Frame(main_frame, bg="#1e1e1e")
        title_frame.pack(pady=(20, 10))
        
        # Emoji robot
        robot_label = tk.Label(title_frame, text="🤖", font=("Segoe UI", 48), 
                              bg="#1e1e1e", fg="#00d4aa")
        robot_label.pack()
        
        # Titre principal
        title_label = tk.Label(title_frame, text="VoxThymio", 
                              font=("Segoe UI", 24, "bold"),
                              bg="#1e1e1e", fg="#00d4aa")
        title_label.pack()
        
        # Sous-titre
        subtitle_label = tk.Label(title_frame, text="Contrôle Vocal Intelligent pour Robot Thymio", 
                                 font=("Segoe UI", 11),
                                 bg="#1e1e1e", fg="#ffffff")
        subtitle_label.pack(pady=(5, 0))
        
        # Progress bar
        progress_frame = tk.Frame(main_frame, bg="#1e1e1e")
        progress_frame.pack(pady=20, fill="x")
        
        self.progress = ttk.Progressbar(progress_frame, 
                                       variable=self.progress_var,
                                       maximum=100,
                                       length=400,
                                       mode='determinate')
        self.progress.pack()
        
        # Status label
        self.status_label = tk.Label(progress_frame, text="Initialisation...", 
                                    font=("Segoe UI", 9),
                                    bg="#1e1e1e", fg="#cccccc")
        self.status_label.pack(pady=(10, 0))
        
        # Footer avec branding
        footer_frame = tk.Frame(main_frame, bg="#1e1e1e")
        footer_frame.pack(side="bottom", pady=(20, 0))
        
        # Logo AI4Innov
        ai4_label = tk.Label(footer_frame, text="AI4Innov", 
                            font=("Segoe UI", 12, "bold"),
                            bg="#1e1e1e", fg="#00d4aa")
        ai4_label.pack()
        
        # Copyright
        copyright_label = tk.Label(footer_frame, 
                                  text="Développé par Espérance AYIWAHOUN", 
                                  font=("Segoe UI", 8),
                                  bg="#1e1e1e", fg="#888888")
        copyright_label.pack()
    
    def update_progress(self, value, status):
        """Met à jour la barre de progression."""
        self.progress_var.set(value)
        self.status_label.config(text=status)
        self.splash.update()
    
    def close(self):
        """Ferme le splash screen."""
        self.splash.destroy()


def show_splash_and_load():
    """Affiche le splash screen et charge l'application."""
    splash = SplashScreen()
    
    def load_app():
        """Charge l'application en arrière-plan."""
        steps = [
            (10, "Chargement des modules..."),
            (25, "Initialisation du contrôleur vocal..."),
            (40, "Configuration de l'interface..."),
            (60, "Préparation des connexions Thymio..."),
            (80, "Finalisation..."),
            (100, "Prêt!")
        ]
        
        for progress, status in steps:
            splash.update_progress(progress, status)
            time.sleep(0.3)  # Simulation du chargement
        
        # Fermer le splash après un court délai
        time.sleep(0.5)
        splash.close()
        
        # Importer et lancer l'application principale
        try:
            from gui.voxthymio_gui import VoxThymioGUI
            app = VoxThymioGUI()
            app.run()
        except ImportError as e:
            import tkinter.messagebox as msgbox
            msgbox.showerror("Erreur", f"Erreur d'importation: {e}")
    
    # Lancer le chargement en arrière-plan
    threading.Thread(target=load_app, daemon=True).start()
    
    # Afficher le splash
    splash.splash.mainloop()


def main():
    """Point d'entrée avec splash screen."""
    show_splash_and_load()


if __name__ == "__main__":
    main()
