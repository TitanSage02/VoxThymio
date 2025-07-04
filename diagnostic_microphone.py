"""
Script de diagnostic pour vérifier la configuration du microphone
et des dépendances pour le contrôle vocal.
"""

import sys
import platform

def check_python_version():
    """Vérifie la version de Python."""
    print("=== DIAGNOSTIC MICROPHONE ===\n")
    print(f"Version Python: {sys.version}")
    print(f"Plateforme: {platform.system()} {platform.release()}")
    
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ requis")
        return False
    else:
        print("✅ Version Python compatible")
        return True

def check_pyaudio():
    """Vérifie l'installation de PyAudio."""
    print("\n=== VÉRIFICATION PYAUDIO ===")
    try:
        import pyaudio
        print("✅ PyAudio installé")
        
        # Test d'initialisation
        pa = pyaudio.PyAudio()
        print("✅ PyAudio initialisé")
        
        # Liste des périphériques
        device_count = pa.get_device_count()
        print(f"📱 Périphériques audio détectés: {device_count}")
        
        if device_count == 0:
            print("❌ Aucun périphérique audio détecté")
            pa.terminate()
            return False
        
        # Affichage des périphériques d'entrée
        input_devices = []
        for i in range(device_count):
            info = pa.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                input_devices.append((i, info['name']))
                print(f"  🎤 [{i}] {info['name']} - {info['maxInputChannels']} canaux")
        
        pa.terminate()
        
        if not input_devices:
            print("❌ Aucun microphone détecté")
            return False
        else:
            print(f"✅ {len(input_devices)} microphone(s) détecté(s)")
            return True
            
    except ImportError:
        print("❌ PyAudio non installé")
        print("   Installation: pip install pyaudio")
        return False
    except Exception as e:
        print(f"❌ Erreur PyAudio: {e}")
        return False

def check_speech_recognition():
    """Vérifie l'installation de SpeechRecognition."""
    print("\n=== VÉRIFICATION SPEECH RECOGNITION ===")
    try:
        import speech_recognition as sr
        print("✅ SpeechRecognition installé")
        
        # Test d'initialisation
        recognizer = sr.Recognizer()
        print("✅ Recognizer initialisé")
        
        # Test du microphone
        try:
            mic = sr.Microphone()
            print("✅ Microphone accessible via SpeechRecognition")
            return True
        except Exception as e:
            print(f"❌ Erreur microphone SpeechRecognition: {e}")
            return False
            
    except ImportError:
        print("❌ SpeechRecognition non installé")
        print("   Installation: pip install SpeechRecognition")
        return False
    except Exception as e:
        print(f"❌ Erreur SpeechRecognition: {e}")
        return False

def test_microphone_recording():
    """Teste l'enregistrement avec le microphone."""
    print("\n=== TEST ENREGISTREMENT ===")
    try:
        import speech_recognition as sr
        
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        
        print("🎤 Calibrage du microphone...")
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        print("✅ Calibrage terminé")
        
        print("🎤 Test d'enregistrement (parlez maintenant pendant 3 secondes)...")
        with mic as source:
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
        print("✅ Enregistrement réussi")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'enregistrement: {e}")
        return False

def check_internet_connection():
    """Vérifie la connexion internet pour Google Speech API."""
    print("\n=== VÉRIFICATION CONNEXION INTERNET ===")
    try:
        import urllib.request
        urllib.request.urlopen('https://www.google.com', timeout=5)
        print("✅ Connexion internet disponible")
        return True
    except:
        print("❌ Pas de connexion internet")
        print("   La reconnaissance vocale Google nécessite une connexion internet")
        return False

def provide_solutions():
    """Fournit des solutions pour les problèmes courants."""
    print("\n=== SOLUTIONS POUR PROBLÈMES COURANTS ===")
    
    print("\n🔧 PROBLÈMES PYAUDIO:")
    print("Windows:")
    print("  - Télécharger le wheel depuis: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio")
    print("  - Installer avec: pip install pyaudio‑0.2.11‑cp39‑cp39‑win_amd64.whl")
    
    print("\nLinux (Ubuntu/Debian):")
    print("  - sudo apt-get install python3-pyaudio")
    print("  - sudo apt-get install portaudio19-dev")
    print("  - pip install pyaudio")
    
    print("\nmacOS:")
    print("  - brew install portaudio")
    print("  - pip install pyaudio")
    
    print("\n🔧 PROBLÈMES MICROPHONE:")
    print("- Vérifier que le microphone est connecté")
    print("- Vérifier les permissions du microphone")
    print("- Tester le microphone avec un autre logiciel")
    print("- Redémarrer l'ordinateur")
    
    print("\n🔧 PROBLÈMES RECONNAISSANCE:")
    print("- Vérifier la connexion internet")
    print("- Parler clairement et distinctement")
    print("- Réduire le bruit ambiant")
    print("- Rapprocher le microphone")

def main():
    """Fonction principale du diagnostic."""
    success = True
    
    success &= check_python_version()
    success &= check_pyaudio()
    success &= check_speech_recognition()
    success &= check_internet_connection()
    
    if success:
        success &= test_microphone_recording()
    
    print("\n" + "="*50)
    if success:
        print("✅ DIAGNOSTIC RÉUSSI")
        print("Votre système est prêt pour le contrôle vocal!")
    else:
        print("❌ DIAGNOSTIC ÉCHOUÉ")
        print("Consultez les solutions ci-dessous:")
        provide_solutions()
    
    print("="*50)

if __name__ == "__main__":
    main()