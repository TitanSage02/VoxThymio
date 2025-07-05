# 🤖 VoxThymio - Contrôle Vocal Intelligent

> **Système de contrôle vocal pour robot Thymio**  
> Développé par **Espérance AYIWAHOUN** pour **AI4Innov**

![VoxThymio](https://img.shields.io/badge/VoxThymio-v1.0-00d4aa?style=for-the-badge&logo=robot)
![AI4Innov](https://img.shields.io/badge/AI4Innov-Innovation-00d4aa?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## ✨ Aperçu

**VoxThymio** révolutionne l'interaction avec le robot Thymio grâce à une interface vocale naturelle et intuitive. Plus besoin de programmation complexe : parlez simplement à votre robot !

### 🎯 Fonctionnalités Principales

- 🎤 **Contrôle vocal en français** - Commandes naturelles et intuitives
- 🎮 **Interface graphique moderne** - Design professionnel avec branding AI4Innov  
- 🔌 **Connexion simplifiée** - Détection automatique du robot Thymio
- 📊 **Journal d'activité** - Suivi en temps réel des actions
- 🛡️ **Robustesse** - Gestion d'erreurs et récupération automatique

---

## 🚀 Installation Rapide

### Option 1: Exécutable (Recommandé)
1. **Téléchargez** `VoxThymio.exe` depuis `dist/VoxThymio.exe`
2. **Double-cliquez** pour lancer (aucune installation requise)
3. **Connectez** votre robot Thymio
4. **Profitez** du contrôle vocal !

### Option 2: Code Source
```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer l'interface graphique
python voxthymio_gui.py
```

### Option 3: Avec Splash Screen
```bash
# Lancer avec écran de démarrage
python voxthymio_launcher.py
```

---

## 🎮 Guide d'Utilisation

### 🔌 Connexion Initial
1. **Connectez** votre Thymio via USB ou Bluetooth
2. **Lancez** VoxThymio
3. **Cliquez** "Connexion" dans l'interface
4. **Attendez** la confirmation "Robot connecté"

### 🎤 Commandes Vocales
| Commande | Synonymes | Action |
|----------|-----------|---------|
| `"avance"` | "en avant" | Avancer |
| `"recule"` | "en arrière" | Reculer |
| `"gauche"` | "tourne à gauche" | Tourner à gauche |
| `"droite"` | "tourne à droite" | Tourner à droite |
| `"stop"` | "arrête" | Arrêter |

### 🎮 Contrôle Manuel
- Utilisez les **boutons directionnels** pour un contrôle précis
- **Stop d'urgence** toujours accessible
- **Journal d'activité** pour suivre toutes les actions

---

## 📋 Configuration Requise

### 🔧 Système
- **OS** : Windows 10/11 (64-bit)
- **RAM** : 4 GB minimum, 8 GB recommandé
- **Espace** : 500 MB libre
- **Microphone** : Intégré ou externe

### 🤖 Robot
- **Thymio II** avec firmware récent
- **Connexion** : USB ou Bluetooth
- **Drivers** : Thymio Suite installé (recommandé)

---

## 🛠️ Développement

### Architecture Technique
```
VoxThymio/
├── src/
│   ├── voice_controller.py      # Reconnaissance vocale
│   └── communication/
│       └── thymio_controller.py # Communication robot
├── voxthymio_gui.py            # Interface graphique
├── voxthymio_launcher.py       # Splash screen
├── build_executable.py        # Script de packaging
└── dist/
    └── VoxThymio.exe          # Exécutable final
```

### Technologies Utilisées
- **Python 3.10+** - Langage principal
- **tkinter** - Interface graphique
- **SpeechRecognition** - Reconnaissance vocale
- **tdmclient** - Communication Thymio
- **PyInstaller** - Packaging exécutable

---

## 📦 Créer l'Exécutable

### Méthode Automatique
```bash
python build_executable.py
```

### Méthode Manuelle
```bash
pyinstaller --onefile --windowed --name=VoxThymio --icon=robot.ico voxthymio_gui.py
```

---

## 📞 Support & Contact

**Développeur** : Espérance AYIWAHOUN  
**Organisation** : AI4Innov  
**Version** : 1.0.0  
**Licence** : MIT  

---

**🎉 VoxThymio - L'avenir du contrôle robotique vocal**

*Développé avec passion par Espérance AYIWAHOUN pour AI4Innov*