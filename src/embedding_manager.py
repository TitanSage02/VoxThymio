"""
Gestionnaire d'embeddings utilisant BERT français pour VoxThymio
Permet de générer des embeddings de descriptions en langage naturel
et d'effectuer des recherches de similarité.

Développé par Espérance AYIWAHOUN pour AI4Innov
"""

import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from typing import List, Tuple, Dict, Any
import warnings

# Suppression des avertissements
warnings.filterwarnings("ignore", category=FutureWarning)


class EmbeddingManager:
    """
    Gestionnaire d'embeddings utilisant un modèle BERT français.
    Génère des embeddings à partir de descriptions en langage naturel.
    """
    
    def __init__(self, model_name: str = "camembert-base"):
        """
        Initialise le gestionnaire d'embeddings.
        
        Args:
            model_name (str): Nom du modèle BERT français à utiliser.
                             Par défaut: "camembert-base" (BERT français)
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🔧 Utilisation du périphérique : {self.device}")
        
        try:
            # Chargement du modèle et tokenizer BERT français
            print(f"📥 Chargement du modèle {model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            
            # Transfert sur le bon périphérique
            self.model.to(self.device)
            self.model.eval()
            
            print("✅ Modèle BERT français chargé et configuré.")
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement du modèle: {e}")
            raise RuntimeError(f"Impossible de charger le modèle {model_name}: {str(e)}")
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Génère un embedding pour un texte donné.
        
        Args:
            text (str): Texte à encoder
            
        Returns:
            np.ndarray: Embedding du texte (vecteur de features)
        """
        # Nettoyage et préparation du texte
        cleaned_text = self._clean_text(text)
        
        # Tokenisation
        inputs = self.tokenizer(
            cleaned_text,
            return_tensors='pt',
            truncation=True,
            padding=True,
            max_length=128
        )
        
        # Déplacement sur le bon périphérique
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Génération de l'embedding
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Utilisation du token [CLS] (premier token) comme représentation
            embedding = outputs.last_hidden_state[0][0].cpu().numpy()
        
        return embedding
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        Génère des embeddings pour une liste de textes.
        
        Args:
            texts (List[str]): Liste de textes à encoder
            
        Returns:
            List[np.ndarray]: Liste des embeddings
        """
        embeddings = []
        for text in texts:
            embedding = self.generate_embedding(text)
            embeddings.append(embedding)
        return embeddings
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calcule la similarité cosinus entre deux embeddings.
        
        Args:
            embedding1 (np.ndarray): Premier embedding
            embedding2 (np.ndarray): Deuxième embedding
            
        Returns:
            float: Score de similarité entre 0 et 1
        """
        # Calcul de la similarité cosinus
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        # Normalisation entre 0 et 1
        return (similarity + 1) / 2
    
    def find_most_similar(self, query_embedding: np.ndarray, 
                         embeddings: List[np.ndarray], 
                         threshold: float = 0.6) -> Tuple[int, float]:
        """
        Trouve l'embedding le plus similaire à une requête.
        
        Args:
            query_embedding (np.ndarray): Embedding de la requête
            embeddings (List[np.ndarray]): Liste des embeddings de référence
            threshold (float): Seuil de similarité minimum
            
        Returns:
            Tuple[int, float]: Index de l'embedding le plus similaire et son score
                              (-1, 0.0) si aucun ne dépasse le seuil
        """
        if not embeddings:
            return -1, 0.0
        
        max_similarity = 0.0
        best_index = -1
        
        for i, embedding in enumerate(embeddings):
            similarity = self.calculate_similarity(query_embedding, embedding)
            if similarity > max_similarity and similarity >= threshold:
                max_similarity = similarity
                best_index = i
        
        return best_index, max_similarity
    
    def _clean_text(self, text: str) -> str:
        """
        Nettoie et normalise le texte d'entrée.
        
        Args:
            text (str): Texte à nettoyer
            
        Returns:
            str: Texte nettoyé
        """
        if not text:
            return ""
        
        # Conversion en minuscules et suppression des espaces superflus
        cleaned = text.lower().strip()
        # Suppression des caractères de contrôle et normalisation des espaces
        cleaned = ' '.join(cleaned.split())
        
        return cleaned
    
    def get_embedding_info(self) -> Dict[str, Any]:
        """
        Retourne des informations sur le modèle d'embedding.
        
        Returns:
            Dict[str, Any]: Informations sur le modèle
        """
        return {
            "model_name": self.model.config.name_or_path if hasattr(self.model, 'config') else "Unknown",
            "embedding_dim": self.model.config.hidden_size if hasattr(self.model, 'config') else "Unknown",
            "device": str(self.device),
            "vocab_size": len(self.tokenizer) if self.tokenizer else "Unknown"
        }
