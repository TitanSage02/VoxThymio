# Interface Graphique VoxThymio

## 🎨 Vue d'ensemble

L'interface graphique VoxThymio offre un contrôle complet et intuitif du système de reconnaissance vocale pour robot Thymio. Développée par **Espérance AYIWAHOUN** pour **AI4Innov**.

## 🚀 Lancement

### Méthode 1 : Depuis la racine du projet
```bash
python main.py
```

### Méthode 2 : Directement depuis le dossier GUI
```bash
cd gui
python launcher.py
```

### Méthode 3 : Lancement direct
```bash
cd gui
python voxthymio_gui.py
```

## 🏗️ Architecture de l'Interface

### Zone de Contrôle Vocal (Gauche)
- **Boutons de contrôle** : Écouter, Pause, Arrêter
- **Visualisation audio** : Barre de progression du niveau sonore
- **Configuration** : Mode apprentissage, seuils configurables
- **Feedback** : Affichage des dernières commandes reconnues

### Zone de Gestion des Commandes (Droite)
Organisée en 3 onglets :

#### 📚 Bibliothèque
- Liste de toutes les commandes disponibles
- Recherche et filtrage
- Modification et suppression des commandes personnalisées
- Test des commandes

#### ➕ Nouvelle Commande
- Création de commandes personnalisées
- Éditeur de code Aseba avec coloration syntaxique
- Test de similarité sémantique
- Validation avant ajout

#### 🤖 Assistant
- Templates de code prêts à l'emploi
- Suggestions contextuelles
- Documentation intégrée

### Barre d'État (Bas)
- Informations développeur
- Statuts de connexion (Thymio, Audio)
- Compteur de commandes
- Latence et mode d'apprentissage

## ⚙️ Configuration

### Fichier `config.json`
L'interface utilise un fichier de configuration JSON pour personnaliser :

```json
{
    "application": {
        "name": "VoxThymio",
        "version": "1.0",
        "developer": "Espérance AYIWAHOUN",
        "organization": "AI4Innov"
    },
    "ui": {
        "colors": {
            "primary": "#00d4aa",
            "secondary": "#2c3e50"
        },
        "window": {
            "width": 1200,
            "height": 800
        }
    },
    "voice": {
        "execution_threshold": 0.5,
        "learning_threshold": 0.85
    }
}
```

### Paramètres Modifiables
- **Seuils de similarité** : Via les curseurs dans l'interface
- **Mode d'apprentissage** : Case à cocher
- **Templates de code** : Modifiables dans config.json

## 🎯 Fonctionnalités Principales

### Contrôle Vocal
1. **Activation** : Clic sur "ÉCOUTER"
2. **Reconnaissance** : Le système écoute et analyse
3. **Exécution** : Commandes reconnues envoyées au robot
4. **Apprentissage** : Nouvelles variantes apprises automatiquement

### Création de Commandes
1. **Description** : Saisir la commande en langage naturel
2. **Code Aseba** : Écrire le code correspondant
3. **Test de similarité** : Vérifier les conflits potentiels
4. **Sauvegarde** : Ajout à la base de données

### Templates Disponibles
- **Mouvement** : Avancer/reculer
- **Rotation** : Tourner gauche/droite
- **Capteurs** : Lecture des proximètres
- **LEDs** : Contrôle d'éclairage
- **Sons** : Émission de tonalités
- **Temporisateurs** : Gestion du temps

## 🛠️ Dépannage

### Problèmes Courants

#### Interface ne se lance pas
```bash
# Vérifier les dépendances
pip install -r ../requirements.txt

# Tester tkinter
python -c "import tkinter; print('Tkinter OK')"
```

#### Erreur d'import des modules
```bash
# Lancer depuis le launcher
python launcher.py

# Ou vérifier le PYTHONPATH
export PYTHONPATH=$PYTHONPATH:../src
```

#### Robot non détecté
- Vérifier que Thymio Suite est fermé
- Reconnecter le câble USB
- Redémarrer le robot

### Messages d'Erreur

| Erreur | Solution |
|--------|----------|
| "Module smart_voice_controller not found" | Utiliser `launcher.py` |
| "No Thymio robot detected" | Vérifier connexion USB/Bluetooth |
| "Audio device not available" | Vérifier permissions microphone |
| "Config file not found" | Créer config.json ou utiliser défauts |

## 🎨 Personnalisation

### Thèmes
Modifiez les couleurs dans `config.json` :
```json
"colors": {
    "primary": "#your_color",
    "secondary": "#your_color",
    "background": "#your_color"
}
```

### Templates Personnalisés
Ajoutez vos propres templates :
```json
"templates": {
    "custom_move": {
        "name": "Mon Mouvement",
        "code": "// Votre code ici"
    }
}
```

## 📝 Structure des Fichiers

```
gui/
├── voxthymio_gui.py      # Interface principale
├── launcher.py           # Script de lancement
├── config.json           # Configuration
├── README.md            # Cette documentation
└── __pycache__/         # Cache Python
```

## 🤝 Contribution

Pour contribuer à l'interface :

1. **Fork** le projet
2. **Créer** une branche feature
3. **Modifier** les fichiers GUI
4. **Tester** l'interface
5. **Soumettre** une Pull Request

### Standards de Code
- Respecter PEP 8
- Commenter les nouvelles fonctionnalités
- Tester sur différentes résolutions d'écran
- Maintenir la compatibilité avec la configuration JSON

---

**Interface VoxThymio** - Contrôle intuitif pour robots intelligents ! 🤖✨
