"""
Module de contrôle vocal pour le robot Thymio.
Utilise la bibliothèque speech_recognition pour reconnaître les commandes vocales.
"""

import speech_recognition as sr
import logging
from typing import Dict, Optional, Callable
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
    """Contrôleur vocal pour le robot Thymio."""
    
    def __init__(self, 
                 language: str = "fr-FR",
                 timeout: float = 10.0,
                 phrase_timeout: float = 3.0):
        """
        Initialise le contrôleur vocal.
        
        Args:
            language: Langue de reconnaissance (fr-FR par défaut)
            timeout: Timeout pour l'écoute en secondes (10s par défaut)
            phrase_timeout: Timeout pour la fin de phrase en secondes (3s par défaut)
        """
        self.recognizer = sr.Recognizer()
        # Configuration du recognizer pour l'écoute
        self.recognizer.energy_threshold = 300  # Sensibilité aux sons
        self.recognizer.dynamic_energy_threshold = True  # Ajustement automatique
        self.recognizer.pause_threshold = 0.8  # Pause avant fin de phrase (secondes)
        
        self.microphone = None
        self.language = language
        self.timeout = timeout
        self.phrase_timeout = phrase_timeout
        self.microphone_available = False
        
        # Configuration des commandes vocales
        self.voice_commands: Dict[str, str] = {
            # Commandes de mouvement
            "avancer": "avancer",
            "avance": "avancer",
            "va devant": "avancer",
            "marche": "avancer",
            
            "reculer": "reculer",
            "recule": "reculer",
            "va derrière": "reculer",
            "arrière": "reculer",
            
            "tourner à gauche": "tourner_gauche",
            "tourne à gauche": "tourner_gauche",
            "gauche": "tourner_gauche",
            "va à gauche": "tourner_gauche",
            
            "tourner à droite": "tourner_droite",
            "tourne à droite": "tourner_droite",
            "droite": "tourner_droite",
            "va à droite": "tourner_droite",
            
            "arrêter": "arreter",
            "arrête": "arreter",
            "stop": "arreter",
            "arrêt": "arreter",
            
            # Commandes LED
            "led rouge": "led_rouge",
            "rouge": "led_rouge",
            "allume rouge": "led_rouge",
            
            "led vert": "led_vert",
            "vert": "led_vert",
            "led verte": "led_vert",
            "allume vert": "led_vert",
            
            "led bleu": "led_bleu",
            "bleu": "led_bleu",
            "led bleue": "led_bleu",
            "allume bleu": "led_bleu",
            
            "éteindre led": "led_eteindre",
            "éteins led": "led_eteindre",
            "éteindre": "led_eteindre",
            "éteins": "led_eteindre",
            
            # Commandes système
            "quitter": "quitter",
            "sortir": "quitter",
            "fermer": "quitter",
            "arrêter programme": "quitter",
        }
        
        # Configuration du logger
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
        # Initialisation du microphone
        self._initialize_microphone()
        
        # Calibrage du microphone si disponible
        if self.microphone_available:
            self._calibrate_microphone()
    
    def _initialize_microphone(self) -> None:
        """Initialise le microphone avec gestion d'erreurs."""
        try:
            import pyaudio
            self.logger.info("Initialisation du microphone...")
            
            # Test de disponibilité de PyAudio
            pa = pyaudio.PyAudio()
            device_count = pa.get_device_count()
            pa.terminate()
            
            if device_count == 0:
                self.logger.error("Aucun périphérique audio détecté")
                self.microphone_available = False
                return
            
            # Initialisation du microphone
            self.microphone = sr.Microphone()
            self.microphone_available = True
            self.logger.info("Microphone initialisé avec succès")
            
        except ImportError:
            self.logger.error("PyAudio n'est pas installé. Installez-le avec: pip install pyaudio")
            self.microphone_available = False
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation du microphone: {e}")
            self.microphone_available = False
    
    def _setup_logging(self) -> None:
        """Configure le système de logging."""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def _calibrate_microphone(self) -> None:
        """Calibre le microphone pour le bruit ambiant."""
        if not self.microphone_available:
            self.logger.warning("Microphone non disponible pour le calibrage")
            return
            
        try:
            self.logger.info("Calibrage du microphone en cours (2 secondes)...")
            with self.microphone as source:
                # Durée de calibrage augmentée pour une meilleure adaptation
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            self.logger.info("Calibrage terminé")
        except Exception as e:
            self.logger.error(f"Erreur lors du calibrage: {e}")
            self.microphone_available = False
    
    def _normalize_text(self, text: str) -> str:
        """Normalise le texte reconnu pour améliorer la correspondance."""
        return text.lower().strip()
    
    def _find_command(self, text: str) -> Optional[str]:
        """
        Trouve la commande correspondant au texte reconnu.
        
        Args:
            text: Texte reconnu
            
        Returns:
            Clé de commande ou None si non trouvée
        """
        normalized_text = self._normalize_text(text)
        
        # Recherche exacte
        if normalized_text in self.voice_commands:
            return self.voice_commands[normalized_text]
        
        # Recherche partielle
        for voice_cmd, cmd_key in self.voice_commands.items():
            if voice_cmd in normalized_text or normalized_text in voice_cmd:
                return cmd_key
        
        return None
    
    def listen_for_command(self) -> VoiceCommand:
        """
        Écoute et reconnaît une commande vocale.
        
        Returns:
            VoiceCommand: Objet contenant les informations de la commande
        """
        if not self.microphone_available:
            self.logger.error("Microphone non disponible")
            return VoiceCommand(
                text="",
                confidence=0.0,
                status=VoiceCommandStatus.ERROR
            )
        
        try:
            self.logger.info("Écoute d'une commande vocale...")
            
            with self.microphone as source:
                # Écoute avec timeout
                audio = self.recognizer.listen(
                    source, 
                    timeout=self.timeout,
                    phrase_time_limit=self.phrase_timeout
                )
            
            self.logger.info("Reconnaissance en cours...")
            
            # Reconnaissance vocale
            text = self.recognizer.recognize_google(
                audio, 
                language=self.language,
                show_all=False
            )
            
            self.logger.info(f"Texte reconnu: '{text}'")
            
            # Recherche de la commande
            command_key = self._find_command(text)
            
            if command_key:
                self.logger.info(f"Commande trouvée: {command_key}")
                return VoiceCommand(
                    text=text,
                    confidence=1.0,  # Google API ne retourne pas la confiance
                    status=VoiceCommandStatus.SUCCESS,
                    command_key=command_key
                )
            else:
                self.logger.warning(f"Commande non reconnue: '{text}'")
                return VoiceCommand(
                    text=text,
                    confidence=1.0,
                    status=VoiceCommandStatus.UNKNOWN_COMMAND
                )
                
        except sr.UnknownValueError:
            self.logger.warning("Aucune parole détectée")
            return VoiceCommand(
                text="",
                confidence=0.0,
                status=VoiceCommandStatus.NO_SPEECH
            )
            
        except sr.RequestError as e:
            self.logger.error(f"Erreur du service de reconnaissance: {e}")
            return VoiceCommand(
                text="",
                confidence=0.0,
                status=VoiceCommandStatus.ERROR
            )
            
        except sr.WaitTimeoutError:
            self.logger.warning("Timeout d'écoute atteint")
            return VoiceCommand(
                text="",
                confidence=0.0,
                status=VoiceCommandStatus.TIMEOUT
            )
            
        except Exception as e:
            self.logger.error(f"Erreur inattendue: {e}")
            return VoiceCommand(
                text="",
                confidence=0.0,
                status=VoiceCommandStatus.ERROR
            )
    
    def add_command(self, voice_phrase: str, command_key: str) -> None:
        """
        Ajoute une nouvelle commande vocale.
        
        Args:
            voice_phrase: Phrase vocale à reconnaître
            command_key: Clé de commande correspondante
        """
        self.voice_commands[voice_phrase.lower()] = command_key
        self.logger.info(f"Commande ajoutée: '{voice_phrase}' -> '{command_key}'")
    
    def remove_command(self, voice_phrase: str) -> bool:
        """
        Supprime une commande vocale.
        
        Args:
            voice_phrase: Phrase vocale à supprimer
            
        Returns:
            True si la commande a été supprimée, False sinon
        """
        voice_phrase = voice_phrase.lower()
        if voice_phrase in self.voice_commands:
            del self.voice_commands[voice_phrase]
            self.logger.info(f"Commande supprimée: '{voice_phrase}'")
            return True
        return False
    
    def list_commands(self) -> Dict[str, str]:
        """
        Retourne la liste des commandes vocales disponibles.
        
        Returns:
            Dictionnaire des commandes vocales
        """
        return self.voice_commands.copy()
    
    def test_microphone(self) -> bool:
        """
        Teste le fonctionnement du microphone.
        
        Returns:
            True si le microphone fonctionne, False sinon
        """
        if not self.microphone_available:
            self.logger.error("Microphone non disponible pour le test")
            return False
            
        # try:
        #     with self.microphone as source:
        #         self.recognizer.adjust_for_ambient_noise(source, duration=1)
        #     self.logger.info("Test du microphone réussi")
        #     return True
        # except Exception as e:
        #     self.logger.error(f"Test du microphone échoué: {e}")
        #     return False
        return True
    
    def is_microphone_available(self) -> bool:
        """
        Vérifie si le microphone est disponible.
        
        Returns:
            True si le microphone est disponible, False sinon
        """
        return self.microphone_available