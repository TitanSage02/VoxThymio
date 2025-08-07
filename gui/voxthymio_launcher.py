"""
Module de contrôle vocal pour VoxThymio.
Interface graphique complète permettant la commande vocale et textuelle.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, font, filedialog
import asyncio
import threading
from typing import Dict, Any, List
import json
import datetime
from pathlib import Path

# Ajout du répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.smart_voice_controller import SmartVoiceController
from src.speech_recognizer import SpeechRecognizer
from src.controller.thymio_controller import ThymioController

class VoxThymioLauncher:
    """
    Lanceur simplifié pour l'interface VoxThymio
    """
    
    def __init__(self):
        """Initialise le lanceur."""
        self.root = tk.Tk()
        self.root.title("VoxThymio Launcher")
        self.root.geometry("500x300")
        self.root.resizable(False, False)
        
        # Configuration de l'icône si disponible
        try:
            icon_path = Path(__file__).parent / "robot.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass
        
        # Couleurs
        bg_color = "#1A1F26"
        accent_color = "#00D7FF"
        text_color = "#FFFFFF"
        
        # Configuration du fond
        self.root.configure(bg=bg_color)
        
        # Titre
        title_label = tk.Label(
            self.root, 
            text="VoxThymio",
            font=("Segoe UI", 24, "bold"),
            fg=accent_color,
            bg=bg_color
        )
        title_label.pack(pady=(30, 10))
        
        subtitle_label = tk.Label(
            self.root, 
            text="Contrôle vocal intelligent pour Thymio",
            font=("Segoe UI", 12),
            fg=text_color,
            bg=bg_color
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Boutons
        button_frame = tk.Frame(self.root, bg=bg_color)
        button_frame.pack(fill="x", padx=50)
        
        # Style pour les boutons
        button_style = {
            "font": ("Segoe UI", 12),
            "fg": "#FFFFFF",
            "activeforeground": "#FFFFFF",
            "borderwidth": 0,
            "highlightthickness": 0,
            "padx": 20,
            "pady": 10,
            "width": 20
        }
        
        gui_button = tk.Button(
            button_frame, 
            text="Interface graphique",
            bg="#00D7FF",
            activebackground="#00B8CC",
            command=self.launch_gui,
            **button_style
        )
        gui_button.pack(pady=5)
        
        console_button = tk.Button(
            button_frame, 
            text="Mode console",
            bg="#FF6B35",
            activebackground="#E55A2B",
            command=self.launch_console,
            **button_style
        )
        console_button.pack(pady=5)
        
        # Version
        version_label = tk.Label(
            self.root, 
            text="v3.0 Dynamique - AI4Innov © 2023",
            font=("Segoe UI", 8),
            fg="#B8C5D1",
            bg=bg_color
        )
        version_label.pack(side="bottom", pady=10)
    
    def launch_gui(self):
        """Lance l'interface graphique."""
        self.root.destroy()
        
        from gui.voxthymio_gui import VoxThymioIntelligentGUI
        gui = VoxThymioIntelligentGUI()
        gui.run()
    
    def launch_console(self):
        """Lance l'interface console."""
        self.root.destroy()
        
        # Exécute le script console dans un nouveau processus
        import subprocess
        subprocess.run([sys.executable, "voxthymio_console.py"])
    
    def run(self):
        """Démarre l'application."""
        self.root.mainloop()


if __name__ == "__main__":
    launcher = VoxThymioLauncher()
    launcher.run()
