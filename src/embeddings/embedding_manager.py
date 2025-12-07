"""
Embeddings Module
Handles generation and management of document embeddings
"""

import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer
from src.utils import get_logger


logger = get_logger(__name__)


class EmbeddingManager:
    """
    Manages document embedding generation using sentence-transformers
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding manager
        
        Args:
            model_name: Name of the sentence-transformer model
        """
        self.model_name = model_name
        self.model = None
        self.embedding_dimension = None
        self.logger = logger
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model"""
        try:
            self.logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.embedding_dimension = self.model.get_sentence_embedding_dimension()
            self.logger.info(
                f"Model loaded successfully. Embedding dimension: {self.embedding_dimension}"
            )
        except Exception as e:
            self.logger.error(f"Failed to load model {self.model_name}: {e}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings to embed
        
        Returns:
            NumPy array of embeddings (shape: [len(texts), embedding_dimension])
        """
        if not self.model:
            raise ValueError("Model not loaded. Call _load_model() first.")
        
        if not texts:
            return np.array([])
        
        try:
            self.logger.info(f"Generating embeddings for {len(texts)} texts")
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            self.logger.info(f"Generated embeddings with shape: {embeddings.shape}")
            return embeddings
        except Exception as e:
            self.logger.error(f"Error generating embeddings: {e}")
            raise
    
    def generate_embedding_for_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for a single query
        
        Args:
            query: Query text
        
        Returns:
            NumPy array of embedding (shape: [embedding_dimension])
        """
        if not query:
            raise ValueError("Query cannot be empty")
        
        embeddings = self.generate_embeddings([query])
        return embeddings[0]
    
    def get_model_info(self) -> dict:
        """
        Get information about the loaded model
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dimension,
            "model_type": "sentence-transformers",
        }
