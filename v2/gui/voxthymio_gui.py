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
import sys
from pathlib import Path
import time
from datetime import datetime

# Ajout du chemin racine
sys.path.append(str(Path(__file__).parent))

from src.communication.thymio_controller import ThymioController
from src.voice_controller import VoiceController, VoiceCommandStatus

MODEL_PATH = Path(__file__).parent.parent / "models"

class VoxThymioGUI:
    """Interface graphique moderne pour VoxThymio."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.controller = None
        self.voice_controller = None
        self.voice_mode = False
        self.voice_thread = None
        self.voice_active = False
        
        self.setup_window()
        self.create_widgets()
        self.setup_async()
    
    def setup_window(self):
        """Configure la fenêtre principale."""
        self.root.title("VoxThymio - Contrôle Vocal Intelligent")
        self.root.geometry("900x700")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(True, True)
        
        # Style moderne
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configuration des couleurs
        style.configure('Title.TLabel', 
                       background="#1e1e1e", 
                       foreground="#00d4aa", 
                       font=("Segoe UI", 20, "bold"))
        
        style.configure('Header.TLabel', 
                       background="#1e1e1e", 
                       foreground="#ffffff", 
                       font=("Segoe UI", 12, "bold"))
        
        style.configure('Status.TLabel', 
                       background="#1e1e1e", 
                       foreground="#ffd700", 
                       font=("Segoe UI", 10))
        
        style.configure('Modern.TButton', 
                       background="#00d4aa", 
                       foreground="white", 
                       font=("Segoe UI", 10, "bold"),
                       relief="flat")
        
        style.map('Modern.TButton',
                 background=[('active', '#00b894')])
        
        style.configure('Voice.TButton', 
                       background="#e74c3c", 
                       foreground="white", 
                       font=("Segoe UI", 12, "bold"),
                       relief="flat")
        
        # Icône
        try:
            self.root.iconbitmap(default="robot.ico")
        except:
            pass
    
    def create_widgets(self):
        """Crée tous les widgets de l'interface."""
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#1e1e1e")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # En-tête
        self.create_header(main_frame)
        
        # Colonnes principales
        left_frame = tk.Frame(main_frame, bg="#1e1e1e")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        right_frame = tk.Frame(main_frame, bg="#1e1e1e")
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Widgets de gauche
        self.create_connection_panel(left_frame)
        self.create_control_panel(left_frame)
        
        # Widgets de droite
        self.create_voice_panel(right_frame)
        self.create_log_panel(right_frame)
        
        # Pied de page
        self.create_footer(main_frame)
    
    def create_header(self, parent):
        """Crée l'en-tête de l'application."""
        header_frame = tk.Frame(parent, bg="#1e1e1e")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Logo et titre
        title_frame = tk.Frame(header_frame, bg="#1e1e1e")
        title_frame.pack(side="left")
        
        title_label = ttk.Label(title_frame, text="🤖 VoxThymio", style="Title.TLabel")
        title_label.pack()
        
        subtitle = ttk.Label(title_frame, 
                            text="Contrôle vocal intelligent pour le robot Thymio",
                            style="Status.TLabel")
        subtitle.pack()
        
        # Informations de développeur
        dev_frame = tk.Frame(header_frame, bg="#1e1e1e")
        dev_frame.pack(side="right")
        
        dev_label = ttk.Label(dev_frame, 
                             text="Développé par Espérance AYIWAHOUN",
                             style="Status.TLabel")
        dev_label.pack(anchor="e")
        
        company_label = ttk.Label(dev_frame, 
                                 text="AI4Innov",
                                 style="Header.TLabel")
        company_label.pack(anchor="e")
    
    def create_connection_panel(self, parent):
        """Panneau de connexion au robot."""
        frame = tk.LabelFrame(parent, text="🔌 Connexion robot", 
                             bg="#2d2d2d", fg="white", 
                             font=("Segoe UI", 10, "bold"))
        frame.pack(fill="x", pady=(0, 10))
        
        # Status de connexion
        self.connection_status = ttk.Label(frame, 
                                         text="❌ Non connecté",
                                         style="Status.TLabel")
        self.connection_status.pack(pady=5)
        
        # Boutons de connexion
        btn_frame = tk.Frame(frame, bg="#2d2d2d")
        btn_frame.pack(pady=5)
        
        self.connect_btn = ttk.Button(btn_frame, 
                                     text="Se connecter",
                                     style="Modern.TButton",
                                     command=self.connect_robot)
        self.connect_btn.pack(side="left", padx=5)
        
        self.disconnect_btn = ttk.Button(btn_frame, 
                                        text="Déconnecter",
                                        style="Modern.TButton",
                                        command=self.disconnect_robot,
                                        state="disabled")
        self.disconnect_btn.pack(side="left", padx=5)
    
    def create_control_panel(self, parent):
        """Panneau de contrôle manuel."""
        frame = tk.LabelFrame(parent, text="🎮 Contrôle manuel", 
                             bg="#2d2d2d", fg="white", 
                             font=("Segoe UI", 10, "bold"))
        frame.pack(fill="x", pady=(0, 10))
        
        # Boutons de mouvement
        movement_frame = tk.LabelFrame(frame, text="Mouvement", 
                                      bg="#2d2d2d", fg="white")
        movement_frame.pack(fill="x", padx=10, pady=5)
        
        # Grille de boutons de mouvement
        btn_grid = tk.Frame(movement_frame, bg="#2d2d2d")
        btn_grid.pack(pady=5)
        
        # Ligne 1: Avancer
        ttk.Button(btn_grid, text="⬆️ Avancer", 
                  command=lambda: self.manual_command("avancer"),
                  style="Modern.TButton").grid(row=0, column=1, padx=2, pady=2)
        
        # Ligne 2: Gauche, Stop, Droite
        ttk.Button(btn_grid, text="⬅️ Gauche", 
                  command=lambda: self.manual_command("tourner_gauche"),
                  style="Modern.TButton").grid(row=1, column=0, padx=2, pady=2)
        
        ttk.Button(btn_grid, text="⏹️ STOP", 
                  command=lambda: self.manual_command("arreter"),
                  style="Voice.TButton").grid(row=1, column=1, padx=2, pady=2)
        
        ttk.Button(btn_grid, text="➡️ Droite", 
                  command=lambda: self.manual_command("tourner_droite"),
                  style="Modern.TButton").grid(row=1, column=2, padx=2, pady=2)
        
        # Ligne 3: Reculer
        ttk.Button(btn_grid, text="⬇️ Reculer", 
                  command=lambda: self.manual_command("reculer"),
                  style="Modern.TButton").grid(row=2, column=1, padx=2, pady=2)
        
        # Boutons LED
        led_frame = tk.LabelFrame(frame, text="LEDs", 
                                 bg="#2d2d2d", fg="white")
        led_frame.pack(fill="x", padx=10, pady=5)
        
        led_grid = tk.Frame(led_frame, bg="#2d2d2d")
        led_grid.pack(pady=5)
        
        ttk.Button(led_grid, text="🔴 Rouge", 
                  command=lambda: self.manual_command("led_rouge"),
                  style="Modern.TButton").grid(row=0, column=0, padx=2, pady=2)
        
        ttk.Button(led_grid, text="🟢 Vert", 
                  command=lambda: self.manual_command("led_vert"),
                  style="Modern.TButton").grid(row=0, column=1, padx=2, pady=2)
        
        ttk.Button(led_grid, text="🔵 Bleu", 
                  command=lambda: self.manual_command("led_bleu"),
                  style="Modern.TButton").grid(row=0, column=2, padx=2, pady=2)
        
        ttk.Button(led_grid, text="⚫ Éteindre", 
                  command=lambda: self.manual_command("led_eteindre"),
                  style="Modern.TButton").grid(row=0, column=3, padx=2, pady=2)
    
    def create_voice_panel(self, parent):
        """Panneau de contrôle vocal."""
        frame = tk.LabelFrame(parent, text="🎤 Contrôle Vocal", 
                             bg="#2d2d2d", fg="white", 
                             font=("Segoe UI", 10, "bold"))
        frame.pack(fill="x", pady=(0, 10))
        
        # Status du microphone
        self.mic_status = ttk.Label(frame, 
                                   text="🎤 Microphone: En cours d'initialisation...",
                                   style="Status.TLabel")
        self.mic_status.pack(pady=5)
        
        # Bouton vocal principal
        self.voice_btn = ttk.Button(frame, 
                                   text="🎤 ACTIVER LE CONTRÔLE VOCAL",
                                   style="Voice.TButton",
                                   command=self.toggle_voice_mode)
        self.voice_btn.pack(pady=10, padx=20, fill="x")
        
        # Zone de commandes vocales
        commands_frame = tk.LabelFrame(frame, text="Commandes Disponibles", 
                                      bg="#2d2d2d", fg="white")
        commands_frame.pack(fill="x", padx=10, pady=5)
        
        commands_text = """
                🎯 MOUVEMENT: "avancer", "reculer", "gauche", "droite", "stop"
                💡 LEDs: "rouge", "vert", "bleu", "éteindre"
                🔧 SYSTÈME: "quitter"
                """.strip()
        
        commands_label = tk.Label(commands_frame, text=commands_text, 
                                 bg="#2d2d2d", fg="#00d4aa", 
                                 font=("Consolas", 9), justify="left")
        commands_label.pack(padx=10, pady=5)
        
        # Indicateur vocal
        self.voice_indicator = tk.Label(frame, 
                                       text="🔇 Mode vocal inactif", 
                                       bg="#2d2d2d", fg="#888888",
                                       font=("Segoe UI", 10, "bold"))
        self.voice_indicator.pack(pady=5)
    
    def create_log_panel(self, parent):
        """Panneau de logs."""
        frame = tk.LabelFrame(parent, text="📋 Journal d'Activité", 
                             bg="#2d2d2d", fg="white", 
                             font=("Segoe UI", 10, "bold"))
        frame.pack(fill="both", expand=True)
        
        # Zone de texte avec scroll
        self.log_text = scrolledtext.ScrolledText(frame, 
                                                 height=15, 
                                                 bg="#1a1a1a", 
                                                 fg="#00d4aa",
                                                 font=("Consolas", 9),
                                                 state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Bouton de nettoyage
        ttk.Button(frame, text="🗑️ Effacer les logs", 
                  command=self.clear_logs,
                  style="Modern.TButton").pack(pady=5)
    
    def create_footer(self, parent):
        """Pied de page avec informations."""
        footer_frame = tk.Frame(parent, bg="#1e1e1e")
        footer_frame.pack(fill="x", pady=(20, 0))
        
        # Ligne de séparation
        separator = tk.Frame(footer_frame, height=1, bg="#00d4aa")
        separator.pack(fill="x", pady=(0, 10))
        
        # Informations
        info_frame = tk.Frame(footer_frame, bg="#1e1e1e")
        info_frame.pack(fill="x")
        
        copyright_label = ttk.Label(info_frame, 
                                   text="© 2025 AI4Innov - VoxThymio v1.0",
                                   style="Status.TLabel")
        copyright_label.pack(side="left")
        
        self.time_label = ttk.Label(info_frame, 
                                   text=self.get_current_time(),
                                   style="Status.TLabel")
        self.time_label.pack(side="right")
        
        # Mise à jour de l'heure
        self.update_time()
    
    def setup_async(self):
        """Configure le support asynchrone."""
        self.loop = None
        self.async_thread = None
    
    def log_message(self, message, level="INFO"):
        """Ajoute un message au journal."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Couleurs selon le niveau
        colors = {
            "INFO": "#00d4aa",
            "WARNING": "#ffd700", 
            "ERROR": "#e74c3c",
            "SUCCESS": "#00ff88"
        }
        
        color = colors.get(level, "#ffffff")
        
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.config(state="disabled")
        self.log_text.see("end")
        
        # Mise à jour de l'interface
        self.root.update_idletasks()
    
    def clear_logs(self):
        """Efface le journal."""
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, "end")
        self.log_text.config(state="disabled")
        self.log_message("Journal effacé", "INFO")
    
    def get_current_time(self):
        """Retourne l'heure actuelle."""
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    def update_time(self):
        """Met à jour l'affichage de l'heure."""
        self.time_label.config(text=self.get_current_time())
        self.root.after(1000, self.update_time)
    
    def connect_robot(self):
        """Connecte le robot en arrière-plan."""
        self.log_message("🔌 Tentative de connexion au robot Thymio...", "INFO")
        self.connect_btn.config(state="disabled", text="Connexion...")
        
        def connect_async():
            async def do_connect():
                self.controller = ThymioController()
                success = await self.controller.connect()
                
                if success:
                    self.root.after(0, self.on_connection_success)
                else:
                    self.root.after(0, self.on_connection_failed)
            
            # Créer nouvelle boucle pour ce thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(do_connect())
            loop.close()
        
        threading.Thread(target=connect_async, daemon=True).start()
    
    def on_connection_success(self):
        """Callback de connexion réussie."""
        self.log_message("✅ Robot Thymio connecté avec succès !", "SUCCESS")
        self.connection_status.config(text="✅ Connecté", foreground="#00ff88")
        self.connect_btn.config(state="disabled", text="Connecté")
        self.disconnect_btn.config(state="normal")
        
        # Initialiser le contrôleur vocal
        self.init_voice_controller()
    
    def on_connection_failed(self):
        """Callback de connexion échouée."""
        self.log_message("❌ Échec de connexion au robot", "ERROR")
        self.log_message("   Vérifiez que Thymio Suite est lancé", "WARNING")
        self.connection_status.config(text="❌ Échec de connexion", foreground="#e74c3c")
        self.connect_btn.config(state="normal", text="Réessayer")
        
        messagebox.showerror("Erreur de connexion", 
                           "Impossible de se connecter au robot Thymio.\n"
                           "Vérifiez que Thymio Suite est lancé et le robot connecté.")
    
    def init_voice_controller(self):
        """Initialise le contrôleur vocal."""
        self.log_message("🎤 Initialisation du contrôleur vocal...", "INFO")
        
        try:
            self.voice_controller = VoiceController(intent_model_path=MODEL_PATH)
            
            if self.voice_controller.is_microphone_available():
                self.log_message("✅ Microphone détecté et configuré", "SUCCESS")
                self.mic_status.config(text="🎤 Microphone: ✅ Prêt", 
                                     foreground="#00ff88")
                self.voice_btn.config(state="normal")
            else:
                self.log_message("⚠️ Microphone non disponible", "WARNING")
                self.mic_status.config(text="🎤 Microphone: ❌ Indisponible", 
                                     foreground="#ffd700")
                self.voice_btn.config(state="disabled")
                
        except Exception as e:
            self.log_message(f"❌ Erreur d'initialisation vocale: {e}", "ERROR")
            self.mic_status.config(text="🎤 Microphone: ❌ Erreur", 
                                 foreground="#e74c3c")
    
    def disconnect_robot(self):
        """Déconnecte le robot."""
        self.log_message("🔌 Déconnexion du robot...", "INFO")
        
        # Arrêter le mode vocal
        if self.voice_mode:
            self.toggle_voice_mode()
        
        def disconnect_async():
            async def do_disconnect():
                if self.controller:
                    await self.controller.disconnect()
                self.root.after(0, self.on_disconnection_complete)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(do_disconnect())
            loop.close()
        
        threading.Thread(target=disconnect_async, daemon=True).start()
    
    def on_disconnection_complete(self):
        """Callback de déconnexion terminée."""
        self.log_message("👋 Robot déconnecté", "INFO")
        self.connection_status.config(text="❌ Non connecté", foreground="#888888")
        self.connect_btn.config(state="normal", text="Se connecter")
        self.disconnect_btn.config(state="disabled")
        self.voice_btn.config(state="disabled")
        self.mic_status.config(text="🎤 Microphone: En attente...", 
                             foreground="#888888")
    
    def manual_command(self, command):
        """Exécute une commande manuelle."""
        if not self.controller or not self.controller.is_connected():
            self.log_message("❌ Robot non connecté", "ERROR")
            messagebox.showerror("Erreur", "Robot non connecté !")
            return
        
        self.log_message(f"🎮 Commande manuelle: {command}", "INFO")
        
        def execute_async():
            async def do_execute():
                result = await self.controller.execute_command(command)
                message = f"✅ Commande '{command}' exécutée" if result else f"❌ Échec de '{command}'"
                level = "SUCCESS" if result else "ERROR"
                self.root.after(0, lambda: self.log_message(message, level))
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(do_execute())
            loop.close()
        
        threading.Thread(target=execute_async, daemon=True).start()
    
    def toggle_voice_mode(self):
        """Active/désactive le mode vocal."""
        if not self.voice_controller or not self.voice_controller.is_microphone_available():
            messagebox.showerror("Erreur", "Microphone non disponible !")
            return
        
        if not self.controller or not self.controller.is_connected():
            messagebox.showerror("Erreur", "Robot non connecté !")
            return
        
        self.voice_mode = not self.voice_mode
        
        if self.voice_mode:
            self.start_voice_mode()
        else:
            self.stop_voice_mode()
    
    def start_voice_mode(self):
        """Démarre le mode vocal."""
        self.log_message("🎤 Mode vocal activé", "SUCCESS")
        self.voice_btn.config(text="🔇 ARRÊTER LE CONTRÔLE VOCAL")
        self.voice_indicator.config(text="🎤 Mode vocal ACTIF - Parlez maintenant !", 
                                  foreground="#00ff88")
        
        self.voice_active = True
        self.voice_thread = threading.Thread(target=self.voice_listener, daemon=True)
        self.voice_thread.start()
    
    def stop_voice_mode(self):
        """Arrête le mode vocal."""
        self.log_message("🔇 Mode vocal désactivé", "INFO")
        self.voice_btn.config(text="🎤 ACTIVER LE CONTRÔLE VOCAL")
        self.voice_indicator.config(text="🔇 Mode vocal inactif", 
                                  foreground="#888888")
        
        self.voice_active = False
        if self.voice_thread:
            self.voice_thread.join(timeout=1)
    
    def voice_listener(self):
        """Thread d'écoute vocale."""
        # Créer boucle pour ce thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        while self.voice_active and self.voice_mode:
            try:
                self.root.after(0, lambda: self.voice_indicator.config(
                    text="🎤 Écoute en cours...", foreground="#ffd700"))
                
                command = self.voice_controller.listen_for_command()
                
                if not self.voice_active:
                    break
                
                if command.status == VoiceCommandStatus.SUCCESS:
                    self.root.after(0, lambda cmd=command: self.process_voice_command(cmd))
                elif command.status == VoiceCommandStatus.UNKNOWN_COMMAND:
                    self.root.after(0, lambda: self.log_message(
                        f"❓ Commande inconnue: '{command.text}'", "WARNING"))
                elif command.status == VoiceCommandStatus.TIMEOUT:
                    self.root.after(0, lambda: self.voice_indicator.config(
                        text="🎤 Timeout - Parlez maintenant !", foreground="#ffd700"))
                elif command.status == VoiceCommandStatus.NO_SPEECH:
                    self.root.after(0, lambda: self.voice_indicator.config(
                        text="🎤 Aucune parole - Réessayez !", foreground="#ffd700"))
                
                time.sleep(0.1)
                
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"❌ Erreur vocale: {e}", "ERROR"))
                time.sleep(1)
        
        loop.close()
        
        # Remettre l'indicateur à l'état normal
        if not self.voice_mode:
            self.root.after(0, lambda: self.voice_indicator.config(
                text="🔇 Mode vocal inactif", foreground="#888888"))
    
    def process_voice_command(self, command):
        """Traite une commande vocale reconnue."""
        self.log_message(f"🎤 Commande vocale: '{command.text}'", "SUCCESS")
        self.voice_indicator.config(text="🎤 Commande reconnue !", foreground="#00ff88")
        
        if command.command_key == "quitter":
            self.voice_mode = False
            self.stop_voice_mode()
            return
        
        # Exécuter la commande
        def execute_voice_command():
            async def do_execute():
                result = await self.controller.execute_command(command.command_key)
                message = f"✅ '{command.command_key}' exécutée" if result else f"❌ Échec de '{command.command_key}'"
                level = "SUCCESS" if result else "ERROR"
                self.root.after(0, lambda: self.log_message(message, level))
                
                # Remettre l'indicateur en écoute
                if self.voice_mode:
                    self.root.after(0, lambda: self.voice_indicator.config(
                        text="🎤 Mode vocal ACTIF - Parlez maintenant !", foreground="#00ff88"))
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(do_execute())
            loop.close()
        
        threading.Thread(target=execute_voice_command, daemon=True).start()
    
    def on_closing(self):
        """Gestion de la fermeture de l'application."""
        if self.voice_mode:
            self.stop_voice_mode()
        
        if self.controller and self.controller.is_connected():
            self.log_message("🔌 Déconnexion en cours...", "INFO")
            
            def final_disconnect():
                async def do_disconnect():
                    await self.controller.disconnect()
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(do_disconnect())
                loop.close()
                
                self.root.quit()
            
            threading.Thread(target=final_disconnect, daemon=True).start()
            
            # Attendre un peu puis fermer
            self.root.after(2000, self.root.quit)
        else:
            self.root.quit()
    
    def run(self):
        """Lance l'application."""
        self.log_message("🚀 VoxThymio démarré", "SUCCESS")
        self.log_message("Développé par Espérance AYIWAHOUN pour AI4Innov", "INFO")
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()


def main():
    """Point d'entrée principal."""
    try:
        app = VoxThymioGUI()
        app.run()
    except Exception as e:
        messagebox.showerror("Erreur fatale", f"Erreur critique: {e}")


if __name__ == "__main__":
    main()
