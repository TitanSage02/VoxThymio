"""
Nouveau contrôleur vocal utilisant BERT français et la recherche de similarité
pour VoxThymio. Permet d'ajouter dynamiquement des commandes.

Développé par Espérance AYIWAHOUN pour AI4Innov
"""

import asyncio
import json
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

from .embedding_manager import EmbeddingManager
from .command_manager import VectorDatabase
from .communication.thymio_controller import ThymioController


class SmartVoiceController:
    """
    Contrôleur vocal intelligent utilisant des embeddings BERT français
    pour la compréhension et l'exécution de commandes.
    """
    
    def __init__(self, thymio_controller: ThymioController):
        """
        Initialise le contrôleur vocal intelligent.
        
        Args:
            thymio_controller (ThymioController): Contrôleur de communication avec Thymio
        """
        self.thymio_controller = thymio_controller
        
        # Gestionnaires
        print("🔧 Initialisation du système intelligent...")
        self.embedding_manager = EmbeddingManager()
        self.vector_db = VectorDatabase()
        
        # Configuration des seuils
        self.EXECUTION_THRESHOLD = 0.6   # Seuil pour exécuter une commande
        self.LEARNING_THRESHOLD = 0.85   # Seuil pour apprendre automatiquement
        
        # État du système
        self.is_learning_mode = False
        self.pending_command = None
        
        # Initialisation avec les commandes de base
        self._load_default_commands()
        
        print("✅ Système vocal intelligent initialisé.")
    
    async def process_voice_command(self, user_input: str) -> Dict[str, Any]:
        """
        Traite une commande vocale et retourne le résultat.
        
        Args:
            user_input (str): Commande vocale de l'utilisateur
            
        Returns:
            Dict[str, Any]: Résultat du traitement
        """
        if not user_input or not user_input.strip():
            return {
                'status': 'error',
                'message': 'Commande vide reçue.',
                'action': 'none'
            }
        
        print(f"🎤 Traitement de: '{user_input}'")
        
        try:
            # Génération de l'embedding de la requête
            query_embedding = self.embedding_manager.generate_embedding(user_input)
            
            # Recherche de similarité
            best_match = self.vector_db.get_best_match(
                query_embedding, 
                threshold=self.EXECUTION_THRESHOLD
            )
            
            if best_match:
                similarity = best_match['similarity']
                
                # Exécution directe si seuil atteint
                if similarity >= self.EXECUTION_THRESHOLD:
                    return await self._execute_command(best_match, similarity)
                    
            else:
                # Aucune commande correspondante trouvée
                return await self._handle_unknown_command(user_input, query_embedding)
                
        except Exception as e:
            print(f"❌ Erreur lors du traitement: {e}")
            return {
                'status': 'error',
                'message': f'Erreur interne: {str(e)}',
                'action': 'none'
            }
    
    async def _execute_command(self, command_match: Dict[str, Any], 
                             similarity: float) -> Dict[str, Any]:
        """
        Exécute une commande correspondante.
        
        Args:
            command_match (Dict[str, Any]): Commande à exécuter
            similarity (float): Score de similarité
            
        Returns:
            Dict[str, Any]: Résultat de l'exécution
        """
        command_id = command_match['command_id']
        code = command_match['code']
        description = command_match['description']
        
        print(f"🚀 Exécution de '{command_id}' (similarité: {similarity:.2f})")
        print(f"📝 Description: {description}")
        
        try:
            # Exécution du code sur Thymio
            if await self.thymio_controller.execute_code(code):
                return {
                    'status': 'success',
                    'message': f'Commande "{command_id}" exécutée avec succès.',
                    'action': 'executed',
                    'command_id': command_id,
                    'similarity': similarity,
                    'description': description
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Échec de l\'exécution de la commande "{command_id}".',
                    'action': 'failed',
                    'command_id': command_id
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Erreur lors de l\'exécution: {str(e)}',
                'action': 'error'
            }
    
    async def _handle_unknown_command(self, user_input: str, 
                                    query_embedding) -> Dict[str, Any]:
        """
        Gère une commande inconnue.
        
        Args:
            user_input (str): Commande de l'utilisateur
            query_embedding: Embedding de la requête
            
        Returns:
            Dict[str, Any]: Résultat du traitement
        """
        # Recherche de commandes similaires pour suggestions
        similar_commands = self.vector_db.search_similar_commands(
            query_embedding, 
            n_results=3, 
            min_similarity=0.3
        )
        
        suggestions = [
            f"'{cmd['description']}' (similarité: {cmd['similarity']:.2f})"
            for cmd in similar_commands
        ]
        
        message = f"❓ Commande inconnue: '{user_input}'"
        if suggestions:
            message += f"\n💡 Suggestions: {', '.join(suggestions)}"
        
        return {
            'status': 'unknown',
            'message': message,
            'action': 'suggest',
            'user_input': user_input,
            'suggestions': suggestions,
            'embedding': query_embedding.tolist()  # Pour une éventuelle utilisation future
        }
    
    def add_new_command(self, command_id: str, description: str, 
                       code: str, category: str = "custom") -> Dict[str, Any]:
        """
        Ajoute une nouvelle commande au système.
        
        Args:
            command_id (str): Identifiant unique de la commande
            description (str): Description en langage naturel
            code (str): Code Thymio associé
            category (str): Catégorie de la commande
            
        Returns:
            Dict[str, Any]: Résultat de l'ajout
        """
        try:
            # Génération de l'embedding
            embedding = self.embedding_manager.generate_embedding(description)
            
            # Vérification des conflits potentiels
            similar_commands = self.vector_db.search_similar_commands(
                embedding, 
                n_results=3, 
                min_similarity=0.8
            )
            
            if similar_commands and similar_commands[0]['similarity'] > 0.9:
                return {
                    'status': 'warning',
                    'message': f'Une commande très similaire existe déjà: "{similar_commands[0]["description"]}"',
                    'action': 'conflict',
                    'similar_command': similar_commands[0]
                }
            
            # Ajout à la base vectorielle
            if self.vector_db.add_command(command_id, description, code, embedding, category):
                return {
                    'status': 'success',
                    'message': f'Commande "{command_id}" ajoutée avec succès.',
                    'action': 'added',
                    'command_id': command_id,
                    'description': description,
                    'similar_commands': similar_commands[:2]  # Afficher quelques commandes similaires
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Échec de l\'ajout de la commande "{command_id}".',
                    'action': 'failed'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Erreur lors de l\'ajout: {str(e)}',
                'action': 'error'
            }
    
    def get_all_commands(self) -> List[Dict[str, Any]]:
        """
        Récupère toutes les commandes disponibles.
        
        Returns:
            List[Dict[str, Any]]: Liste des commandes
        """
        return self.vector_db.get_all_commands()
    
    def delete_command(self, command_id: str) -> Dict[str, Any]:
        """
        Supprime une commande du système.
        
        Args:
            command_id (str): Identifiant de la commande
            
        Returns:
            Dict[str, Any]: Résultat de la suppression
        """
        if self.vector_db.delete_command(command_id):
            return {
                'status': 'success',
                'message': f'Commande "{command_id}" supprimée.',
                'action': 'deleted'
            }
        else:
            return {
                'status': 'error',
                'message': f'Échec de la suppression de "{command_id}".',
                'action': 'failed'
            }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques du système.
        
        Returns:
            Dict[str, Any]: Statistiques du système
        """
        db_stats = self.vector_db.get_stats()
        embedding_info = self.embedding_manager.get_embedding_info()
        
        return {
            'database': db_stats,
            'embedding_model': embedding_info,
            'thresholds': {
                'execution': self.EXECUTION_THRESHOLD,
                'learning': self.LEARNING_THRESHOLD
            }
        }
    
    def _load_default_commands(self):
        """
        Charge les commandes par défaut depuis commands.json.
        """
        commands_file = Path(__file__).parent.parent / "commands.json"
        
        if not commands_file.exists():
            print("⚠️ Fichier commands.json non trouvé. Aucune commande par défaut chargée.")
            return
        
        try:
            with open(commands_file, 'r', encoding='utf-8') as f:
                default_commands = json.load(f)
            
            # Descriptions en français pour les commandes de base
            descriptions = {
                "avancer": "faire avancer le robot vers l'avant",
                "avancer_lent": "avancer lentement vers l'avant",
                "avancer_rapide": "avancer rapidement vers l'avant",
                "reculer": "faire reculer le robot vers l'arrière",
                "reculer_lent": "reculer lentement vers l'arrière",
                "reculer_rapide": "reculer rapidement vers l'arrière",
                "arreter": "arrêter le robot complètement",
                "tourner_gauche": "tourner vers la gauche",
                "tourner_droite": "tourner vers la droite",
                "tourner_gauche_lent": "tourner lentement vers la gauche",
                "tourner_droite_lent": "tourner lentement vers la droite",
                "led_rouge": "allumer la LED en rouge",
                "led_vert": "allumer la LED en vert",
                "led_bleu": "allumer la LED en bleu",
                "led_jaune": "allumer la LED en jaune",
                "led_violet": "allumer la LED en violet",
                "led_blanc": "allumer la LED en blanc",
                "led_eteindre": "éteindre toutes les LEDs",
                "son_heureux": "jouer un son joyeux",
                "son_triste": "jouer un son triste",
                "son_silence": "arrêter tous les sons",
                "volume_max": "mettre le volume au maximum",
                "volume_moyen": "mettre le volume moyen",
                "volume_bas": "mettre le volume bas",
                "note_do": "jouer la note Do",
                "note_re": "jouer la note Ré",
                "note_mi": "jouer la note Mi",
                "note_fa": "jouer la note Fa",
                "note_sol": "jouer la note Sol"
            }
            
            added_count = 0
            for cmd_id, code in default_commands.items():
                description = descriptions.get(cmd_id, f"commande {cmd_id}")
                
                # Vérifier si la commande existe déjà
                if not self.vector_db.command_exists(cmd_id):
                    embedding = self.embedding_manager.generate_embedding(description)
                    if self.vector_db.add_command(cmd_id, description, code, embedding, "default"):
                        added_count += 1
            
            print(f"✅ {added_count} commandes par défaut ajoutées à la base vectorielle.")
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement des commandes par défaut: {e}")
    
    def update_thresholds(self, execution_threshold: float = None, 
                         learning_threshold: float = None) -> Dict[str, Any]:
        """
        Met à jour les seuils de similarité.
        
        Args:
            execution_threshold (float): Nouveau seuil d'exécution
            learning_threshold (float): Nouveau seuil d'apprentissage
            
        Returns:
            Dict[str, Any]: Résultat de la mise à jour
        """
        if execution_threshold is not None:
            if 0.0 <= execution_threshold <= 1.0:
                self.EXECUTION_THRESHOLD = execution_threshold
            else:
                return {
                    'status': 'error',
                    'message': 'Le seuil d\'exécution doit être entre 0.0 et 1.0'
                }
        
        if learning_threshold is not None:
            if 0.0 <= learning_threshold <= 1.0:
                self.LEARNING_THRESHOLD = learning_threshold
            else:
                return {
                    'status': 'error',
                    'message': 'Le seuil d\'apprentissage doit être entre 0.0 et 1.0'
                }
        
        return {
            'status': 'success',
            'message': 'Seuils mis à jour avec succès.',
            'thresholds': {
                'execution': self.EXECUTION_THRESHOLD,
                'learning': self.LEARNING_THRESHOLD
            }
        }
