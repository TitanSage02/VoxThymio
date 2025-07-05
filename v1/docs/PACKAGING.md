# Guide de Packaging VoxThymio

## Prérequis
- Python 3.8+
- Toutes les dépendances installées (`pip install -r requirements.txt`)
- Robot Thymio connecté (optionnel pour les tests)

## Création de l'exécutable

### Méthode automatique (recommandée)
```bash
python build_executable.py
```

Cette commande va :
1. Installer PyInstaller automatiquement
2. Créer les fichiers de version et configuration
3. Générer l'exécutable final dans `dist/VoxThymio.exe`

### Méthode manuelle
```bash
# Installer PyInstaller
pip install pyinstaller

# Créer l'exécutable
pyinstaller --onefile --windowed --name=VoxThymio --icon=robot.ico --add-data="src;src" --hidden-import=tdmclient --hidden-import=speech_recognition --hidden-import=pyaudio voxthymio_gui.py
```

## Distribution

L'exécutable final `VoxThymio.exe` est autonome et peut être distribué sans Python.

### Contenu du package de distribution
- `VoxThymio.exe` - Exécutable principal
- `README.md` - Documentation utilisateur

## Test de l'exécutable

1. Copiez `VoxThymio.exe` dans un nouveau dossier
2. Connectez votre robot Thymio
3. Lancez l'exécutable
4. Testez toutes les fonctionnalités

## Dépannage

### Erreur "Module not found"
- Vérifiez que tous les modules sont listés dans `--hidden-import`
- Utilisez le fichier .spec pour plus de contrôle

### Erreur d'icône
- Supprimez `--icon=robot.ico` si le fichier n'existe pas
- Créez une icône .ico ou utilisez une icône par défaut

### Taille importante de l'exécutable
- Normal pour un exécutable "onefile" (~50-100 MB)
- Contient Python et toutes les dépendances

---
Développé par Espérance AYIWAHOUN pour AI4Innov
