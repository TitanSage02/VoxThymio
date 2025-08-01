"""
Classification d'intention basée sur BERT pour le projet VoxThymio
Développé par Espérance AYIWAHOUN pour AI4Innov
"""

import torch
from transformers import BertTokenizer, BertForSequenceClassification
import joblib
import re
import warnings

# Suppression des avertissements liés à la dépréciation de certaines fonctionnalités
warnings.filterwarnings("ignore", category=FutureWarning)

class IntentClassifier:
    """
    Classe pour la classification d'intention utilisant un modèle BERT entraîné.
    Permet de charger le modèle, le tokenizer et l'encodeur de labels,
    de prétraiter le texte d'entrée et de prédire l'intention.
    """
    def __init__(self, model_path='./intent_model'):
        """
        Initialise le classificateur en chargeant le modèle, le tokenizer et l'encodeur de labels.

        Args:
            model_path (str): Chemin vers le répertoire contenant le modèle sauvegardé,
                              le tokenizer et l'encodeur de labels.
        """
        # Détection du matériel disponible (CPU/GPU)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Utilisation du périphérique : {self.device}")

        try:
            # Chargement du tokenizer
            self.tokenizer = BertTokenizer.from_pretrained(model_path)
            print("✅ Tokenizer chargé.")

            # Chargement du modèle avec suppression des avertissements liés à l'API dépréciée
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.model = BertForSequenceClassification.from_pretrained(model_path)
            
            # Transfert du modèle sur le bon périphérique (CPU/GPU)
            self.model.to(self.device)
            
            # Passage en mode évaluation (désactive dropout, etc.)
            self.model.eval()
            print("✅ Modèle BERT chargé et configuré.")

            # Chargement de l'encodeur de labels
            self.label_encoder = joblib.load(f'{model_path}/label_encoder.pkl')
            print("✅ Encodeur de labels chargé.")
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement du modèle: {e}")
            raise RuntimeError(f"Impossible de charger le modèle depuis {model_path}: {str(e)}")

    def clean_text(self, text):
        """
        Prétraite le texte d'entrée en le mettant en minuscules et en supprimant
        les caractères spéciaux, sauf les lettres accentuées, les chiffres,
        les espaces, les tirets et les apostrophes.

        Args:
            text (str): Le texte à nettoyer.

        Returns:
            str: Le texte nettoyé.
        """
        text = text.lower()
        text = re.sub(r"[^\w\sàâçéèêëîïôûùüÿñæœ'-]", '', text)
        return text

    def predict(self, text):
        """
        Prédit l'intention d'un texte donné.

        Args:
            text (str): Le texte dont on veut prédire l'intention.

        Returns:
            str: Le label de l'intention prédite.
        """
        # Prétraitement du texte
        cleaned_text = self.clean_text(text)

        # Tokenization avec les paramètres recommandés
        encoding = self.tokenizer(
            cleaned_text,
            return_tensors='pt',  # Retourne des tenseurs PyTorch
            truncation=True,      # Tronque le texte si nécessaire
            padding='max_length', # Padding uniforme (plus stable)
            max_length=128        # Longueur maximale standard
        )

        # Déplacement des tenseurs sur le bon périphérique
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)

        # Prédiction
        with torch.no_grad(), warnings.catch_warnings():
            warnings.simplefilter("ignore")
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            predicted_label_id = torch.argmax(logits, dim=1).item()

        # Décodage du label prédit
        predicted_label = self.label_encoder.inverse_transform([predicted_label_id])[0]

        return predicted_label
