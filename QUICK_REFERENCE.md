"""
Quick Reference Guide - Shrimp Pond RAG Pipeline
Tested and verified working system
"""

# ============================================================================
# QUICK REFERENCE GUIDE - SHRIMP POND RAG PIPELINE
# ============================================================================

## 🚀 GETTING STARTED (Quick Setup)

### 1. Activate Virtual Environment
```bash
source /home/raj/chatbotpractice/.venv/bin/activate
cd /home/raj/chatbotpractice/shrimp_rag_pipeline
```

### 2. Run the Web App
```bash
streamlit run app.py
```
App opens at: http://localhost:8501

### 3. Ask Questions!
Use the Query tab to ask about your shrimp pond data.

---

## ✅ VERIFIED WORKING QUERIES

These queries have been tested and work correctly:

### 1. Direct Pond Questions
```
"What is the survival rate in pond D14?"
"Show me the biomass for pond D16"
"Pond D11 performance data"
"Stocking information for pond H4"
```

### 2. General Metric Queries
```
"Survival rate analysis"
"Biomass and growth information"
"Pond performance metrics"
"Crop status and information"
```

### 3. Comparative Analysis
```
"Compare pond performance"
"Active vs harvested crops"
"Historical survival rates"
```

### 4. Specific Data Requests
```
"ACTIVE crops information"
"HARVESTED crop details"
"Current cycle data"
```

---

## 📊 HOW THE SYSTEM WORKS

```
Your Question
    ↓
Vector Embedding
    ↓
Semantic Search (Find relevant data)
    ↓
Retrieved Documents
    ↓
LLM Processing (OpenAI)
    ↓
Intelligent Answer
```

---

## 🎯 AVAILABLE DATA

### Ponds:
D11, D13, D14, D16, H4, C3, E9, and 30+ others

### Key Metrics:
- **Survival Rate** - Percentage of shrimp that survived
- **Biomass (BM)** - Total weight of shrimp
- **ABW** - Average Body Weight
- **FCR** - Feed Conversion Ratio
- **Stocking** - Number of shrimp stocked
- **DOC** - Days on Culture
- **Status** - ACTIVE or HARVESTED

---

## 💻 COMMAND LINE USAGE

### Test the System
```bash
# Run comprehensive tests
python test_vector_retrieval.py

# Quick demo
python quickstart.py

# Analyze data
python analyze_data.py
```

### Python Code
```python
from rag_pipeline import RAGPipeline

# Initialize
pipeline = RAGPipeline(config_dir="./config")

# Ask a question
result = pipeline.query("What is the survival rate in pond D14?")

# Get the answer
print(result["response"])

# See retrieved documents
for doc in result["retrieved_documents"]:
    print(f"Score: {doc['similarity_score']:.4f}")
    print(f"Content: {doc['content']}")
```

---

## 📁 PROJECT STRUCTURE

```
shrimp_rag_pipeline/
├── app.py                 # Web interface
├── rag_pipeline.py        # Main system
├── test_vector_retrieval.py  # Test suite ✅
├── TEST_RESULTS.md        # Test results ✅
├── config/
│   ├── settings.yaml      # Configuration
│   └── prompts.yaml       # LLM prompts
├── src/                   # Core modules
├── data/
│   ├── raw/
│   │   └── pond_data.json # Your data (472 records)
│   └── vectorstore/       # Database
└── logs/
    ├── pipeline.log
    ├── app.log
    └── test_vector_retrieval.log ✅
```

---

## 🔧 CONFIGURATION

### settings.yaml - Key Settings
```yaml
openai:
  model: "gpt-3.5-turbo"      # Use GPT-4 for better quality
  temperature: 0.7            # 0.3=factual, 0.9=creative
  max_tokens: 1500            # Response length

vectorstore:
  chunk_size: 500             # Document chunk size
  top_k: 5                    # Number of results

retrieval:
  similarity_threshold: 0.0   # Minimum relevance score
```

### Change Model to GPT-4
```yaml
openai:
  model: "gpt-4"
```

### More Factual Responses
```yaml
openai:
  temperature: 0.3
```

---

## 🐛 TROUBLESHOOTING

### "No API Key" Error
✅ Fixed - .env file is configured

### "No documents found"
Solution:
```bash
# Data is already ingested during test
# If needed, re-ingest via web app UI or:
python test_vector_retrieval.py  # Ingests automatically
```

### Low retrieval scores
Try these queries instead:
```
"What is the survival rate?"
"Show me pond D14"
"Biomass information"
```

### Slow responses
Check if:
- Internet connection is stable
- OpenAI API is responding
- Model is gpt-3.5-turbo (not gpt-4)

---

## 📈 SYSTEM STATUS

All components verified and working:
- ✅ Data loading (472 records)
- ✅ Embeddings (384 dimensions)
- ✅ Vector database (472 documents)
- ✅ Semantic search (tested)
- ✅ LLM integration (OpenAI)
- ✅ Web interface (Streamlit)

---

## 📊 TEST RESULTS SUMMARY

```
Environment Setup         ✅ PASS
Data Loading             ✅ PASS
Embeddings Generation    ✅ PASS
Vector Store Setup       ✅ PASS
Data Ingestion          ✅ PASS
Vector Retrieval        ✅ PASS
Full RAG Query          ✅ PASS
─────────────────────────────────
Total: 7/7 tests passed ✅
```

---

## 🎓 LEARNING RESOURCES

### Files to Read:
1. **README.md** - Complete documentation
2. **SETUP_GUIDE.md** - Installation guide
3. **TEST_RESULTS.md** - Test results and queries
4. **PROJECT_SUMMARY.md** - Architecture overview

### View Logs:
```bash
# Real-time logs
tail -f logs/pipeline.log

# Test logs
cat logs/test_vector_retrieval.log
```

---

## 💡 TIPS FOR BEST RESULTS

### Write Clear Questions
```
✅ "What is the survival rate in pond D14?"
❌ "D14 survival?"
```

### Mention Specific Ponds
```
✅ "Pond D14 performance"
❌ "Performance"
```

### Use Complete Metrics
```
✅ "Average body weight"
❌ "ABW" (acronym)
```

### Ask About Status
```
✅ "Show me ACTIVE crops"
❌ "Current crops"
```

---

## 🚀 NEXT STEPS

1. ✅ **System is ready to use!**

2. **Start web app:**
   ```bash
   streamlit run app.py
   ```

3. **Try a query:**
   - "What is the survival rate in pond D14?"
   - "Show me pond D16 performance"
   - "ACTIVE crops information"

4. **Explore data:**
   - Use Data Ingestion tab
   - View Analytics dashboard
   - Check logs

5. **Customize:**
   - Edit config/prompts.yaml
   - Adjust settings.yaml
   - Add new data

---

## 📞 QUICK HELP

### How to run tests?
```bash
python test_vector_retrieval.py
```

### How to see logs?
```bash
tail -f logs/pipeline.log
```

### How to reset data?
```bash
rm -rf data/vectorstore/
python test_vector_retrieval.py  # Re-ingest
```

### How to use Python API?
```python
from rag_pipeline import RAGPipeline
pipeline = RAGPipeline()
result = pipeline.query("your question")
print(result["response"])
```

---

## ✨ YOU'RE ALL SET!

The Shrimp Pond RAG Pipeline is:
- ✅ Installed
- ✅ Configured
- ✅ Tested
- ✅ Ready to use

**Start the app:**
```bash
streamlit run app.py
```

**Enjoy!** 🦐
