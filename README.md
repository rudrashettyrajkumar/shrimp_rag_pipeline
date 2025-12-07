# Shrimp Pond RAG Pipeline

A production-ready Retrieval-Augmented Generation (RAG) system for analyzing shrimp pond operations data using OpenAI's language models.

## Features

- **Data Ingestion**: Load and preprocess shrimp pond data from JSON/CSV files
- **Semantic Search**: Find relevant documents using sentence-transformers embeddings
- **Vector Storage**: Store and retrieve embeddings efficiently with ChromaDB
- **LLM Integration**: Generate intelligent responses using OpenAI API
- **Web Interface**: Interactive Streamlit UI for easy access
- **Comprehensive Logging**: Track all operations and errors
- **Modular Architecture**: Clean separation of concerns for easy maintenance

## Project Structure

```
shrimp_rag_pipeline/
├── app.py                      # Streamlit application
├── rag_pipeline.py            # Main RAG pipeline orchestrator
├── setup.py                   # Setup and initialization
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── config/
│   ├── settings.yaml         # Application configuration
│   └── prompts.yaml          # LLM prompt templates
├── src/
│   ├── ingestion/            # Data loading and preprocessing
│   ├── embeddings/           # Embedding generation
│   ├── vectorstore/          # Vector store management
│   ├── retrieval/            # Document retrieval
│   ├── generation/           # LLM integration
│   └── utils/                # Utility modules
├── data/
│   ├── raw/                  # Input data files
│   └── vectorstore/          # ChromaDB storage
└── logs/                      # Application logs
```

## Installation

### Prerequisites

- Python 3.8+
- OpenAI API key

### Setup

1. **Clone or navigate to the project directory:**
```bash
cd shrimp_rag_pipeline
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set OpenAI API key:**
```bash
export OPENAI_API_KEY='your-api-key-here'
```

On Windows (Command Prompt):
```bash
set OPENAI_API_KEY=your-api-key-here
```

On Windows (PowerShell):
```bash
$env:OPENAI_API_KEY='your-api-key-here'
```

## Usage

### Web Interface (Recommended)

Run the Streamlit application:

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

**Features:**
- 🔍 **Query**: Ask questions about pond operations
- 📥 **Data Ingestion**: Load new data files
- 📈 **Analytics**: View pipeline statistics
- ⚙️ **Settings**: Configure and manage the pipeline

### Programmatic Usage

```python
from rag_pipeline import RAGPipeline

# Initialize pipeline
pipeline = RAGPipeline(config_dir="./config")

# Ingest data
num_docs = pipeline.ingest_data("./data/raw/pond_data.json")

# Query the system
result = pipeline.query("What is the survival rate in pond D14?", top_k=5)

# Access results
print(result["response"])
print(f"Retrieved {result['num_documents_retrieved']} documents")
```

## Configuration

### Settings (config/settings.yaml)

Edit this file to customize:
- OpenAI model selection and parameters
- Embedding model configuration
- Vector store settings
- Chunking parameters

### Prompts (config/prompts.yaml)

Customize LLM prompts for different query types:
- Pond performance analysis
- Survival analysis
- Feed conversion queries
- Biomass calculations

## Data Format

### Input JSON Format

```json
{
  "data": [
    {
      "Pond": "D14",
      "Crop ID": "F1D14C22025.23",
      "Stocking": 632061,
      "Survival Rate": "60%",
      "FCR": 1.4,
      "ABW": 21.04,
      "status": "HARVESTED",
      ...
    }
  ]
}
```

### Supported Fields

- **Pond**: Pond identifier
- **Crop ID**: Unique crop identifier
- **Stocking Date**: Date of stocking
- **Stocking**: Number of shrimp stocked
- **DOC**: Days on culture
- **ABW**: Average body weight
- **Survival Rate**: Percentage of shrimp that survived
- **FCR**: Feed Conversion Ratio
- **BM**: Biomass
- **status**: Current status (ACTIVE/HARVESTED)

## API Endpoints

### RAG Pipeline Methods

#### `ingest_data(file_path: str) -> int`
Load and process data from a file.
- **Returns**: Number of documents added

#### `query(query: str, top_k: int = 5) -> Dict`
Process a query and generate response.
- **Returns**: Dictionary with query results and response

#### `get_pipeline_info() -> Dict`
Get pipeline configuration and status.
- **Returns**: Configuration details

#### `reset_vectorstore()`
Clear all documents from vector store.

## Key Components

### DataLoader
Loads data from JSON and CSV files.

### DataPreprocessor
Cleans and prepares data, converts to LangChain Documents.

### EmbeddingManager
Generates embeddings using sentence-transformers.

### VectorStore
Manages ChromaDB collection for storing and retrieving embeddings.

### Retriever
Performs semantic search to find relevant documents.

### LLMClient
Interfaces with OpenAI API for response generation.

### PromptBuilder
Constructs prompts for different query types and detects query intent.

## Logging

All operations are logged to `./logs/pipeline.log`. Check logs for:
- Data ingestion progress
- Query processing details
- Error messages
- Performance metrics

## Performance Optimization

### For Large Datasets

1. **Increase batch size**: Modify `ingestion.batch_size` in settings.yaml
2. **Optimize chunk size**: Adjust `vectorstore.chunk_size` based on your data
3. **Use GPU embeddings**: Ensure sentence-transformers uses available GPU

### For Better Responses

1. **Adjust temperature**: Lower for factual answers, higher for creative
2. **Increase top_k**: Retrieve more documents for comprehensive context
3. **Fine-tune prompts**: Customize prompts.yaml for better results

## Troubleshooting

### OpenAI API Errors
- Verify API key is set correctly
- Check API quota and usage
- Ensure model name is valid

### Memory Issues
- Reduce chunk size
- Lower batch size for ingestion
- Use smaller embedding model

### No Results Found
- Check if data is ingested
- Verify vector store has documents
- Lower similarity threshold

## Example Queries

1. "What is the survival rate in pond D14?"
2. "Compare the FCR across different cycles"
3. "Which pond has the highest biomass?"
4. "What is the average stocking density?"
5. "Show me active crops and their current status"

## License

This project is provided as-is for shrimp farming operations analysis.

## Support

For issues or questions:
1. Check the logs in `./logs/`
2. Review the configuration in `./config/`
3. Verify data format matches expected structure

## Future Enhancements

- [ ] Database integration for persistent storage
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Export reports functionality
- [ ] Fine-tuned models for domain-specific knowledge
- [ ] Real-time data streaming
- [ ] User authentication and role management
