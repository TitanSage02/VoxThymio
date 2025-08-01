import torch
from transformers import BertTokenizer, BertForSequenceClassification
import joblib
import re

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
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Utilisation du périphérique : {self.device}")

        # Chargement du tokenizer
        self.tokenizer = BertTokenizer.from_pretrained(model_path)
        print("Tokenizer chargé.")

        # Chargement du modèle
        self.model = BertForSequenceClassification.from_pretrained(model_path)
        self.model.to(self.device) # Assure que le modèle est sur le bon périphérique
        self.model.eval() # Met le modèle en mode évaluation

        # Chargement de l'encodeur de labels
        self.label_encoder = joblib.load(f'{model_path}/label_encoder.pkl')

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

        # Tokenization
        encoding = self.tokenizer(
            cleaned_text,
            return_tensors='pt', # Retourne des tenseurs PyTorch
            truncation=True,
            padding=True
        )

        # Déplacement des tenseurs sur le bon périphérique
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)

        # Prédiction
        with torch.no_grad(): 
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            predicted_label_id = torch.argmax(logits, dim=1).item()

        # Décodage du label prédit
        predicted_label = self.label_encoder.inverse_transform([predicted_label_id])[0]

        return predicted_label
