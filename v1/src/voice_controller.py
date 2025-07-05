"""
Contrôleur vocal pour le robot Thymio.
"""

import speech_recognition as sr
import logging
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum


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
    """Contrôleur vocal simplifié pour le robot Thymio."""
    
    def __init__(self):
        """Initialise le contrôleur vocal."""
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        self.microphone = None
        self.timeout = 10.0
        self.phrase_timeout = 3.0
        self.microphone_available = False
        
        # Commandes vocales
        self.voice_commands: Dict[str, str] = {
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
        
        self._setup_logging()
        self._initialize_microphone()
    
    def _initialize_microphone(self) -> None:
        """Initialise le microphone."""
        try:
            self.microphone = sr.Microphone()
            self.microphone_available = True

            # Calibrage
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            self.logger.info("✅ Microphone initialisé")
        
        except Exception as e:
            self.logger.error(f"❌ Erreur microphone: {e}")
            self.microphone_available = False
    
    def _setup_logging(self) -> None:
        """Configure le logging simplifié."""
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
        
        # Recherche partielle si recherche exacte échoue
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
                audio = self.recognizer.listen(
                                    source, 
                                    timeout=self.timeout, 
                                    phrase_time_limit=self.phrase_timeout
                                    )
            
            # Reconnaissance vocale
            text = self.recognizer.recognize_google(audio, language="fr-FR")
            self.logger.info(f"Texte reconnu: '{text}'")
            
            # Recherche de la commande
            command_key = self._find_command(text)
            
            if command_key:
                return VoiceCommand(
                    text=text, 
                    confidence=1.0, 
                    status=VoiceCommandStatus.SUCCESS, 
                    command_key=command_key
                )
            else:
                return VoiceCommand(
                    text=text, 
                    confidence=1.0, 
                    status=VoiceCommandStatus.UNKNOWN_COMMAND
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
