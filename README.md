# VoxThymio - Contrôle Vocal Simplifié

Contrôlez votre robot Thymio avec des commandes vocales simples.

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

```bash
python main.py
```

## Commandes Vocales

- **Mouvement**: "avancer", "reculer", "gauche", "droite", "stop"
- **LEDs**: "rouge", "vert", "bleu", "éteindre"
- **Système**: "quitter"

## Interface

- **Mode manuel**: Utilisez les touches 1-9
- **Mode vocal**: Activez avec 'v' et parlez
- **Quitter**: Tapez '0' ou dites "quitter"

## Structure

```
VoxThymio/
├── main.py                     # Interface principale
├── src/
│   ├── voice_controller.py     # Reconnaissance vocale
│   └── communication/
│       └── thymio_controller.py # Contrôle Thymio
└── requirements.txt
```

Système optimisé pour une utilisation simple et efficace ! 🤖🎤