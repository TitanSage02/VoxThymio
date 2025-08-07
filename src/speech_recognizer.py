"""
Module de reconnaissance vocale.
"""

import time
import logging
import numpy as np
from typing import Optional, Dict, Any
from pathlib import Path

USE_FASTER_WHISPER = False

if USE_FASTER_WHISPER:
    try:
        from faster_whisper import WhisperModel
        import sounddevice as sd
        FASTER_WHISPER_AVAILABLE = True
    except ImportError:
        print("⚠️ faster-whisper non disponible, fallback vers speech_recognition")
        import speech_recognition as sr
        FASTER_WHISPER_AVAILABLE = False
else : 
    import speech_recognition as sr
    FASTER_WHISPER_AVAILABLE = False

class SpeechRecognizer:
    """
    Reconnaissance vocale temps réel.
    """
    
    def __init__(self, language: str = "fr", model_size: str = "small"):
        """
        Initialise le reconnaisseur vocal.

        Args:
            language (str): Code de langue ('fr', 'en', etc.)
            model_size (str): Taille du modèle ('tiny', 'small', 'base', 'large')
        """
        self.language = language
        self.model_size = model_size
        self.is_listening = False
        
        # Configuration audio temps réel
        self.sample_rate = 16000
        self.chunk_duration = 5.0  # Durée des chunks audio (secondes)
        self.min_audio_length = 0.5  # Durée minimum pour traitement
        self.silence_threshold = 0.01  # Seuil de silence
        
        # Initialisation du modèle
        self._initialize_model()

        logging.info(f"🎤 Reconnaissance vocale initialisée (modèle: {model_size})")

    def _initialize_model(self):
        """Initialise le modèle de reconnaissance selon la disponibilité."""
        if FASTER_WHISPER_AVAILABLE:
            try:
                # Configuration optimisée pour faster-whisper
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"
                compute_type = "float16" if device == "cuda" else "int8"
                
                print(f"🔧 Chargement du modèle faster-whisper '{self.model_size}' sur {device}")
                
                self.model = WhisperModel(
                    self.model_size,
                    device=device,
                    compute_type=compute_type,
                    cpu_threads=4,
                    download_root=str(Path.home() / ".cache" / "whisper")
                )
                
                self.recognition_engine = "faster-whisper"
                print("✅ faster-whisper initialisé avec succès")
                
            except Exception as e:
                print(f"❌ Erreur faster-whisper: {e}, fallback vers speech_recognition")
                self._fallback_to_speech_recognition()
        else:
            self._fallback_to_speech_recognition()
    
    def _fallback_to_speech_recognition(self):
        """Fallback vers speech_recognition classique."""
        self.recognizer = sr.Recognizer()
        self.recognition_engine = "speech_recognition"
        
        # Configuration optimisée
        self.recognizer.energy_threshold = 300
        self.recognizer.pause_threshold = 0.8
        self.recognizer.dynamic_energy_threshold = True
        
        print("✅ speech_recognition initialisé comme fallback")
    
    # ========================================
    # MÉTHODES D'ÉCOUTE PRINCIPALES
    # ========================================
    def listen(self, timeout: float = 5.0) -> Optional[str]:
        """
        Écoute une seule commande vocale.
        
        Args:
            timeout (float): Timeout d'écoute en secondes
            
        Returns:
            Optional[str]: Texte reconnu ou None
        """
        start_time = time.time()
        
        try:
            if self.recognition_engine == "faster-whisper":
                return self._listen_once_whisper(timeout)
            else:
                return self._listen_once_sr(timeout)
                
        except Exception as e:
            print(f"❌ Erreur lors de l'écoute: {e}")
            return None

    
    def _listen_once_whisper(self, timeout: float) -> Optional[str]:
        """Écoute avec faster-whisper."""
        print("🎤 Écoute en cours...")
        
        # Enregistrement audio
        duration = min(timeout, 8.0)  # Max 8 secondes
        audio_data = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.float32
        )
        sd.wait()  # Attendre la fin de l'enregistrement
        
        # Vérification du niveau audio
        if np.max(np.abs(audio_data)) < self.silence_threshold:
            print("🔇 Aucun son détecté")
            return None
        
        # Transcription
        try:
            segments, info = self.model.transcribe(
                audio_data.flatten(),
                language=self.language,
                beam_size=1,  # Plus rapide
                best_of=1,
                temperature=0.0,
                condition_on_previous_text=False,
                vad_filter=True,  # Détection d'activité vocale
                vad_parameters=dict(
                    min_silence_duration_ms=500,
                    max_speech_duration_s=8.0
                )
            )
            
            # Extraction du texte
            text_segments = []
            for segment in segments:
                if segment.text.strip():
                    text_segments.append(segment.text.strip())
            
            if text_segments:
                result = " ".join(text_segments)
                print(f"✅ Reconnu: '{result}'")
                return result
            else:
                print("🔇 Aucune parole détectée")
                return None
                
        except Exception as e:
            print(f"❌ Erreur de transcription: {e}")
            return None
    
    def _listen_once_sr(self, timeout: float) -> Optional[str]:
        """Écoute avec speech_recognition."""
        print("🎤 Écoute en cours (speech_recognition)...")
        
        try:
            with sr.Microphone() as source:
                # Ajustement au bruit ambiant rapide
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Écoute
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=8.0
                )
            
            # Transcription avec Google si disponible
            try:
                text = self.recognizer.recognize_google(audio, language=f"{self.language}-FR")
                if text:
                    result = text.strip()
                    print(f"✅ Reconnu (Google): '{result}'")
                    return result
            except:
                    pass
            
            print("🔇 Aucune parole détectée")
            return None
            
        except sr.WaitTimeoutError:
            print("⏱️ Timeout d'écoute")
            return None
        
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return None
   
    def calibrate_microphone(self, duration: float = 2.0) -> Dict[str, Any]:
        """
        Calibre le microphone au bruit ambiant.
        
        Args:
            duration: Durée de calibration en secondes
            
        Returns:
            None
        """
        print(f"🔧 Calibration du microphone ({duration}s)...")
        
        try:
            if self.recognition_engine == "faster-whisper":
                # Test audio avec sounddevice
                test_audio = sd.rec(
                    int(duration * self.sample_rate),
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype=np.float32
                )
                sd.wait()
                
                # Calcul du niveau de bruit
                noise_level = np.mean(np.abs(test_audio))
                self.silence_threshold = max(noise_level * 3, 0.01)
                
                print(f"✅ Calibration terminée: niveau de bruit {noise_level}, seuil de silence {self.silence_threshold}")
            else:
                # Calibration speech_recognition
                with sr.Microphone() as source:
                    before_threshold = self.recognizer.energy_threshold
                    self.recognizer.adjust_for_ambient_noise(source, duration=duration)
                    after_threshold = self.recognizer.energy_threshold
                
                print(f"✅ Calibration terminée: seuil avant {before_threshold}, après {after_threshold}")
        
        except Exception as e:
            return


# Test
def test_recognition():
    """Test complet du système de reconnaissance."""
    print("🧪 Test du système de reconnaissance vocale")
    print("=" * 60)
    
    # Initialisation
    recognizer = SpeechRecognizer(language="fr", model_size="small")

    # Calibration
    print("\n🔧 Calibration du microphone...")
    recognizer.calibrate_microphone(duration=2.0)
    
    try: 
        while True : 
            # Test de reconnaissance
            print("\n2️⃣ Test de reconnaissance vocale")
            print("🗣️ Dites quelque chose...")
            result = recognizer.listen(timeout=5.0)
            print(f"Résultat: {result if result else 'Rien détecté'}")
    except KeyboardInterrupt:
        print("\n🔚 Test terminé par l'utilisateur.")
        return


if __name__ == "__main__":    
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("Module de reconnaissance vocale - VoxThymio")
    print("=" * 56)

    test_recognition()