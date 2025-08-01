# 🤖 VoxThymio v1 – Contrôle Vocal Intelligent pour Thymio

> **Système de contrôle vocal pour robot Thymio**  
> Développé par **Espérance AYIWAHOUN** pour **AI4Innov**

![VoxThymio](https://img.shields.io/badge/VoxThymio-v1.0-00d4aa?style=for-the-badge&logo=robot)
![AI4Innov](https://img.shields.io/badge/AI4Innov-Innovation-00d4aa?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## ✨ Présentation

**VoxThymio v1** révolutionne l’interaction avec le robot Thymio grâce à une interface vocale naturelle et intuitive. Plus besoin de programmation complexe : parlez simplement à votre robot !

### 🎯 Fonctionnalités principales

- 🎤 **Contrôle vocal en français** – Commandes naturelles et intuitives
- 🖥️ **Interface graphique moderne** – Design professionnel avec branding AI4Innov
- 🔌 **Connexion simplifiée** – Détection automatique du robot Thymio
- 📈 **Journal d’activité** – Suivi en temps réel des actions
- 🛡️ **Robustesse** – Gestion d’erreurs et récupération automatique

---

## 🚀 Installation

### 1. Exécutable (recommandé)
1. Téléchargez `VoxThymio.exe` depuis `dist/VoxThymio.exe`
2. Double-cliquez pour lancer (aucune installation requise)
3. Connectez votre robot Thymio
4. Profitez du contrôle vocal !

### 2. Depuis le code source

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer l’interface graphique
python voxthymio_gui.py
```

### 3. Avec écran de démarrage

```bash
python voxthymio_launcher.py
```

---

## 🕹️ Utilisation

### Connexion initiale
1. Connectez votre Thymio via USB ou Bluetooth
2. Lancez VoxThymio
3. Cliquez sur « Connexion » dans l’interface
4. Attendez la confirmation « Robot connecté »

### Commandes vocales principales

| Commande   | Synonymes             | Action                |
|------------|-----------------------|-----------------------|
| avance     | en avant              | Avancer               |
| recule     | en arrière            | Reculer               |
| gauche     | tourne à gauche       | Tourner à gauche      |
| droite     | tourne à droite       | Tourner à droite      |
| stop       | arrête                | Arrêter               |

### Contrôle manuel
- Utilisez les boutons directionnels pour un contrôle précis
- Stop d’urgence toujours accessible
- Journal d’activité pour suivre toutes les actions

---

## 🖥️ Configuration requise

- **OS** : Windows 10/11 (64-bit)
- **RAM** : 4 Go minimum (8 Go recommandé)
- **Espace disque** : 500 Mo libre
- **Microphone** : Intégré ou externe
- **Robot** : Thymio II avec firmware récent, connexion USB/Bluetooth, Thymio Suite installé

---

## 🛠️ Développement

### Architecture

```
VoxThymio/
├── src/
│   ├── voice_controller.py        # Reconnaissance vocale
│   └── communication/
│       └── thymio_controller.py  # Communication robot
├── voxthymio_gui.py              # Interface graphique
├── voxthymio_launcher.py         # Splash screen
├── utils/build_executable.py     # Script de packaging
└── dist/VoxThymio.exe            # Exécutable final
```

### Technologies

- **Python 3.10+**
- **tkinter** (interface graphique)
- **SpeechRecognition** (reconnaissance vocale)
- **tdmclient** (communication Thymio)
- **PyInstaller** (packaging)

---

## 📦 Création de l’exécutable

Automatique :
```bash
python utils/build_executable.py
```

Manuelle :
```bash
pyinstaller --onefile --windowed --name=VoxThymio --icon=gui/robot.ico gui/voxthymio_gui.py
```

---

## 📞 Support & Contact

**Développeur** : Espérance AYIWAHOUN  
**Organisation** : AI4Innov  
**Licence** : MIT

---

**🎉 VoxThymio – L’avenir du contrôle robotique vocal !**

*Développé avec passion par Espérance AYIWAHOUN pour AI4Innov*