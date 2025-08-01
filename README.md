# VoxThymio

VoxThymio est une suite logicielle open-source permettant de contrôler le robot Thymio à la voix ou via des commandes manuelles. Le projet propose deux versions majeures : la V1 (stable, orientée démonstration) et la V2 (modulaire, évolutive, intégrant l'IA pour la compréhension du langage naturel).

---

## Table des matières
- [Présentation générale](#présentation-générale)
- [V1 – Version Démonstration](#v1--version-démonstration)
- [V2 – Version Modulaire et IA](#v2--version-modulaire-et-ia)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Auteurs et Licence](#auteurs-et-licence)

---

## Présentation générale

VoxThymio permet de piloter un robot Thymio à l'aide de la voix, en français, ou via des commandes clavier. Il s'adresse aux enseignants, makers, chercheurs ou toute personne souhaitant expérimenter la robotique éducative et l'IA appliquée à la compréhension du langage naturel.

Deux versions sont proposées :
- **V1** : version démonstration, simple à utiliser, idéale pour des ateliers ou des présentations.
- **V2** : version avancée, modulaire, intégrant un classifieur d'intention basé sur BERT pour une compréhension plus naturelle des commandes vocales.

---

## V1 – Version Démonstration

- Interface simple, orientée démonstration.
- Contrôle vocal de Thymio avec un ensemble de commandes prédéfinies.
- Utilisation de bibliothèques classiques de reconnaissance vocale.
- Packaging facile pour une utilisation sur différents postes.
- Idéale pour des ateliers, des démonstrations ou une première prise en main.

**Structure** : voir le dossier `v1/`.

---

## V2 – Version Modulaire et IA

- Architecture modulaire (dossier `v2/`).
- Contrôle vocal avancé : intégration d'un modèle BERT pour la classification d'intention (compréhension du langage naturel).
- Possibilité d'ajouter facilement de nouvelles commandes ou de nouveaux modules.
- Séparation claire entre la logique de reconnaissance vocale, la gestion des commandes et la communication avec le robot.
- Prise en charge de l'évolution du projet (ajout de notebooks, d'exemples, etc.).

**Points clés** :
- Utilisation de `transformers`, `torch`, `joblib` pour l'IA.
- Fichier `commands.json` pour la configuration des commandes.
- Notebooks pour l'entraînement et l'expérimentation.

---

## Installation

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/TitanSage02/Vox-Thymio.git
   ```
2. Installez les dépendances pour la version souhaitée :
   - Pour la V1 : `cd v1 && pip install -r requirements.txt`
   - Pour la V2 : `cd v2 && pip install -r requirements.txt`

---

## Utilisation

- **V1** : Lancez `main.py` dans le dossier `v1/` pour démarrer l'interface de démonstration.
- **V2** : Lancez `main.py` dans le dossier `v2/` pour profiter de la version avancée avec IA.

Des exemples et des notebooks sont disponibles dans le dossier `v2/notebooks/` pour l'entraînement ou l'expérimentation autour de la classification d'intention.

---

## Auteurs et Licence

Projet développé par Espérance AYIWAHOUN pour dans le cadre du projet TechEduc porté par Ai4Innov. Licence MIT.

Pour toute question ou contribution, ouvrez une issue ou contactez les auteurs via GitHub.
