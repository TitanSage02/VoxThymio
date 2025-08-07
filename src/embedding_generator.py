import numpy as np
import torch
from sentence_transformers import SentenceTransformer
import re
from typing import List, Union


class EmbeddingGenerator:
    """
    Génère des embeddings en utilisant un modèle Sentence Transformers multilingue
    spécialement conçu pour la similarité sémantique.
    """
    
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initialise le gestionnaire d'embeddings.
        
        Args:
            model_name (str): Nom du modèle Sentence Transformers.
                             Par défaut: "paraphrase-multilingual-MiniLM-L12-v2"
        """
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🔧 Utilisation du périphérique : {self.device}")
        
        try:
            # Chargement du modèle Sentence Transformers
            print(f"📥 Chargement du modèle {model_name}...")
            self.model = SentenceTransformer(model_name, 
                                             device=str(self.device),
                                             backend="torch")
            
            print("✅ Modèle Sentence Transformers chargé et configuré.")
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement du modèle: {e}")
            raise RuntimeError(f"Impossible de charger le modèle {model_name}: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """
        Nettoie et normalise le texte d'entrée.
        
        Args:
            text (str): Texte à nettoyer
            
        Returns:
            str: Texte nettoyé
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Suppression des caractères spéciaux excessifs
        text = re.sub(r'[^\w\sàâäéèêëïîôöùûüÿç\'-]', ' ', text)
        
        # Normalisation des espaces
        text = re.sub(r'\s+', ' ', text)
        
        # Suppression des espaces en début/fin
        text = text.strip()
        
        return text
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Génère un embedding pour un texte donné.
        
        Args:
            text (str): Texte à encoder
            
        Returns:
            np.ndarray: Embedding du texte (vecteur de features normalisé)
        """
        # Nettoyage et préparation du texte
        cleaned_text = self._clean_text(text)
        
        if not cleaned_text.strip():
            raise ValueError("Le texte d'entrée est vide après nettoyage.")
        
        try:
            # Génération de l'embedding avec Sentence Transformers
            # Le modèle gère automatiquement la tokenisation, l'encodage et la normalisation
            embedding = self.model.encode(
                cleaned_text,
                convert_to_numpy=True,
                normalize_embeddings=True  # Normalisation automatique
            )
            
            return embedding
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération de l'embedding: {e}")
            raise RuntimeError(f"Impossible de générer l'embedding pour le texte: {str(e)}")
    
    def generate_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """
        Génère des embeddings pour une liste de textes (traitement par batch pour de meilleures performances).
        
        Args:
            texts (List[str]): Liste de textes à encoder
            
        Returns:
            np.ndarray: Array des embeddings (shape: [n_texts, embedding_dim])
        """
        if not texts:
            raise ValueError("La liste de textes est vide.")
        
        # Nettoyage de tous les textes
        cleaned_texts = [self._clean_text(text) for text in texts]
        
        # Vérification que tous les textes ne sont pas vides
        if all(not text.strip() for text in cleaned_texts):
            raise ValueError("Tous les textes sont vides après nettoyage.")
        
        try:
            # Génération des embeddings par batch
            embeddings = self.model.encode(
                cleaned_texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
                batch_size=32,  # Ajustable selon la mémoire disponible
                show_progress_bar=len(texts) > 10  # Progress bar pour les gros batches
            )
            
            return embeddings
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération des embeddings par batch: {e}")
            raise RuntimeError(f"Impossible de générer les embeddings: {str(e)}")
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Calcule la similarité cosinus entre deux textes.
        
        Args:
            text1 (str): Premier texte
            text2 (str): Deuxième texte
            
        Returns:
            float: Score de similarité entre -1 et 1
        """
        try:
            # Génération des embeddings pour les deux textes
            embeddings = self.generate_embeddings_batch([text1, text2])
            
            # Calcul de la similarité cosinus
            # (Les embeddings sont déjà normalisés, donc le produit scalaire = similarité cosinus)
            similarity = np.dot(embeddings[0], embeddings[1])
            
            return float(similarity)
            
        except Exception as e:
            print(f"❌ Erreur lors du calcul de similarité: {e}")
            raise RuntimeError(f"Impossible de calculer la similarité: {str(e)}")
    
    def compute_similarity_matrix(self, texts: List[str]) -> np.ndarray:
        """
        Calcule la matrice de similarité pour une liste de textes.
        
        Args:
            texts (List[str]): Liste de textes
            
        Returns:
            np.ndarray: Matrice de similarité (shape: [n_texts, n_texts])
        """
        if len(texts) < 2:
            raise ValueError("Il faut au moins 2 textes pour calculer une matrice de similarité.")
        
        try:
            # Génération de tous les embeddings
            embeddings = self.generate_embeddings_batch(texts)
            
            # Calcul de la matrice de similarité (produit matriciel)
            similarity_matrix = np.dot(embeddings, embeddings.T)
            
            return similarity_matrix
            
        except Exception as e:
            print(f"❌ Erreur lors du calcul de la matrice de similarité: {e}")
            raise RuntimeError(f"Impossible de calculer la matrice de similarité: {str(e)}")
    
    def get_model_info(self) -> dict:
        """
        Retourne des informations sur le modèle utilisé.
        
        Returns:
            dict: Informations sur le modèle
        """
        return {
            "model_name": self.model._modules['0'].auto_model.config.name_or_path,
            "embedding_dimension": self.model.get_sentence_embedding_dimension(),
            "max_sequence_length": self.model.max_seq_length,
            "device": str(self.device)
        }


# Test local du module
if __name__ == "__main__":
    import time
    
    print("🧪 Test du gestionnaire d'embeddings avec Sentence Transformers")
    
    # Initialisation du gestionnaire
    print("\n📥 Chargement du modèle d'embeddings...")
    manager = EmbeddingGenerator()
    
    # Informations sur le modèle
    info = manager.get_model_info()
    print("\n📊 Informations sur le modèle:")
    for key, value in info.items():
        print(f"  • {key}: {value}")
    
    # Test de génération d'embeddings individuels
    test_texts = [
        "Avancer à pleine vitesse",
        "Tourne à droite rapidement", 
        "Allume les LED en bleu",
        "Recule en arrière"
    ]
    
    print("\n🔢 Test de génération d'embeddings individuels:")
    embeddings_individual = []
    
    for text in test_texts:
        print(f"\n  • Texte: '{text}'")
        
        # Mesure du temps d'exécution
        start_time = time.time()
        embedding = manager.generate_embedding(text)
        end_time = time.time()
        duration = end_time - start_time
        
        embeddings_individual.append(embedding)
        
        print(f"    Dimension: {embedding.shape}")
        print(f"    Norme: {np.linalg.norm(embedding):.4f}")
        print(f"    Premiers éléments: {embedding[:3]}...")
        print(f"    Temps: {duration:.3f}s")
    
    # Test de génération par lot (plus efficace)
    print("\n🚀 Test de génération d'embeddings par lot:")
    start_time = time.time()
    batch_embeddings = manager.generate_embeddings_batch(test_texts)
    end_time = time.time()
    batch_duration = end_time - start_time
    
    print(f"  • Nombre d'embeddings générés: {len(batch_embeddings)}")
    print(f"  • Forme du batch: {batch_embeddings.shape}")
    print(f"  • Temps total pour le batch: {batch_duration:.3f}s")
    print(f"  • Temps moyen par embedding: {batch_duration/len(test_texts):.3f}s")
    
    # Test de similarité avec la méthode intégrée
    print("\n🔍 Test de similarité entre textes (méthode intégrée):")
    for i in range(len(test_texts)):
        for j in range(i+1, len(test_texts)):
            similarity = manager.compute_similarity(test_texts[i], test_texts[j])
            print(f"  • '{test_texts[i]}' vs '{test_texts[j]}': {similarity:.4f}")
    
    # Test de la matrice de similarité complète
    print("\n🔍 Test de matrice de similarité complète:")
    similarity_matrix = manager.compute_similarity_matrix(test_texts)
    print(f"  • Forme de la matrice: {similarity_matrix.shape}")
    print("  • Matrice de similarité:")
    
    # Affichage formaté de la matrice
    print("    ", end="")
    for i, text in enumerate(test_texts):
        print(f"{i:>8}", end="")
    print()
    
    for i, text in enumerate(test_texts):
        print(f"{i}: ", end="")
        for j in range(len(test_texts)):
            print(f"{similarity_matrix[i,j]:>8.4f}", end="")
        print(f"  ({text[:25]}...)" if len(text) > 25 else f"  ({text})")
    

    
    # Test avec des phrases plus variées pour vérifier la discrimination
    print("\n🎯 Test de discrimination avec des phrases plus variées:")
    varied_texts = [
        "Avance tout droit rapidement", 
        "Marche lentement vers l'avant",
        "Éteint toutes les lumières",
        "Calculer la racine carrée de 64"  # Hors sujet
    ]
    
    reference_text = "Avancer à pleine vitesse"
    print(f"  Référence: '{reference_text}'")
    
    for text in varied_texts:
        similarity = manager.compute_similarity(reference_text, text)
        print(f"  • vs '{text}': {similarity:.4f}")
    
    print("\n✅ Test terminé! ")