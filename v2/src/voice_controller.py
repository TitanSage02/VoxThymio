"""
Contrôleur vocal pour le robot Thymio - Version 2
Support amélioré pour les commandes vocales
"""

import speech_recognition as sr
import logging
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import pathlib

# Classification d'intention
from .intent_classifier import IntentClassifier


class VoiceCommandStatus(Enum):
    """États possibles d'une commande vocale."""
    SUCCESS = "success"
    ERROR = "error"
    UNKNOWN_COMMAND = "unknown_command"
    NO_SPEECH = "no_speech"
    TIMEOUT = "timeout"


@dataclass
class VoiceCommand:
    """Représente une commande vocale reconnue."""
    text: str
    confidence: float
    status: VoiceCommandStatus
    command_key: Optional[str] = None


class VoiceController:
    """Contrôleur vocal pour le robot Thymio."""
    
    def __init__(self, intent_model_path: str = './intent_model'):
        """Initialise le contrôleur vocal."""
        # Configuration du reconnaisseur
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        # Configuration du microphone
        self.microphone = None
        self.timeout = 10.0
        self.phrase_timeout = 3.0
        self.microphone_available = False
        
        # Configuration du logging et initialisation du microphone
        self._setup_logging()
        self._initialize_microphone()

        # Chargement des commandes pour la reconnaissance vocale
        self._load_voice_commands()

        # Chargement du classifieur d'intention
        self.intent_classifier = IntentClassifier(model_path=intent_model_path)
        
        
    
    def _load_voice_commands(self) -> None:
        """Charge les commandes depuis le fichier JSON et les associe à des commandes vocales."""
        # Commandes par défaut
        self.voice_commands = {
            "avancer": "avancer",
            "avance": "avancer",
            "reculer": "reculer",
            "recule": "reculer",
            "gauche": "tourner_gauche",
            "droite": "tourner_droite",
            "arrêter": "arreter",
            "arrête": "arreter",
            "stop": "arreter",
            "rouge": "led_rouge",
            "vert": "led_vert",
            "bleu": "led_bleu",
            "éteindre": "led_eteindre",
            "quitter": "quitter"
        }
        
        # Association vocale pour toutes les commandes dans le fichier JSON
        try:
            # Charge les commandes Thymio disponibles
            commands_path = pathlib.Path(__file__).parent.parent / "commands.json"
            
            with open(commands_path, 'r', encoding='utf-8') as f:
                commands = json.load(f)
            
            # # Crée les correspondances vocales automatiques
            # for cmd in commands.keys():
            #     # Créer des variantes phonétiques pertinentes
            #     self._add_voice_mappings(cmd)
                
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du chargement des commandes vocales: {e}")
    
    # def _add_voice_mappings(self, command_key: str) -> None:
    #     """Ajoute des mappings vocaux pour une commande."""
    #     # Ajoute la version de base
    #     self.voice_commands[command_key] = command_key
        
    #     # Ajoute des variantes selon le type de commande
    #     if command_key.startswith("avancer"):
    #         if command_key == "avancer":
    #             self.voice_commands["avance"] = command_key
        
    #     elif command_key.startswith("reculer"):
    #         if command_key == "reculer":
    #             self.voice_commands["recule"] = command_key
        
    #     elif "gauche" in command_key:
    #         # Variantes pour tourner à gauche
    #         if command_key == "tourner_gauche":
    #             self.voice_commands["gauche"] = command_key
    #             self.voice_commands["à gauche"] = command_key
    #             self.voice_commands["tourne à gauche"] = command_key
    #             self.voice_commands["va à gauche"] = command_key
    #         if command_key == "tourner_gauche_lent":
    #             self.voice_commands["gauche lent"] = command_key
    #             self.voice_commands["tourne lentement à gauche"] = command_key
        
    #     elif "droite" in command_key:
    #         # Variantes pour tourner à droite
    #         if command_key == "tourner_droite":
    #             self.voice_commands["droite"] = command_key
    #             self.voice_commands["à droite"] = command_key
    #             self.voice_commands["tourne à droite"] = command_key
    #             self.voice_commands["va à droite"] = command_key
    #         if command_key == "tourner_droite_lent":
    #             self.voice_commands["droite lent"] = command_key
    #             self.voice_commands["tourne lentement à droite"] = command_key
        
    #     elif command_key == "arreter":
    #         self.voice_commands["arrête"] = command_key
    #         self.voice_commands["stop"] = command_key
    #         self.voice_commands["arrête-toi"] = command_key
        
    #     elif command_key.startswith("led_"):
    #         color = command_key.replace("led_", "")
    #         self.voice_commands[color] = command_key
    #         self.voice_commands[f"lumière {color}"] = command_key
        
    #     elif command_key.startswith("note_"):
    #         note = command_key.replace("note_", "")
    #         self.voice_commands[note] = command_key
    #         self.voice_commands[f"joue {note}"] = command_key
    #         self.voice_commands[f"note {note}"] = command_key
        
    #     elif command_key.startswith("son_"):
    #         son = command_key.replace("son_", "")
    #         self.voice_commands[son] = command_key
    #         self.voice_commands[f"son {son}"] = command_key
            
    def _initialize_microphone(self) -> None:
        """Initialise le microphone."""
        try:
            self.microphone = sr.Microphone()
            self.microphone_available = True

            # Calibrage pour le bruit ambiant
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
            
            self.logger.info("✅ Microphone initialisé et calibré")
        
        except Exception as e:
            self.logger.error(f"❌ Erreur microphone: {e}")
            self.microphone_available = False
    
    def _setup_logging(self) -> None:
        """Configure le logging."""
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def _find_command(self, text: str) -> Optional[str]:
        """Trouve la commande correspondant au texte reconnu."""
        text = text.lower().strip()
        
        # Recherche exacte
        if text in self.voice_commands:
            return self.voice_commands[text]
        
        # Recherche partielle
        for voice_cmd, cmd_key in self.voice_commands.items():
            if voice_cmd in text:
                return cmd_key
        
        return None
    
    def listen_for_command(self) -> VoiceCommand:
        """Écoute et reconnaît une commande vocale."""
        if not self.microphone_available:
            return VoiceCommand(
                text="", 
                confidence=0.0, 
                status=VoiceCommandStatus.ERROR
            )

        try:
            with self.microphone as source:
                self.logger.info("🎤 Écoute...")
                audio = self.recognizer.listen(
                                    source, 
                                    timeout=self.timeout, 
                                    phrase_time_limit=self.phrase_timeout
                                    )
            
            # Reconnaissance vocale avec Google (fr-FR)
            text = self.recognizer.recognize_google(audio, language="fr-FR")
           
            # Passer à whisper 
            # text = self.recognizer.recognize_whisper(audio, language="fr-FR")
            # self.recognizer.recognize_whisper(audio, language="fr-FR")
            if not text:
                return VoiceCommand(
                    text="", 
                    confidence=0.0, 
                    status=VoiceCommandStatus.NO_SPEECH
                )
            
            self.logger.info(f"🗣️ Texte reconnu: '{text}'")
            

            # Utilisation du classifieur d'intention pour déterminer la commande
            try:
                predicted_intent = self.intent_classifier.predict(text)
                if predicted_intent in self.voice_commands:
                    return VoiceCommand(
                        text=text,
                        confidence=1.0,
                        status=VoiceCommandStatus.SUCCESS,
                        command_key=self.voice_commands[predicted_intent]
                    )
                else:
                    return VoiceCommand(
                        text=text,
                        confidence=1.0,
                        status=VoiceCommandStatus.UNKNOWN_COMMAND
                    )
            except Exception as e:
                self.logger.error(f"Erreur classification d'intention: {e}")
                return VoiceCommand(
                    text=text,
                    confidence=1.0,
                    status=VoiceCommandStatus.ERROR
                )

        except sr.UnknownValueError:
            return VoiceCommand(
                text="", 
                confidence=0.0, 
                status=VoiceCommandStatus.NO_SPEECH
            )
        
        except sr.WaitTimeoutError:
            return VoiceCommand(
                text="", 
                confidence=0.0, 
                status=VoiceCommandStatus.TIMEOUT
            )
        
        except Exception as e:
            self.logger.error(f"Erreur: {e}")
            return VoiceCommand(
                text="", 
                confidence=0.0, 
                status=VoiceCommandStatus.ERROR
            )

    def is_microphone_available(self) -> bool:
        """Vérifie si le microphone est disponible."""
        return self.microphone_available
    
    def list_commands(self) -> Dict[str, str]:
        """Retourne la liste des commandes vocales disponibles."""
        return self.voice_commands.copy()
    
    def get_available_commands_by_category(self) -> Dict[str, List[Tuple[str, str]]]:
        """Retourne les commandes disponibles organisées par catégorie."""
        categories = {
            "Mouvement": [],
            "LEDs": [],
            "Sons": [],
            "Système": [],
            "Autres": []
        }
        
        # Liste unique des commandes disponibles (évite les doublons)
        unique_commands = {}
        for voice_cmd, cmd in self.voice_commands.items():
            if cmd not in unique_commands:
                unique_commands[cmd] = voice_cmd
        
        # Catégorisation des commandes
        for cmd, voice_cmd in unique_commands.items():
            if any(x in cmd for x in ["avancer", "reculer", "tourner", "pivoter", "demi_tour"]):
                categories["Mouvement"].append((cmd, voice_cmd))
            elif any(x in cmd for x in ["led", "leds"]):
                categories["LEDs"].append((cmd, voice_cmd))
            elif any(x in cmd for x in ["son", "note", "volume"]):
                categories["Sons"].append((cmd, voice_cmd))
            elif cmd == "quitter" or cmd == "arreter":
                categories["Système"].append((cmd, voice_cmd))
            else:
                categories["Autres"].append((cmd, voice_cmd))
        
        return categories
