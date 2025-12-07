"""
RAG Pipeline Orchestrator
Main class that coordinates all components of the RAG pipeline
"""

import os
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from src.ingestion import DataLoader, DataPreprocessor
from src.embeddings import EmbeddingManager
from src.vectorstore import VectorStore
from src.retrieval import Retriever
from src.generation import LLMClient, PromptBuilder
from src.utils import get_logger, get_config_loader

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

logger = get_logger(__name__)


class RAGPipeline:
    """
    Complete RAG pipeline that orchestrates all components
    """
    
    def __init__(self, config_dir: str = "./config"):
        """
        Initialize the RAG pipeline
        
        Args:
            config_dir: Path to configuration directory
        """
        self.logger = logger
        self.logger.info("Initializing RAG Pipeline...")
        
        # Load configuration
        self.config_loader = get_config_loader(config_dir)
        self.settings = self.config_loader.get_settings()
        self.prompts = self.config_loader.get_prompts()
        
        # Initialize components
        self.data_loader = DataLoader()
        self.data_preprocessor = DataPreprocessor()
        self.embedding_manager = EmbeddingManager(
            model_name=self.settings.get("embeddings", {}).get("model_name", "all-MiniLM-L6-v2")
        )
        self.vectorstore = VectorStore(
            collection_name=self.settings.get("vectorstore", {}).get("collection_name", "shrimp_pond_rag"),
            persist_directory=self.settings.get("vectorstore", {}).get("persist_directory", "./data/vectorstore")
        )
        self.retriever = Retriever(self.vectorstore, self.embedding_manager)
        
        # Initialize LLM client
        api_key = os.getenv("OPENAI_API_KEY")
        self.llm_client = LLMClient(
            api_key=api_key,
            model=self.settings.get("openai", {}).get("model", "gpt-3.5-turbo"),
            temperature=self.settings.get("openai", {}).get("temperature", 0.7),
            max_tokens=self.settings.get("openai", {}).get("max_tokens", 1500)
        )
        
        # Initialize prompt builder
        self.prompt_builder = PromptBuilder(self.prompts)
        
        # Text splitter for chunking
        vectorstore_config = self.settings.get("vectorstore", {})
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=vectorstore_config.get("chunk_size", 500),
            chunk_overlap=vectorstore_config.get("chunk_overlap", 100),
            separators=vectorstore_config.get("separators", ["\n\n", "\n", " ", ""])
        )
        
        self.logger.info("RAG Pipeline initialized successfully")
    
    def ingest_data(self, data_file_path: str) -> int:
        """
        Ingest data from a file and populate the vector store
        
        Args:
            data_file_path: Path to input data file (JSON or CSV)
        
        Returns:
            Number of documents added
        """
        try:
            self.logger.info(f"Starting data ingestion from: {data_file_path}")
            
            # Load data
            if data_file_path.endswith('.json'):
                records = self.data_loader.load_json(data_file_path)
            elif data_file_path.endswith('.csv'):
                records = self.data_loader.load_csv(data_file_path)
            else:
                raise ValueError("Supported formats: JSON, CSV")
            
            self.logger.info(f"Loaded {len(records)} records")
            
            # Preprocess data
            preprocessed_records = self.data_preprocessor.preprocess_records(records)
            
            # Convert to documents
            documents = self.data_preprocessor.convert_to_documents(
                preprocessed_records,
                source=os.path.basename(data_file_path)
            )
            
            self.logger.info(f"Created {len(documents)} documents")
            
            # Split documents into chunks
            chunked_docs = self.text_splitter.split_documents(documents)
            self.logger.info(f"Split into {len(chunked_docs)} chunks")
            
            # Generate embeddings
            texts = [doc.page_content for doc in chunked_docs]
            embeddings = self.embedding_manager.generate_embeddings(texts)
            
            # Add to vector store
            num_added = self.vectorstore.add_documents(chunked_docs, embeddings)
            
            self.logger.info(f"Data ingestion completed. Added {num_added} documents")
            return num_added
        
        except Exception as e:
            self.logger.error(f"Error during data ingestion: {e}")
            raise
    
    def query(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Process a query and generate a response
        
        Args:
            query: User query string
            top_k: Number of top documents to retrieve
        
        Returns:
            Dictionary with query results and response
        """
        try:
            self.logger.info(f"Processing query: '{query}'")
            
            # Retrieve relevant documents
            retrieved_docs = self.retriever.retrieve(query, top_k=top_k)
            
            # Format context from retrieved documents
            context = self._format_context(retrieved_docs)
            
            # Detect query type
            query_type = self.prompt_builder.detect_query_type(query)
            self.logger.info(f"Detected query type: {query_type}")
            
            # Build prompts
            system_prompt = self.prompt_builder.build_system_prompt()
            user_message = self.prompt_builder.build_query_prompt(
                query=query,
                context=context,
                prompt_type=query_type
            )
            
            # Generate response
            response = self.llm_client.generate(
                system_prompt=system_prompt,
                user_message=user_message
            )
            
            self.logger.info("Response generated successfully")
            
            return {
                "query": query,
                "retrieved_documents": retrieved_docs,
                "context": context,
                "response": response,
                "query_type": query_type,
                "num_documents_retrieved": len(retrieved_docs),
            }
        
        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            raise
    
    def _format_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        """
        Format retrieved documents as context string
        
        Args:
            retrieved_docs: List of retrieved documents
        
        Returns:
            Formatted context string
        """
        if not retrieved_docs:
            return "No relevant documents found."
        
        context_lines = []
        for i, doc in enumerate(retrieved_docs, 1):
            context_lines.append(f"Document {i} (Similarity: {doc['similarity_score']:.4f}):")
            context_lines.append(doc['content'])
            context_lines.append("")
        
        return "\n".join(context_lines)
    
    def reset_vectorstore(self):
        """Reset the vector store (delete all documents)"""
        try:
            self.logger.warning("Resetting vector store...")
            self.vectorstore.delete_collection()
            # Reinitialize collection
            self.vectorstore._initialize_chromadb()
            self.logger.info("Vector store reset successfully")
        except Exception as e:
            self.logger.error(f"Error resetting vector store: {e}")
            raise
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """
        Get information about the pipeline configuration
        
        Returns:
            Dictionary with pipeline information
        """
        return {
            "vectorstore_info": self.vectorstore.get_collection_info(),
            "embedding_model": self.embedding_manager.get_model_info(),
            "llm_model": self.llm_client.get_model_info(),
            "configuration": {
                "openai": self.settings.get("openai", {}),
                "embeddings": self.settings.get("embeddings", {}),
                "vectorstore": self.settings.get("vectorstore", {}),
            }
        }
