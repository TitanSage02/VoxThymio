# VoxThymio

Un système de contrôle vocal pour robot Thymio utilisant la reconnaissance vocale en temps réel.

## 📋 Vue d'ensemble

VoxThymio permet de contrôler un robot Thymio par commandes vocales en français. Le projet combine traitement audio en temps réel, reconnaissance vocale avec Whisper, et communication avec le robot pour offrir une interface naturelle et intuitive.

## 🎯 Objectifs

- Contrôle vocal temps réel du robot Thymio
- Latence de transcription < 2s
- Robustesse aux bruits environnementaux
- Support des commandes simples et séquences complexes

## 🏗️ Architecture

```
Audio Input → Prétraitement → Whisper-small → Parsing → Thymio Robot
     ↓              ↓            ↓           ↓         ↓
  Microphone   Filtres/Noise   Speech-to-  Command   Movement
               Suppression     Text        Analysis   Execution
```

## 📅 Planning de développement (12 semaines)

### Phase 1 : Communication Thymio (Semaines 1-4)
**Objectif** : Établir la communication bidirectionnelle avec le robot

**Tâches principales :**
- Configuration du protocole de communication
- Développement d'un client léger PC
- Test des commandes de base

**Livrable :** Script de test + documentation

### Phase 2 : Pipeline audio (Semaines 5-6)
**Objectif** : Préparer le traitement audio optimal

**Tâches principales :**
- Implémentation du filtrage passe-bas
- Suppression de bruit
- Normalisation et segmentation en trames
- Validation qualité audio

**Livrable :** Démonstration avant/après suppression de bruit

### Phase 3 : Intégration Whisper (Semaines 7-9)
**Objectif** : Intégrer et optimiser la reconnaissance vocale

**Tâches principales :**
- Installation et configuration Whisper-small
- Mesure des performances (latence, WER)
- Optimisation du pipeline audio
- Tests de robustesse

**Livrable :** Prototype CLI audio→texte + rapport de performances

### Phase 4 : Validation et déploiement (Semaines 10-12)
**Objectif** : Finaliser le système complet

**Tâches principales :**
- Parsing par mots-clés
- Intégration LLM optionnelle pour commandes complexes
- Chaînage complet du pipeline
- Tests en conditions réelles

**Livrable :** Démonstration complète + rapport final + code packagé

## 🛠️ Technologies utilisées

- **Robot** : Thymio
- **Reconnaissance vocale** : OpenAI Whisper-small
- **Communication** : USB/Wi-Fi selon configuration
- **Langage** : Python/Aseba

## 📊 Métriques de performance

### Cibles de performance
- **Latence transcription** : < 2ms
- **Taux d'erreur (WER)** : < 10% sur commandes prédéfinies
- **Robustesse bruit** : Fonctionnel jusqu'à X dB de bruit ambiant
- **Taux de compréhension** : > 90% en conditions normales

### Commandes supportées
- Commandes simples : "avance", "recule", "tourne à gauche/droite", "arrête"
- Séquences : "avance puis tourne à droite"
- Paramètres : "avance de 2 mètres", "tourne de 90 degrés"

## 🚀 Installation et utilisation

*[Section à compléter plus tard]*

### Prérequis
- Python 3.8+
- Robot Thymio II
- Microphone compatible
- Dépendances Python (requirements.txt)

### Installation rapide
```bash
git clone https://github.com/TitanSage02/vox-thymio.git
cd vox-thymio
pip install -r requirements.txt
```

### Test de base
```bash
python tests/test_communication.py  # Test communication Thymio
python tests/test_audio.py          # Test pipeline audio
python main.py                      # Lancement du système complet
```

## 📁 Structure du projet

```
vox-thymio/
├── src/
│   ├── communication/    # Modules communication Thymio
│   ├── audio/           # Traitement audio et suppression bruit
│   ├── speech/          # Intégration Whisper
│   └── parsing/         # Analyse et parsing des commandes
├── tests/               # Tests unitaires et d'intégration
├── docs/                # Documentation technique
├── notebooks/           # Notebooks de démonstration
└── examples/            # Exemples d'utilisation
```

## 🧪 Tests et validation

### Tests automatisés
- Tests unitaires pour chaque composant
- Tests d'intégration du pipeline complet
- Benchmarks de performance

### Tests manuels
- Validation avec différents locuteurs
- Tests en environnement bruité
- Validation des commandes complexes

## 📈 Suivi de projet

**Revues programmées :**
- Fin de chaque phase avec le tuteur
- Ajustement des priorités selon les résultats
- Validation des livrables avant phase suivante


## 📞 Contact

*[Informations de contact à ajouter]*

---

*Dernière mise à jour : Mai 2025*
*Version : 0.1.0 *