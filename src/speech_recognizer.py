"""
Module de reconnaissance vocale pour VoxThymio.
Permet d'acquérir des commandes audio via le microphone.
"""

import speech_recognition as sr
import threading
import time
import queue
import logging
from typing import Optional, Callable, Dict, Any, List, Tuple

class SpeechRecognizer:
    """
    Classe de reconnaissance vocale permettant d'acquérir des commandes
    à partir du microphone de l'utilisateur.
    """
    
    def __init__(self, language: str = "fr-FR"):
        """
        Initialise le reconnaisseur de parole.
        
        Args:
            language (str): Code de langue pour la reconnaissance vocale
        """
        self.recognizer = sr.Recognizer()
        self.language = language
        self.is_listening = False
        self.command_queue = queue.Queue()
        self.listen_thread = None
        self.callback = None
        
        # Configuration du niveau de bruit ambiant
        self.energy_threshold = 300  # Niveau de détection de son
        self.pause_threshold = 0.8   # Pause considérée comme fin de phrase (secondes)
        self.recognizer.energy_threshold = self.energy_threshold
        self.recognizer.pause_threshold = self.pause_threshold
        
        # Statistiques
        self.stats = {
            "total_attempts": 0,
            "successful_recognitions": 0,
            "failed_recognitions": 0,
            "last_error": None,
            "last_success_time": None
        }
        
        logging.info("🎤 Module de reconnaissance vocale initialisé")
    
    def start_listening(self, callback: Optional[Callable[[str], None]] = None) -> bool:
        """
        Démarre l'écoute en continu en arrière-plan.
        
        Args:
            callback (Callable): Fonction à appeler pour chaque commande reconnue
        
        Returns:
            bool: True si l'écoute a démarré avec succès
        """
        if self.is_listening:
            logging.warning("🎤 Le système est déjà en écoute")
            return False
        
        self.callback = callback
        self.is_listening = True
        self.listen_thread = threading.Thread(target=self._continuous_listen)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        
        logging.info("Démarrage de l'écoute vocale")
        return True
    
    def stop_listening(self) -> bool:
        """
        Arrête l'écoute en continu.
        
        Returns:
            bool: True si l'écoute a été arrêtée avec succès
        """
        if not self.is_listening:
            return False
        
        self.is_listening = False
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=1.0)
        
        logging.info("Arrêt de l'écoute vocale")
        return True
    
    def _continuous_listen(self):
        """
        Fonction d'écoute continue exécutée dans un thread séparé.
        Récupère le son du microphone et le transforme en texte.
        """
        while self.is_listening:
            try:
                # Acquisition audio depuis le microphone
                with sr.Microphone() as source:
                    logging.debug("🔊 Ajustement au bruit ambiant...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    
                    logging.debug("🎤 Écoute en cours...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                # Tentative de reconnaissance
                self.stats["total_attempts"] += 1
                try:
                    # Utilisation de l'API Google pour la reconnaissance
                    text = self.recognizer.recognize_google(audio, language=self.language)
                    
                    if text:
                        logging.info(f"🎤 Commande vocale reconnue: '{text}'")
                        self.stats["successful_recognitions"] += 1
                        self.stats["last_success_time"] = time.time()
                        
                        # Ajoute à la file d'attente et appelle le callback si défini
                        self.command_queue.put(text)
                        if self.callback:
                            self.callback(text)
                
                except sr.UnknownValueError:
                    logging.debug("🎤 Parole non reconnue")
                    self.stats["failed_recognitions"] += 1
                    self.stats["last_error"] = "UnknownValueError"
                
                except sr.RequestError as e:
                    logging.error(f"❌ Erreur de requête API: {e}")
                    self.stats["failed_recognitions"] += 1
                    self.stats["last_error"] = f"RequestError: {str(e)}"
                
            except Exception as e:
                logging.error(f"❌ Erreur lors de l'écoute: {e}")
                self.stats["failed_recognitions"] += 1
                self.stats["last_error"] = str(e)
                time.sleep(1)  # Pause pour éviter de surcharger le CPU en cas d'erreur
    
    def get_next_command(self, timeout: float = 0.1) -> Optional[str]:
        """
        Récupère la prochaine commande vocale de la file d'attente.
        
        Args:
            timeout (float): Temps maximum d'attente en secondes
            
        Returns:
            Optional[str]: Commande vocale ou None si rien n'est disponible
        """
        try:
            return self.command_queue.get(block=True, timeout=timeout)
        except queue.Empty:
            return None
    
    def listen_once(self) -> Tuple[bool, str]:
        """
        Écoute une seule commande vocale (bloquant).
        
        Returns:
            Tuple[bool, str]: (succès, texte ou message d'erreur)
        """
        try:
            with sr.Microphone() as source:
                print("🔊 Ajustement au bruit ambiant...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                print("🎤 Parlez maintenant...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            try:
                text = self.recognizer.recognize_google(audio, language=self.language)
                return True, text
            
            except sr.UnknownValueError:
                return False, "Parole non reconnue"
            
            except sr.RequestError as e:
                return False, f"Erreur d'API: {e}"
                
        except Exception as e:
            return False, f"Erreur: {e}"
    
    def calibrate_mic(self, duration: float = 2.0) -> Dict[str, Any]:
        """
        Calibre le microphone au bruit ambiant.
        
        Args:
            duration (float): Durée d'échantillonnage en secondes
            
        Returns:
            Dict[str, Any]: Résultats de la calibration
        """
        try:
            with sr.Microphone() as source:
                print(f"🔊 Calibration du microphone pendant {duration} secondes...")
                print("🔊 Silence, s'il vous plaît...")
                
                # Échantillonnage du bruit ambiant
                before_threshold = self.recognizer.energy_threshold
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
                after_threshold = self.recognizer.energy_threshold
                
                # Application des valeurs
                self.energy_threshold = after_threshold
                
                return {
                    "status": "success",
                    "before_threshold": before_threshold,
                    "after_threshold": after_threshold,
                    "adjustment": after_threshold - before_threshold
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques de reconnaissance vocale.
        
        Returns:
            Dict[str, Any]: Statistiques
        """
        success_rate = 0
        if self.stats["total_attempts"] > 0:
            success_rate = (self.stats["successful_recognitions"] / 
                           self.stats["total_attempts"]) * 100
            
        return {
            "total_attempts": self.stats["total_attempts"],
            "successful_recognitions": self.stats["successful_recognitions"],
            "failed_recognitions": self.stats["failed_recognitions"],
            "success_rate": success_rate,
            "last_error": self.stats["last_error"],
            "is_listening": self.is_listening,
            "language": self.language,
            "energy_threshold": self.energy_threshold,
            "pause_threshold": self.pause_threshold
        }
    
    def update_settings(self, energy_threshold: Optional[int] = None,
                      pause_threshold: Optional[float] = None,
                      language: Optional[str] = None) -> Dict[str, Any]:
        """
        Met à jour les paramètres de reconnaissance vocale.
        
        Args:
            energy_threshold (int): Seuil d'énergie pour la détection du son
            pause_threshold (float): Seuil de pause en secondes
            language (str): Code de langue
            
        Returns:
            Dict[str, Any]: Résultats de la mise à jour
        """
        changes = []
        
        if energy_threshold is not None and energy_threshold > 0:
            self.energy_threshold = energy_threshold
            self.recognizer.energy_threshold = energy_threshold
            changes.append(f"Seuil d'énergie: {energy_threshold}")
        
        if pause_threshold is not None and 0.1 <= pause_threshold <= 3.0:
            self.pause_threshold = pause_threshold
            self.recognizer.pause_threshold = pause_threshold
            changes.append(f"Seuil de pause: {pause_threshold}")
        
        if language is not None:
            self.language = language
            changes.append(f"Langue: {language}")
        
        return {
            "status": "success",
            "changes": changes,
            "current_settings": {
                "energy_threshold": self.energy_threshold,
                "pause_threshold": self.pause_threshold,
                "language": self.language
            }
        }


# Test du module si exécuté directement
if __name__ == "__main__":
    import time
    
    # Configuration du logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Test de reconnaissance simple
    recognizer = SpeechRecognizer(language="fr-FR")
    
    # Test de calibration
    calibration = recognizer.calibrate_mic(duration=1.0)
    print(f"Calibration: {calibration}")
    
    # Fonction de callback pour les commandes reconnues
    def on_command(text):
        print(f"✨ Commande reçue: '{text}'")
    
    # Démarrage de l'écoute continue
    recognizer.start_listening(callback=on_command)
    
    try:
        print("Écoute en cours... (Ctrl+C pour arrêter)")
        
        # Boucle de test pendant 30 secondes
        end_time = time.time() + 30
        while time.time() < end_time:
            # Vérification toutes les secondes pour les nouvelles commandes
            time.sleep(1)
            
            # On peut aussi récupérer manuellement depuis la file
            command = recognizer.get_next_command(timeout=0.1)
            if command:
                print(f"📝 Commande de la file: '{command}'")
        
    except KeyboardInterrupt:
        print("\nArrêt demandé par l'utilisateur")
    
    finally:
        # Arrêt de l'écoute
        recognizer.stop_listening()
        
        # Affichage des statistiques
        stats = recognizer.get_stats()
        print("\n📊 Statistiques:")
        for key, value in stats.items():
            print(f"  • {key}: {value}")
