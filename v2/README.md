# 🤖 VoxThymio – Contrôle intelligent du robot Thymio

> **Système avancé de contrôle vocal et manuel pour robot Thymio**  
> Développé par **AI4Innov**

![VoxThymio](https://img.shields.io/badge/VoxThymio-v2.0-00d4aa?style=for-the-badge&logo=robot)
![AI4Innov](https://img.shields.io/badge/AI4Innov-Innovation-00d4aa?style=for-the-badge)
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

**VoxThymio** est un système avancé de contrôle du robot éducatif Thymio, qui intègre deux modes complémentaires :

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
- **Thymio Suite** (installé et en cours d'exécution)
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
   - Conversion parole → texte via Google Speech Recognition
   - Support du français

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
| **Avertissements du modèle** | Ces avertissements sont généralement sans conséquence et ont été supprimés dans les dernières versions |
| **Commande reconnue mais non exécutée** | Vérifiez la syntaxe du code Aseba dans `commands.json` |

> ⚠️ **Important** : Si vous avez modifié les noms des commandes (clés) dans `commands.json`, le modèle BERT ne pourra pas les reconnaître. Vous devez réentraîner le modèle pour prendre en compte ces modifications.

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👤 Développeur

**VoxThymio** a été développé par **Espérance AYIWAHOUN** pour **AI4Innov**.

---

** VoxThymio **