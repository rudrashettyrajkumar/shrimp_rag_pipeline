"""
Streamlit Application for Shrimp Pond RAG Chatbot
Interactive UI for querying and analyzing shrimp pond data
"""

import streamlit as st
import os
import sys
from pathlib import Path
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from rag_pipeline import RAGPipeline
from src.utils import get_logger, LoggerManager

# Configure logging
LoggerManager.configure_logger(
    log_file="./logs/app.log",
    level="INFO"
)
logger = get_logger(__name__)


# Page configuration
st.set_page_config(
    page_title="Shrimp Pond RAG Assistant",
    page_icon="🦐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stTabs [data-baseweb="tab-list"] button {
        width: 100%;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_pipeline():
    """Initialize the RAG pipeline"""
    if "pipeline" not in st.session_state:
        try:
            st.session_state.pipeline = RAGPipeline(config_dir="./config")
            st.session_state.pipeline_initialized = True
            logger.info("RAG Pipeline initialized")
        except Exception as e:
            st.error(f"Failed to initialize pipeline: {str(e)}")
            logger.error(f"Pipeline initialization error: {e}")
            st.session_state.pipeline_initialized = False
    
    return st.session_state.get("pipeline_initialized", False)


def ingest_data_tab():
    """Tab for data ingestion"""
    st.header("📥 Data Ingestion")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Load Shrimp Pond Data")
        
        # File path input
        data_file = st.text_input(
            "Enter path to data file (JSON or CSV)",
            value="./data/raw/pond_data.json",
            help="Path to your input data file"
        )
        
        # Display file information
        if data_file and os.path.exists(data_file):
            file_size = os.path.getsize(data_file) / (1024 * 1024)  # Convert to MB
            st.info(f"✓ File found | Size: {file_size:.2f} MB")
            
            if st.button("🚀 Start Ingestion", key="ingest_btn"):
                with st.spinner("Ingesting data..."):
                    try:
                        num_docs = st.session_state.pipeline.ingest_data(data_file)
                        st.success(f"✓ Successfully ingested {num_docs} documents")
                        logger.info(f"Data ingestion completed: {num_docs} documents")
                    except Exception as e:
                        st.error(f"Error during ingestion: {str(e)}")
                        logger.error(f"Ingestion error: {e}")
        else:
            st.warning("⚠️ File not found. Please check the path.")
    
    with col2:
        st.subheader("Collection Info")
        try:
            info = st.session_state.pipeline.vectorstore.get_collection_info()
            st.metric("Documents in Store", info["document_count"])
        except:
            st.metric("Documents in Store", 0)


def query_tab():
    """Tab for querying the system"""
    st.header("🔍 Ask Questions")
    
    # Initialize chat history if not exists
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Query input
    col1, col2 = st.columns([4, 1])
    
    with col1:
        query = st.text_input(
            "Ask a question about shrimp pond operations:",
            placeholder="e.g., What is the survival rate in pond D14?",
            key="query_input"
        )
    
    with col2:
        search_button = st.button("🔎 Search", use_container_width=True)
    
    # Advanced options (collapsible)
    with st.expander("⚙️ Advanced Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            top_k = st.slider("Number of documents to retrieve", 1, 10, 5)
        
        with col2:
            sim_threshold = st.slider("Similarity threshold", 0.0, 1.0, 0.3)
    
    # Process query
    if search_button and query:
        with st.spinner("Processing query..."):
            try:
                result = st.session_state.pipeline.query(query, top_k=top_k)
                
                # Add to chat history
                st.session_state.chat_history.append({
                    "query": query,
                    "response": result["response"],
                    "timestamp": datetime.now().isoformat(),
                    "num_docs": result["num_documents_retrieved"],
                })
                
                logger.info(f"Query processed: {query}")
                
                # Display response in tabs
                response_col1, response_col2 = st.columns([1.5, 1])
                
                with response_col1:
                    st.subheader("💬 Response")
                    st.write(result["response"])
                
                with response_col2:
                    st.subheader("📊 Query Metrics")
                    st.metric("Documents Retrieved", result["num_documents_retrieved"])
                    st.metric("Query Type", result["query_type"])
                
                # Display retrieved documents
                with st.expander("📄 Retrieved Documents"):
                    for i, doc in enumerate(result["retrieved_documents"], 1):
                        st.write(f"**Document {i}** (Similarity: {doc['similarity_score']:.4f})")
                        st.write(f"**Pond:** {doc['metadata'].get('pond', 'N/A')}")
                        st.write(f"**Crop ID:** {doc['metadata'].get('crop_id', 'N/A')}")
                        st.write(f"**Status:** {doc['metadata'].get('status', 'N/A')}")
                        st.divider()
                        st.text(doc['content'])
                        st.divider()
            
            except Exception as e:
                st.error(f"Error processing query: {str(e)}")
                logger.error(f"Query error: {e}")
    
    # Display chat history
    if st.session_state.chat_history:
        st.divider()
        st.subheader("📜 Chat History")
        
        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"Q: {chat['query'][:50]}... ({chat['timestamp'][-8:]})"):
                st.write(f"**Documents Retrieved:** {chat['num_docs']}")
                st.write("**Response:**")
                st.write(chat['response'])
        
        # Clear history button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()


def analytics_tab():
    """Tab for analytics and insights"""
    st.header("📈 Analytics & Insights")
    
    # Get pipeline info
    try:
        pipeline_info = st.session_state.pipeline.get_pipeline_info()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Documents in Store",
                pipeline_info["vectorstore_info"]["document_count"]
            )
        
        with col2:
            st.metric(
                "Embedding Dimension",
                pipeline_info["embedding_model"]["embedding_dimension"]
            )
        
        with col3:
            st.metric(
                "LLM Model",
                pipeline_info["llm_model"]["model"].split("/")[-1]
            )
        
        with col4:
            st.metric(
                "Temperature",
                f"{pipeline_info['llm_model']['temperature']}"
            )
        
        # Configuration details
        st.subheader("Configuration Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**OpenAI Settings:**")
            openai_config = pipeline_info["configuration"]["openai"]
            for key, value in openai_config.items():
                if key != "api_key":
                    st.text(f"{key}: {value}")
        
        with col2:
            st.write("**Embeddings Settings:**")
            emb_config = pipeline_info["configuration"]["embeddings"]
            for key, value in emb_config.items():
                st.text(f"{key}: {value}")
    
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")


def settings_tab():
    """Tab for application settings"""
    st.header("⚙️ Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("API Configuration")
        
        # Check API key status
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            st.success("✓ OpenAI API Key is configured")
        else:
            st.warning("⚠️ OpenAI API Key not found")
            st.info("Set OPENAI_API_KEY environment variable")
    
    with col2:
        st.subheader("Vector Store")
        
        if st.button("🔄 Reset Vector Store", help="Delete all documents and reset collection"):
            try:
                with st.spinner("Resetting vector store..."):
                    st.session_state.pipeline.reset_vectorstore()
                    st.success("✓ Vector store reset successfully")
                    logger.info("Vector store reset")
            except Exception as e:
                st.error(f"Error resetting vector store: {str(e)}")
    
    st.divider()
    
    # Logging information
    st.subheader("Logging")
    
    col1, col2 = st.columns(2)
    
    with col1:
        log_file = "./logs/app.log"
        if os.path.exists(log_file):
            file_size = os.path.getsize(log_file) / 1024  # KB
            st.text(f"Log file: {log_file}")
            st.text(f"Size: {file_size:.2f} KB")
            
            if st.button("📋 View Recent Logs"):
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        recent_logs = lines[-20:]  # Last 20 lines
                    
                    with st.expander("Recent Log Entries"):
                        st.code("".join(recent_logs), language="log")
                except Exception as e:
                    st.error(f"Error reading logs: {e}")


def main():
    """Main application"""
    # Header
    st.markdown("""
    # 🦐 Shrimp Pond RAG Assistant
    
    An intelligent chatbot for analyzing shrimp pond operations and performance metrics.
    Powered by Retrieval-Augmented Generation (RAG) with OpenAI.
    """)
    
    # Initialize pipeline
    if not initialize_pipeline():
        st.error("Failed to initialize the pipeline. Please check the logs.")
        return
    
    # Sidebar
    with st.sidebar:
        st.title("Navigation")
        
        # Display pipeline status
        try:
            doc_count = st.session_state.pipeline.vectorstore.get_collection_info()["document_count"]
            if doc_count > 0:
                st.success(f"✓ Pipeline Ready ({doc_count} docs)")
            else:
                st.warning("⚠️ No documents ingested")
        except:
            st.error("⚠️ Pipeline Error")
        
        st.divider()
        
        # Navigation menu
        page = st.radio(
            "Select a section:",
            ["🔍 Query", "📥 Data Ingestion", "📈 Analytics", "⚙️ Settings"],
            label_visibility="collapsed"
        )
    
    # Main content based on selected page
    if page == "🔍 Query":
        query_tab()
    elif page == "📥 Data Ingestion":
        ingest_data_tab()
    elif page == "📈 Analytics":
        analytics_tab()
    elif page == "⚙️ Settings":
        settings_tab()
    
    # Footer
    st.divider()
    st.markdown("""
    ---
    Made with ❤️ for Shrimp Farming Operations | Powered by RAG Pipeline
    """)


if __name__ == "__main__":
    main()
