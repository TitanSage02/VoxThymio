"""
Contrôleur vocal pour le robot Thymio
Pipeline : Audio → Transcription → Classification BERT → Commande

Développé par Espérance AYIWAHOUN pour AI4Innov
Projet : VoxThymio - Système de contrôle intelligent du robot Thymio
"""

import speech_recognition as sr
import logging
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import pathlib
import time

# Classification d'intention basée sur BERT
from .intent_classifier import IntentClassifier


class VoiceCommandStatus(Enum):
    """États possibles d'une commande vocale."""
    SUCCESS = "success"           # Commande reconnue avec succès
    ERROR = "error"               # Erreur technique
    UNKNOWN_COMMAND = "unknown_command"  # Commande non reconnue
    NO_SPEECH = "no_speech"       # Pas de parole détectée
    TIMEOUT = "timeout"           # Timeout d'écoute


@dataclass
class VoiceCommand:
    """Représente une commande vocale reconnue.
    
    Attributes:
        text: Texte brut transcrit
        confidence: Niveau de confiance (0.0-1.0)
        status: Statut de la commande (voir VoiceCommandStatus)
        command_key: Clé de commande identifiée (si succès)
    """
    text: str
    confidence: float
    status: VoiceCommandStatus
    command_key: Optional[str] = None


class VoiceController:
    """Contrôleur vocal pour le robot Thymio.
    
    Implémente le pipeline complet:
    1. Capture audio (via microphone)
    2. Transcription (via Google Speech Recognition)
    3. Classification d'intention (via modèle BERT)
    4. Mappage vers commande Thymio
    """
    
    def __init__(self, intent_model_path: str = './intent_model'):
        """Initialise le contrôleur vocal avec le pipeline complet.
        
        Args:
            intent_model_path: Chemin vers le modèle BERT de classification d'intention
        """
        # Configuration du reconnaisseur vocal
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300          # Sensibilité du microphone
        self.recognizer.dynamic_energy_threshold = True # Ajustement automatique
        self.recognizer.pause_threshold = 0.8           # Pause entre les mots (secondes)
        
        # Configuration des timeouts
        self.timeout = 10.0             # Timeout global de la session d'écoute
        self.phrase_timeout = 10.0       # Timeout pour une phrase individuelle

        # Configuration du microphone
        self.microphone = None
        self.microphone_available = False
        
        # Journalisation et initialisation
        self._setup_logging()
        self._initialize_microphone()
        self._check_whisper_availability()

        # Chargement des commandes pour la reconnaissance vocale
        self._load_voice_commands()

        # Chargement du classifieur d'intention BERT
        self.logger.info(f"Chargement du modèle BERT depuis: {intent_model_path}")
        self.intent_classifier = IntentClassifier(model_path=intent_model_path)
    
    def _check_whisper_availability(self) -> None:
        """Vérifie si Whisper est disponible et correctement installé."""
        try:
            # Tenter d'accéder à la méthode recognize_whisper
            if not hasattr(self.recognizer, 'recognize_whisper'):
                self.logger.warning("⚠️ Whisper n'est pas disponible dans cette version de SpeechRecognition")
                self.logger.info("ℹ️ Installation recommandée: pip install --upgrade speechrecognition openai-whisper")
                return False
            
            self.logger.info("✅ Whisper est disponible pour la reconnaissance vocale locale")
        
            return True
        
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la vérification de Whisper: {e}")
            return False
    
    def _load_voice_commands(self) -> None:
        """Charge les commandes vocales depuis le fichier JSON.
        
        Le modèle BERT est déjà entraîné pour prédire directement
        les commandes qui sont définies dans commands.json.
        """
        try:
            # Chemin vers commands.json
            commands_path = pathlib.Path(__file__).parent.parent / "commands.json"
            
            with open(commands_path, 'r', encoding='utf-8') as f:
                commands = json.load(f)
                
            # Stocke les commandes disponibles - pas besoin de mapping complexe
            # puisque le modèle BERT renvoie directement ces commandes
            self.available_commands = list(commands.keys())
            
            # Initialise un dictionnaire vide - sert uniquement à la compatibilité
            self.voice_commands = {}
            
            self.logger.info(f"✅ {len(commands)} commandes chargées depuis {commands_path}")
                
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du chargement des commandes: {e}")
            self.available_commands = [
                "avancer", "reculer", "arreter", "tourner_gauche", "tourner_droite",
                "led_rouge", "led_vert", "led_bleu", "led_eteindre", "quitter"
            ]
            self.logger.info("⚠️ Utilisation des commandes par défaut uniquement")
            
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
    
    def listen_for_command(self) -> VoiceCommand:
        """Écoute, reconnaît et interprète une commande vocale.
        
        Pipeline complet:
        1. Capture audio via microphone
        2. Transcription via Google Speech Recognition
        3. Classification d'intention via modèle BERT
        4. Mappage vers commande Thymio
        
        Returns:
            VoiceCommand: Objet contenant le résultat du traitement
        """
        # Vérification de la disponibilité du microphone
        if not self.microphone_available:
            return VoiceCommand(
                text="", 
                confidence=0.0, 
                status=VoiceCommandStatus.ERROR
            )

        try:
            # 1. CAPTURE AUDIO
            start_time = time.time()
            self.logger.info("🎤 Capture audio en cours...")
            
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source, 
                    timeout=self.timeout,
                    phrase_time_limit=self.phrase_timeout
                )
            
            capture_duration = time.time() - start_time
            self.logger.info(f"✓ Audio capturé ({capture_duration:.1f}s)")
            
            # 2. TRANSCRIPTION VOCALE
            self.logger.info("🔄 Transcription en cours...")
            try:
                raise AttributeError("Passage forcé à l'usage de Whisper") 
            

                # Utilisation de Whisper pour la reconnaissance vocale locale
                text = self.recognizer.recognize_whisper(audio, language="fr")
                self.logger.info(f"✓ Texte transcrit : '{text}'")

            except AttributeError:
                text = self.recognizer.recognize_google(audio, language="fr-FR")
                self.logger.info(f"✓ Texte transcrit : '{text}'")
            
            except Exception as e:
                self.logger.error(f"❌ Erreur de transcription Whisper: {e}")
                return VoiceCommand(
                    text="", 
                    confidence=0.0, 
                    status=VoiceCommandStatus.ERROR
                )
            
            if not text:
                return VoiceCommand(
                    text="", 
                    confidence=0.0, 
                    status=VoiceCommandStatus.NO_SPEECH
                )
            
            self.logger.info(f"✓ Texte transcrit: '{text}'")
            
            # 3. CLASSIFICATION D'INTENTION VIA BERT
            try:
                self.logger.info("🧠 Classification d'intention en cours...")
                predicted_intent = self.intent_classifier.predict(text)
                self.logger.info(f"✓ Intention identifiée: '{predicted_intent}'")
                
                # 4. VÉRIFICATION DE LA COMMANDE PRÉDITE
                if predicted_intent in self.available_commands:
                    self.logger.info(f"✓ Commande valide: '{predicted_intent}'")
                    
                    return VoiceCommand(
                        text=text,
                        confidence=1.0,  # Confiance fixée à 1.0 pour BERT
                        status=VoiceCommandStatus.SUCCESS,
                        command_key=predicted_intent
                    )
                else:
                    self.logger.warning(f"⚠️ Commande non reconnue: '{predicted_intent}'")
                    return VoiceCommand(
                        text=text,
                        confidence=1.0,
                        status=VoiceCommandStatus.UNKNOWN_COMMAND
                    )
            except Exception as e:
                self.logger.error(f"❌ Erreur de classification: {e}")
                return VoiceCommand(
                    text=text,
                    confidence=0.0,
                    status=VoiceCommandStatus.ERROR
                )

        except sr.UnknownValueError:
            self.logger.warning("⚠️ Parole non reconnue")
            return VoiceCommand(
                text="", 
                confidence=0.0, 
                status=VoiceCommandStatus.NO_SPEECH
            )
        
        except sr.WaitTimeoutError:
            self.logger.warning("⚠️ Timeout d'écoute")
            return VoiceCommand(
                text="", 
                confidence=0.0, 
                status=VoiceCommandStatus.TIMEOUT
            )
        
        except Exception as e:
            self.logger.error(f"❌ Erreur: {e}")
            return VoiceCommand(
                text="", 
                confidence=0.0, 
                status=VoiceCommandStatus.ERROR
            )

    def is_microphone_available(self) -> bool:
        """Vérifie si le microphone est disponible pour le contrôle vocal.
        
        Returns:
            bool: True si un microphone est disponible, False sinon
        """
        return self.microphone_available
    
    def list_commands(self) -> List[str]:
        """Retourne la liste des commandes disponibles.
        
        Returns:
            List[str]: Liste des commandes disponibles
        """
        return self.available_commands.copy()
    
    def get_available_commands_by_category(self) -> Dict[str, List[str]]:
        """Organise les commandes disponibles par catégorie pour l'affichage.
        
        Returns:
            Dict[str, List[str]]: Dictionnaire catégorie → liste de commandes
        """
        categories = {
            "Mouvement": [],
            "LEDs": [],
            "Sons": [],
            "Système": [],
            "Autres": []
        }
        
        # Catégorisation des commandes
        for cmd in self.available_commands:
            if any(x in cmd for x in ["avancer", "reculer", "tourner", "pivoter", "demi_tour"]):
                categories["Mouvement"].append(cmd)
            elif any(x in cmd for x in ["led", "leds"]):
                categories["LEDs"].append(cmd)
            elif any(x in cmd for x in ["son", "note", "volume"]):
                categories["Sons"].append(cmd)
            elif cmd == "quitter" or cmd == "arreter":
                categories["Système"].append(cmd)
            else:
                categories["Autres"].append(cmd)
        
        return categories
