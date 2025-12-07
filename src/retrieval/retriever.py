"""
Retrieval Module
Handles query processing and document retrieval from vector store
"""

from typing import List, Dict, Any
import numpy as np
from src.embeddings import EmbeddingManager
from src.vectorstore import VectorStore
from src.utils import get_logger


logger = get_logger(__name__)


class Retriever:
    """
    Retrieves relevant documents based on query similarity
    """
    
    def __init__(
        self,
        vectorstore: VectorStore,
        embedding_manager: EmbeddingManager
    ):
        """
        Initialize the retriever
        
        Args:
            vectorstore: VectorStore instance
            embedding_manager: EmbeddingManager instance
        """
        self.vectorstore = vectorstore
        self.embedding_manager = embedding_manager
        self.logger = logger
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.0,
        where_filter: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: Query string
            top_k: Number of top documents to retrieve
            similarity_threshold: Minimum similarity score threshold
            where_filter: Optional metadata filter
        
        Returns:
            List of relevant documents
        """
        try:
            self.logger.info(f"Retrieving documents for query: '{query}'")
            
            # Generate embedding for query
            query_embedding = self.embedding_manager.generate_embedding_for_query(query)
            
            # Search in vector store
            results = self.vectorstore.search(
                query_embedding=query_embedding,
                top_k=top_k,
                where_filter=where_filter
            )
            
            # Filter by similarity threshold
            filtered_results = [
                result for result in results
                if result['similarity_score'] >= similarity_threshold
            ]
            
            self.logger.info(
                f"Retrieved {len(filtered_results)} documents "
                f"(threshold: {similarity_threshold})"
            )
            
            return filtered_results
        
        except Exception as e:
            self.logger.error(f"Error retrieving documents: {e}")
            raise
    
    def retrieve_by_pond(
        self,
        query: str,
        pond_name: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents for a specific pond
        
        Args:
            query: Query string
            pond_name: Pond name to filter by
            top_k: Number of top documents to retrieve
        
        Returns:
            List of relevant documents for the pond
        """
        where_filter = {"pond": {"$eq": pond_name}}
        return self.retrieve(
            query=query,
            top_k=top_k,
            where_filter=where_filter
        )
    
    def retrieve_by_status(
        self,
        query: str,
        status: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents by crop status
        
        Args:
            query: Query string
            status: Crop status (e.g., 'ACTIVE', 'HARVESTED')
            top_k: Number of top documents to retrieve
        
        Returns:
            List of relevant documents
        """
        where_filter = {"status": {"$eq": status}}
        return self.retrieve(
            query=query,
            top_k=top_k,
            where_filter=where_filter
        )
    
    def format_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Format retrieval results as readable text
        
        Args:
            results: List of retrieval results
        
        Returns:
            Formatted string representation
        """
        if not results:
            return "No relevant documents found."
        
        formatted_lines = ["=== Retrieved Documents ===\n"]
        
        for result in results:
            formatted_lines.append(f"Rank: {result['rank']}")
            formatted_lines.append(f"Similarity Score: {result['similarity_score']:.4f}")
            formatted_lines.append(f"Pond: {result['metadata'].get('pond', 'N/A')}")
            formatted_lines.append(f"Crop ID: {result['metadata'].get('crop_id', 'N/A')}")
            formatted_lines.append(f"Status: {result['metadata'].get('status', 'N/A')}")
            formatted_lines.append("\nContent:")
            formatted_lines.append(result['content'])
            formatted_lines.append("\n" + "=" * 50 + "\n")
        
        return "\n".join(formatted_lines)
