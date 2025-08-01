# 🤖 VoxThymio v2 – Contrôle Vocal Avancé pour Thymio

> **Nouvelle génération de contrôle vocal pour robot Thymio**  
> Développé par **Espérance AYIWAHOUN** pour **AI4Innov**

![VoxThymio](https://img.shields.io/badge/VoxThymio-v2.0-00d4aa?style=for-the-badge&logo=robot)
![AI4Innov](https://img.shields.io/badge/AI4Innov-Innovation-00d4aa?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## ✨ Présentation

**VoxThymio v2** propose un contrôle vocal avancé du robot Thymio. Cette version exploite un classifieur d’intention pour une expérience utilisateur optimale.

---

## 🚀 Fonctionnalités

- 🎤 Reconnaissance vocale avancée (français)
- 🧠 Classification d’intention pour interprétation intelligente des commandes
- 🖥️ Interface utilisateur interactive en terminal
- 🛠️ Mode manuel ou vocal
- 🔧 Personnalisation facile des commandes

---

## 🖥️ Configuration requise

- **Python** ≥ 3.8
- **Thymio Suite** installé et en cours d’exécution
- **Microphone** (intégré ou externe)

---

## ⚡ Installation

1. Clonez le dépôt et placez-vous dans le dossier `v2`
2. Installez les dépendances :
    ```bash
    pip install -r requirements.txt
    ```
3. Lancez la simulation dans Thymio Suite ou connectez un robot Thymio
4. Exécutez l’application :
    ```bash
    python main.py
    ```


---

## 🕹️ Modes d’utilisation

- **Mode manuel** : sélectionnez les commandes par leur numéro dans l’interface.
- **Mode vocal** : activez le mode vocal et prononcez les commandes clairement.

---

## 🛠️ Architecture technique

```
v2/
├── src/
│   ├── voice_controller.py        # Contrôleur vocal & classification d’intention
│   ├── intent_classifier.py       # Classifieur d’intention (machine learning)
│   └── communication/
│       └── thymio_controller.py   # Communication avec Thymio
├── commands.json                  # Commandes personnalisables
├── main.py                        # Point d’entrée
└── requirements.txt               # Dépendances
```

---

## 📄 Licence

Ce projet est sous licence MIT.

---

**🎉 VoxThymio – Le futur du contrôle vocal pour Thymio !**