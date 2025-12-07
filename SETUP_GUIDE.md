"""
SETUP AND INSTALLATION GUIDE
Comprehensive guide to set up and run the Shrimp Pond RAG Pipeline
"""

# ============================================================================
# SHRIMP POND RAG PIPELINE - SETUP GUIDE
# ============================================================================

## OVERVIEW

The Shrimp Pond RAG Pipeline is a production-ready Retrieval-Augmented 
Generation system that combines:
- Data ingestion and preprocessing
- Semantic search with embeddings
- Vector storage with ChromaDB
- LLM integration with OpenAI
- Interactive web interface with Streamlit

## PREREQUISITES

Before starting, ensure you have:
- Python 3.8 or higher
- pip (Python package manager)
- An OpenAI API key (from https://platform.openai.com/api-keys)
- Git (optional, for version control)


## INSTALLATION STEPS

### 1. NAVIGATE TO PROJECT DIRECTORY
```bash
cd /home/raj/chatbotpractice/shrimp_rag_pipeline
```

### 2. CREATE VIRTUAL ENVIRONMENT
```bash
# On macOS/Linux:
python3 -m venv venv
source venv/bin/activate

# On Windows (Command Prompt):
python -m venv venv
venv\Scripts\activate

# On Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. INSTALL DEPENDENCIES
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. SET UP ENVIRONMENT VARIABLES
Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Alternatively, set the environment variable directly:

**On macOS/Linux:**
```bash
export OPENAI_API_KEY='your-api-key-here'
```

**On Windows (Command Prompt):**
```bash
set OPENAI_API_KEY=your-api-key-here
```

**On Windows (PowerShell):**
```bash
$env:OPENAI_API_KEY='your-api-key-here'
```

### 5. PREPARE DATA
Place your `pond_data.json` file in the `data/raw/` directory:
```
data/
└── raw/
    └── pond_data.json
```


## RUNNING THE APPLICATION

### Option 1: WEB INTERFACE (RECOMMENDED)
```bash
streamlit run app.py
```

This will:
- Open a web browser at http://localhost:8501
- Display the interactive Shrimp Pond RAG Assistant
- Allow you to ingest data and ask questions

### Option 2: QUICK START SCRIPT
```bash
python quickstart.py
```

This demonstrates:
- Pipeline initialization
- Data ingestion
- Sample queries
- Pipeline information

### Option 3: DATA ANALYSIS
```bash
python analyze_data.py
```

This provides:
- Data structure analysis
- Field statistics
- Categorical breakdowns
- Sample records

### Option 4: PROGRAMMATIC USAGE
```python
from rag_pipeline import RAGPipeline

# Initialize
pipeline = RAGPipeline(config_dir="./config")

# Ingest data
pipeline.ingest_data("./data/raw/pond_data.json")

# Query
result = pipeline.query("What is the survival rate in pond D14?")
print(result["response"])
```


## PROJECT STRUCTURE EXPLAINED

```
shrimp_rag_pipeline/
│
├── app.py                          # Main Streamlit application
├── rag_pipeline.py                 # RAG pipeline orchestrator
├── setup.py                        # Setup and configuration
├── quickstart.py                   # Quick start demonstration
├── analyze_data.py                 # Data analysis tool
├── requirements.txt                # Python dependencies
├── README.md                       # Full documentation
├── .env.example                    # Environment template
│
├── config/
│   ├── settings.yaml              # Configuration settings
│   └── prompts.yaml               # LLM prompt templates
│
├── src/
│   ├── ingestion/                 # Data loading and preprocessing
│   │   ├── data_loader.py
│   │   └── __init__.py
│   │
│   ├── embeddings/                # Embedding generation
│   │   ├── embedding_manager.py
│   │   └── __init__.py
│   │
│   ├── vectorstore/               # Vector store management
│   │   ├── chroma_store.py
│   │   └── __init__.py
│   │
│   ├── retrieval/                 # Document retrieval
│   │   ├── retriever.py
│   │   └── __init__.py
│   │
│   ├── generation/                # LLM integration
│   │   ├── llm_client.py
│   │   └── __init__.py
│   │
│   ├── utils/                     # Utilities
│   │   ├── logger.py
│   │   ├── config_loader.py
│   │   ├── helpers.py
│   │   └── __init__.py
│   │
│   └── __init__.py
│
├── data/
│   ├── raw/                       # Input data files
│   │   └── pond_data.json
│   └── vectorstore/               # ChromaDB storage (auto-created)
│
├── logs/                          # Application logs (auto-created)
│   ├── pipeline.log
│   └── app.log
│
└── notebooks/                     # For Jupyter notebooks
```


## CONFIGURATION

### settings.yaml
Customize application behavior:
- OpenAI model and parameters
- Embedding model settings
- Vector store configuration
- Data chunking parameters
- Logging settings

### prompts.yaml
Customize LLM prompts:
- System prompt
- Query-specific prompts
- Query type detection
- Response evaluation

Edit these files to fine-tune the pipeline for your needs.


## USING THE WEB INTERFACE

### Navigation Menu
Located in the left sidebar with 4 main sections:

1. **🔍 Query** (Default)
   - Ask questions about pond operations
   - View retrieved documents
   - Chat history maintained per session

2. **📥 Data Ingestion**
   - Upload new data files
   - Monitor ingestion progress
   - View collection statistics

3. **📈 Analytics**
   - Pipeline statistics
   - Configuration details
   - Model information

4. **⚙️ Settings**
   - API status
   - Vector store management
   - View application logs

### Example Queries
Try these queries after loading data:

1. "What is the survival rate in pond D14?"
2. "Which ponds have the highest FCR?"
3. "Show me active crops and their status"
4. "What is the average stocking density?"
5. "Compare biomass across different cycles"


## TROUBLESHOOTING

### Issue: "OpenAI API Key not found"
**Solution:** Set OPENAI_API_KEY environment variable
```bash
export OPENAI_API_KEY='your-key'
```

### Issue: "Data file not found"
**Solution:** Place pond_data.json in data/raw/ directory
```bash
cp /path/to/pond_data.json ./data/raw/
```

### Issue: "No documents in collection"
**Solution:** Ingest data using the web interface or:
```bash
python quickstart.py
```

### Issue: Streamlit not starting
**Solution:** Install/upgrade Streamlit
```bash
pip install --upgrade streamlit
```

### Issue: Memory errors with large datasets
**Solution:** Reduce batch size in config/settings.yaml
```yaml
ingestion:
  batch_size: 50  # Reduce from 100
```

### Issue: Slow embeddings generation
**Solution:** Use GPU if available or smaller model
```yaml
embeddings:
  model_name: "all-MiniLM-L6-v2"  # Lightweight model
```


## PERFORMANCE TIPS

1. **For faster ingestion:**
   - Increase batch_size in settings.yaml
   - Use SSD for data/vectorstore directory
   - Reduce chunk_size if data is large

2. **For better responses:**
   - Increase top_k (retrieve more documents)
   - Adjust temperature in settings.yaml
   - Fine-tune prompts in prompts.yaml
   - Use gpt-4 for more complex analysis

3. **For lower costs:**
   - Use gpt-3.5-turbo (default)
   - Reduce top_k if sufficient results
   - Cache responses for repeated queries


## DEVELOPMENT FEATURES

### Logging
All operations logged to `logs/pipeline.log`:
```bash
tail -f logs/pipeline.log  # View real-time logs
```

### Type Hints
All code includes type hints for better IDE support:
```python
def ingest_data(self, data_file_path: str) -> int:
    """Ingest data and return number of documents added"""
```

### Modular Design
Each component is independent and testable:
```python
from src.embeddings import EmbeddingManager
embedding_manager = EmbeddingManager()
embeddings = embedding_manager.generate_embeddings(texts)
```


## NEXT STEPS

1. **Load Data:**
   - Use the Data Ingestion tab in the app
   - Or run: `python quickstart.py`

2. **Ask Questions:**
   - Use the Query tab
   - Try the example queries

3. **Analyze Results:**
   - Check Analytics tab for statistics
   - Review logs in Settings

4. **Customize:**
   - Edit config/prompts.yaml for better responses
   - Adjust config/settings.yaml for performance
   - Modify src/ modules for custom logic


## API REFERENCE

### RAGPipeline Class

```python
from rag_pipeline import RAGPipeline

pipeline = RAGPipeline(config_dir="./config")

# Ingest data
num_docs = pipeline.ingest_data(file_path)

# Query
result = pipeline.query(query_string, top_k=5)

# Get info
info = pipeline.get_pipeline_info()

# Reset
pipeline.reset_vectorstore()
```

### Query Results Structure
```python
{
    "query": "Original query",
    "response": "LLM generated response",
    "retrieved_documents": [
        {
            "id": "doc_xxx",
            "content": "Document content",
            "metadata": {"pond": "D14", ...},
            "similarity_score": 0.92,
            "rank": 1
        },
        ...
    ],
    "query_type": "pond_performance",
    "num_documents_retrieved": 5
}
```


## SUPPORT AND DOCUMENTATION

- **README.md**: Full feature documentation
- **logs/pipeline.log**: Detailed operation logs
- **config/**: Customization examples
- **src/**: Well-commented source code


## QUICK COMMANDS

```bash
# Activate environment
source venv/bin/activate

# Install/upgrade dependencies
pip install -r requirements.txt

# Run web app
streamlit run app.py

# Quick start demo
python quickstart.py

# Analyze data
python analyze_data.py

# View logs
tail -f logs/pipeline.log

# Reset pipeline
rm -rf data/vectorstore/*
```


## SUCCESS CHECKLIST

Before using in production:
- [ ] Virtual environment created and activated
- [ ] Requirements installed successfully
- [ ] OPENAI_API_KEY set in environment
- [ ] Data file placed in data/raw/
- [ ] Quick start script runs successfully
- [ ] Web app launches without errors
- [ ] Data ingestion completes
- [ ] Sample queries return results
- [ ] Logs are being generated


## WHAT'S NEXT?

Once setup is complete, you can:
1. Ingest your own pond data
2. Ask complex questions about operations
3. Generate reports and insights
4. Integrate with other systems
5. Deploy to production


For more information, see README.md
"""

if __name__ == "__main__":
    print(__doc__)
