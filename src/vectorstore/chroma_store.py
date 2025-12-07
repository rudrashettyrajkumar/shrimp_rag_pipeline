"""
Vector Store Module
Manages storage and retrieval of document embeddings using ChromaDB
"""

import os
import uuid
from typing import List, Dict, Any
import numpy as np
import chromadb
from langchain_core.documents import Document
from src.utils import get_logger


logger = get_logger(__name__)


class VectorStore:
    """
    Manages document storage and similarity search using ChromaDB
    """
    
    def __init__(
        self,
        collection_name: str = "shrimp_pond_rag",
        persist_directory: str = "./data/vectorstore"
    ):
        """
        Initialize the vector store
        
        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist ChromaDB data
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self.logger = logger
        self._initialize_chromadb()
    
    def _initialize_chromadb(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Create persist directory if it doesn't exist
            os.makedirs(self.persist_directory, exist_ok=True)
            
            self.logger.info(f"Initializing ChromaDB at: {self.persist_directory}")
            
            # Initialize ChromaDB client with persistence
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Shrimp Pond RAG Collection"}
            )
            
            self.logger.info(f"ChromaDB initialized with collection: {self.collection_name}")
            self.logger.info(f"Existing documents in collection: {self.collection.count()}")
        
        except Exception as e:
            self.logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    def add_documents(
        self,
        documents: List[Document],
        embeddings: np.ndarray,
        batch_size: int = 100
    ) -> int:
        """
        Add documents and their embeddings to the collection
        
        Args:
            documents: List of Document objects
            embeddings: NumPy array of embeddings
            batch_size: Batch size for adding documents
        
        Returns:
            Number of documents added
        """
        if len(documents) != embeddings.shape[0]:
            raise ValueError(
                f"Number of documents ({len(documents)}) "
                f"does not match number of embeddings ({embeddings.shape[0]})"
            )
        
        try:
            self.logger.info(f"Adding {len(documents)} documents to collection")
            
            total_added = 0
            
            # Process in batches
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i + batch_size]
                batch_embeddings = embeddings[i:i + batch_size]
                
                # Prepare batch data
                ids = []
                metadatas = []
                document_texts = []
                embeddings_list = []
                
                for j, (doc, embedding) in enumerate(zip(batch_docs, batch_embeddings)):
                    doc_id = f"doc_{uuid.uuid4().hex[:8]}_{i + j}"
                    ids.append(doc_id)
                    
                    metadata = dict(doc.metadata) if doc.metadata else {}
                    metadata["doc_index"] = i + j
                    metadata["content_length"] = len(doc.page_content)
                    metadatas.append(metadata)
                    
                    document_texts.append(doc.page_content)
                    embeddings_list.append(embedding.tolist())
                
                # Add batch to collection
                self.collection.add(
                    ids=ids,
                    metadatas=metadatas,
                    documents=document_texts,
                    embeddings=embeddings_list
                )
                
                total_added += len(batch_docs)
                self.logger.info(f"Added batch of {len(batch_docs)} documents")
            
            self.logger.info(
                f"Successfully added {total_added} documents. "
                f"Total documents in collection: {self.collection.count()}"
            )
            
            return total_added
        
        except Exception as e:
            self.logger.error(f"Error adding documents: {e}")
            raise
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        where_filter: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of top results to return
            where_filter: Optional ChromaDB where filter
        
        Returns:
            List of search results
        """
        try:
            self.logger.info(f"Searching for top {top_k} similar documents")
            
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k,
                where=where_filter
            )
            
            # Process results
            search_results = []
            
            if results['documents'] and results['documents'][0]:
                documents = results['documents'][0]
                metadatas = results['metadatas'][0]
                distances = results['distances'][0]
                ids = results['ids'][0]
                
                for i, (doc_id, document, metadata, distance) in enumerate(
                    zip(ids, documents, metadatas, distances)
                ):
                    similarity_score = 1 - distance  # Convert distance to similarity
                    
                    search_results.append({
                        "id": doc_id,
                        "content": document,
                        "metadata": metadata,
                        "similarity_score": float(similarity_score),
                        "distance": float(distance),
                        "rank": i + 1
                    })
            
            self.logger.info(f"Found {len(search_results)} similar documents")
            return search_results
        
        except Exception as e:
            self.logger.error(f"Error searching documents: {e}")
            raise
    
    def delete_collection(self):
        """Delete the current collection"""
        try:
            self.logger.warning(f"Deleting collection: {self.collection_name}")
            self.client.delete_collection(name=self.collection_name)
            self.logger.info("Collection deleted successfully")
        except Exception as e:
            self.logger.error(f"Error deleting collection: {e}")
            raise
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection
        
        Returns:
            Dictionary with collection information
        """
        return {
            "collection_name": self.collection_name,
            "document_count": self.collection.count(),
            "persist_directory": self.persist_directory,
        }
