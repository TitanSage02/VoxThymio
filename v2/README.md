# VoxThymio V2

Contrôle vocal avancé pour le robot Thymio.

## À propos

VoxThymio V2 est une application de contrôle vocal avancé pour le robot Thymio. Cette version supporte toutes les commandes définies dans le fichier `commands.json`, permettant un contrôle complet du robot par la voix.

## Fonctionnalités

- Support de nombreuses commandes vocales: mouvements, LEDs, sons, etc.
- Interface utilisateur interactive en terminal
- Mode de contrôle manuel ou vocal
- Configuration des commandes via un fichier JSON

## Configuration requise

- Python 3.8 ou supérieur
- Thymio Suite installé et en cours d'exécution
- Un microphone pour le contrôle vocal

## Installation

1. Installez les dépendances:

```bash
pip install -r requirements.txt
```

2. Lancezla simulation dans Thymio Suite ou connectez un robot Thymio

3. Exécutez l'application:

```bash
python main.py
```

## Personnalisation des commandes

Les commandes sont définies dans le fichier `commands.json`. Vous pouvez modifier ce fichier pour ajouter, supprimer ou ajuster des commandes.

### Format des commandes

```json
{
    "nom_commande": "code_aseba",
    ...
}
```

## Modes d'utilisation

### Mode manuel
Sélectionnez les commandes par leur numéro dans l'interface.

### Mode vocal
Activez le mode vocal et prononcez les commandes clairement.

## Licence