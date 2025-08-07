"""
Contrôleur vocal pour VoxThymio permettant d'ajouter dynamiquement des commandes au système.
"""

import asyncio
import json
from typing import Dict, Any, List
from pathlib import Path

from embedding_generator import EmbeddingGenerator
from embedding_manager import EmbeddingManager
from speech_recognizer import SpeechRecognizer
from controller.thymio_controller import ThymioController


class SmartVoiceController:
    """
    Contrôleur vocal pour la compréhension et l'exécution de commandes.
    """
    
    def __init__(self, thymio_controller: ThymioController):
        """
        Initialise le contrôleur vocal.
        
        Args:
            thymio_controller (ThymioController): Contrôleur de communication avec Thymio
        """
        self.thymio_controller = thymio_controller
        
        # Gestionnaires
        print("🔧 Initialisation du système...")
        self.embedding_generator = EmbeddingGenerator()
        self.vector_db = EmbeddingManager()
        
        # Reconnaissance vocale
        self.speech_recognizer = SpeechRecognizer(language="fr-FR")
        self.is_voice_active = False
        
        # Configuration des seuils
        self.EXECUTION_THRESHOLD = 0.5   # Seuil pour exécuter une commande
        self.LEARNING_THRESHOLD = 0.85   # Seuil pour apprendre automatiquement
        
        # État du système
        self.is_learning_mode = False
        self.pending_command = None
        
        # Initialisation avec les commandes en mémoire
        self._load_commands()

        print("✅ Système initialisé.")

    async def process_command(self, user_input: str) -> Dict[str, Any]:
        """
        Traite une commande textuelle et retourne le résultat.

        Args:   
            user_input (str): Commande textuelle de l'utilisateur

        Returns:
            Dict[str, Any]: Résultat du traitement
        """

        # Vérification de la validité de la commande
        if not user_input or not user_input.strip():
            return {
                'status': 'error', 
                'message': 'Commande vide reçue.',
                'action': 'none'
            }
        
        # Normalisation de l'entrée
        user_input = user_input.lower().strip()
        print(f"Traitement de: '{user_input}'")
        
        try:
            # Génération de l'embedding de la requête
            query_embedding = self.embedding_generator.generate_embedding(user_input)
            
            # Recherche de similarité
            best_match = self.vector_db.get_best_match(
                query_embedding, 
                threshold=self.EXECUTION_THRESHOLD
            )
            
            if best_match:
                similarity = best_match['similarity']
                
                # Si seuil d'appprentissage atteint
                if similarity >= self.LEARNING_THRESHOLD and self.is_learning_mode:
                    print(f"🔍 Apprentissage de la commande: '{user_input}' (similarité: {similarity:.2f})")
                    
                    # Ajout de la nouvelle commande
                    self.add_new_command(
                        command_id=f"custom_{len(self.vector_db.get_all_commands()) + 1}",
                        description=user_input,
                        code=self.pending_command or "motor.left.target = 0\nmotor.right.target = 0"
                    )

                # Exécution directe si seuil atteint
                if similarity >= self.EXECUTION_THRESHOLD:
                    return await self._execute_command(best_match, similarity)
                    
            else:
                # Aucune commande correspondante trouvée
                return self._handle_unknown_command(user_input, query_embedding)
                
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
            await self.thymio_controller.execute_code(code)
            return {
                'status': 'success',
                'message': f'Commande "{command_id}" exécutée avec succès.',
                'action': 'executed',
                'command_id': command_id,
                'similarity': similarity, 
                'description': description
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Échec de l\'exécution de la commande "{command_id}".',
                'action': 'failed',
                'command_id': command_id
            }
   
    def _handle_unknown_command(self, user_input: str, 
                                    query_embedding) -> Dict[str, Any]:
        """
        Gère une commande inconnue.
        
        Args:
            user_input (str): Commande de l'utilisateur
            query_embedding: Embedding de la requête
            
        Returns:
            Dict[str, Any]: Résultat du traitement
        """
        # Recherche de commandes similaires pour suggestions avec un seuil bas
        similar_commands = self.vector_db.search_similar_commands(
            query_embedding, 
            n_results=3, 
            min_similarity=0.4  # Seuil bas pour obtenir des suggestions pertinentes
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
            'suggestions': suggestions
        }
    
    def add_new_command(self, command_id: str, description: str, 
                       code: str) -> Dict[str, Any]:
        """
        Ajoute une nouvelle commande au système.
        
        Args:
            command_id (str): Identifiant unique de la commande
            description (str): Description en langage naturel
            code (str): Code Thymio associé
            
        Returns:
            Dict[str, Any]: Résultat de l'ajout
        """
        try:
            # Génération de l'embedding
            embedding = self.embedding_generator.generate_embedding(description)

            # Vérification de la qualité de l'embedding
            if embedding is None or len(embedding) == 0:
                raise ValueError("Impossible de générer un embedding valide")

            # Vérification des conflits potentiels
            similar_commands = self.vector_db.search_similar_commands(
                embedding, 
                n_results=3, 
                min_similarity=0.8
            )
            
            if similar_commands and similar_commands[0]['similarity'] > 0.9:
                print(f"⚠️ Commande similaire trouvée: {similar_commands[0]['description']} (ID: {similar_commands[0]['command_id']})")
                return
            
            # Ajout à la base vectorielle
            if self.vector_db.add_command(command_id, description, code, embedding):
               print(f"✅ Commande '{command_id}' ajoutée avec succès.")
            else:
                print(f"❌ Échec de l'ajout de la commande '{command_id}'.")    
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout de la commande '{command_id}': {e}")

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
        embedding_info = self.embedding_generator.get_model_info()
        
        return {
            'database': db_stats,
            'embedding_model': embedding_info,
            'thresholds': {
                'execution': self.EXECUTION_THRESHOLD,
                'learning': self.LEARNING_THRESHOLD
            }
        }
    
    def _load_commands(self):
        """
        Charge les commandes depuis commands.json.
        """
        commands_file = Path(__file__).parent / "commands.json"
        
        if not commands_file.exists():
            print(f"⚠️ Fichier commands.json non trouvé à {commands_file}. Aucune commande chargée.")
            return

        try:
            with open(commands_file, 'r', encoding='utf-8') as f:
                commands = json.load(f)

            added_count = 0
            for cmd_id, cmd_info in commands.items():
                description = cmd_info["description"]
                code = cmd_info["code"]

                # Vérifier si la commande existe déjà
                if not self.vector_db.command_exists(cmd_id):
                    embedding = self.embedding_generator.generate_embedding(description)
                    if self.vector_db.add_command(cmd_id, description, code, embedding):
                        added_count += 1
                        
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
    
    # --- Méthodes pour la reconnaissance vocale --- #
    async def voice_recognition(self) -> Dict[str, Any]:
        """
        Démarre la reconnaissance vocale en continu.
       
        Returns:
            Dict[str, Any]: Résultat du démarrage
        """
        if self.is_voice_active:
            return {
                'status': 'warning',
                'message': 'La reconnaissance vocale est déjà active'
            }
        
        try:
            while True:
                # Lance la reconnaissance vocale
                text = self.speech_recognizer.listen()
                if text:
                    print(f"🎤 Commande vocale reconnue: '{text}'")
                    await self._on_voice_command_recognized(text)    
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Erreur lors de l\'activation: {str(e)}',
                'action': 'voice_error'
            }
    
    async def _on_voice_command_recognized(self, text: str):
        """
        Callback appelé lorsqu'une commande vocale est reconnue.
        
        Args:
            text (str): Texte reconnu
        """
        if not text:
            return
            
        # Filtrer les entrées très courtes qui sont souvent des erreurs de reconnaissance
        if len(text.strip()) < 2:
            print(f"🎤 Entrée vocale ignorée car trop courte: '{text}'")
            return
            
        print(f"🎤 Commande vocale reconnue: '{text}'")
        
        # Traitement de la commande
        result = await  self.process_command(text)
        
        # Affichage du résultat
        if result['status'] == 'success':
            print(f"✅ {result['message']}")
        elif result['status'] == 'unknown':
            print(f"❓ {result['message']}")
        else:
            print(f"❌ {result['message']}")


if __name__ == "__main__":
    import asyncio
    from pathlib import Path
    from controller.thymio_controller import ThymioController

    async def run_test():
        print("🔬 Test du SmartVoiceController")

        # Initialiser l'interface de communication avec le robot Thymio
        thymio_ctrl = ThymioController()
        await thymio_ctrl.connect()

        # Initialiser le contrôleur vocal
        voice_ctrl = SmartVoiceController(thymio_ctrl)

        # Test 1: Commandes simples
        print("\n📝 TEST 1: Commandes textuelles simples")
        test_commands = [
            "avance",
            "recule", 
            "tourne à droite",
            "arrête-toi"
        ]

        for cmd in test_commands:
            print(f"\nTest de la commande: '{cmd}'")
            result = await voice_ctrl.process_command(cmd) 
            print(f"Résultat: {result['status']} - {result['message']}")
            await asyncio.sleep(1)

        # Test 2: Commandes similaires
        print("\n📝 TEST 2: Commandes avec variations")
        variations = [
            "va tout droit",
            "arrête le robot", 
            "tourne vers la droite",
            "stop"
        ]

        for cmd in variations:
            print(f"\n🔹 Test de variation: '{cmd}'")
            result = await voice_ctrl.process_command(cmd)
            print(f"Résultat: {result['status']} - {result['message']}")
            await asyncio.sleep(1)

        # Test voix
        print("\n📝 TEST VOIX: Démarrage de la reconnaissance vocale")
        try:
            # 🛠️ Lancer la reconnaissance vocale dans une tâche séparée
            voice_task = asyncio.create_task(voice_ctrl.voice_recognition())

            # Attendre 20 secondes pour la démo
            await asyncio.sleep(20)

            # 🛠️ Annuler proprement la tâche
            voice_task.cancel()
            try:
                await voice_task
            except asyncio.CancelledError:
                print("🔇 Tâche de reconnaissance vocale annulée.")
        except Exception as e:
            print(f"❌ Erreur pendant le test vocal : {e}")

        # Fermer la connexion
        await thymio_ctrl.disconnect()
        print("\n✅ Test terminé")

    # 🛠️ Exécuter proprement l'événement principal
    try:
        asyncio.run(run_test())
    except KeyboardInterrupt:
        print("\n🛑 Arrêté par l'utilisateur.")
