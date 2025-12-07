"""
Quick Start Script
Demonstrates how to use the RAG Pipeline programmatically
"""

import sys
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from rag_pipeline import RAGPipeline
from src.utils import get_logger, LoggerManager

# Configure logging
LoggerManager.configure_logger(log_file="./logs/quickstart.log", level="INFO")
logger = get_logger(__name__)


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def main():
    """Run quick start demo"""
    
    print_section("Shrimp Pond RAG Pipeline - Quick Start")
    
    try:
        # Step 1: Initialize pipeline
        print("\n[1/5] Initializing RAG Pipeline...")
        pipeline = RAGPipeline(config_dir="./config")
        print("✓ Pipeline initialized successfully")
        
        # Display configuration
        pipeline_info = pipeline.get_pipeline_info()
        print("\nConfiguration:")
        print(f"  - Embedding Model: {pipeline_info['embedding_model']['model_name']}")
        print(f"  - LLM Model: {pipeline_info['llm_model']['model']}")
        print(f"  - Documents in Store: {pipeline_info['vectorstore_info']['document_count']}")
        
        # Step 2: Check if data is loaded
        doc_count = pipeline_info['vectorstore_info']['document_count']
        
        if doc_count == 0:
            # Step 2a: Load data
            print("\n[2/5] Loading data...")
            data_file = "./data/raw/pond_data.json"
            
            if not os.path.exists(data_file):
                print(f"⚠️  Data file not found at {data_file}")
                print("Please ensure pond_data.json is in the data/raw/ directory")
                return
            
            num_docs = pipeline.ingest_data(data_file)
            print(f"✓ Data loaded successfully: {num_docs} documents")
        else:
            print(f"\n[2/5] Using existing data ({doc_count} documents)")
        
        # Step 3: Demonstrate queries
        print("\n[3/5] Processing sample queries...")
        
        sample_queries = [
            "What is the survival rate in pond D14?",
            "Which pond has the highest biomass?",
            "Tell me about the current active crops",
        ]
        
        for i, query in enumerate(sample_queries, 1):
            print(f"\nQuery {i}: {query}")
            print("-" * 70)
            
            try:
                result = pipeline.query(query, top_k=3)
                
                print(f"\n📊 Results:")
                print(f"  - Query Type: {result['query_type']}")
                print(f"  - Documents Retrieved: {result['num_documents_retrieved']}")
                print(f"\n💬 Response:")
                print(f"  {result['response'][:300]}...")
                
            except Exception as e:
                print(f"⚠️  Error processing query: {e}")
        
        # Step 4: Display pipeline info
        print("\n[4/5] Pipeline Information")
        print("-" * 70)
        print(json.dumps(pipeline_info, indent=2, default=str))
        
        # Step 5: Summary
        print_section("Quick Start Complete!")
        
        print("""
✓ Pipeline is ready to use!

Next steps:
1. Run the Streamlit app: streamlit run app.py
2. Or use the pipeline programmatically:
   
   from rag_pipeline import RAGPipeline
   pipeline = RAGPipeline()
   result = pipeline.query("Your question here")
   print(result['response'])

For more information, see README.md
        """)
        
        logger.info("Quick start completed successfully")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Quick start failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import json
    exit(main())
