"""
Interface graphique VoxThymio v1.0
Développé par Espérance AYIWAHOUN pour AI4Innov

Interface utilisateur complète pour le contrôle vocal et la gestion des commandes Thymio.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import asyncio
import threading
import json
from pathlib import Path
import sys
import os
import time

# Ajouter le répertoire src au path pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from smart_voice_controller import SmartVoiceController
    from controller.thymio_controller import ThymioController
except ImportError as e:
    print(f"Erreur d'import: {e}")
    print("Assurez-vous que les modules src sont dans le PATH")


class VoxThymioGUI:
    """Interface graphique principale de VoxThymio."""
    
    def __init__(self):
        """Initialise l'interface graphique."""
        # Charger la configuration
        self.load_config()
        
        self.root = tk.Tk()
        self.root.title(f"{self.config['application']['name']} v{self.config['application']['version']} - {self.config['application']['organization']}")
        
        window_config = self.config['ui']['window']
        self.root.geometry(f"{window_config['width']}x{window_config['height']}")
        self.root.minsize(window_config['min_width'], window_config['min_height'])
        
        # Configuration des couleurs depuis le fichier config
        self.colors = self.config['ui']['colors']
        
        # Variables d'état
        self.is_listening = False
        self.is_learning_mode = tk.BooleanVar(value=True)
        
        voice_config = self.config['voice']
        self.execution_threshold = tk.DoubleVar(value=voice_config['execution_threshold'])
        self.learning_threshold = tk.DoubleVar(value=voice_config['learning_threshold'])
        
        # Contrôleurs
        self.thymio_controller = None
        self.voice_controller = None
        self.voice_task = None
        
        # Configuration du style
        self.setup_styles()
        
        # Création de l'interface
        self.create_interface()
        
        # Initialisation asynchrone
        self.root.after(100, self.initialize_controllers)
    
    def load_config(self):
        """Charge la configuration depuis le fichier JSON."""
        config_path = Path(__file__).parent / "config.json"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print("⚠️ Fichier config.json non trouvé, utilisation des valeurs par défaut")
            self.config = self.get_default_config()
        except json.JSONDecodeError as e:
            print(f"⚠️ Erreur dans config.json: {e}, utilisation des valeurs par défaut")
            self.config = self.get_default_config()
    
    def get_default_config(self):
        """Retourne la configuration par défaut."""
        return {
            "application": {
                "name": "VoxThymio",
                "version": "1.0",
                "developer": "Espérance AYIWAHOUN",
                "organization": "AI4Innov"
            },
            "ui": {
                "colors": {
                    "primary": "#00d4aa",
                    "secondary": "#2c3e50",
                    "background": "#ecf0f1",
                    "text_dark": "#2c3e50",
                    "text_light": "#ffffff",
                    "success": "#27ae60",
                    "warning": "#f39c12",
                    "danger": "#e74c3c"
                },
                "window": {
                    "width": 1200,
                    "height": 800,
                    "min_width": 1000,
                    "min_height": 700
                }
            },
            "voice": {
                "execution_threshold": 0.5,
                "learning_threshold": 0.85
            }
        }
    
    def setup_styles(self):
        """Configure les styles ttk personnalisés."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Style pour les boutons principaux
        style.configure('Primary.TButton',
                       background=self.colors['primary'],
                       foreground=self.colors['background'],
                       borderwidth=1,
                       focuscolor='none',
                       font=('Consolas', 10, 'bold'))
        
        style.map('Primary.TButton',
                 background=[('active', self.colors['hover']),
                           ('pressed', self.colors['accent'])])
        
        # Style pour les boutons de contrôle (sombre avec bordure néon)
        style.configure('Control.TButton',
                       background=self.colors['card'],
                       foreground=self.colors['text_dark'],
                       borderwidth=1,
                       relief='solid',
                       font=('Consolas', 9))
        
        style.map('Control.TButton',
                 background=[('active', self.colors['secondary']),
                           ('pressed', self.colors['primary'])])
        
        # Style pour les frames (effet terminal)
        style.configure('Card.TFrame',
                       background=self.colors['card'],
                       relief='solid',
                       borderwidth=1)
        
        # Style pour les labels (texte cyberpunk)
        style.configure('Hack.TLabel',
                       background=self.colors['background'],
                       foreground=self.colors['primary'],
                       font=('Consolas', 10, 'bold'))
        
        # Style pour les entrées de texte
        style.configure('Hack.TEntry',
                       background=self.colors['terminal'],
                       foreground=self.colors['text_light'],
                       borderwidth=1,
                       relief='solid',
                       font=('Consolas', 10))
        
        # Style pour les checkboxes
        style.configure('Hack.TCheckbutton',
                       background=self.colors['card'],
                       foreground=self.colors['text_dark'],
                       font=('Consolas', 9))
        
        # Style pour les progressbars (effet néon)
        style.configure('Hack.Horizontal.TProgressbar',
                       background=self.colors['primary'],
                       troughcolor=self.colors['terminal'],
                       borderwidth=1,
                       relief='solid')
    
    def create_interface(self):
        """Crée l'interface utilisateur principale."""
        # Configuration de la grille principale
        self.root.configure(bg=self.colors['background'])
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Zone de contrôle vocal (gauche)
        self.create_voice_control_panel()
        
        # Zone de gestion des commandes (droite)
        self.create_commands_panel()
        
        # Barre d'état (bas)
        self.create_status_bar()
    
    def create_voice_control_panel(self):
        """Crée le panneau de contrôle vocal."""
        # Frame principal pour le contrôle vocal
        voice_frame = ttk.Frame(self.root, style='Card.TFrame', padding="10")
        voice_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        voice_frame.grid_rowconfigure(1, weight=1)
        
        # Titre du panneau
        title_label = ttk.Label(voice_frame, text="🎤 >>> CONTRÔLE VOCAL CYBERNÉTIQUE <<<", 
                               style='Hack.TLabel',
                               font=('Consolas', 12, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Boutons de contrôle
        btn_frame = ttk.Frame(voice_frame)
        btn_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        
        self.listen_btn = ttk.Button(btn_frame, text=">>> ÉCOUTER <<<", 
                                    style='Primary.TButton',
                                    command=self.toggle_listening)
        self.listen_btn.pack(side='left', padx=(0, 5))
        
        self.pause_btn = ttk.Button(btn_frame, text="|| PAUSE", 
                                   style='Control.TButton',
                                   command=self.pause_listening,
                                   state='disabled')
        self.pause_btn.pack(side='left', padx=(0, 5))
        
        self.stop_btn = ttk.Button(btn_frame, text="⏹ KILL", 
                                  style='Control.TButton',
                                  command=self.stop_listening,
                                  state='disabled')
        self.stop_btn.pack(side='left')
        
        # Visualisation audio (effet néon)
        audio_frame = ttk.LabelFrame(voice_frame, text="⚡ SIGNAL NEURAL", padding="5",
                                   style='Card.TFrame')
        audio_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        
        self.audio_bar = ttk.Progressbar(audio_frame, length=300, mode='determinate',
                                       style='Hack.Horizontal.TProgressbar')
        self.audio_bar.pack(side='left', padx=(0, 10))
        
        self.volume_label = ttk.Label(audio_frame, text="🔊 0%", style='Hack.TLabel',
                                    font=('Consolas', 9))
        self.volume_label.pack(side='left')
        
        # Mode d'apprentissage (style cyberpunk)
        learning_frame = ttk.LabelFrame(voice_frame, text="⚙️ NEURAL CONFIG", padding="5",
                                      style='Card.TFrame')
        learning_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        
        learning_check = ttk.Checkbutton(learning_frame, 
                                        text="🧠 AUTO-LEARNING MODE",
                                        variable=self.is_learning_mode,
                                        command=self.toggle_learning_mode,
                                        style='Hack.TCheckbutton')
        learning_check.pack(anchor='w')
        
        # Seuils configurables (style terminal)
        thresholds_frame = ttk.LabelFrame(voice_frame, text="🎯 NEURAL THRESHOLDS", padding="5",
                                        style='Card.TFrame')
        thresholds_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        
        # Seuil d'exécution
        exec_title = ttk.Label(thresholds_frame, text=">>> EXECUTION:", style='Hack.TLabel')
        exec_title.pack(anchor='w')
        exec_scale = ttk.Scale(thresholds_frame, from_=0.0, to=1.0, 
                              variable=self.execution_threshold,
                              orient='horizontal', length=250,
                              command=self.update_execution_threshold)
        exec_scale.pack(fill='x', pady=(0, 5))
        
        self.exec_label = ttk.Label(thresholds_frame, text="50%", style='Hack.TLabel')
        self.exec_label.pack(anchor='w')
        
        # Seuil d'apprentissage
        learn_title = ttk.Label(thresholds_frame, text=">>> LEARNING:", style='Hack.TLabel')
        learn_title.pack(anchor='w', pady=(10, 0))
        learn_scale = ttk.Scale(thresholds_frame, from_=0.0, to=1.0,
                               variable=self.learning_threshold,
                               orient='horizontal', length=250,
                               command=self.update_learning_threshold)
        learn_scale.pack(fill='x', pady=(0, 5))
        
        self.learn_label = ttk.Label(thresholds_frame, text="85%", style='Hack.TLabel')
        self.learn_label.pack(anchor='w')
        
        # Zone de feedback (style terminal)
        feedback_frame = ttk.LabelFrame(voice_frame, text="💻 NEURAL FEEDBACK", padding="5",
                                      style='Card.TFrame')
        feedback_frame.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=(0, 10))
        voice_frame.grid_rowconfigure(5, weight=1)
        
        self.command_text = scrolledtext.ScrolledText(feedback_frame, height=8, width=40,
                                                     wrap=tk.WORD, state='disabled',
                                                     bg=self.colors['terminal'],
                                                     fg=self.colors['primary'],
                                                     font=('Consolas', 9),
                                                     insertbackground=self.colors['primary'])
        self.command_text.pack(fill='both', expand=True)
    
    def create_commands_panel(self):
        """Crée le panneau de gestion des commandes."""
        # Frame principal pour les commandes
        commands_frame = ttk.Frame(self.root, style='Card.TFrame', padding="10")
        commands_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        commands_frame.grid_rowconfigure(2, weight=1)
        
        # Titre du panneau
        title_label = ttk.Label(commands_frame, text="📚 >>> ARSENAL DE COMMANDES NEURAL <<<", 
                               style='Hack.TLabel',
                               font=('Consolas', 12, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Notebook pour organiser les onglets
        notebook = ttk.Notebook(commands_frame)
        notebook.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        commands_frame.grid_rowconfigure(1, weight=1)
        
        # Onglet Bibliothèque
        self.create_library_tab(notebook)
        
        # Onglet Nouvelle Commande
        self.create_new_command_tab(notebook)
        
        # Onglet Assistant
        self.create_assistant_tab(notebook)
        
        # Commandes rapides
        self.create_quick_commands(commands_frame)
    
    def create_library_tab(self, parent):
        """Crée l'onglet bibliothèque de commandes."""
        library_frame = ttk.Frame(parent, padding="10")
        parent.add(library_frame, text="📚 Bibliothèque")
        
        # Barre de recherche
        search_frame = ttk.Frame(library_frame)
        search_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(search_frame, text="🔍").pack(side='left')
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side='left', fill='x', expand=True, padx=(5, 10))
        self.search_entry.bind('<KeyRelease>', self.filter_commands)
        self.search_entry.bind('<FocusIn>', self.on_search_focus_in)
        self.search_entry.bind('<FocusOut>', self.on_search_focus_out)
        
        # Ajouter le placeholder text
        self.search_placeholder = "Rechercher..."
        self.search_entry.insert(0, self.search_placeholder)
        self.search_entry.config(foreground='grey')
        
        filter_combo = ttk.Combobox(search_frame, values=["Toutes", "Système", "Personnalisées"],
                                   state="readonly", width=12)
        filter_combo.set("Toutes")
        filter_combo.pack(side='left')
        
        # Liste des commandes
        list_frame = ttk.Frame(library_frame)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Treeview pour les commandes
        columns = ('Type', 'Commande', 'Description')
        self.commands_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configuration des colonnes
        self.commands_tree.heading('Type', text='Type')
        self.commands_tree.heading('Commande', text='Commande')
        self.commands_tree.heading('Description', text='Description')
        
        self.commands_tree.column('Type', width=80)
        self.commands_tree.column('Commande', width=120)
        self.commands_tree.column('Description', width=200)
        
        # Scrollbar pour la liste
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.commands_tree.yview)
        self.commands_tree.configure(yscrollcommand=scrollbar.set)
        
        self.commands_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Boutons d'actions
        actions_frame = ttk.Frame(library_frame)
        actions_frame.pack(fill='x')
        
        ttk.Button(actions_frame, text="✏️ Modifier", 
                  command=self.edit_command).pack(side='left', padx=(0, 5))
        ttk.Button(actions_frame, text="🗑️ Supprimer", 
                  command=self.delete_command).pack(side='left', padx=(0, 5))
        ttk.Button(actions_frame, text="🧪 Tester", 
                  command=self.test_command).pack(side='left')
    
    def create_new_command_tab(self, parent):
        """Crée l'onglet de création de nouvelle commande."""
        new_cmd_frame = ttk.Frame(parent, padding="10")
        parent.add(new_cmd_frame, text="➕ Nouvelle")
        
        # Description
        ttk.Label(new_cmd_frame, text="📝 Description:", 
                 font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.desc_entry = ttk.Entry(new_cmd_frame, width=50)
        self.desc_entry.pack(fill='x', pady=(0, 10))
        
        # Code Aseba
        ttk.Label(new_cmd_frame, text="🔧 Code Aseba:", 
                 font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        code_frame = ttk.Frame(new_cmd_frame)
        code_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.code_text = scrolledtext.ScrolledText(code_frame, height=10, width=50,
                                                  wrap=tk.NONE, font=('Consolas', 10))
        self.code_text.pack(fill='both', expand=True)
        
        # Test de similarité
        similarity_frame = ttk.LabelFrame(new_cmd_frame, text="🎯 Test Sémantique", padding="5")
        similarity_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(similarity_frame, text="VÉRIFIER SIMILARITÉ",
                  command=self.check_similarity).pack(side='left')
        
        self.similarity_label = ttk.Label(similarity_frame, text="Aucun test effectué")
        self.similarity_label.pack(side='left', padx=(10, 0))
        
        # Boutons d'actions
        actions_frame = ttk.Frame(new_cmd_frame)
        actions_frame.pack(fill='x')
        
        ttk.Button(actions_frame, text="💾 SAUVEGARDER", 
                  style='Primary.TButton',
                  command=self.save_new_command).pack(side='left', padx=(0, 5))
        ttk.Button(actions_frame, text="🧪 TESTER", 
                  command=self.test_new_command).pack(side='left', padx=(0, 5))
        ttk.Button(actions_frame, text="❌ EFFACER", 
                  command=self.clear_new_command).pack(side='left')
    
    def create_assistant_tab(self, parent):
        """Crée l'onglet assistant de code."""
        assistant_frame = ttk.Frame(parent, padding="10")
        parent.add(assistant_frame, text="🤖 Assistant")
        
        # Modèles rapides
        ttk.Label(assistant_frame, text="Modèles rapides:", 
                 font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        templates_frame = ttk.Frame(assistant_frame)
        templates_frame.pack(fill='x', pady=(0, 10))
        
        templates = ["Mouvement", "Rotation", "Capteurs", "LEDs", "Sons", "Temporisateurs"]
        for i, template in enumerate(templates):
            row = i // 3
            col = i % 3
            if row == 0:
                templates_frame.grid_rowconfigure(row, weight=1)
            if col == 0:
                templates_frame.grid_columnconfigure(col, weight=1)
            
            btn = ttk.Button(templates_frame, text=template,
                           command=lambda t=template: self.insert_template(t))
            btn.grid(row=row, column=col, padx=2, pady=2, sticky='ew')
        
        # Suggestions
        suggestions_frame = ttk.LabelFrame(assistant_frame, text="💡 Suggestions", padding="5")
        suggestions_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.suggestions_text = scrolledtext.ScrolledText(suggestions_frame, height=8, 
                                                         state='disabled', wrap=tk.WORD)
        self.suggestions_text.pack(fill='both', expand=True)
        
        # Documentation
        ttk.Button(assistant_frame, text="📖 Documentation Aseba",
                  command=self.open_documentation).pack(fill='x')
    
    def create_quick_commands(self, parent):
        """Crée les boutons de commandes rapides."""
        quick_frame = ttk.LabelFrame(parent, text=">>> QUICK COMMANDS <<<", padding="5",
                                   style='Card.TFrame')
        quick_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        # Première ligne
        row1 = ttk.Frame(quick_frame)
        row1.pack(fill='x', pady=(0, 5))
        
        ttk.Button(row1, text="⬆️ FWD", style='Control.TButton',
                  command=lambda: self.execute_quick_command("avancer")).pack(side='left', padx=(0, 5))
        ttk.Button(row1, text="⬇️ BCK", style='Control.TButton',
                  command=lambda: self.execute_quick_command("reculer")).pack(side='left', padx=(0, 5))
        ttk.Button(row1, text="⏹️ KILL", style='Control.TButton',
                  command=lambda: self.execute_quick_command("arreter")).pack(side='left')
        
        # Deuxième ligne
        row2 = ttk.Frame(quick_frame)
        row2.pack(fill='x')
        
        ttk.Button(row2, text="⬅️ L", style='Control.TButton',
                  command=lambda: self.execute_quick_command("tourner_gauche")).pack(side='left', padx=(0, 5))
        ttk.Button(row2, text="➡️ R", style='Control.TButton',
                  command=lambda: self.execute_quick_command("tourner_droite")).pack(side='left')
    
    def create_status_bar(self):
        """Crée la barre d'état en bas de l'interface."""
        status_frame = ttk.Frame(self.root, style='Card.TFrame', padding="5")
        status_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        
        # Informations sur l'application (style hack)
        app_info = ttk.Label(status_frame, 
                           text=f"� {self.config['application']['name']} v{self.config['application']['version']} "
                                f">>> CODED BY {self.config['application']['developer']} @ {self.config['application']['organization']} <<<",
                           style='Hack.TLabel',
                           font=('Consolas', 8, 'bold'))
        app_info.pack(side='left')
        
        # Statuts (style cyberpunk)
        self.status_thymio = ttk.Label(status_frame, text="🤖 THYMIO: [OFFLINE]", 
                                     style='Hack.TLabel', font=('Consolas', 8))
        self.status_thymio.pack(side='left', padx=(20, 10))
        
        self.status_audio = ttk.Label(status_frame, text="🎤 NEURAL: [OFFLINE]", 
                                    style='Hack.TLabel', font=('Consolas', 8))
        self.status_audio.pack(side='left', padx=(0, 10))
        
        self.status_commands = ttk.Label(status_frame, text="📚 ARSENAL: [0]", 
                                       style='Hack.TLabel', font=('Consolas', 8))
        self.status_commands.pack(side='left', padx=(0, 10))
        
        self.status_latency = ttk.Label(status_frame, text="⚡ PING: [--ms]", 
                                      style='Hack.TLabel', font=('Consolas', 8))
        self.status_latency.pack(side='left', padx=(0, 10))
        
        self.status_learning = ttk.Label(status_frame, text="🧠 AUTO-LEARNING: [ACTIVE]", 
                                       style='Hack.TLabel', font=('Consolas', 8))
        self.status_learning.pack(side='right')
    
    # Méthodes de contrôle
    def initialize_controllers(self):
        """Initialise les contrôleurs de manière asynchrone."""
        def init_async():
            try:
                # Initialisation du contrôleur Thymio
                self.thymio_controller = ThymioController()
                
                # Créer un nouveau loop pour ce thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    # Tentative de connexion
                    if loop.run_until_complete(self.thymio_controller.connect()):
                        self.root.after(0, lambda: self.update_status("thymio", True))
                        
                        # Initialisation du contrôleur vocal
                        self.voice_controller = SmartVoiceController(self.thymio_controller)
                        self.root.after(0, lambda: self.update_status("audio", True))
                        
                        # Charger les commandes
                        self.root.after(0, self.load_commands)
                    else:
                        self.root.after(0, lambda: self.update_status("thymio", False))
                        self.root.after(0, lambda: messagebox.showwarning("Connexion", 
                                             "Impossible de se connecter au robot Thymio.\n"
                                             "Vérifiez que le robot est allumé et connecté."))
                finally:
                    loop.close()
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Erreur d'initialisation", 
                                       f"Erreur lors de l'initialisation: {str(e)}"))
        
        # Exécuter dans un thread séparé
        thread = threading.Thread(target=init_async)
        thread.daemon = True
        thread.start()
    
    def update_status(self, component, status):
        """Met à jour le statut d'un composant avec le style cyberpunk."""
        if component == "thymio":
            text = "🤖 THYMIO: [ONLINE]" if status else "🤖 THYMIO: [OFFLINE]"
            self.status_thymio.config(text=text)
        elif component == "audio":
            text = "🎤 NEURAL: [ONLINE]" if status else "🎤 NEURAL: [OFFLINE]"
            self.status_audio.config(text=text)
    
    def toggle_listening(self):
        """Active/désactive l'écoute vocale."""
        if not self.voice_controller:
            messagebox.showwarning("Erreur", "Contrôleur vocal non initialisé")
            return
        
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()
    
    def start_listening(self):
        """Démarre l'écoute vocale."""
        self.is_listening = True
        self.listen_btn.config(text=">>> EN ÉCOUTE... <<<", state='disabled')
        self.pause_btn.config(state='normal')
        self.stop_btn.config(state='normal')
        
        def listen_loop():
            try:
                # Créer un nouveau loop pour ce thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    loop.run_until_complete(self.voice_controller.voice_recognition())
                finally:
                    loop.close()
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Erreur", f"Erreur d'écoute: {str(e)}"))
        
        self.voice_task = threading.Thread(target=listen_loop)
        self.voice_task.daemon = True
        self.voice_task.start()
    
    def pause_listening(self):
        """Met en pause l'écoute vocale."""
        # TODO: Implémenter la pause
        pass
    
    def stop_listening(self):
        """Arrête l'écoute vocale."""
        self.is_listening = False
        self.listen_btn.config(text=">>> ÉCOUTER <<<", state='normal')
        self.pause_btn.config(state='disabled')
        self.stop_btn.config(state='disabled')
    
    def toggle_learning_mode(self):
        """Active/désactive le mode d'apprentissage."""
        if self.voice_controller:
            self.voice_controller.is_learning_mode = self.is_learning_mode.get()
        
        status = "[ACTIVE]" if self.is_learning_mode.get() else "[INACTIVE]"
        self.status_learning.config(text=f"🧠 AUTO-LEARNING: {status}")
    
    def update_execution_threshold(self, value):
        """Met à jour le seuil d'exécution."""
        percentage = int(float(value) * 100)
        self.exec_label.config(text=f"{percentage}%")
        
        if self.voice_controller:
            self.voice_controller.EXECUTION_THRESHOLD = float(value)
    
    def update_learning_threshold(self, value):
        """Met à jour le seuil d'apprentissage."""
        percentage = int(float(value) * 100)
        self.learn_label.config(text=f"{percentage}%")
        
        if self.voice_controller:
            self.voice_controller.LEARNING_THRESHOLD = float(value)
    
    def load_commands(self):
        """Charge les commandes dans la liste."""
        if not self.voice_controller:
            return
        
        # Effacer la liste existante
        for item in self.commands_tree.get_children():
            self.commands_tree.delete(item)
        
        # Charger les commandes
        commands = self.voice_controller.get_all_commands()
        for cmd in commands:
            cmd_type = "🆕" if cmd.get('custom', False) else "✅"
            self.commands_tree.insert('', 'end', values=(
                cmd_type,
                cmd.get('command_id', ''),
                cmd.get('description', '')
            ))
        
        # Mettre à jour le compteur (style hack)
        self.status_commands.config(text=f"📚 ARSENAL: [{len(commands)}]")
    
    def filter_commands(self, event=None):
        """Filtre les commandes selon la recherche."""
        search_text = self.search_entry.get()
        
        # Ignorer si c'est le placeholder
        if search_text == self.search_placeholder:
            return
            
        # TODO: Implémenter le filtrage réel
        # Pour l'instant, on peut juste afficher le texte de recherche
        if search_text:
            print(f"Recherche: {search_text}")
    
    def on_search_focus_in(self, event):
        """Gestionnaire quand le champ de recherche reçoit le focus."""
        if self.search_entry.get() == self.search_placeholder:
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(foreground='black')
    
    def on_search_focus_out(self, event):
        """Gestionnaire quand le champ de recherche perd le focus."""
        if not self.search_entry.get():
            self.search_entry.insert(0, self.search_placeholder)
            self.search_entry.config(foreground='grey')
    
    def edit_command(self):
        """Modifie une commande sélectionnée."""
        selection = self.commands_tree.selection()
        if not selection:
            messagebox.showwarning("Sélection", "Veuillez sélectionner une commande à modifier")
            return
        # TODO: Implémenter l'édition
    
    def delete_command(self):
        """Supprime une commande sélectionnée."""
        selection = self.commands_tree.selection()
        if not selection:
            messagebox.showwarning("Sélection", "Veuillez sélectionner une commande à supprimer")
            return
        # TODO: Implémenter la suppression
    
    def test_command(self):
        """Teste une commande sélectionnée."""
        selection = self.commands_tree.selection()
        if not selection:
            messagebox.showwarning("Sélection", "Veuillez sélectionner une commande à tester")
            return
        # TODO: Implémenter le test
    
    def check_similarity(self):
        """Vérifie la similarité de la nouvelle commande."""
        description = self.desc_entry.get().strip()
        if not description:
            messagebox.showwarning("Description", "Veuillez saisir une description")
            return
        
        if not self.voice_controller:
            messagebox.showwarning("Erreur", "Contrôleur vocal non initialisé")
            return
        
        try:
            # Générer l'embedding
            embedding = self.voice_controller.embedding_generator.generate_embedding(description)
            
            # Rechercher des commandes similaires
            similar = self.voice_controller.vector_db.search_similar_commands(
                embedding, n_results=3, min_similarity=0.3
            )
            
            if similar:
                best_match = similar[0]
                similarity = best_match['similarity']
                self.similarity_label.config(
                    text=f"Similarité max: {similarity:.2f} avec '{best_match['description']}'"
                )
                
                if similarity > 0.8:
                    messagebox.showwarning("Similarité élevée", 
                                         f"Cette commande est très similaire à '{best_match['description']}' "
                                         f"(similarité: {similarity:.2f})")
            else:
                self.similarity_label.config(text="Aucune commande similaire trouvée")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du test de similarité: {str(e)}")
    
    def save_new_command(self):
        """Sauvegarde une nouvelle commande."""
        description = self.desc_entry.get().strip()
        code = self.code_text.get(1.0, tk.END).strip()
        
        if not description or not code:
            messagebox.showwarning("Données incomplètes", 
                                 "Veuillez saisir une description et du code")
            return
        
        if not self.voice_controller:
            messagebox.showwarning("Erreur", "Contrôleur vocal non initialisé")
            return
        
        try:
            # Générer un ID unique
            import time
            command_id = f"custom_{int(time.time())}"
            
            # Ajouter la commande
            self.voice_controller.add_new_command(command_id, description, code)
            
            # Recharger la liste
            self.load_commands()
            
            # Effacer les champs
            self.clear_new_command()
            
            messagebox.showinfo("Succès", "Commande ajoutée avec succès!")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {str(e)}")
    
    def test_new_command(self):
        """Teste la nouvelle commande."""
        code = self.code_text.get(1.0, tk.END).strip()
        
        if not code:
            messagebox.showwarning("Code manquant", "Veuillez saisir du code à tester")
            return
        
        if not self.thymio_controller:
            messagebox.showwarning("Erreur", "Robot Thymio non connecté")
            return
        
        def test_code():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    result = loop.run_until_complete(self.thymio_controller.execute_code(code))
                    if result:
                        self.root.after(0, lambda: messagebox.showinfo("Test", "Code exécuté avec succès!"))
                    else:
                        self.root.after(0, lambda: messagebox.showerror("Test", "Erreur lors de l'exécution du code"))
                finally:
                    loop.close()
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Erreur", f"Erreur lors du test: {str(e)}"))
        
        # Exécuter dans un thread séparé
        thread = threading.Thread(target=test_code)
        thread.daemon = True
        thread.start()
    
    def clear_new_command(self):
        """Efface les champs de nouvelle commande."""
        self.desc_entry.delete(0, tk.END)
        self.code_text.delete(1.0, tk.END)
        self.similarity_label.config(text="Aucun test effectué")
    
    def insert_template(self, template_name):
        """Insère un template de code."""
        templates = self.config.get('templates', {})
        
        # Templates par défaut si pas dans la config
        default_templates = {
            "Mouvement": "motor.left.target = 200\nmotor.right.target = 200",
            "Rotation": "motor.left.target = -100\nmotor.right.target = 100",
            "Capteurs": "call prox.horizontal\nif prox.horizontal[2] > 1000 then\n  motor.left.target = 0\n  motor.right.target = 0\nend",
            "LEDs": "call leds.top(32, 32, 32)",
            "Sons": "call sound.freq(440, 100)",
            "Temporisateurs": "timer.period[0] = 1000"
        }
        
        # Chercher d'abord dans la config, puis dans les templates par défaut
        template_code = ""
        for template_key, template_data in templates.items():
            if template_data.get('name') == template_name:
                template_code = template_data.get('code', '')
                break
        
        if not template_code:
            template_code = default_templates.get(template_name, "")
        
        if template_code:
            current_pos = self.code_text.index(tk.INSERT)
            self.code_text.insert(current_pos, template_code + "\n")
            
            # Ajouter des suggestions dans la zone assistant
            self.update_suggestions(template_name)
    
    def update_suggestions(self, template_name):
        """Met à jour les suggestions en fonction du template sélectionné."""
        suggestions = {
            "Mouvement": [
                "• Ajustez les valeurs target pour changer la vitesse",
                "• Valeurs positives = avancer, négatives = reculer",
                "• Utilisez des valeurs différentes pour courber la trajectoire"
            ],
            "Rotation": [
                "• Moteur gauche négatif + moteur droit positif = rotation gauche", 
                "• Inversez les signes pour tourner à droite",
                "• Diminuez les valeurs pour une rotation plus lente"
            ],
            "Capteurs": [
                "• prox.horizontal[2] = capteur central avant",
                "• Valeurs > 1000 indiquent un obstacle proche",
                "• Utilisez différents indices [0-6] pour autres capteurs"
            ],
            "LEDs": [
                "• leds.top(rouge, vert, bleu) avec valeurs 0-32",
                "• leds.circle pour les LEDs circulaires",
                "• leds.buttons pour les LEDs des boutons"
            ],
            "Sons": [
                "• sound.freq(fréquence, durée) en Hz et 1/10 secondes",
                "• 440 Hz = note La, 880 Hz = La aigu",
                "• sound.system pour les sons système prédéfinis"
            ],
            "Temporisateurs": [
                "• timer.period[0] définit l'intervalle en ms",
                "• Utilisez onevent timer0 pour déclencher des actions",
                "• timer.period[0] = 0 pour arrêter le timer"
            ]
        }
        
        template_suggestions = suggestions.get(template_name, ["Template inséré avec succès"])
        
        self.suggestions_text.config(state='normal')
        self.suggestions_text.delete(1.0, tk.END)
        self.suggestions_text.insert(tk.END, f"💡 Suggestions pour {template_name}:\n\n")
        for suggestion in template_suggestions:
            self.suggestions_text.insert(tk.END, f"{suggestion}\n")
        self.suggestions_text.config(state='disabled')
    
    def save_config(self):
        """Sauvegarde la configuration actuelle."""
        config_path = Path(__file__).parent / "config.json"
        
        # Mettre à jour les seuils dans la config
        self.config['voice']['execution_threshold'] = self.execution_threshold.get()
        self.config['voice']['learning_threshold'] = self.learning_threshold.get()
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Erreur lors de la sauvegarde de la config: {e}")
    
    def on_closing(self):
        """Gestionnaire de fermeture de l'application."""
        # Sauvegarder la configuration
        self.save_config()
        
        # Arrêter l'écoute vocale si active
        if self.is_listening:
            self.stop_listening()
        
        # Déconnecter le robot
        if self.thymio_controller:
            def disconnect():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    try:
                        loop.run_until_complete(self.thymio_controller.disconnect())
                    finally:
                        loop.close()
                except:
                    pass
            
            # Déconnexion rapide dans un thread
            thread = threading.Thread(target=disconnect)
            thread.daemon = True
            thread.start()
            thread.join(timeout=2)  # Attendre max 2 secondes
        
        # Fermer l'application
        self.root.destroy()
    
    def open_documentation(self):
        """Ouvre la documentation Aseba."""
        import webbrowser
        webbrowser.open("https://www.thymio.org/programming/")
    
    def execute_quick_command(self, command):
        """Exécute une commande rapide."""
        if not self.voice_controller:
            messagebox.showwarning("Erreur", "Contrôleur vocal non initialisé")
            return
        
        def execute_command():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    result = loop.run_until_complete(self.voice_controller.process_command(command))
                    
                    # Afficher le résultat dans la zone de feedback
                    def update_feedback():
                        self.command_text.config(state='normal')
                        self.command_text.insert(tk.END, f"\n> {command}\n")
                        self.command_text.insert(tk.END, f"Résultat: {result['status']} - {result['message']}\n")
                        self.command_text.see(tk.END)
                        self.command_text.config(state='disabled')
                    
                    self.root.after(0, update_feedback)
                    
                finally:
                    loop.close()
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Erreur", f"Erreur lors de l'exécution: {str(e)}"))
        
        # Exécuter dans un thread séparé
        thread = threading.Thread(target=execute_command)
        thread.daemon = True
        thread.start()
    
    def run(self):
        """Lance l'interface graphique."""
        # Configurer le gestionnaire de fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("Application fermée par l'utilisateur")
            self.on_closing()
        finally:
            # Nettoyage final
            pass


def main():
    """Point d'entrée principal de l'application."""
    try:
        app = VoxThymioGUI()
        app.run()
    except Exception as e:
        print(f"Erreur fatale: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
