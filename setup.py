"""
Entry point for the Shrimp Pond RAG Pipeline
This script sets up the pipeline and provides utility functions
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from rag_pipeline import RAGPipeline
from src.utils import LoggerManager, get_logger

# Configure logging
LoggerManager.configure_logger(
    log_file="./logs/pipeline.log",
    level="INFO"
)
logger = get_logger(__name__)


def setup_environment():
    """Setup environment directories and check API keys"""
    logger.info("Setting up environment...")
    
    # Create necessary directories
    directories = [
        "./logs",
        "./data/raw",
        "./data/vectorstore",
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Directory ready: {directory}")
    
    # Check API keys
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY not set. Please set it in environment variables.")
        raise ValueError(
            "OPENAI_API_KEY environment variable is required. "
            "Please set it before running the application."
        )
    
    logger.info("✓ Environment setup complete")


def main():
    """Main entry point"""
    try:
        # Setup
        setup_environment()
        
        # Initialize pipeline
        logger.info("Initializing RAG Pipeline...")
        pipeline = RAGPipeline(config_dir="./config")
        logger.info("✓ Pipeline initialized")
        
        # Print pipeline info
        pipeline_info = pipeline.get_pipeline_info()
        print("\n" + "="*60)
        print("RAG Pipeline Configuration")
        print("="*60)
        print(f"Vector Store: {pipeline_info['vectorstore_info']['collection_name']}")
        print(f"Embedding Model: {pipeline_info['embedding_model']['model_name']}")
        print(f"LLM Model: {pipeline_info['llm_model']['model']}")
        print(f"Documents in store: {pipeline_info['vectorstore_info']['document_count']}")
        print("="*60 + "\n")
        
        return pipeline
    
    except Exception as e:
        logger.error(f"Error during setup: {e}")
        raise


if __name__ == "__main__":
    pipeline = main()
