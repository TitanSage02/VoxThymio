# 🤖 VoxThymio – Contrôle intelligent du robot Thymio

> **Système avancé de contrôle vocal et manuel pour robot Thymio**  
> Développé par **Espérance AYIWAHOUN** pour **AI4Innov**

![VoxThymio](https://img.shields.io/badge/VoxThymio-v2.0-00d4aa?style=for-the-badge&logo=robot)
![AI4Innov](https://img.shields.io/badge/AI4Innov-Innovation-00d4aa?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-≥3.8-blue?style=for-the-badge&logo=python)
![Whisper](https://img.shields.io/badge/Speech--to--Text-Whisper-informational?style=for-the-badge)
![BERT](https://img.shields.io/badge/NLP-BERT-yellow?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

## 📋 Sommaire

- [Présentation](#-présentation)
- [Fonctionnalités](#-fonctionnalités)
- [Configuration requise](#-configuration-requise)
- [Installation](#-installation)
- [Modes d'utilisation](#-modes-dutilisation)
  - [Mode manuel (clavier)](#mode-manuel-clavier)
  - [Mode vocal (IA)](#mode-vocal-ia)
- [Pipeline de traitement vocal](#-pipeline-de-traitement-vocal)
- [Architecture technique](#-architecture-technique)
- [Personnalisation](#-personnalisation)
- [Dépannage](#-dépannage)
- [Licence](#-licence)

## ✨ Présentation

# VoxThymio - Contrôle Intelligent avec IA

**VoxThymio** est un système de contrôle intelligent pour le robot Thymio utilisant l'intelligence artificielle pour comprendre et exécuter des commandes en langage naturel français.

## 🚀 Nouvelle Architecture Intelligente

Cette version révolutionnaire utilise :
- **BERT français** (CamemBERT) pour la compréhension du langage naturel
- **ChromaDB** comme base vectorielle pour stocker les embeddings
- **Recherche de similarité** pour matcher les commandes
- **Apprentissage dynamique** pour ajouter de nouvelles commandes

### 🧠 Fonctionnement de l'IA

1. **Génération d'embeddings** : BERT convertit les descriptions en vecteurs numériques
2. **Recherche de similarité** : Comparaison cosinus entre la requête et les commandes stockées
3. **Seuils intelligents** :
   - **≥ 0.6** : Exécution automatique de la commande
   - **≥ 0.85** : Apprentissage automatique d'une nouvelle commande

## 📦 Installation

### Prérequis
- **Python 3.8+**
- **Thymio Suite** installé et robot connecté
- **8GB RAM minimum** (pour BERT)

### Installation automatique
```bash
python install.py
```

### Installation manuelle
```bash
pip install -r requirements.txt
```

## 🎮 Utilisation

### Mode Console
```bash
python main.py
```

### Interface Graphique
```bash
python launch_gui.py
```

## 🎤 Commandes Vocales Exemples

### Mouvements
- "avancer rapidement"
- "tourner vers la gauche"
- "reculer lentement"
- "arrêter le robot"

### Éclairage
- "allumer la LED en rouge"
- "LED bleue"
- "éteindre toutes les lumières"

### Sons
- "jouer un son heureux"
- "volume maximum"
- "jouer la note Do"

## ➕ Ajouter des Commandes Personnalisées

### Via l'Interface Graphique
1. Onglet "Commandes" → "Ajouter une Nouvelle Commande"
2. Saisir :
   - **ID** : identifiant unique (ex: "dance_move")
   - **Description** : "faire danser le robot en tournant"
   - **Code Thymio** : 
     ```
     motor.left.target = 200
     motor.right.target = -200
     timer.period[0] = 1000
     ```
   - **Catégorie** : custom, movement, lights, sounds, advanced

### Via l'API Python
```python
# Connexion et ajout d'une commande
await voice_controller.process_voice_command("faire clignoter les LEDs en vert")

# Ajout manuel
result = voice_controller.add_new_command(
    command_id="blink_green",
    description="faire clignoter les LEDs en vert",
    code="call leds.top(0,32,0)
timer.period[0] = 500",
    category="lights"
)
```

## 🏗️ Architecture du Système

```
VoxThymio/
├── main.py                     # Interface console principale
├── launch_gui.py              # Lanceur interface graphique
├── install.py                 # Script d'installation
├── requirements.txt           # Dépendances Python
├── config.json               # Configuration système
├── commands.json             # Commandes par défaut
├── src/                      # Code source principal
│   ├── embedding_manager.py    # Gestionnaire BERT français
│   ├── command_manager.py      # Base vectorielle ChromaDB
│   ├── smart_voice_controller.py # Contrôleur IA principal
│   └── communication/
│       └── thymio_controller.py # Communication Thymio
├── gui/                      # Interface graphique
│   ├── modern_voxthymio_gui.py # GUI moderne avec Tkinter
│   └── robot.ico             # Icône de l'application
├── vector_db/               # Base ChromaDB (auto-créé)
├── logs/                    # Fichiers de log
└── exports/                 # Exportations de données
```

## ⚙️ Configuration Avancée

### Ajustement des Seuils
```python
# Via l'interface ou le code
voice_controller.update_thresholds(
    execution_threshold=0.7,    # Plus strict pour l'exécution
    learning_threshold=0.9      # Plus strict pour l'apprentissage
)
```

### Modèles BERT Disponibles
- `camembert-base` (par défaut) - Équilibré performance/mémoire
- `camembert-large` - Meilleure précision, plus de mémoire
- `flaubert/flaubert_base_cased` - Alternative française

## 📊 Monitoring et Statistiques

L'interface graphique propose :
- **Tableau de bord** avec métriques en temps réel
- **Analyse des similarités** pour tester les commandes
- **Gestion des seuils** avec visualisation
- **Export/Import** des bases de commandes

## 🔧 Dépannage

### Erreurs Courantes

**"Modèle BERT non trouvé"**
```bash
# Vérifier la connexion internet et relancer
python -c "from transformers import AutoModel; AutoModel.from_pretrained('camembert-base')"
```

**"ChromaDB database locked"**
```bash
# Supprimer le dossier vector_db et relancer
rm -rf vector_db/
```

**"Thymio non détecté"**
- Vérifier que Thymio Suite est lancé
- Vérifier la connexion USB/Wireless
- Redémarrer le robot

### Performance
- **CPU** : Multithreading automatique
- **GPU** : Détection automatique CUDA si disponible
- **Mémoire** : Optimisation automatique des embeddings

## 🎯 Exemples d'Utilisation Avancée

### Séquences Complexes
```python
# Créer une séquence de danse
await voice_controller.process_voice_command("créer une danse avec des LEDs colorées")
```

### Commandes Conditionnelles
```python
# Ajouter une commande basée sur les capteurs
command_code = """
if prox.horizontal[2] > 1000:
    motor.left.target = -200
    motor.right.target = 200
else:
    motor.left.target = 200
    motor.right.target = 200
"""
```

## 🤝 Contribution

Le système est conçu pour être extensible :
1. **Nouveaux modèles BERT** : Modifier `embedding_manager.py`
2. **Nouvelles bases vectorielles** : Étendre `command_manager.py`
3. **Interfaces supplémentaires** : Créer dans `gui/`

## 📄 Licence

Développé par **Espérance AYIWAHOUN** pour **AI4Innov**.

## 🏆 Fonctionnalités Clés

✅ **Compréhension naturelle** du français avec BERT  
✅ **Apprentissage automatique** de nouvelles commandes  
✅ **Interface graphique moderne** avec contrôles avancés  
✅ **Base vectorielle persistante** avec ChromaDB  
✅ **Système de seuils configurables** pour la précision  
✅ **Export/Import** de configurations de commandes  
✅ **Monitoring en temps réel** des performances IA  
✅ **Support multi-plateforme** (Windows, Linux, macOS)  

---

**VoxThymio - Quand l'intelligence artificielle rencontre la robotique éducative !** 🤖✨

- **Mode manuel** : contrôle précis via clavier
- **Mode vocal** : contrôle par la voix grâce à l'intelligence artificielle

Cette version exploite un modèle BERT de classification d'intention pour interpréter intelligemment les commandes vocales en français, offrant une expérience utilisateur naturelle et intuitive.

## 🚀 Fonctionnalités

- **Interface de contrôle unifiée** :
  - Mode manuel (contrôle clavier)
  - Mode vocal (contrôle par la voix)

- **Pipeline IA complet** :
  - 🎤 Capture audio via microphone
  - 📝 Transcription vocale (Speech-to-Text)
  - 🧠 Classification d'intention avec BERT
  - 🤖 Exécution de commande sur Thymio

- **Expérience utilisateur optimisée** :
  - Interface console claire et colorée
  - Retour visuel sur chaque étape du processus
  - Organisation des commandes par catégorie

- **Système robuste** :
  - Gestion des erreurs et timeouts
  - Calibration automatique du microphone
  - Communication asynchrone avec Thymio

## 🖥️ Configuration requise

- **Python** ≥ 3.8
- **Thymio** (connecté ou emulé avec Thymio Suite)
- **Microphone** (intégré ou externe)
- **Hardware recommandé** :
  - CPU : Core i3 ou équivalent
  - RAM : 4GB minimum (8GB recommandé)
  - Stockage : 500MB d'espace libre

## ⚡ Installation

1. **Clonez le dépôt et placez-vous dans le dossier `v2`**
   ```bash
   git clone https://github.com/AI4Innov/VoxThymio.git
   cd VoxThymio/v2
   ```

2. **Créez un environnement virtuel (recommandé)**
   ```bash
   python -m venv venv
   # Sur Windows
   venv\Scripts\activate
   # Sur macOS/Linux
   source venv/bin/activate
   ```

3. **Installez les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Préparez le robot Thymio**
   - Lancez Thymio Suite
   - Connectez un robot Thymio physique ou utilisez le simulateur

5. **Exécutez l'application**
   ```bash
   python main.py
   ```

## 🕹️ Modes d'utilisation

### Mode manuel (clavier)

Le mode manuel permet un contrôle précis du robot via le clavier :

1. Lorsque l'application démarre, vous êtes par défaut en mode manuel
2. Utilisez les numéros affichés pour exécuter les commandes :
   - Exemple : tapez `1` pour exécuter la commande "avancer"
3. Commandes système :
   - `v` : Passer en mode vocal
   - `l` : Afficher toutes les commandes disponibles
   - `0` : Quitter l'application

### Mode vocal (IA)

Le mode vocal utilise l'IA pour interpréter vos commandes vocales :

1. Depuis le mode manuel, tapez `v` pour activer le mode vocal
2. Attendez le signal d'écoute ("Écoute en cours...")
3. Énoncez clairement votre commande (ex: "Avance", "Tourne à gauche", "Allume la LED rouge")
4. Le système :
   - Capture votre voix
   - Transcrit la parole en texte
   - Analyse l'intention avec BERT
   - Exécute la commande correspondante sur le robot
5. Pour revenir au mode manuel, dites "Quitter" ou attendez un timeout

## 🔄 Pipeline de traitement vocal

Le traitement d'une commande vocale suit le pipeline suivant :

1. **Capture audio** 
   - Via le microphone avec calibration automatique
   - Gestion des timeouts et du bruit ambiant

2. **Transcription vocale**
   - Conversion parole → texte via Whisper (local, sans connexion Internet)
   - Support du français et haute précision
   - Fonctionnement entièrement hors ligne

3. **Classification d'intention par BERT**
   - Analyse du texte avec modèle BERT pré-entraîné
   - Identification directe de la commande à exécuter
   - Le modèle a été entraîné pour reconnaître les commandes dans `commands.json`

4. **Vérification et exécution**
   - Vérification que la commande identifiée existe
   - Exécution du code Aseba associé à la commande
   - Retour d'état de l'exécution

> 💡 **Note technique** : Contrairement aux systèmes traditionnels qui nécessitent un mappage manuel entre les phrases reconnues et les commandes, notre modèle BERT a été directement entraîné pour prédire les commandes exactes utilisées dans `commands.json`.

## 🛠️ Architecture technique

```
v2/
├── main.py                        # Point d'entrée et interface utilisateur
├── commands.json                  # Définition des commandes Thymio (personnalisable)
├── requirements.txt               # Dépendances Python
│
├── src/                           # Code source principal
│   ├── __init__.py
│   ├── voice_controller.py        # Contrôleur vocal & pipeline de traitement
│   ├── intent_classifier.py       # Classificateur d'intention BERT
│   │
│   └── communication/             # Communication avec le robot
│       ├── __init__.py
│       └── thymio_controller.py   # Contrôleur Thymio (via tdmclient)
│
├── models/                        # Modèles d'IA pré-entraînés
│   ├── config.json                # Configuration du modèle BERT
│   ├── model.safetensors          # Poids du modèle BERT
│   ├── label_encoder.pkl          # Encodeur d'étiquettes
│   ├── vocab.txt                  # Vocabulaire BERT
│   └── ...
│
└── notebooks/                     # Notebooks d'entraînement et d'analyse
    ├── classification_intention_robot.ipynb
    └── Intent_dataset.csv         # Jeu de données d'entraînement
```

## 🔧 Personnalisation

### Personnalisation des commandes existantes

1. Ouvrez le fichier `commands.json`
2. **Important** : Ne modifiez que le code Aseba (valeurs), pas les noms des commandes (clés)
3. Format du fichier :
   ```json
   {
     "nom_commande": "code_aseba_correspondant"
   }
   ```
4. Exemple de modification du code d'une commande existante :
   ```json
   "avancer": "motor.left.target = 300\nmotor.right.target = 300"  // Vitesse augmentée
   ```

> ⚠️ **Attention** : Le modèle BERT a été spécifiquement entraîné pour reconnaître les noms de commandes existants (les clés dans `commands.json`). Modifier ou ajouter de nouvelles clés ne fonctionnera pas sans réentraîner le modèle.

### Ajout de nouvelles commandes

Pour ajouter une commande entièrement nouvelle, vous devez :

1. Ajouter l'entrée dans `commands.json`
2. Réentraîner le modèle BERT (voir ci-dessous)

### Modification du modèle vocal

Pour améliorer la reconnaissance vocale ou ajouter de nouvelles intentions :

1. Enrichissez le dataset dans `notebooks/Intent_dataset.csv` avec les nouvelles commandes
2. Réentraînez le modèle avec le notebook `classification_intention_robot.ipynb`
3. Exportez le nouveau modèle dans le dossier `models/`

## 🔍 Dépannage

| Problème | Solution |
|----------|----------|
| **"Microphone non disponible"** | Vérifiez que votre microphone est connecté et autorisé dans les paramètres système |
| **"Impossible de se connecter au Thymio"** | Assurez-vous que Thymio Suite est en cours d'exécution et qu'un robot est disponible |
| **"Commande non reconnue"** | La parole n'a pas été correctement associée à une commande dans `commands.json`. Parlez plus clairement ou utilisez des mots-clés plus proches des commandes existantes |
| **"Erreur de classification"** | Problème avec le modèle BERT. Vérifiez que tous les fichiers dans le dossier `models/` sont présents et non corrompus |
| **"Erreur Whisper"** | Assurez-vous que Whisper est correctement installé. Exécutez `pip install openai-whisper` |
| **"Modèle Whisper lent"** | Optez pour faster-whisper (`pip install faster-whisper`) et modifiez le code pour l'utiliser |
| **Avertissements du modèle** | Ces avertissements sont généralement sans conséquence et ont été supprimés dans les dernières versions |
| **Commande reconnue mais non exécutée** | Vérifiez la syntaxe du code Aseba dans `commands.json` |

> ⚠️ **Important** : Si vous avez modifié les noms des commandes (clés) dans `commands.json`, le modèle BERT ne pourra pas les reconnaître. Vous devez réentraîner le modèle pour prendre en compte ces modifications.

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👤 Développeur

**VoxThymio** a été développé par **Espérance AYIWAHOUN** pour **AI4Innov**.