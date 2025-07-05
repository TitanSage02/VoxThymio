# Module de Communication Thymio

Ce module permet de contrôler un robot Thymio via une interface Python simple et intuitive.

## Installation

```bash
pip install tdmclient
```

## Utilisation de base

```python
from src.communication.thymio_controller import ThymioController

# Création d'une instance du contrôleur
controller = ThymioController()

# Connexion au robot
if controller.connect():
    # Envoi de commandes
    controller.send_command("avancer")  # Fait avancer le robot
    controller.send_command("arreter")  # Arrête le robot
    
    # Lecture des capteurs
    sensors = controller.get_sensors()
    print(sensors)
    
    # Déconnexion
    controller.disconnect()
```

## Commandes disponibles

- `avancer` : Fait avancer le robot
- `reculer` : Fait reculer le robot
- `tourner_gauche` : Fait tourner le robot à gauche
- `tourner_droite` : Fait tourner le robot à droite
- `arreter` : Arrête le robot

<!-- ## Capteurs

Le module permet d'accéder aux capteurs suivants :
- Capteurs de proximité horizontaux
- Capteurs de sol -->

## Exemple interactif

Un exemple d'interface interactive est disponible dans `examples/interactive_control.py`. Pour l'utiliser :

```bash
python examples/interactive_control.py
```

## Dépannage

### Problèmes courants

1. **Erreur de connexion**
   - Vérifiez que le Thymio est bien connecté
   - Assurez-vous que le port est correct
   - Vérifiez que le Thymio est allumé

2. **Commandes non reçues**
   - Vérifiez l'état de la connexion
   - Assurez-vous que le robot est alimenté

### Logs

Les erreurs sont affichées dans la console avec des messages explicatifs.

## API Référence

### ThymioController

#### `__init__()`
Initialise le contrôleur avec les paramètres de connexion.

#### `connect() -> bool`
Établit la connexion avec le robot.

#### `disconnect()`
Déconnecte proprement le robot.

#### `send_command(command: str) -> bool`
Envoie une commande au robot.