"""
Gestionnaire de base vectorielle utilisant ChromaDB pour VoxThymio
Stocke et gère les embeddings des commandes avec leurs métadonnées.

Développé par Espérance AYIWAHOUN pour AI4Innov
"""

import chromadb
from chromadb.config import Settings
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import json
import os
from pathlib import Path


class VectorDatabase:
    """
    Gestionnaire de base vectorielle pour stocker et rechercher des commandes
    basées sur leurs embeddings.
    """
    
    def __init__(self, db_path: str = "./vector_db"):
        """
        Initialise la base vectorielle.
        
        Args:
            db_path (str): Chemin vers la base de données ChromaDB
        """
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True)
        
        # Configuration de ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Collection pour les commandes
        self.collection_name = "voxthymio_commands"
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            print(f"✅ Collection '{self.collection_name}' chargée.")
        except Exception:
            # Créer la collection si elle n'existe pas
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}  # Utilise la distance cosinus
            )
            print(f"✅ Collection '{self.collection_name}' créée.")
    
    def add_command(self, command_id: str, description: str, 
                   code: str, embedding: np.ndarray, 
                   category: str = "custom") -> bool:
        """
        Ajoute une nouvelle commande à la base vectorielle.
        
        Args:
            command_id (str): Identifiant unique de la commande
            description (str): Description en langage naturel
            code (str): Code associé à la commande
            embedding (np.ndarray): Embedding de la description
            category (str): Catégorie de la commande
            
        Returns:
            bool: True si ajouté avec succès, False sinon
        """
        try:
            # Vérifier si la commande existe déjà
            if self.command_exists(command_id):
                print(f"⚠️ La commande '{command_id}' existe déjà. Mise à jour...")
                return self.update_command(command_id, description, code, embedding, category)
            
            # Convertir l'embedding en liste pour ChromaDB
            embedding_list = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
            
            # Métadonnées de la commande
            metadata = {
                "command_id": command_id,
                "description": description,
                "code": code,
                "category": category,
                "created_at": str(np.datetime64('now'))
            }
            
            # Ajout à la collection
            self.collection.add(
                embeddings=[embedding_list],
                documents=[description],
                metadatas=[metadata],
                ids=[command_id]
            )
            
            print(f"✅ Commande '{command_id}' ajoutée avec succès.")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout de la commande '{command_id}': {e}")
            return False
    
    def search_similar_commands(self, query_embedding: np.ndarray, 
                              n_results: int = 5, 
                              min_similarity: float = 0.6) -> List[Dict[str, Any]]:
        """
        Recherche les commandes les plus similaires à une requête.
        
        Args:
            query_embedding (np.ndarray): Embedding de la requête
            n_results (int): Nombre maximum de résultats
            min_similarity (float): Seuil de similarité minimum
            
        Returns:
            List[Dict[str, Any]]: Liste des commandes similaires avec leurs scores
        """
        try:
            # Convertir l'embedding en liste
            embedding_list = query_embedding.tolist() if isinstance(query_embedding, np.ndarray) else query_embedding
            
            # Recherche dans la collection
            results = self.collection.query(
                query_embeddings=[embedding_list],
                n_results=n_results
            )
            
            # Traitement des résultats
            similar_commands = []
            if results and results['ids'] and results['ids'][0]:
                for i, command_id in enumerate(results['ids'][0]):
                    # ChromaDB retourne des distances, nous devons calculer la similarité
                    distance = results['distances'][0][i]
                    similarity = 1 - distance  # Conversion distance -> similarité
                    
                    if similarity >= min_similarity:
                        metadata = results['metadatas'][0][i]
                        similar_commands.append({
                            'command_id': command_id,
                            'similarity': similarity,
                            'description': metadata.get('description', ''),
                            'code': metadata.get('code', ''),
                            'category': metadata.get('category', 'unknown'),
                            'metadata': metadata
                        })
            
            return similar_commands
            
        except Exception as e:
            print(f"❌ Erreur lors de la recherche: {e}")
            return []
    
    def get_best_match(self, query_embedding: np.ndarray, 
                      threshold: float = 0.6) -> Optional[Dict[str, Any]]:
        """
        Trouve la meilleure correspondance pour une requête.
        
        Args:
            query_embedding (np.ndarray): Embedding de la requête
            threshold (float): Seuil de similarité minimum
            
        Returns:
            Optional[Dict[str, Any]]: Meilleure correspondance ou None
        """
        results = self.search_similar_commands(query_embedding, n_results=1, min_similarity=threshold)
        return results[0] if results else None
    
    def command_exists(self, command_id: str) -> bool:
        """
        Vérifie si une commande existe dans la base.
        
        Args:
            command_id (str): Identifiant de la commande
            
        Returns:
            bool: True si la commande existe
        """
        try:
            result = self.collection.get(ids=[command_id])
            return len(result['ids']) > 0
        except Exception:
            return False
    
    def update_command(self, command_id: str, description: str, 
                      code: str, embedding: np.ndarray, 
                      category: str = "custom") -> bool:
        """
        Met à jour une commande existante.
        
        Args:
            command_id (str): Identifiant de la commande
            description (str): Nouvelle description
            code (str): Nouveau code
            embedding (np.ndarray): Nouvel embedding
            category (str): Nouvelle catégorie
            
        Returns:
            bool: True si mis à jour avec succès
        """
        try:
            # Supprimer l'ancienne version
            self.collection.delete(ids=[command_id])
            
            # Ajouter la nouvelle version
            return self.add_command(command_id, description, code, embedding, category)
            
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour de '{command_id}': {e}")
            return False
    
    def delete_command(self, command_id: str) -> bool:
        """
        Supprime une commande de la base.
        
        Args:
            command_id (str): Identifiant de la commande
            
        Returns:
            bool: True si supprimé avec succès
        """
        try:
            self.collection.delete(ids=[command_id])
            print(f"✅ Commande '{command_id}' supprimée.")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la suppression de '{command_id}': {e}")
            return False
    
    def get_all_commands(self) -> List[Dict[str, Any]]:
        """
        Récupère toutes les commandes de la base.
        
        Returns:
            List[Dict[str, Any]]: Liste de toutes les commandes
        """
        try:
            results = self.collection.get()
            commands = []
            
            if results['ids']:
                for i, command_id in enumerate(results['ids']):
                    metadata = results['metadatas'][i]
                    commands.append({
                        'command_id': command_id,
                        'description': metadata.get('description', ''),
                        'code': metadata.get('code', ''),
                        'category': metadata.get('category', 'unknown'),
                        'created_at': metadata.get('created_at', ''),
                        'metadata': metadata
                    })
            
            return commands
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des commandes: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retourne des statistiques sur la base vectorielle.
        
        Returns:
            Dict[str, Any]: Statistiques de la base
        """
        try:
            commands = self.get_all_commands()
            categories = {}
            
            for cmd in commands:
                category = cmd.get('category', 'unknown')
                categories[category] = categories.get(category, 0) + 1
            
            return {
                'total_commands': len(commands),
                'categories': categories,
                'collection_name': self.collection_name,
                'db_path': str(self.db_path)
            }
            
        except Exception as e:
            print(f"❌ Erreur lors du calcul des statistiques: {e}")
            return {}
    
    def reset_database(self) -> bool:
        """
        Remet à zéro la base vectorielle (supprime toutes les commandes).
        
        Returns:
            bool: True si réussi
        """
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print("✅ Base vectorielle remise à zéro.")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la remise à zéro: {e}")
            return False
