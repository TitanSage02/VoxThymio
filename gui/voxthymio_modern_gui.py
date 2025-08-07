"""
VoxThymio - Interface Graphique 
Contrôle vocal pour robot Thymio

Développé par Espérance AYIWAHOUN dans le 
cadre du projet TechEduc porté par AI4Innov 
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import asyncio
import threading
import json
import sys
from pathlib import Path
import time
from datetime import datetime

# Ajout du chemin racine
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

try:
    from src.controller.thymio_controller import ThymioController
    from src.smart_voice_controller import SmartVoiceController
    from src.speech_recognizer import SpeechRecognizer
except ImportError as e:
    print(f"❌ Erreur d'importation: {e}")
    print("Vérifiez que les modules src/ sont présents")
    raise

# Chemins des modèles et configuration
CONFIG_PATH = Path(__file__).parent / "config.json"
MODELS_PATH = Path(__file__).parent.parent / "models"

class VoxThymioGUI:
    """Interface graphique moderne pour VoxThymio."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.thymio_controller = None
        self.voice_controller = None
        self.voice_mode = False
        self.voice_thread = None
        self.voice_active = False
        
        # Charger la configuration
        self.load_config()
        
        self.setup_window()
        self.create_widgets()
        self.setup_async()
    
    def load_config(self):
        """Charge la configuration depuis le fichier JSON."""
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                external_config = json.load(f)
                # Merge avec la config par défaut pour s'assurer que toutes les clés existent
                default_config = self.get_default_config()
                
                # Utiliser les couleurs du fichier externe si elles existent, sinon utiliser les par défaut
                if 'ui' in external_config and 'colors' in external_config['ui']:
                    external_colors = external_config['ui']['colors']
                    # Mapper les couleurs du fichier externe vers notre structure
                    default_config['ui']['colors'].update({
                        'primary': external_colors.get('primary', '#00ff41'),
                        'secondary': external_colors.get('secondary', '#0d1117'),
                        'background': external_colors.get('background', '#010409'),
                        'panel': external_colors.get('card', '#161b22'),
                        'text_primary': external_colors.get('text_light', '#00ff41'),
                        'text_secondary': external_colors.get('text_light', '#00ff41'),
                        'text_normal': external_colors.get('text_dark', '#c9d1d9'),
                        'accent': external_colors.get('accent', '#00d4ff'),
                        'success': external_colors.get('success', '#39ff14'),
                        'warning': external_colors.get('warning', '#ffaa00'),
                        'danger': external_colors.get('danger', '#ff073a')
                    })
                
                self.config = default_config
                
        except FileNotFoundError:
            print("⚠️ Fichier config.json non trouvé, utilisation des valeurs par défaut")
            self.config = self.get_default_config()
        except json.JSONDecodeError as e:
            print(f"⚠️ Erreur dans config.json: {e}, utilisation des valeurs par défaut")
            self.config = self.get_default_config()
    
    def get_default_config(self):
        """Retourne la configuration par défaut avec style cyberpunk."""
        return {
            "application": {
                "name": "VoxThymio",
                "version": "1.0",
                "developer": "Espérance AYIWAHOUN",
                "organization": "AI4Innov - TechEduc"
            },
            "ui": {
                "colors": {
                    "primary": "#00ff41",
                    "secondary": "#ff0080", 
                    "background": "#0d1117",
                    "panel": "#161b22",
                    "text_primary": "#00ff41",
                    "text_secondary": "#ff0080",
                    "text_normal": "#c9d1d9",
                    "accent": "#00d4ff",
                    "success": "#39ff14",
                    "warning": "#ffaa00", 
                    "danger": "#ff073a"
                },
                "window": {
                    "width": 1200,
                    "height": 700,
                    "min_width": 1000,
                    "min_height": 600
                }
            },
            "voice": {
                "execution_threshold": 0.5,
                "learning_threshold": 0.85
            }
        }
    
    def setup_window(self):
        """Configure la fenêtre principale avec style cyberpunk."""
        config = self.config
        app_config = config['application']
        ui_config = config['ui']
        colors = ui_config['colors']
        window_config = ui_config['window']
        
        self.root.title(f"{app_config['name']} - Contrôle Vocal Intelligent")
        self.root.geometry(f"{window_config['width']}x{window_config['height']}")
        self.root.minsize(window_config['min_width'], window_config['min_height'])
        self.root.configure(bg=colors['background'])
        self.root.resizable(True, True)
        
        # Style cyberpunk avancé
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configuration des styles avec thème cyberpunk
        style.configure('Cyber.Title.TLabel', 
                       background=colors['background'], 
                       foreground=colors['primary'], 
                       font=("Orbitron", 24, "bold"),
                       relief="flat")
        
        style.configure('Cyber.Header.TLabel', 
                       background=colors['background'], 
                       foreground=colors['text_normal'], 
                       font=("Orbitron", 14, "bold"))
        
        style.configure('Cyber.Status.TLabel', 
                       background=colors['background'], 
                       foreground=colors['accent'], 
                       font=("Consolas", 10))
        
        style.configure('Cyber.Info.TLabel', 
                       background=colors['background'], 
                       foreground=colors['text_secondary'], 
                       font=("Consolas", 9))
        
        # Boutons avec effet cyberpunk
        style.configure('Cyber.Primary.TButton', 
                       background=colors['primary'], 
                       foreground=colors['background'], 
                       font=("Orbitron", 10, "bold"),
                       relief="flat",
                       borderwidth=0,
                       focuscolor="none")
        
        style.map('Cyber.Primary.TButton',
                 background=[('active', '#00cc66'), ('pressed', '#009944')])
        
        style.configure('Cyber.Secondary.TButton', 
                       background=colors['secondary'], 
                       foreground=colors['background'], 
                       font=("Orbitron", 10, "bold"),
                       relief="flat",
                       borderwidth=0,
                       focuscolor="none")
                       
        style.map('Cyber.Secondary.TButton',
                 background=[('active', '#cc0066'), ('pressed', '#990044')])
        
        style.configure('Cyber.Connect.TButton', 
                       background=colors['accent'], 
                       foreground=colors['background'], 
                       font=("Orbitron", 10, "bold"),
                       relief="flat",
                       borderwidth=0,
                       focuscolor="none")
                       
        style.map('Cyber.Connect.TButton',
                 background=[('active', '#e6c200'), ('pressed', '#ccaa00')])
        
        style.configure('Cyber.Disabled.TButton', 
                       background="#2d3748", 
                       foreground="#718096", 
                       font=("Orbitron", 10),
                       relief="flat",
                       borderwidth=0)
        
        # Styles pour les commandes personnalisées
        style.configure('Cyber.Accent.TButton', 
                       background=colors['accent'], 
                       foreground=colors['background'], 
                       font=("Orbitron", 11, "bold"),
                       relief="flat",
                       borderwidth=0,
                       focuscolor="none")
                       
        style.map('Cyber.Accent.TButton',
                 background=[('active', colors['warning']), ('pressed', colors['success'])])
        
        style.configure('Cyber.Custom.TButton', 
                       background=colors['panel'], 
                       foreground=colors['accent'], 
                       font=("Consolas", 10, "bold"),
                       relief="solid",
                       borderwidth=1,
                       focuscolor="none")
                       
        style.map('Cyber.Custom.TButton',
                 background=[('active', colors['accent']), ('pressed', colors['primary'])],
                 foreground=[('active', colors['background']), ('pressed', colors['background'])])
        
        style.configure('Cyber.Danger.TButton', 
                       background=colors['danger'], 
                       foreground="white", 
                       font=("Orbitron", 9, "bold"),
                       relief="flat",
                       borderwidth=0,
                       focuscolor="none")
                       
        style.map('Cyber.Danger.TButton',
                 background=[('active', '#ff6b7a'), ('pressed', '#e63946')])
        
        # Style pour la barre de progression cyberpunk
        style.configure('Cyber.Horizontal.TProgressbar',
                       background=colors['primary'],
                       troughcolor=colors['panel'],
                       borderwidth=0,
                       lightcolor=colors['primary'],
                       darkcolor=colors['primary'])
        
        # Icône
        try:
            icon_path = Path(__file__).parent / "robot.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass
    
    def create_widgets(self):
        """Crée tous les widgets de l'interface."""
        colors = self.config['ui']['colors']
        
        # Frame principal avec style cyberpunk
        main_frame = tk.Frame(self.root, bg=colors['background'])
        main_frame.pack(fill="both", expand=True, padx=10, pady=8)
        
        # En-tête cyberpunk
        self.create_header(main_frame)
        
        # Colonnes principales avec séparateur lumineux
        content_frame = tk.Frame(main_frame, bg=colors['background'])
        content_frame.pack(fill="both", expand=True, pady=(8, 0))
        
        left_frame = tk.Frame(content_frame, bg=colors['background'])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 6))
        
        # Séparateur vertical cyberpunk
        separator_frame = tk.Frame(content_frame, bg=colors['primary'], width=2)
        separator_frame.pack(side="left", fill="y", padx=2)
        
        right_frame = tk.Frame(content_frame, bg=colors['background'])
        right_frame.pack(side="right", fill="both", expand=True, padx=(6, 0))
        
        # Widgets de gauche
        self.create_connection_panel(left_frame)
        self.create_control_panel(left_frame)
        self.create_custom_commands_panel(left_frame)
        
        # Widgets de droite
        self.create_voice_panel(right_frame)
        self.create_log_panel(right_frame)
        
        # Pied de page cyberpunk
        self.create_footer(main_frame)
    
    def create_header(self, parent):
        """Crée l'en-tête cyberpunk de l'application."""
        colors = self.config['ui']['colors']
        app_config = self.config['application']
        
        header_frame = tk.Frame(parent, bg=colors['background'])
        header_frame.pack(fill="x", pady=(0, 12))
        
        # Logo et titre avec effet néon
        title_frame = tk.Frame(header_frame, bg=colors['background'])
        title_frame.pack(side="left")
        
        title_label = ttk.Label(title_frame, text="⚡ VoxThymio", style="Cyber.Title.TLabel")
        title_label.pack()
        
        subtitle = ttk.Label(title_frame, 
                            text="// CONTRÔLE VOCAL INTELLIGENT //",
                            style="Cyber.Status.TLabel")
        subtitle.pack()
        
        # Informations de développeur cyberpunk
        dev_frame = tk.Frame(header_frame, bg=colors['background'])
        dev_frame.pack(side="right")
        
        dev_label = ttk.Label(dev_frame, 
                             text=f"DEV: {app_config['developer']}",
                             style="Cyber.Info.TLabel")
        dev_label.pack(anchor="e")
        
        org_label = ttk.Label(dev_frame, 
                             text=f"ORG: {app_config['organization']}",
                             style="Cyber.Header.TLabel")
        org_label.pack(anchor="e")
        
        # Ligne de séparation néon
        separator = tk.Frame(header_frame, height=2, bg=colors['primary'])
        separator.pack(fill="x", pady=(10, 0))
    
    def create_connection_panel(self, parent):
        """Panneau de connexion au robot avec style cyberpunk."""
        colors = self.config['ui']['colors']
        
        frame = tk.LabelFrame(parent, text="⚡ CONNEXION ROBOT", 
                             bg=colors['panel'], fg=colors['primary'], 
                             font=("Orbitron", 11, "bold"),
                             relief="solid", bd=2)
        frame.pack(fill="x", pady=(0, 8))
        
        # Status de connexion avec effet néon
        status_frame = tk.Frame(frame, bg=colors['panel'])
        status_frame.pack(pady=6)
        
        self.connection_status = ttk.Label(status_frame, 
                                         text="❌ SYSTÈME DÉCONNECTÉ",
                                         style="Cyber.Status.TLabel")
        self.connection_status.pack()
        
        # Boutons de connexion cyberpunk
        btn_frame = tk.Frame(frame, bg=colors['panel'])
        btn_frame.pack(pady=15)
        
        self.connect_btn = ttk.Button(btn_frame, 
                                     text="🔌 INITIER CONNEXION",
                                     style="Cyber.Connect.TButton",
                                     command=self.connect_robot)
        self.connect_btn.pack(side="left", padx=5, ipadx=12, ipady=6)
        
        self.disconnect_btn = ttk.Button(btn_frame, 
                                        text="🔌 TERMINER LIAISON",
                                        style="Cyber.Disabled.TButton",
                                        command=self.disconnect_robot,
                                        state="disabled")
        self.disconnect_btn.pack(side="left", padx=5, ipadx=12, ipady=6)
    
    def create_control_panel(self, parent):
        """Panneau de contrôle manuel avec style cyberpunk."""
        colors = self.config['ui']['colors']
        
        frame = tk.LabelFrame(parent, text="🎮 CONTRÔLE MANUEL", 
                             bg=colors['panel'], fg=colors['primary'], 
                             font=("Orbitron", 11, "bold"),
                             relief="solid", bd=2)
        frame.pack(fill="x", pady=(0, 8))
        
        # Boutons de mouvement avec grille cyberpunk
        movement_frame = tk.LabelFrame(frame, text=">> NAVIGATION <<", 
                                      bg=colors['panel'], fg=colors['secondary'],
                                      font=("Consolas", 9, "bold"))
        movement_frame.pack(fill="x", padx=10, pady=6)
        
        btn_grid = tk.Frame(movement_frame, bg=colors['panel'])
        btn_grid.pack(pady=8)
        
        # Configuration responsive
        for i in range(3):
            btn_grid.columnconfigure(i, weight=1)
        
        # Ligne 1: Avancer
        ttk.Button(btn_grid, text="⬆ AVANCER", 
                  command=lambda: self.manual_command("avancer"),
                  style="Cyber.Primary.TButton").grid(row=0, column=1, padx=3, pady=3, 
                                              sticky="ew", ipadx=10, ipady=5)
        
        # Ligne 2: Gauche, Stop, Droite
        ttk.Button(btn_grid, text="⬅ GAUCHE", 
                  command=lambda: self.manual_command("tourner_gauche"),
                  style="Cyber.Primary.TButton").grid(row=1, column=0, padx=3, pady=3, 
                                              sticky="ew", ipadx=10, ipady=5)
        
        ttk.Button(btn_grid, text="⏹ ARRÊT", 
                  command=lambda: self.manual_command("arreter"),
                  style="Cyber.Secondary.TButton").grid(row=1, column=1, padx=3, pady=3, 
                                             sticky="ew", ipadx=10, ipady=5)
        
        ttk.Button(btn_grid, text="➡ DROITE", 
                  command=lambda: self.manual_command("tourner_droite"),
                  style="Cyber.Primary.TButton").grid(row=1, column=2, padx=3, pady=3, 
                                              sticky="ew", ipadx=10, ipady=5)
        
        # Ligne 3: Reculer
        ttk.Button(btn_grid, text="⬇ RECULER", 
                  command=lambda: self.manual_command("reculer"),
                  style="Cyber.Primary.TButton").grid(row=2, column=1, padx=3, pady=3, 
                                              sticky="ew", ipadx=10, ipady=5)
        
        # Contrôles LED cyberpunk
        led_frame = tk.LabelFrame(frame, text=">> ÉCLAIRAGE LED <<", 
                                 bg=colors['panel'], fg=colors['secondary'],
                                 font=("Consolas", 9, "bold"))
        led_frame.pack(fill="x", padx=10, pady=6)
        
        led_grid = tk.Frame(led_frame, bg=colors['panel'])
        led_grid.pack(pady=6)
        
        for i in range(4):
            led_grid.columnconfigure(i, weight=1)
        
        # Styles LED spécialisés
        style = ttk.Style()
        style.configure('LED.Red.TButton', background="#ff073a", foreground="white", font=("Orbitron", 9, "bold"))
        style.configure('LED.Green.TButton', background="#39ff14", foreground="black", font=("Orbitron", 9, "bold"))
        style.configure('LED.Blue.TButton', background="#00d4ff", foreground="white", font=("Orbitron", 9, "bold"))
        style.configure('LED.Off.TButton', background="#2d3748", foreground="#a0aec0", font=("Orbitron", 9, "bold"))
        
        ttk.Button(led_grid, text="🔴 ROUGE", 
                  command=lambda: self.manual_command("led_rouge"),
                  style="LED.Red.TButton").grid(row=0, column=0, padx=2, pady=3, 
                                               sticky="ew", ipadx=5, ipady=3)
        
        ttk.Button(led_grid, text="🟢 VERT", 
                  command=lambda: self.manual_command("led_vert"),
                  style="LED.Green.TButton").grid(row=0, column=1, padx=2, pady=3, 
                                                 sticky="ew", ipadx=5, ipady=3)
        
        ttk.Button(led_grid, text="🔵 BLEU", 
                  command=lambda: self.manual_command("led_bleu"),
                  style="LED.Blue.TButton").grid(row=0, column=2, padx=2, pady=3, 
                                                sticky="ew", ipadx=5, ipady=3)
        
        ttk.Button(led_grid, text="⚫ OFF", 
                  command=lambda: self.manual_command("led_eteindre"),
                  style="LED.Off.TButton").grid(row=0, column=3, padx=2, pady=3, 
                                               sticky="ew", ipadx=5, ipady=3)
    
    def create_custom_commands_panel(self, parent):
        """Panneau des touches personnalisées avec style cyberpunk."""
        colors = self.config['ui']['colors']
        
        frame = tk.LabelFrame(parent, text="🔧 TOUCHES PERSONNALISÉES", 
                             bg=colors['panel'], fg=colors['accent'], 
                             font=("Orbitron", 11, "bold"),
                             relief="solid", bd=2)
        frame.pack(fill="x", pady=(0, 8))
        
        # Frame pour les boutons personnalisés
        custom_buttons_frame = tk.Frame(frame, bg=colors['panel'])
        custom_buttons_frame.pack(fill="x", padx=10, pady=6)
        
        # Liste pour stocker les boutons personnalisés
        if not hasattr(self, 'custom_buttons'):
            self.custom_buttons = []
        
        # Zone des boutons personnalisés existants
        self.custom_commands_container = tk.Frame(custom_buttons_frame, bg=colors['panel'])
        self.custom_commands_container.pack(fill="x", pady=(0, 6))
        
        # Bouton pour ajouter une nouvelle commande
        add_button_frame = tk.Frame(custom_buttons_frame, bg=colors['panel'])
        add_button_frame.pack(fill="x")
        
        add_btn = ttk.Button(add_button_frame, text="➕ AJOUTER COMMANDE", 
                            command=self.add_custom_command,
                            style="Cyber.Accent.TButton")
        add_btn.pack(pady=3, ipadx=12, ipady=6)
        
        # Charger les commandes personnalisées existantes
        self.load_custom_commands()
    
    def add_custom_command(self):
        """Ouvre une boîte de dialogue pour ajouter une commande personnalisée."""
        colors = self.config['ui']['colors']
        
        # Fenêtre de dialogue cyberpunk
        dialog = tk.Toplevel(self.root)
        dialog.title("⚡ Nouvelle Commande Personnalisée")
        dialog.geometry("550x500")
        dialog.configure(bg=colors['background'])
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrer la fenêtre
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (550 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"550x500+{x}+{y}")
        
        # Container principal
        main_container = tk.Frame(dialog, bg=colors['background'])
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titre cyberpunk
        title_label = tk.Label(main_container, text=">> CRÉER COMMANDE PERSONNALISÉE <<",
                              bg=colors['background'], fg=colors['primary'],
                              font=("Orbitron", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Nom de la commande
        tk.Label(main_container, text="Nom de la commande:",
                bg=colors['background'], fg=colors['text_normal'],
                font=("Consolas", 11, "bold")).pack(anchor="w", pady=(0, 5))
        
        name_entry = tk.Entry(main_container, bg=colors['panel'], fg=colors['text_normal'],
                             font=("Consolas", 11), relief="solid", bd=2,
                             insertbackground=colors['primary'])
        name_entry.pack(fill="x", pady=(0, 15), ipady=8)
        
        # Description de la commande
        tk.Label(main_container, text="Description (pour reconnaissance vocale):",
                bg=colors['background'], fg=colors['text_normal'],
                font=("Consolas", 11, "bold")).pack(anchor="w", pady=(0, 5))
        
        description_entry = tk.Entry(main_container, bg=colors['panel'], fg=colors['text_normal'],
                                   font=("Consolas", 11), relief="solid", bd=2,
                                   insertbackground=colors['primary'])
        description_entry.pack(fill="x", pady=(0, 15), ipady=8)
        
        # Code Aseba
        tk.Label(main_container, text="Code Aseba (obligatoire):",
                bg=colors['background'], fg=colors['accent'],
                font=("Consolas", 11, "bold")).pack(anchor="w", pady=(0, 5))
        
        code_text = tk.Text(main_container, height=8, bg=colors['panel'], fg=colors['text_normal'],
                           font=("Consolas", 10), relief="solid", bd=2,
                           insertbackground=colors['primary'])
        code_text.pack(fill="both", expand=True, pady=(0, 20))
        
        # Placeholder pour le code
        code_text.insert("1.0", "# Exemple:\n# motor.left.target = 200\n# motor.right.target = 200")
        code_text.bind("<FocusIn>", lambda e: code_text.delete("1.0", "end") if "Exemple:" in code_text.get("1.0", "2.0") else None)
        
        # Frame pour les boutons
        button_container = tk.Frame(main_container, bg=colors['background'])
        button_container.pack(fill="x", pady=(10, 0))
        
        def save_command():
            name = name_entry.get().strip()
            description = description_entry.get().strip()
            code = code_text.get("1.0", "end-1c").strip()
            
            # Vérifier que tous les champs sont remplis
            if not name or not description:
                tk.messagebox.showerror("Erreur", "Le nom et la description sont obligatoires!")
                return
            
            if not code or code == "# Exemple:\n# motor.left.target = 200\n# motor.right.target = 200":
                tk.messagebox.showerror("Erreur", "Le code Aseba est obligatoire!\nVeuillez saisir le code de votre commande.")
                return
            
            # Sauvegarder la commande
            self.save_custom_command(name, description, code)
            dialog.destroy()
        
        # Boutons avec une approche simplifiée
        save_btn = tk.Button(button_container, text="💾 SAUVEGARDER", 
                            command=save_command,
                            bg=colors['primary'], fg=colors['background'],
                            font=("Orbitron", 12, "bold"), 
                            relief="flat", bd=0, cursor="hand2",
                            activebackground=colors['success'], activeforeground=colors['background'])
        save_btn.pack(side="left", padx=(0, 10), pady=5, ipadx=25, ipady=12)
        
        cancel_btn = tk.Button(button_container, text="❌ ANNULER", 
                              command=dialog.destroy,
                              bg=colors['danger'], fg="white",
                              font=("Orbitron", 12, "bold"), 
                              relief="flat", bd=0, cursor="hand2",
                              activebackground="#ff4757", activeforeground="white")
        cancel_btn.pack(side="right", padx=(10, 0), pady=5, ipadx=25, ipady=12)
        
        # Focus sur le premier champ
        name_entry.focus_set()
    
    def save_custom_command(self, name, description, code):
        """Sauvegarde une commande personnalisée."""
        try:
            # Charger les commandes existantes
            commands_path = Path(__file__).parent.parent / "src" / "commands.json"
            if commands_path.exists():
                with open(commands_path, 'r', encoding='utf-8') as f:
                    commands = json.load(f)
            else:
                commands = {}
            
            # Ajouter la nouvelle commande
            commands[description] = {
                "description": description,
                "code": code if code else f"# Commande personnalisée: {name}",
                "custom": True
            }
            
            # Sauvegarder
            with open(commands_path, 'w', encoding='utf-8') as f:
                json.dump(commands, f, ensure_ascii=False, indent=2)
            
            # Ajouter le bouton à l'interface
            self.add_custom_button(name, description)
            
            # Log
            self.log_message(f"✅ Commande '{name}' ajoutée avec succès", "INFO")
            
        except Exception as e:
            self.log_message(f"❌ Erreur lors de la sauvegarde: {e}", "ERROR")
            tk.messagebox.showerror("Erreur", f"Impossible de sauvegarder la commande:\n{e}")
    
    def add_custom_button(self, name, description):
        """Ajoute un bouton pour une commande personnalisée."""
        colors = self.config['ui']['colors']
        
        button_frame = tk.Frame(self.custom_commands_container, bg=colors['panel'])
        button_frame.pack(fill="x", pady=2)
        
        # Bouton principal
        custom_btn = ttk.Button(button_frame, text=f"🔧 {name}", 
                               command=lambda: self.execute_custom_command(description),
                               style="Cyber.Custom.TButton")
        custom_btn.pack(side="left", fill="x", expand=True, padx=(0, 5), ipadx=10, ipady=5)
        
        # Bouton supprimer
        delete_btn = ttk.Button(button_frame, text="🗑", 
                               command=lambda: self.delete_custom_command(name, description, button_frame),
                               style="Cyber.Danger.TButton")
        delete_btn.pack(side="right", ipadx=5, ipady=5)
        
        self.custom_buttons.append((name, description, button_frame))
    
    def execute_custom_command(self, description):
        """Exécute une commande personnalisée."""
        if self.voice_controller:
            try:
                self.voice_controller.process_command(description)
                self.log_message(f"🔧 Commande personnalisée exécutée: {description}", "INFO")
            except Exception as e:
                self.log_message(f"❌ Erreur commande personnalisée: {e}", "ERROR")
        else:
            self.log_message("❌ Contrôleur vocal non initialisé", "ERROR")
    
    def delete_custom_command(self, name, description, button_frame):
        """Supprime une commande personnalisée."""
        if tk.messagebox.askyesno("Confirmer", f"Supprimer la commande '{name}' ?"):
            try:
                # Supprimer du fichier commands.json
                commands_path = Path(__file__).parent.parent / "src" / "commands.json"
                if commands_path.exists():
                    with open(commands_path, 'r', encoding='utf-8') as f:
                        commands = json.load(f)
                    
                    if description in commands:
                        del commands[description]
                        
                        with open(commands_path, 'w', encoding='utf-8') as f:
                            json.dump(commands, f, ensure_ascii=False, indent=2)
                
                # Supprimer de l'interface
                button_frame.destroy()
                self.custom_buttons = [(n, d, f) for n, d, f in self.custom_buttons if f != button_frame]
                
                self.log_message(f"🗑 Commande '{name}' supprimée", "INFO")
                
            except Exception as e:
                self.log_message(f"❌ Erreur lors de la suppression: {e}", "ERROR")
    
    def load_custom_commands(self):
        """Charge les commandes personnalisées existantes."""
        try:
            commands_path = Path(__file__).parent.parent / "src" / "commands.json"
            if commands_path.exists():
                with open(commands_path, 'r', encoding='utf-8') as f:
                    commands = json.load(f)
                
                for description, details in commands.items():
                    if details.get("custom", False):
                        # Extraire le nom de la description ou utiliser une partie de la description
                        name = description.split()[0:2]  # Prendre les 2 premiers mots
                        name = " ".join(name) if len(name) > 1 else description[:20]
                        self.add_custom_button(name, description)
        except Exception as e:
            self.log_message(f"⚠️ Erreur chargement commandes: {e}", "WARNING")

    def create_voice_panel(self, parent):
        """Panneau de contrôle vocal cyberpunk."""
        colors = self.config['ui']['colors']
        
        frame = tk.LabelFrame(parent, text="🎤 INTERFACE VOCALE", 
                             bg=colors['panel'], fg=colors['primary'], 
                             font=("Orbitron", 11, "bold"),
                             relief="solid", bd=2)
        frame.pack(fill="x", pady=(0, 8))
        
        # Status du microphone cyberpunk
        status_frame = tk.Frame(frame, bg=colors['panel'])
        status_frame.pack(pady=6)
        
        self.mic_status = ttk.Label(status_frame, 
                                   text="🎤 SYSTÈME VOCAL: INITIALISATION...",
                                   style="Cyber.Status.TLabel")
        self.mic_status.pack()
        
        # Bouton vocal principal cyberpunk
        self.voice_btn = ttk.Button(frame, 
                                   text="🎤 ACTIVER MODE VOCAL",
                                   style="Cyber.Secondary.TButton",
                                   command=self.toggle_voice_mode)
        self.voice_btn.pack(pady=20, padx=20, fill="x", ipady=12)
        
        # Zone de commandes vocales cyberpunk
        commands_frame = tk.LabelFrame(frame, text=">> COMMANDES DISPONIBLES <<", 
                                      bg=colors['panel'], fg=colors['secondary'],
                                      font=("Consolas", 9, "bold"))
        commands_frame.pack(fill="x", padx=10, pady=8)
        
        commands_text = """⚡ NAVIGATION: "avancer", "reculer", "gauche", "droite", "stop"
🔥 ÉCLAIRAGE: "rouge", "vert", "bleu", "éteindre"  
🛠 SYSTÈME: "quitter" """
        
        commands_label = tk.Label(commands_frame, text=commands_text, 
                                 bg=colors['panel'], fg=colors['text_primary'], 
                                 font=("Consolas", 9), justify="left",
                                 anchor="w")
        commands_label.pack(padx=10, pady=6, fill="x")
        
        # Indicateur vocal cyberpunk
        indicator_frame = tk.Frame(frame, bg=colors['panel'], relief="solid", bd=1,
                                  highlightbackground=colors['primary'], highlightthickness=1)
        indicator_frame.pack(fill="x", padx=20, pady=15)
        
        self.voice_indicator = tk.Label(indicator_frame, 
                                       text="🔇 MODE VOCAL INACTIF", 
                                       bg=colors['panel'], fg=colors['text_secondary'],
                                       font=("Orbitron", 11, "bold"),
                                       pady=10)
        self.voice_indicator.pack(fill="x")
    
    def create_log_panel(self, parent):
        """Panneau de logs cyberpunk."""
        colors = self.config['ui']['colors']
        
        frame = tk.LabelFrame(parent, text="📊 JOURNAL SYSTÈME", 
                             bg=colors['panel'], fg=colors['primary'], 
                             font=("Orbitron", 11, "bold"),
                             relief="solid", bd=2)
        frame.pack(fill="both", expand=True)
        
        # Zone de texte cyberpunk
        log_container = tk.Frame(frame, bg=colors['panel'], relief="sunken", bd=2,
                                highlightbackground=colors['primary'], highlightthickness=1)
        log_container.pack(fill="both", expand=True, padx=10, pady=6)
        
        self.log_text = scrolledtext.ScrolledText(log_container, 
                                                 height=12, 
                                                 bg=colors['background'], 
                                                 fg=colors['text_primary'],
                                                 font=("Consolas", 9),
                                                 state="disabled",
                                                 relief="flat",
                                                 selectbackground=colors['secondary'],
                                                 selectforeground=colors['background'],
                                                 insertbackground=colors['primary'],
                                                 wrap="word")
        self.log_text.pack(fill="both", expand=True, padx=3, pady=3)
        
        # Bouton de nettoyage cyberpunk
        clear_frame = tk.Frame(frame, bg=colors['panel'])
        clear_frame.pack(fill="x", padx=15, pady=10)
        
        ttk.Button(clear_frame, text="🗑 PURGER LOGS", 
                  command=self.clear_logs,
                  style="Cyber.Primary.TButton").pack(pady=5, ipadx=15)
    
    def create_footer(self, parent):
        """Pied de page cyberpunk."""
        colors = self.config['ui']['colors']
        app_config = self.config['application']
        
        footer_frame = tk.Frame(parent, bg=colors['background'])
        footer_frame.pack(fill="x", pady=(20, 0))
        
        # Ligne de séparation cyberpunk
        separator_frame = tk.Frame(footer_frame, bg=colors['background'], height=4)
        separator_frame.pack(fill="x", pady=(0, 15))
        
        separator1 = tk.Frame(separator_frame, height=2, bg=colors['primary'])
        separator1.pack(fill="x")
        
        separator2 = tk.Frame(separator_frame, height=1, bg=colors['secondary'])
        separator2.pack(fill="x", pady=(1, 0))
        
        # Informations cyberpunk
        info_frame = tk.Frame(footer_frame, bg=colors['background'])
        info_frame.pack(fill="x")
        
        copyright_label = ttk.Label(info_frame, 
                                   text=f"© 2025 {app_config['organization']} - {app_config['name']} v{app_config['version']}",
                                   style="Cyber.Info.TLabel")
        copyright_label.pack(side="left")
        
        # Horloge cyberpunk
        self.time_label = ttk.Label(info_frame, 
                                   text=self.get_current_time(),
                                   style="Cyber.Status.TLabel")
        self.time_label.pack(side="right")
        
        # Mise à jour de l'heure
        self.update_time()
    
    def setup_async(self):
        """Configure le support asynchrone."""
        self.loop = None
        self.async_thread = None
    
    def log_message(self, message, level="INFO"):
        """Ajoute un message au journal avec style cyberpunk."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = self.config['ui']['colors']
        
        # Couleurs selon le niveau
        level_colors = {
            "INFO": colors['text_primary'],
            "WARNING": colors['warning'], 
            "ERROR": colors['danger'],
            "SUCCESS": colors['success'],
            "SYSTEM": colors['secondary']
        }
        
        level_symbols = {
            "INFO": "ℹ",
            "WARNING": "⚠",
            "ERROR": "❌",
            "SUCCESS": "✅",
            "SYSTEM": "⚡"
        }
        
        symbol = level_symbols.get(level, "•")
        
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"[{timestamp}] {symbol} {message}\n")
        self.log_text.config(state="disabled")
        self.log_text.see("end")
        
        # Mise à jour de l'interface
        self.root.update_idletasks()
    
    def clear_logs(self):
        """Efface le journal."""
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, "end")
        self.log_text.config(state="disabled")
        self.log_message("LOGS PURGÉS", "SYSTEM")
    
    def get_current_time(self):
        """Retourne l'heure actuelle."""
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    def update_time(self):
        """Met à jour l'affichage de l'heure."""
        self.time_label.config(text=self.get_current_time())
        self.root.after(1000, self.update_time)
    
    def connect_robot(self):
        """Connecte le robot en arrière-plan."""
        self.log_message("INITIATION LIAISON ROBOT THYMIO...", "INFO")
        self.connect_btn.config(state="disabled", text="LIAISON EN COURS...")
        
        def connect_async():
            async def do_connect():
                self.thymio_controller = ThymioController()
                success = await self.thymio_controller.connect()
                
                if success:
                    self.root.after(0, self.on_connection_success)
                else:
                    self.root.after(0, self.on_connection_failed)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(do_connect())
            loop.close()
        
        threading.Thread(target=connect_async, daemon=True).start()
    
    def on_connection_success(self):
        """Callback de connexion réussie."""
        colors = self.config['ui']['colors']
        
        self.log_message("ROBOT THYMIO CONNECTÉ AVEC SUCCÈS", "SUCCESS")
        self.connection_status.config(text="✅ SYSTÈME CONNECTÉ", foreground=colors['success'])
        self.connect_btn.config(state="disabled", text="✅ CONNECTÉ", style="Cyber.Disabled.TButton")
        self.disconnect_btn.config(state="normal", style="Cyber.Connect.TButton")
        
        # Initialiser le contrôleur vocal
        self.init_voice_controller()
    
    def on_connection_failed(self):
        """Callback de connexion échouée."""
        colors = self.config['ui']['colors']
        
        self.log_message("ÉCHEC LIAISON ROBOT", "ERROR")
        self.log_message("VÉRIFIEZ QUE THYMIO SUITE EST LANCÉ", "WARNING")
        self.connection_status.config(text="❌ ÉCHEC CONNEXION", foreground=colors['danger'])
        self.connect_btn.config(state="normal", text="🔄 RÉESSAYER", style="Cyber.Connect.TButton")
        
        messagebox.showerror("Erreur de connexion", 
                           "Impossible de se connecter au robot Thymio.\n"
                           "Vérifiez que Thymio Suite est lancé et le robot connecté.")
    
    def init_voice_controller(self):
        """Initialise le contrôleur vocal."""
        colors = self.config['ui']['colors']
        
        self.log_message("INITIALISATION SYSTÈME VOCAL...", "INFO")
        
        try:
            self.voice_controller = SmartVoiceController(self.thymio_controller)
            
            # Vérifier la disponibilité du microphone
            speech_recognizer = SpeechRecognizer()
            
            self.log_message("MICROPHONE DÉTECTÉ ET CONFIGURÉ", "SUCCESS")
            self.mic_status.config(text="🎤 SYSTÈME VOCAL: ✅ OPÉRATIONNEL", 
                                 foreground=colors['success'])
            self.voice_btn.config(state="normal")
                
        except Exception as e:
            self.log_message(f"ERREUR INITIALISATION VOCALE: {e}", "ERROR")
            self.mic_status.config(text="🎤 SYSTÈME VOCAL: ❌ ERREUR", 
                                 foreground=colors['danger'])
    
    def disconnect_robot(self):
        """Déconnecte le robot."""
        self.log_message("DÉCONNEXION ROBOT...", "INFO")
        
        # Arrêter le mode vocal
        if self.voice_mode:
            self.toggle_voice_mode()
        
        def disconnect_async():
            async def do_disconnect():
                if self.thymio_controller:
                    await self.thymio_controller.disconnect()
                self.root.after(0, self.on_disconnection_complete)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(do_disconnect())
            loop.close()
        
        threading.Thread(target=disconnect_async, daemon=True).start()
    
    def on_disconnection_complete(self):
        """Callback de déconnexion terminée."""
        colors = self.config['ui']['colors']
        
        self.log_message("ROBOT DÉCONNECTÉ", "INFO")
        self.connection_status.config(text="❌ SYSTÈME DÉCONNECTÉ", foreground=colors['text_secondary'])
        self.connect_btn.config(state="normal", text="🔌 INITIER CONNEXION", style="Cyber.Connect.TButton")
        self.disconnect_btn.config(state="disabled", style="Cyber.Disabled.TButton")
        self.voice_btn.config(state="disabled", style="Cyber.Disabled.TButton")
        self.mic_status.config(text="🎤 SYSTÈME VOCAL: EN ATTENTE...", 
                             foreground=colors['text_secondary'])
    
    def manual_command(self, command):
        """Exécute une commande manuelle."""
        if not self.thymio_controller:
            self.log_message("ROBOT NON CONNECTÉ", "ERROR")
            messagebox.showerror("Erreur", "Robot non connecté !")
            return
        
        self.log_message(f"COMMANDE MANUELLE: {command.upper()}", "INFO")
        
        def execute_async():
            async def do_execute():
                result = await self.thymio_controller.execute_command(command)
                message = f"COMMANDE '{command.upper()}' EXÉCUTÉE" if result else f"ÉCHEC '{command.upper()}'"
                level = "SUCCESS" if result else "ERROR"
                self.root.after(0, lambda: self.log_message(message, level))
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(do_execute())
            loop.close()
        
        threading.Thread(target=execute_async, daemon=True).start()
    
    def toggle_voice_mode(self):
        """Active/désactive le mode vocal."""
        if not self.voice_controller:
            messagebox.showerror("Erreur", "Système vocal non disponible !")
            return
        
        if not self.thymio_controller:
            messagebox.showerror("Erreur", "Robot non connecté !")
            return
        
        self.voice_mode = not self.voice_mode
        
        if self.voice_mode:
            self.start_voice_mode()
        else:
            self.stop_voice_mode()
    
    def start_voice_mode(self):
        """Démarre le mode vocal."""
        colors = self.config['ui']['colors']
        
        self.log_message("MODE VOCAL ACTIVÉ", "SUCCESS")
        self.voice_btn.config(text="🔇 DÉSACTIVER MODE VOCAL")
        self.voice_indicator.config(text="🎤 MODE VOCAL ACTIF - PARLEZ MAINTENANT", 
                                  foreground=colors['success'])
        
        self.voice_active = True
        self.voice_thread = threading.Thread(target=self.voice_listener, daemon=True)
        self.voice_thread.start()
    
    def stop_voice_mode(self):
        """Arrête le mode vocal."""
        colors = self.config['ui']['colors']
        
        self.log_message("MODE VOCAL DÉSACTIVÉ", "INFO")
        self.voice_btn.config(text="🎤 ACTIVER MODE VOCAL")
        self.voice_indicator.config(text="🔇 MODE VOCAL INACTIF", 
                                  foreground=colors['text_secondary'])
        
        self.voice_active = False
        if self.voice_thread:
            self.voice_thread.join(timeout=1)
    
    def voice_listener(self):
        """Thread d'écoute vocale."""
        colors = self.config['ui']['colors']
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        while self.voice_active and self.voice_mode:
            try:
                self.root.after(0, lambda: self.voice_indicator.config(
                    text="🎤 ANALYSE EN COURS...", foreground=colors['warning']))
                
                # Utiliser le contrôleur vocal existant
                command_text = self.voice_controller.speech_recognizer.listen()
                
                if not self.voice_active:
                    break
                
                if command_text:
                    self.root.after(0, lambda cmd=command_text: self.process_voice_command(cmd))
                else:
                    self.root.after(0, lambda: self.voice_indicator.config(
                        text="🎤 AUCUNE PAROLE DÉTECTÉE", foreground=colors['warning']))
                
                time.sleep(0.5)
                
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"ERREUR VOCALE: {e}", "ERROR"))
                time.sleep(1)
        
        loop.close()
        
        if not self.voice_mode:
            self.root.after(0, lambda: self.voice_indicator.config(
                text="🔇 MODE VOCAL INACTIF", foreground=colors['text_secondary']))
    
    def process_voice_command(self, command_text):
        """Traite une commande vocale reconnue."""
        colors = self.config['ui']['colors']
        
        self.log_message(f"COMMANDE VOCALE: '{command_text.upper()}'", "SUCCESS")
        self.voice_indicator.config(text="🎤 COMMANDE RECONNUE", foreground=colors['success'])
        
        if "quitter" in command_text.lower():
            self.voice_mode = False
            self.stop_voice_mode()
            return
        
        # Traitement via le contrôleur vocal
        def execute_voice_command():
            async def do_execute():
                result = await self.voice_controller.process_command(command_text)
                
                if result['status'] == 'success':
                    message = f"COMMANDE VOCALE EXÉCUTÉE: {result.get('action', '').upper()}"
                    level = "SUCCESS"
                else:
                    message = f"COMMANDE VOCALE NON RECONNUE: '{command_text.upper()}'"
                    level = "WARNING"
                
                self.root.after(0, lambda: self.log_message(message, level))
                
                if self.voice_mode:
                    self.root.after(0, lambda: self.voice_indicator.config(
                        text="🎤 MODE VOCAL ACTIF - PARLEZ MAINTENANT", 
                        foreground=colors['success']))
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(do_execute())
            loop.close()
        
        threading.Thread(target=execute_voice_command, daemon=True).start()
    
    def on_closing(self):
        """Gestion de la fermeture de l'application."""
        try:
            if self.voice_mode:
                self.log_message("ARRÊT MODE VOCAL...", "INFO")
                self.stop_voice_mode()
            
            if self.thymio_controller:
                self.log_message("DÉCONNEXION EN COURS...", "INFO")
                
                def final_disconnect():
                    try:
                        async def do_disconnect():
                            await self.thymio_controller.disconnect()
                        
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(do_disconnect())
                        loop.close()
                        
                    except Exception as e:
                        print(f"Erreur lors de la déconnexion: {e}")
                    finally:
                        self.root.after(0, self.root.quit)
                
                threading.Thread(target=final_disconnect, daemon=True).start()
                self.root.after(2000, self.root.quit)
            else:
                self.root.quit()
                
        except Exception as e:
            print(f"Erreur lors de la fermeture: {e}")
            self.root.quit()
    
    def run(self):
        """Lance l'application."""
        self.log_message("VOXTHYMIO SYSTÈME INITIALISÉ", "SYSTEM")
        self.log_message(f"DÉVELOPPÉ PAR {self.config['application']['developer']}", "INFO")
        self.log_message(f"PROJET {self.config['application']['organization']}", "INFO")
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()


def main():
    """Point d'entrée principal."""
    try:
        # Vérification des dépendances critiques
        required_modules = [
            "speech_recognition",
            "transformers", 
            "torch",
            "chromadb",
            "sentence_transformers"
        ]
        
        missing_modules = []
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)
        
        if missing_modules:
            messagebox.showerror("Dépendances manquantes", 
                               f"Modules requis non installés:\n{', '.join(missing_modules)}\n\n"
                               "Installez les dépendances avec:\n"
                               "pip install -r requirements.txt")
            return
        
        app = VoxThymioGUI()
        app.run()
        
    except Exception as e:
        import logging
        logging.exception("Erreur fatale")
        messagebox.showerror("Erreur fatale", 
                           f"Erreur critique lors du démarrage:\n{e}\n\n"
                           "Consultez les logs pour plus de détails.")


if __name__ == "__main__":
    main()
