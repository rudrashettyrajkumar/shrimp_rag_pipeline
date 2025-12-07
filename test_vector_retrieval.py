"""
Vector Retrieval Test Suite
Tests the complete vector storage and retrieval pipeline
"""

import sys
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from rag_pipeline import RAGPipeline
from src.utils import get_logger, LoggerManager
from src.ingestion import DataLoader, DataPreprocessor
from src.embeddings import EmbeddingManager
from src.vectorstore import VectorStore

# Configure logging
LoggerManager.configure_logger(log_file="./logs/test_vector_retrieval.log", level="INFO")
logger = get_logger(__name__)


def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def test_environment():
    """Test environment setup"""
    print_section("TEST 1: Environment Configuration")
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        print(f"✓ OPENAI_API_KEY is set")
        print(f"  Key prefix: {api_key[:20]}...")
    else:
        print("✗ OPENAI_API_KEY not found in environment")
        return False
    
    data_file = "./data/raw/pond_data.json"
    if Path(data_file).exists():
        file_size = Path(data_file).stat().st_size / (1024 * 1024)
        print(f"✓ Data file found: {data_file} ({file_size:.2f} MB)")
    else:
        print(f"✗ Data file not found: {data_file}")
        return False
    
    return True


def test_data_loading():
    """Test data loading and preprocessing"""
    print_section("TEST 2: Data Loading and Preprocessing")
    
    try:
        data_loader = DataLoader()
        records = data_loader.load_json("./data/raw/pond_data.json")
        
        print(f"✓ Loaded {len(records)} records")
        
        # Show sample record
        if records:
            sample = records[0]
            print(f"\n✓ Sample record fields: {len(sample)} fields")
            print(f"  - Pond: {sample.get('Pond', 'N/A')}")
            print(f"  - Crop ID: {sample.get('Crop ID', 'N/A')}")
            print(f"  - Status: {sample.get('status', 'N/A')}")
            print(f"  - Survival Rate: {sample.get('Survival\n Rate', 'N/A')}")
        
        # Test preprocessing
        preprocessor = DataPreprocessor()
        preprocessed = preprocessor.preprocess_records(records[:5])
        print(f"\n✓ Preprocessed {len(preprocessed)} sample records")
        
        # Test document conversion
        docs = preprocessor.convert_to_documents(preprocessed)
        print(f"✓ Converted to {len(docs)} documents")
        
        if docs:
            print(f"\n✓ Sample document:")
            print(f"  Content length: {len(docs[0].page_content)} chars")
            print(f"  Metadata: {docs[0].metadata}")
        
        return True
    
    except Exception as e:
        print(f"✗ Error in data loading: {e}")
        logger.error(f"Data loading error: {e}", exc_info=True)
        return False


def test_embeddings():
    """Test embedding generation"""
    print_section("TEST 3: Embeddings Generation")
    
    try:
        embedding_manager = EmbeddingManager(model_name="all-MiniLM-L6-v2")
        print(f"✓ Loaded embedding model: {embedding_manager.model_name}")
        print(f"  Embedding dimension: {embedding_manager.embedding_dimension}")
        
        # Test embedding generation
        test_texts = [
            "What is the survival rate in pond D14?",
            "Pond D14 had a 60% survival rate",
            "Feed conversion ratio FCR calculation"
        ]
        
        embeddings = embedding_manager.generate_embeddings(test_texts)
        
        print(f"\n✓ Generated embeddings:")
        print(f"  Shape: {embeddings.shape}")
        print(f"  Dimension: {embeddings.shape[1]}")
        
        # Test single query embedding
        query_embedding = embedding_manager.generate_embedding_for_query(test_texts[0])
        print(f"\n✓ Generated query embedding:")
        print(f"  Shape: {query_embedding.shape}")
        
        return True
    
    except Exception as e:
        print(f"✗ Error in embeddings: {e}")
        logger.error(f"Embeddings error: {e}", exc_info=True)
        return False


def test_vectorstore():
    """Test vector store operations"""
    print_section("TEST 4: Vector Store Operations")
    
    try:
        vectorstore = VectorStore(
            collection_name="test_shrimp_pond",
            persist_directory="./data/vectorstore"
        )
        
        info = vectorstore.get_collection_info()
        print(f"✓ Vector store initialized")
        print(f"  Collection: {info['collection_name']}")
        print(f"  Current documents: {info['document_count']}")
        
        return True
    
    except Exception as e:
        print(f"✗ Error in vector store: {e}")
        logger.error(f"Vector store error: {e}", exc_info=True)
        return False


def test_complete_ingestion():
    """Test complete data ingestion pipeline"""
    print_section("TEST 5: Complete Data Ingestion")
    
    try:
        pipeline = RAGPipeline(config_dir="./config")
        print(f"✓ RAG Pipeline initialized")
        
        # Check current document count
        info = pipeline.get_pipeline_info()
        current_count = info['vectorstore_info']['document_count']
        print(f"  Current documents in store: {current_count}")
        
        # Ingest data
        print(f"\n  Ingesting data from ./data/raw/pond_data.json...")
        num_docs = pipeline.ingest_data("./data/raw/pond_data.json")
        
        print(f"✓ Data ingestion completed")
        print(f"  Documents added: {num_docs}")
        
        # Verify documents in store
        info = pipeline.get_pipeline_info()
        final_count = info['vectorstore_info']['document_count']
        print(f"  Total documents in store: {final_count}")
        
        if final_count > 0:
            print(f"\n✓ Documents successfully stored in vector database")
            return True
        else:
            print(f"\n✗ No documents found in vector store after ingestion")
            return False
    
    except Exception as e:
        print(f"✗ Error in data ingestion: {e}")
        logger.error(f"Ingestion error: {e}", exc_info=True)
        return False


def test_retrieval():
    """Test vector retrieval with sample queries"""
    print_section("TEST 6: Vector Retrieval")
    
    try:
        pipeline = RAGPipeline(config_dir="./config")
        
        # Check if documents exist
        info = pipeline.get_pipeline_info()
        if info['vectorstore_info']['document_count'] == 0:
            print("⚠️  No documents in vector store. Ingesting data first...")
            pipeline.ingest_data("./data/raw/pond_data.json")
        
        # Test queries
        test_queries = [
            "What is the survival rate in pond D14?",
            "Pond performance and biomass",
            "feed conversion ratio FCR",
            "Stocking density and shrimp growth",
            "D14 C22025 crop cycle",
            "survival rate 60 percent",
            "HARVESTED crops information",
            "average body weight ABW",
        ]
        
        print(f"\nTesting {len(test_queries)} retrieval queries:\n")
        
        successful_queries = []
        
        for i, query in enumerate(test_queries, 1):
            try:
                print(f"Query {i}: {query}")
                
                retrieved_docs = pipeline.retriever.retrieve(query, top_k=3)
                
                if retrieved_docs:
                    print(f"  ✓ Retrieved {len(retrieved_docs)} documents")
                    
                    for j, doc in enumerate(retrieved_docs, 1):
                        score = doc['similarity_score']
                        pond = doc['metadata'].get('pond', 'N/A')
                        crop = doc['metadata'].get('crop_id', 'N/A')
                        print(f"    [{j}] Score: {score:.4f} | Pond: {pond} | Crop: {crop}")
                    
                    successful_queries.append({
                        "query": query,
                        "results": len(retrieved_docs),
                        "scores": [d['similarity_score'] for d in retrieved_docs]
                    })
                else:
                    print(f"  ✗ No documents retrieved")
                
                print()
            
            except Exception as e:
                print(f"  ✗ Error: {e}\n")
                logger.error(f"Query error: {query}: {e}")
        
        # Summary
        print("\n" + "-"*80)
        print(f"RETRIEVAL SUMMARY")
        print(f"Total queries tested: {len(test_queries)}")
        print(f"Successful queries: {len(successful_queries)}")
        print(f"Success rate: {len(successful_queries)/len(test_queries)*100:.1f}%")
        
        if successful_queries:
            print(f"\n✓ Successful Retrieval Queries:")
            for sq in successful_queries:
                avg_score = sum(sq['scores']) / len(sq['scores'])
                print(f"  • {sq['query']}")
                print(f"    Results: {sq['results']}, Avg Score: {avg_score:.4f}")
            return True
        else:
            print(f"\n✗ No successful retrievals")
            return False
    
    except Exception as e:
        print(f"✗ Error in retrieval testing: {e}")
        logger.error(f"Retrieval test error: {e}", exc_info=True)
        return False


def test_full_rag_query():
    """Test complete RAG query with LLM response"""
    print_section("TEST 7: Full RAG Query (with LLM Response)")
    
    try:
        pipeline = RAGPipeline(config_dir="./config")
        
        # Check if documents exist
        info = pipeline.get_pipeline_info()
        if info['vectorstore_info']['document_count'] == 0:
            print("⚠️  No documents in vector store. Ingesting data first...")
            pipeline.ingest_data("./data/raw/pond_data.json")
        
        # Test RAG query
        test_query = "What is the survival rate in pond D14?"
        
        print(f"Query: {test_query}\n")
        print("Processing...")
        
        result = pipeline.query(test_query, top_k=3)
        
        print(f"✓ Query processed successfully")
        print(f"\nQuery Type: {result['query_type']}")
        print(f"Documents Retrieved: {result['num_documents_retrieved']}")
        
        print(f"\n--- Retrieved Context ---")
        for i, doc in enumerate(result['retrieved_documents'], 1):
            print(f"\n[{i}] Similarity: {doc['similarity_score']:.4f}")
            print(f"    Pond: {doc['metadata'].get('pond', 'N/A')}")
            print(f"    Crop ID: {doc['metadata'].get('crop_id', 'N/A')}")
            print(f"    Content: {doc['content'][:200]}...")
        
        print(f"\n--- LLM Response ---")
        print(result['response'])
        
        return True
    
    except Exception as e:
        print(f"✗ Error in full RAG query: {e}")
        logger.error(f"RAG query error: {e}", exc_info=True)
        return False


def diagnose_issues():
    """Diagnose any issues found during testing"""
    print_section("DIAGNOSIS: Troubleshooting")
    
    print("""
Common Issues and Solutions:

1. **No Documents Retrieved**
   - Ensure data was ingested successfully
   - Check if vector embeddings were generated
   - Verify ChromaDB collection has documents
   - Try re-ingesting data

2. **Low Similarity Scores**
   - Adjust query to be more specific
   - Use keywords from actual data
   - Check embedding model is correct
   - Verify data format matches expectations

3. **Module Import Errors**
   - Install dependencies: pip install -r requirements.txt
   - Check Python path includes project root
   - Verify all files are in correct locations

4. **API Key Issues**
   - Ensure .env file has valid OPENAI_API_KEY
   - Check API key is not expired
   - Verify environment variable is loaded

5. **Data File Issues**
   - Ensure pond_data.json is in data/raw/
   - Check JSON file is valid and readable
   - Verify data has required fields
    """)


def main():
    """Run all tests"""
    print("\n" + "█"*80)
    print("█  SHRIMP POND RAG PIPELINE - VECTOR RETRIEVAL TEST SUITE")
    print("█"*80)
    
    tests = [
        ("Environment Setup", test_environment),
        ("Data Loading", test_data_loading),
        ("Embeddings Generation", test_embeddings),
        ("Vector Store Setup", test_vectorstore),
        ("Complete Data Ingestion", test_complete_ingestion),
        ("Vector Retrieval", test_retrieval),
        ("Full RAG Query", test_full_rag_query),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ Unexpected error in {test_name}: {e}")
            logger.error(f"Test {test_name} failed: {e}", exc_info=True)
            results[test_name] = False
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! Vector retrieval is working correctly.")
    elif passed > 0:
        print(f"\n⚠️  {total - passed} test(s) failed. See details above.")
        diagnose_issues()
    else:
        print(f"\n✗ All tests failed. Please diagnose issues above.")
        diagnose_issues()
    
    print("\n" + "█"*80)
    print("Logs saved to: ./logs/test_vector_retrieval.log")
    print("█"*80 + "\n")


if __name__ == "__main__":
    main()
