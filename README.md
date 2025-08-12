# VoxThymio 🤖🎤

> **Système avancé de contrôle vocal et manuel pour robot Thymio**  
> Développé par **Espérance AYIWAHOUN** pour **AI4Innov**

![VoxThymio](https://img.shields.io/badge/VoxThymio-v2.0-00d4aa?style=for-the-badge&logo=robot)
![AI4Innov](https://img.shields.io/badge/AI4Innov-Innovation-00d4aa?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-≥3.8-blue?style=for-the-badge&logo=python)
![Whisper](https://img.shields.io/badge/Speech--to--Text-Whisper-informational?style=for-the-badge)
![BERT](https://img.shields.io/badge/NLP-BERT-yellow?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Contrôle Vocal Intelligent pour Robot Thymio avec IA**

VoxThymio est un système avancé de contrôle vocal pour robots Thymio qui utilise l'intelligence artificielle pour comprendre et exécuter des commandes en langage naturel. Le système apprend dynamiquement de nouvelles commandes et offre une interface intuitive pour contrôler votre robot Thymio par la voix.

[🇬🇧 English Version](./README_EN.md)

## ✨ Caractéristiques principales

- **🎤 Reconnaissance vocale en temps réel** - Support multimodal avec Whisper et SpeechRecognition
- **🧠 Compréhension sémantique** - Utilise des embeddings multilingues pour comprendre les variations de commandes
- **📚 Apprentissage dynamique** - Ajoute automatiquement de nouvelles commandes basées sur la similarité sémantique
- **🔍 Recherche vectorielle** - Base de données ChromaDB pour une recherche efficace de commandes similaires
- **🤖 Contrôle Thymio natif** - Communication directe avec le robot via tdmclient
- **⚙️ Seuils configurables** - Ajustement fin des seuils d'exécution et d'apprentissage

## 🏗️ Architecture

```
VoxThymio/
├── src/
│   ├── smart_voice_controller.py    # Contrôleur principal
│   ├── speech_recognizer.py         # Module de reconnaissance vocale
│   ├── embedding_generator.py       # Génération d'embeddings sémantiques
│   ├── embedding_manager.py         # Gestionnaire de base vectorielle
│   ├── commands.json                # Commandes de base
│   └── controller/
│       └── thymio_controller.py     # Interface Thymio
├── vector_db/                       # Base de données ChromaDB
├── gui/                            # Interface graphique
├── requirements.txt                # Dépendances Python
└── README.md                       # Documentation
```

## 🚀 Installation

### Prérequis
- Python 3.8+
- Robot Thymio avec firmware compatible
- Microphone fonctionnel
- GPU recommandé pour de meilleures performances (optionnel)

### 1. Cloner le repository
```bash
git clone https://github.com/TitanSage02/Vox-Thymio.git
cd VoxThymio
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Configuration audio (Windows)
```bash
# Si pyaudio pose problème
pip install pipwin
pipwin install pyaudio
```

## 🎯 Utilisation

### Utilisation basique
```python
from src.smart_voice_controller import SmartVoiceController
from src.controller.thymio_controller import ThymioController
import asyncio

async def main():
    # Initialiser la connexion Thymio
    thymio = ThymioController()
    await thymio.connect()
    
    # Créer le contrôleur vocal
    voice_controller = SmartVoiceController(thymio)
    
    # Traiter une commande texte
    result = await voice_controller.process_command("avance")
    print(result)
    
    # Démarrer la reconnaissance vocale
    await voice_controller.voice_recognition()

asyncio.run(main())
```

### Commandes disponibles

#### Commandes de base
- **Mouvement** : "avance", "recule", "va tout droit"
- **Rotation** : "tourne à droite", "tourne à gauche", "fais demi-tour"
- **Arrêt** : "arrête", "stop", "arrête-toi"

#### Ajouter de nouvelles commandes
```python
# Ajouter une commande personnalisée
voice_controller.add_new_command(
    command_id="dance",
    description="faire une danse",
    code="motor.left.target = 200\nmotor.right.target = -200\ncall prox.all"
)
```

## 🔧 Configuration

### Ajustement des seuils
```python
# Modifier les seuils de similarité
voice_controller.update_thresholds(
    execution_threshold=0.6,  # Seuil pour exécuter (0.0-1.0)
    learning_threshold=0.85   # Seuil pour apprendre (0.0-1.0)
)
```

### Configuration audio
Modifiez les paramètres dans `speech_recognizer.py` :
```python
# Configuration de reconnaissance vocale
language = "fr-FR"          # Langue de reconnaissance
model_size = "small"        # Taille du modèle Whisper
energy_threshold = 300      # Seuil de détection audio
```

## 📊 Fonctionnement technique

### 1. Pipeline de traitement vocal
1. **Capture audio** → Microphone via PyAudio/SoundDevice
2. **Reconnaissance** → Whisper ou SpeechRecognition
3. **Normalisation** → Nettoyage et préparation du texte
4. **Embedding** → Génération via SentenceTransformer multilingue
5. **Recherche** → Similarité cosinus dans ChromaDB
6. **Exécution** → Code Aseba envoyé au Thymio

### 2. Modèles utilisés
- **Reconnaissance vocale** : OpenAI Whisper ou Google Speech Recognition
- **Embeddings sémantiques** : `paraphrase-multilingual-MiniLM-L12-v2`
- **Base vectorielle** : ChromaDB avec distance cosinus
- **Communication robot** : Protocol Aseba via tdmclient

### 3. Système d'apprentissage
- **Seuil d'exécution** (0.5) : Commandes reconnues sont exécutées
- **Seuil d'apprentissage** (0.85) : Nouvelles variantes sont automatiquement ajoutées
- **Détection de conflits** : Évite les doublons de commandes similaires

## 🧪 Tests et débogage

### Exécuter les tests
```bash
# Test du contrôleur principal
python src/smart_voice_controller.py

# Test de la reconnaissance vocale
python src/speech_recognizer.py

# Test de la communication Thymio
python src/controller/thymio_controller.py
```

### Diagnostic des performances
```python
# Obtenir les statistiques du système
stats = voice_controller.get_system_stats()
print(f"Commandes en base: {stats['database']['total_commands']}")
print(f"Modèle d'embedding: {stats['embedding_model']['model_name']}")
```

## 🛠️ Dépendances principales

| Package | Version | Usage |
|---------|---------|--------|
| `tdmclient` | ≥0.1.0 | Communication Thymio |
| `SpeechRecognition` | ≥3.10.0 | Reconnaissance vocale fallback |
| `openai-whisper` | ≥20230314 | Reconnaissance vocale principale |
| `transformers` | ≥4.0.0 | Modèles d'embeddings |
| `sentence-transformers` | ≥2.2.0 | Embeddings sémantiques |
| `chromadb` | ≥0.4.0 | Base vectorielle |
| `torch` | ≥1.10.0 | Calculs d'embeddings |
| `pyaudio` | ≥0.2.11 | Capture audio |

## 🐛 Résolution de problèmes

### Problèmes courants

#### 1. Erreur de connexion Thymio
```bash
❌ Aucun robot Thymio détecté
```
**Solution** : Vérifiez que le robot est allumé et connecté via USB/Bluetooth.

#### 2. Erreur PyAudio
```bash
❌ OSError: No Default Input Device Available
```
**Solution** : Vérifiez les permissions du microphone et installez PyAudio correctement.

#### 3. Modèle Whisper non trouvé
```bash
❌ Erreur faster-whisper: model not found
```
**Solution** : Le modèle se télécharge automatiquement au premier usage. Vérifiez votre connexion internet.

#### 4. Reconnaissance vocale imprécise
**Solutions** :
- Ajustez `energy_threshold` dans speech_recognizer.py
- Parlez plus clairement et proche du microphone
- Réduisez le bruit ambiant

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/amelioration`)
3. Commitez vos changements (`git commit -am 'Ajout de nouvelle fonctionnalité'`)
4. Push sur la branche (`git push origin feature/amelioration`)
5. Ouvrez une Pull Request

### Standards de code
- Suivez PEP 8 pour le style Python
- Documentez les nouvelles fonctions avec des docstrings
- Ajoutez des tests pour les nouvelles fonctionnalités
- Utilisez des noms de variables explicites en français

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👥 Auteurs

- **TitanSage02** - *Développement principal* - [GitHub](https://github.com/TitanSage02)
- **Ai4Innov** - *Organisation* 

## 🙏 Remerciements

- [Mobsya](https://www.mobsya.org/) pour le robot Thymio et l'écosystème de développement
- [OpenAI](https://openai.com/) pour le modèle Whisper
- [Sentence Transformers](https://www.sbert.net/) pour les embeddings multilingues
- [ChromaDB](https://www.trychroma.com/) pour la base vectorielle
- La communauté open source pour les outils et bibliothèques utilisés

## 📈 Roadmap

- [ ] Interface graphique complète
- [ ] Support de commandes gestuelles
- [ ] Intégration de commandes complexes multi-étapes
- [ ] Support de multiples robots simultanément
- [ ] API REST pour contrôle distant
- [ ] Reconnaissance de l'intention contextuelle
- [ ] Mode d'apprentissage interactif guidé

---

**VoxThymio** - Donnez une voix à votre robot ! 🤖🗣️
