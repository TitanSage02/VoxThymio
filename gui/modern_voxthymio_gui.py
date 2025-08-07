"""
Interface graphique moderne pour VoxThymio avec gestion dynamique des commandes
Permet d'ajouter, modifier et supprimer des commandes via embeddings BERT.

Développé par Espérance AYIWAHOUN pour AI4Innov
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import asyncio
import threading
from typing import Dict, Any, List
import json
from pathlib import Path

from src.smart_voice_controller import SmartVoiceController
from src.communication.thymio_controller import ThymioController


class ModernVoxThymioGUI:
    """
    Interface graphique moderne pour VoxThymio avec système d'embeddings.
    """
    
    def __init__(self):
        """Initialise l'interface graphique."""
        self.root = tk.Tk()
        self.root.title("VoxThymio - Contrôle Intelligent")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Configuration du style
        self.setup_styles()
        
        # Contrôleurs
        self.thymio_controller = None
        self.voice_controller = None
        self.is_connected = False
        
        # Variables d'interface
        self.connection_status = tk.StringVar(value="❌ Déconnecté")
        self.last_command = tk.StringVar(value="Aucune commande")
        self.similarity_threshold = tk.DoubleVar(value=0.6)
        
        # Interface
        self.create_interface()
        
        # Initialisation asynchrone
        self.setup_async_environment()
    
    def setup_styles(self):
        """Configure les styles de l'interface."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Couleurs modernes
        colors = {
            'bg': '#2b2b2b',
            'fg': '#ffffff',
            'select_bg': '#0078d4',
            'accent': '#00d7ff',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'error': '#ff4444'
        }
        
        # Configuration des styles
        style.configure('Modern.TFrame', background=colors['bg'])
        style.configure('Modern.TLabel', background=colors['bg'], foreground=colors['fg'])
        style.configure('Modern.TButton', background=colors['select_bg'], foreground=colors['fg'])
        style.configure('Success.TButton', background=colors['success'], foreground='#000000')
        style.configure('Warning.TButton', background=colors['warning'], foreground='#000000')
        style.configure('Error.TButton', background=colors['error'], foreground=colors['fg'])
    
    def create_interface(self):
        """Crée l'interface utilisateur complète."""
        # Frame principal
        main_frame = ttk.Frame(self.root, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # En-tête
        self.create_header(main_frame)
        
        # Corps principal avec onglets
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True, pady=(10, 0))
        
        # Onglets
        self.create_control_tab(notebook)
        self.create_commands_tab(notebook)
        self.create_learning_tab(notebook)
        self.create_stats_tab(notebook)
    
    def create_header(self, parent):
        """Crée l'en-tête de l'application."""
        header_frame = ttk.Frame(parent, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 10))
        
        # Titre
        title_label = ttk.Label(
            header_frame, 
            text="🤖 VoxThymio - Intelligence Artificielle",
            font=('Arial', 18, 'bold'),
            style='Modern.TLabel'
        )
        title_label.pack(side='left')
        
        # État de connexion
        status_frame = ttk.Frame(header_frame, style='Modern.TFrame')
        status_frame.pack(side='right')
        
        ttk.Label(status_frame, text="État:", style='Modern.TLabel').pack(side='left')
        status_label = ttk.Label(
            status_frame, 
            textvariable=self.connection_status,
            font=('Arial', 10, 'bold'),
            style='Modern.TLabel'
        )
        status_label.pack(side='left', padx=(5, 0))
        
        # Bouton de connexion
        self.connect_btn = ttk.Button(
            status_frame,
            text="Connecter",
            command=self.toggle_connection,
            style='Modern.TButton'
        )
        self.connect_btn.pack(side='left', padx=(10, 0))
    
    def create_control_tab(self, notebook):
        """Crée l'onglet de contrôle vocal."""
        control_frame = ttk.Frame(notebook, style='Modern.TFrame')
        notebook.add(control_frame, text="🎤 Contrôle Vocal")
        
        # Section de commande vocale
        voice_frame = ttk.LabelFrame(control_frame, text="Commande Vocale", style='Modern.TFrame')
        voice_frame.pack(fill='x', padx=10, pady=10)
        
        # Saisie de commande
        ttk.Label(voice_frame, text="Tapez votre commande:", style='Modern.TLabel').pack(anchor='w', padx=10, pady=(10, 5))
        
        command_frame = ttk.Frame(voice_frame, style='Modern.TFrame')
        command_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.command_entry = ttk.Entry(command_frame, font=('Arial', 12))
        self.command_entry.pack(side='left', fill='x', expand=True)
        self.command_entry.bind('<Return>', lambda e: self.process_voice_command())
        
        ttk.Button(
            command_frame,
            text="Exécuter",
            command=self.process_voice_command,
            style='Success.TButton'
        ).pack(side='right', padx=(10, 0))
        
        # Seuil de similarité
        threshold_frame = ttk.Frame(voice_frame, style='Modern.TFrame')
        threshold_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(threshold_frame, text="Seuil de similarité:", style='Modern.TLabel').pack(side='left')
        threshold_scale = ttk.Scale(
            threshold_frame,
            from_=0.1,
            to=1.0,
            variable=self.similarity_threshold,
            orient='horizontal'
        )
        threshold_scale.pack(side='left', fill='x', expand=True, padx=(10, 10))
        
        threshold_label = ttk.Label(threshold_frame, text="0.60", style='Modern.TLabel')
        threshold_label.pack(side='right')
        
        # Mise à jour du label du seuil
        def update_threshold_label(*args):
            threshold_label.config(text=f"{self.similarity_threshold.get():.2f}")
        self.similarity_threshold.trace('w', update_threshold_label)
        
        # Résultats
        results_frame = ttk.LabelFrame(control_frame, text="Résultats", style='Modern.TFrame')
        results_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            height=15,
            bg='#1e1e1e',
            fg='#ffffff',
            font=('Consolas', 10)
        )
        self.results_text.pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_commands_tab(self, notebook):
        """Crée l'onglet de gestion des commandes."""
        commands_frame = ttk.Frame(notebook, style='Modern.TFrame')
        notebook.add(commands_frame, text="⚙️ Commandes")
        
        # Section d'ajout de commande
        add_frame = ttk.LabelFrame(commands_frame, text="Ajouter une Nouvelle Commande", style='Modern.TFrame')
        add_frame.pack(fill='x', padx=10, pady=10)
        
        # Grille pour les champs
        add_grid = ttk.Frame(add_frame, style='Modern.TFrame')
        add_grid.pack(fill='x', padx=10, pady=10)
        
        # ID de commande
        ttk.Label(add_grid, text="ID Commande:", style='Modern.TLabel').grid(row=0, column=0, sticky='w', pady=5)
        self.cmd_id_entry = ttk.Entry(add_grid, font=('Arial', 10))
        self.cmd_id_entry.grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        # Description
        ttk.Label(add_grid, text="Description:", style='Modern.TLabel').grid(row=1, column=0, sticky='w', pady=5)
        self.cmd_desc_entry = ttk.Entry(add_grid, font=('Arial', 10))
        self.cmd_desc_entry.grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        # Catégorie
        ttk.Label(add_grid, text="Catégorie:", style='Modern.TLabel').grid(row=2, column=0, sticky='w', pady=5)
        self.cmd_category_combo = ttk.Combobox(
            add_grid,
            values=["custom", "movement", "lights", "sounds", "advanced"],
            font=('Arial', 10)
        )
        self.cmd_category_combo.set("custom")
        self.cmd_category_combo.grid(row=2, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        add_grid.columnconfigure(1, weight=1)
        
        # Code Thymio
        ttk.Label(add_frame, text="Code Thymio:", style='Modern.TLabel').pack(anchor='w', padx=10, pady=(10, 5))
        self.cmd_code_text = scrolledtext.ScrolledText(
            add_frame,
            height=5,
            bg='#1e1e1e',
            fg='#ffffff',
            font=('Consolas', 10)
        )
        self.cmd_code_text.pack(fill='x', padx=10, pady=(0, 10))
        
        # Boutons
        btn_frame = ttk.Frame(add_frame, style='Modern.TFrame')
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(
            btn_frame,
            text="Ajouter Commande",
            command=self.add_new_command,
            style='Success.TButton'
        ).pack(side='left')
        
        ttk.Button(
            btn_frame,
            text="Tester Code",
            command=self.test_command_code,
            style='Warning.TButton'
        ).pack(side='left', padx=(10, 0))
        
        ttk.Button(
            btn_frame,
            text="Effacer",
            command=self.clear_command_form,
            style='Modern.TButton'
        ).pack(side='right')
        
        # Liste des commandes existantes
        list_frame = ttk.LabelFrame(commands_frame, text="Commandes Existantes", style='Modern.TFrame')
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Treeview pour les commandes
        self.commands_tree = ttk.Treeview(
            list_frame,
            columns=('description', 'category', 'created_at'),
            show='tree headings'
        )
        
        self.commands_tree.heading('#0', text='ID Commande')
        self.commands_tree.heading('description', text='Description')
        self.commands_tree.heading('category', text='Catégorie')
        self.commands_tree.heading('created_at', text='Créé le')
        
        self.commands_tree.column('#0', width=150)
        self.commands_tree.column('description', width=300)
        self.commands_tree.column('category', width=100)
        self.commands_tree.column('created_at', width=150)
        
        # Scrollbar pour le treeview
        tree_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.commands_tree.yview)
        self.commands_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.commands_tree.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=10)
        tree_scroll.pack(side='right', fill='y', pady=10, padx=(0, 10))
        
        # Boutons de gestion
        manage_frame = ttk.Frame(list_frame, style='Modern.TFrame')
        manage_frame.pack(side='bottom', fill='x', padx=10, pady=10)
        
        ttk.Button(
            manage_frame,
            text="Actualiser",
            command=self.refresh_commands_list,
            style='Modern.TButton'
        ).pack(side='left')
        
        ttk.Button(
            manage_frame,
            text="Supprimer",
            command=self.delete_selected_command,
            style='Error.TButton'
        ).pack(side='right')
    
    def create_learning_tab(self, notebook):
        """Crée l'onglet d'apprentissage intelligent."""
        learning_frame = ttk.Frame(notebook, style='Modern.TFrame')
        notebook.add(learning_frame, text="🧠 Apprentissage")
        
        # Configuration des seuils
        config_frame = ttk.LabelFrame(learning_frame, text="Configuration de l'IA", style='Modern.TFrame')
        config_frame.pack(fill='x', padx=10, pady=10)
        
        # Seuils
        thresholds_frame = ttk.Frame(config_frame, style='Modern.TFrame')
        thresholds_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(thresholds_frame, text="Seuil d'exécution:", style='Modern.TLabel').grid(row=0, column=0, sticky='w', pady=5)
        self.exec_threshold_var = tk.DoubleVar(value=0.6)
        exec_scale = ttk.Scale(thresholds_frame, from_=0.1, to=1.0, variable=self.exec_threshold_var, orient='horizontal')
        exec_scale.grid(row=0, column=1, sticky='ew', padx=10, pady=5)
        self.exec_label = ttk.Label(thresholds_frame, text="0.60", style='Modern.TLabel')
        self.exec_label.grid(row=0, column=2, pady=5)
        
        ttk.Label(thresholds_frame, text="Seuil d'apprentissage:", style='Modern.TLabel').grid(row=1, column=0, sticky='w', pady=5)
        self.learn_threshold_var = tk.DoubleVar(value=0.85)
        learn_scale = ttk.Scale(thresholds_frame, from_=0.1, to=1.0, variable=self.learn_threshold_var, orient='horizontal')
        learn_scale.grid(row=1, column=1, sticky='ew', padx=10, pady=5)
        self.learn_label = ttk.Label(thresholds_frame, text="0.85", style='Modern.TLabel')
        self.learn_label.grid(row=1, column=2, pady=5)
        
        thresholds_frame.columnconfigure(1, weight=1)
        
        # Mise à jour des labels
        def update_exec_label(*args):
            self.exec_label.config(text=f"{self.exec_threshold_var.get():.2f}")
        def update_learn_label(*args):
            self.learn_label.config(text=f"{self.learn_threshold_var.get():.2f}")
        
        self.exec_threshold_var.trace('w', update_exec_label)
        self.learn_threshold_var.trace('w', update_learn_label)
        
        # Bouton d'application
        ttk.Button(
            config_frame,
            text="Appliquer les Seuils",
            command=self.update_thresholds,
            style='Success.TButton'
        ).pack(pady=10)
        
        # Section de test de similarité
        test_frame = ttk.LabelFrame(learning_frame, text="Test de Similarité", style='Modern.TFrame')
        test_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Entrée de test
        ttk.Label(test_frame, text="Phrase de test:", style='Modern.TLabel').pack(anchor='w', padx=10, pady=(10, 5))
        
        test_input_frame = ttk.Frame(test_frame, style='Modern.TFrame')
        test_input_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.test_entry = ttk.Entry(test_input_frame, font=('Arial', 12))
        self.test_entry.pack(side='left', fill='x', expand=True)
        
        ttk.Button(
            test_input_frame,
            text="Tester",
            command=self.test_similarity,
            style='Modern.TButton'
        ).pack(side='right', padx=(10, 0))
        
        # Résultats de similarité
        ttk.Label(test_frame, text="Résultats de similarité:", style='Modern.TLabel').pack(anchor='w', padx=10, pady=(10, 5))
        
        self.similarity_results = scrolledtext.ScrolledText(
            test_frame,
            height=10,
            bg='#1e1e1e',
            fg='#ffffff',
            font=('Consolas', 10)
        )
        self.similarity_results.pack(fill='both', expand=True, padx=10, pady=(0, 10))
    
    def create_stats_tab(self, notebook):
        """Crée l'onglet de statistiques."""
        stats_frame = ttk.Frame(notebook, style='Modern.TFrame')
        notebook.add(stats_frame, text="📊 Statistiques")
        
        # Statistiques générales
        general_frame = ttk.LabelFrame(stats_frame, text="Statistiques Générales", style='Modern.TFrame')
        general_frame.pack(fill='x', padx=10, pady=10)
        
        self.stats_text = scrolledtext.ScrolledText(
            general_frame,
            height=10,
            bg='#1e1e1e',
            fg='#ffffff',
            font=('Consolas', 10)
        )
        self.stats_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Boutons de gestion
        stats_btn_frame = ttk.Frame(general_frame, style='Modern.TFrame')
        stats_btn_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(
            stats_btn_frame,
            text="Actualiser",
            command=self.refresh_stats,
            style='Modern.TButton'
        ).pack(side='left')
        
        ttk.Button(
            stats_btn_frame,
            text="Exporter JSON",
            command=self.export_commands,
            style='Modern.TButton'
        ).pack(side='left', padx=(10, 0))
        
        ttk.Button(
            stats_btn_frame,
            text="Réinitialiser Base",
            command=self.reset_database,
            style='Error.TButton'
        ).pack(side='right')
    
    def setup_async_environment(self):
        """Configure l'environnement asynchrone."""
        self.loop = asyncio.new_event_loop()
        self.async_thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.async_thread.start()
    
    def _run_async_loop(self):
        """Exécute la boucle asynchrone dans un thread séparé."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    def run_async(self, coro):
        """Exécute une coroutine dans la boucle asynchrone."""
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future
    
    def toggle_connection(self):
        """Bascule la connexion avec Thymio."""
        if not self.is_connected:
            self.run_async(self._connect_thymio())
        else:
            self.run_async(self._disconnect_thymio())
    
    async def _connect_thymio(self):
        """Connecte à Thymio."""
        try:
            self.thymio_controller = ThymioController()
            await self.thymio_controller.connect()
            
            self.voice_controller = SmartVoiceController(self.thymio_controller)
            
            self.is_connected = True
            self.root.after(0, lambda: [
                self.connection_status.set("✅ Connecté"),
                self.connect_btn.config(text="Déconnecter"),
                self.log_message("🔗 Connexion établie avec Thymio", "success")
            ])
            
            # Actualiser la liste des commandes
            self.root.after(100, self.refresh_commands_list)
            self.root.after(200, self.refresh_stats)
            
        except Exception as e:
            self.root.after(0, lambda: [
                self.connection_status.set("❌ Erreur de connexion"),
                self.log_message(f"❌ Erreur de connexion: {str(e)}", "error")
            ])
    
    async def _disconnect_thymio(self):
        """Déconnecte de Thymio."""
        try:
            if self.thymio_controller:
                await self.thymio_controller.disconnect()
            
            self.thymio_controller = None
            self.voice_controller = None
            self.is_connected = False
            
            self.root.after(0, lambda: [
                self.connection_status.set("❌ Déconnecté"),
                self.connect_btn.config(text="Connecter"),
                self.log_message("🔌 Déconnexion de Thymio", "info")
            ])
            
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"❌ Erreur de déconnexion: {str(e)}", "error"))
    
    def process_voice_command(self):
        """Traite une commande vocale."""
        if not self.is_connected or not self.voice_controller:
            messagebox.showwarning("Attention", "Veuillez d'abord vous connecter à Thymio.")
            return
        
        command = self.command_entry.get().strip()
        if not command:
            return
        
        # Mise à jour du seuil
        if self.voice_controller:
            self.voice_controller.update_thresholds(execution_threshold=self.similarity_threshold.get())
        
        self.log_message(f"🎤 Commande reçue: '{command}'", "info")
        self.command_entry.delete(0, tk.END)
        
        # Traitement asynchrone
        future = self.run_async(self._process_command_async(command))
        
        # Callback pour traiter le résultat
        def handle_result():
            try:
                result = future.result(timeout=0.1)
                if result:
                    self._handle_command_result(result)
            except:
                self.root.after(100, handle_result)  # Réessayer plus tard
        
        self.root.after(100, handle_result)
    
    async def _process_command_async(self, command: str):
        """Traite une commande de manière asynchrone."""
        if self.voice_controller:
            return await self.voice_controller.process_voice_command(command)
        return None
    
    def _handle_command_result(self, result: Dict[str, Any]):
        """Gère le résultat d'une commande."""
        status = result.get('status', 'unknown')
        message = result.get('message', 'Pas de message')
        
        if status == 'success':
            self.log_message(f"✅ {message}", "success")
            if 'similarity' in result:
                self.log_message(f"   Similarité: {result['similarity']:.2f}", "info")
        elif status == 'unknown':
            self.log_message(f"❓ {message}", "warning")
            if 'suggestions' in result and result['suggestions']:
                self.log_message("   Suggestions:", "info")
                for suggestion in result['suggestions'][:3]:
                    self.log_message(f"   - {suggestion}", "info")
        elif status == 'error':
            self.log_message(f"❌ {message}", "error")
        else:
            self.log_message(f"ℹ️ {message}", "info")
    
    def add_new_command(self):
        """Ajoute une nouvelle commande."""
        if not self.voice_controller:
            messagebox.showwarning("Attention", "Veuillez d'abord vous connecter à Thymio.")
            return
        
        cmd_id = self.cmd_id_entry.get().strip()
        description = self.cmd_desc_entry.get().strip()
        code = self.cmd_code_text.get('1.0', tk.END).strip()
        category = self.cmd_category_combo.get()
        
        if not all([cmd_id, description, code]):
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires.")
            return
        
        result = self.voice_controller.add_new_command(cmd_id, description, code, category)
        
        if result['status'] == 'success':
            messagebox.showinfo("Succès", result['message'])
            self.clear_command_form()
            self.refresh_commands_list()
            self.log_message(f"➕ Commande '{cmd_id}' ajoutée", "success")
        elif result['status'] == 'warning':
            response = messagebox.askyesno("Attention", f"{result['message']}\\n\\nVoulez-vous continuer ?")
            if response:
                # Forcer l'ajout en modifiant légèrement l'ID
                new_id = f"{cmd_id}_v2"
                result = self.voice_controller.add_new_command(new_id, description, code, category)
                if result['status'] == 'success':
                    messagebox.showinfo("Succès", f"Commande ajoutée avec l'ID '{new_id}'")
                    self.clear_command_form()
                    self.refresh_commands_list()
        else:
            messagebox.showerror("Erreur", result['message'])
    
    def test_command_code(self):
        """Teste le code d'une commande."""
        if not self.is_connected or not self.thymio_controller:
            messagebox.showwarning("Attention", "Veuillez d'abord vous connecter à Thymio.")
            return
        
        code = self.cmd_code_text.get('1.0', tk.END).strip()
        if not code:
            messagebox.showwarning("Attention", "Veuillez saisir du code à tester.")
            return
        
        self.log_message(f"🧪 Test du code: {code[:50]}...", "info")
        future = self.run_async(self._test_code_async(code))
        
        def handle_test_result():
            try:
                success = future.result(timeout=0.1)
                if success:
                    self.log_message("✅ Code testé avec succès", "success")
                    messagebox.showinfo("Test", "Code exécuté avec succès sur Thymio !")
                else:
                    self.log_message("❌ Échec du test du code", "error")
                    messagebox.showerror("Test", "Échec de l'exécution du code.")
            except:
                self.root.after(100, handle_test_result)
        
        self.root.after(100, handle_test_result)
    
    async def _test_code_async(self, code: str):
        """Teste du code de manière asynchrone."""
        if self.thymio_controller:
            return await self.thymio_controller.execute_code(code)
        return False
    
    def clear_command_form(self):
        """Efface le formulaire de commande."""
        self.cmd_id_entry.delete(0, tk.END)
        self.cmd_desc_entry.delete(0, tk.END)
        self.cmd_code_text.delete('1.0', tk.END)
        self.cmd_category_combo.set("custom")
    
    def refresh_commands_list(self):
        """Actualise la liste des commandes."""
        if not self.voice_controller:
            return
        
        # Vider le treeview
        for item in self.commands_tree.get_children():
            self.commands_tree.delete(item)
        
        # Récupérer et afficher les commandes
        commands = self.voice_controller.get_all_commands()
        for cmd in commands:
            created_at = cmd.get('created_at', 'N/A')
            if created_at and 'T' in created_at:
                created_at = created_at.split('T')[0]  # Garder seulement la date
            
            self.commands_tree.insert(
                '',
                'end',
                text=cmd['command_id'],
                values=(
                    cmd['description'][:50] + '...' if len(cmd['description']) > 50 else cmd['description'],
                    cmd['category'],
                    created_at
                )
            )
    
    def delete_selected_command(self):
        """Supprime la commande sélectionnée."""
        selection = self.commands_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une commande à supprimer.")
            return
        
        if not self.voice_controller:
            return
        
        item = selection[0]
        command_id = self.commands_tree.item(item, 'text')
        
        if messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir supprimer la commande '{command_id}' ?"):
            result = self.voice_controller.delete_command(command_id)
            if result['status'] == 'success':
                messagebox.showinfo("Succès", result['message'])
                self.refresh_commands_list()
                self.log_message(f"🗑️ Commande '{command_id}' supprimée", "info")
            else:
                messagebox.showerror("Erreur", result['message'])
    
    def update_thresholds(self):
        """Met à jour les seuils de l'IA."""
        if not self.voice_controller:
            messagebox.showwarning("Attention", "Veuillez d'abord vous connecter à Thymio.")
            return
        
        exec_threshold = self.exec_threshold_var.get()
        learn_threshold = self.learn_threshold_var.get()
        
        result = self.voice_controller.update_thresholds(exec_threshold, learn_threshold)
        
        if result['status'] == 'success':
            messagebox.showinfo("Succès", "Seuils mis à jour avec succès.")
            self.log_message(f"⚙️ Seuils mis à jour - Exécution: {exec_threshold:.2f}, Apprentissage: {learn_threshold:.2f}", "info")
        else:
            messagebox.showerror("Erreur", result['message'])
    
    def test_similarity(self):
        """Teste la similarité d'une phrase."""
        if not self.voice_controller:
            messagebox.showwarning("Attention", "Veuillez d'abord vous connecter à Thymio.")
            return
        
        test_text = self.test_entry.get().strip()
        if not test_text:
            return
        
        try:
            # Générer l'embedding de la phrase de test
            embedding_manager = self.voice_controller.embedding_manager
            vector_db = self.voice_controller.vector_db
            
            query_embedding = embedding_manager.generate_embedding(test_text)
            similar_commands = vector_db.search_similar_commands(query_embedding, n_results=5, min_similarity=0.1)
            
            # Afficher les résultats
            self.similarity_results.delete('1.0', tk.END)
            self.similarity_results.insert(tk.END, f"Phrase testée: '{test_text}'\\n\\n")
            self.similarity_results.insert(tk.END, "Commandes similaires trouvées:\\n")
            self.similarity_results.insert(tk.END, "=" * 50 + "\\n\\n")
            
            if similar_commands:
                for i, cmd in enumerate(similar_commands, 1):
                    similarity = cmd['similarity']
                    status = "🟢 EXÉCUTION" if similarity >= self.voice_controller.EXECUTION_THRESHOLD else "🟡 SUGGESTION"
                    
                    self.similarity_results.insert(tk.END, f"{i}. {cmd['command_id']} ({status})\\n")
                    self.similarity_results.insert(tk.END, f"   Description: {cmd['description']}\\n")
                    self.similarity_results.insert(tk.END, f"   Similarité: {similarity:.3f}\\n")
                    self.similarity_results.insert(tk.END, f"   Catégorie: {cmd['category']}\\n\\n")
            else:
                self.similarity_results.insert(tk.END, "Aucune commande similaire trouvée.\\n")
            
        except Exception as e:
            self.similarity_results.delete('1.0', tk.END)
            self.similarity_results.insert(tk.END, f"Erreur lors du test: {str(e)}")
    
    def refresh_stats(self):
        """Actualise les statistiques."""
        if not self.voice_controller:
            return
        
        try:
            stats = self.voice_controller.get_system_stats()
            
            self.stats_text.delete('1.0', tk.END)
            self.stats_text.insert(tk.END, "📊 STATISTIQUES VOXTHYMIO\\n")
            self.stats_text.insert(tk.END, "=" * 40 + "\\n\\n")
            
            # Statistiques de la base
            db_stats = stats.get('database', {})
            self.stats_text.insert(tk.END, "🗄️ BASE VECTORIELLE\\n")
            self.stats_text.insert(tk.END, f"   Total commandes: {db_stats.get('total_commands', 0)}\\n")
            
            categories = db_stats.get('categories', {})
            if categories:
                self.stats_text.insert(tk.END, "   Catégories:\\n")
                for cat, count in categories.items():
                    self.stats_text.insert(tk.END, f"     - {cat}: {count}\\n")
            
            self.stats_text.insert(tk.END, f"   Chemin: {db_stats.get('db_path', 'N/A')}\\n\\n")
            
            # Statistiques du modèle
            model_stats = stats.get('embedding_model', {})
            self.stats_text.insert(tk.END, "🧠 MODÈLE D'EMBEDDING\\n")
            self.stats_text.insert(tk.END, f"   Modèle: {model_stats.get('model_name', 'N/A')}\\n")
            self.stats_text.insert(tk.END, f"   Dimension: {model_stats.get('embedding_dim', 'N/A')}\\n")
            self.stats_text.insert(tk.END, f"   Périphérique: {model_stats.get('device', 'N/A')}\\n")
            self.stats_text.insert(tk.END, f"   Vocabulaire: {model_stats.get('vocab_size', 'N/A')}\\n\\n")
            
            # Seuils actuels
            thresholds = stats.get('thresholds', {})
            self.stats_text.insert(tk.END, "⚙️ CONFIGURATION IA\\n")
            self.stats_text.insert(tk.END, f"   Seuil d'exécution: {thresholds.get('execution', 'N/A')}\\n")
            self.stats_text.insert(tk.END, f"   Seuil d'apprentissage: {thresholds.get('learning', 'N/A')}\\n\\n")
            
            # État de connexion
            self.stats_text.insert(tk.END, "🔗 CONNEXION\\n")
            self.stats_text.insert(tk.END, f"   Thymio: {'✅ Connecté' if self.is_connected else '❌ Déconnecté'}\\n")
            
        except Exception as e:
            self.stats_text.delete('1.0', tk.END)
            self.stats_text.insert(tk.END, f"Erreur lors de la récupération des statistiques: {str(e)}")
    
    def export_commands(self):
        """Exporte les commandes en JSON."""
        if not self.voice_controller:
            messagebox.showwarning("Attention", "Veuillez d'abord vous connecter à Thymio.")
            return
        
        try:
            commands = self.voice_controller.get_all_commands()
            
            export_data = {
                'export_date': str(np.datetime64('now')),
                'total_commands': len(commands),
                'commands': commands
            }
            
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Exporter les commandes"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("Succès", f"Commandes exportées vers {filename}")
                self.log_message(f"📤 Commandes exportées vers {filename}", "success")
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export: {str(e)}")
    
    def reset_database(self):
        """Remet à zéro la base vectorielle."""
        if not self.voice_controller:
            messagebox.showwarning("Attention", "Veuillez d'abord vous connecter à Thymio.")
            return
        
        if messagebox.askyesno(
            "ATTENTION", 
            "Cette action supprimera TOUTES les commandes de la base vectorielle.\\n\\n"
            "Cette action est IRRÉVERSIBLE.\\n\\n"
            "Êtes-vous absolument sûr de vouloir continuer ?"
        ):
            try:
                if self.voice_controller.vector_db.reset_database():
                    messagebox.showinfo("Succès", "Base vectorielle remise à zéro.")
                    self.refresh_commands_list()
                    self.refresh_stats()
                    self.log_message("🔄 Base vectorielle remise à zéro", "warning")
                    
                    # Recharger les commandes par défaut
                    self.voice_controller._load_default_commands()
                    self.refresh_commands_list()
                    self.log_message("✅ Commandes par défaut rechargées", "success")
                else:
                    messagebox.showerror("Erreur", "Échec de la remise à zéro.")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur: {str(e)}")
    
    def log_message(self, message: str, level: str = "info"):
        """Ajoute un message au log."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        colors = {
            "info": "#ffffff",
            "success": "#00ff88",
            "warning": "#ffaa00",
            "error": "#ff4444"
        }
        
        self.results_text.insert(tk.END, f"[{timestamp}] {message}\\n")
        self.results_text.see(tk.END)
    
    def run(self):
        """Lance l'interface graphique."""
        try:
            print("🚀 Démarrage de VoxThymio GUI...")
            self.refresh_stats()  # Chargement initial des stats
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\\n👋 Arrêt de l'application...")
        finally:
            if hasattr(self, 'loop') and self.loop.is_running():
                self.loop.call_soon_threadsafe(self.loop.stop)


def main():
    """Point d'entrée principal."""
    app = ModernVoxThymioGUI()
    app.run()


if __name__ == "__main__":
    main()
