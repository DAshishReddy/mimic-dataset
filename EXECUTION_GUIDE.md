# Execution Guide for MIMIC Dataset RAG Pipeline

## How to Execute the RAG Pipeline

### Method 1: Using Python Module (-m flag)
```bash
cd /Users/anjeereddy/Documents/Workspace/mimic-dataset

# Execute RAG Pipeline
python -m mimic_dataset.main '{"STEP": "RAG_PIPELINE"}'

# Or with other steps
python -m mimic_dataset.main '{"STEP": "BRONZE_LOAD"}'
python -m mimic_dataset.main '{"STEP": "SILVER_TRANSFORM_LOAD"}'
python -m mimic_dataset.main '{"STEP": "QUALITY_CHECK"}'
python -m mimic_dataset.main '{"STEP": "GOLD_TRANSFORM_LOAD"}'
```

### Method 2: Using Entry Point (from pyproject.toml)
```bash
# After installing with pip install -e .
run '{"STEP": "RAG_PIPELINE"}'
```

### Method 3: Direct Python Script
```bash
cd /Users/anjeereddy/Documents/Workspace/mimic-dataset

# With step parameter
python -c "from src.mimic_dataset.main import main; main('{\"STEP\": \"RAG_PIPELINE\"}')"
```

### Method 4: Direct Python Execution (now working with __main__ block)
```bash
cd /Users/anjeereddy/Documents/Workspace/mimic-dataset

# Run and provide step as stdin or modify pyproject.toml entry point
python src/mimic_dataset/main.py
```

### Method 5: Interactive Python
```python
from mimic_dataset.main import main
import json

# Execute RAG Pipeline
main(json.dumps({"STEP": "RAG_PIPELINE"}))
```

### Method 6: Direct Module Imports (Most Flexible)
```python
from mimic_dataset.gen_ai.rag_pipeline import execute_rag_pipeline

# Run full pipeline
artifacts = execute_rag_pipeline()

# Use individual functions as needed
from mimic_dataset.gen_ai.rag_pipeline import ask_mimic_bot
answer = ask_mimic_bot("Questions?", artifacts['index'])
```

---

## Full ETL Pipeline Execution

Run the complete ETL pipeline with all steps:

```bash
#!/bin/bash
# Execute all steps in sequence

echo "🔄 Starting MIMIC ETL Pipeline..."

echo "1️⃣  Loading data to BRONZE..."
python -m mimic_dataset.main '{"STEP": "BRONZE_LOAD"}'

echo "2️⃣  Transforming and loading to SILVER..."
python -m mimic_dataset.main '{"STEP": "SILVER_TRANSFORM_LOAD"}'

echo "3️⃣  Running quality checks..."
python -m mimic_dataset.main '{"STEP": "QUALITY_CHECK"}'

echo "4️⃣  Loading to GOLD layer..."
python -m mimic_dataset.main '{"STEP": "GOLD_TRANSFORM_LOAD"}'

echo "5️⃣  Executing RAG Pipeline..."
python -m mimic_dataset.main '{"STEP": "RAG_PIPELINE"}'

echo "✅ Pipeline completed successfully!"
```

---

## Execution Examples

### Example 1: RAG Pipeline Only
```bash
python -m mimic_dataset.main '{"STEP": "RAG_PIPELINE"}'
```

### Example 2: Using with Python Script
```python
import sys
import json
from mimic_dataset.main import main

# Define the step
step = {
    "STEP": "RAG_PIPELINE"
}

# Execute
main(json.dumps(step))
```

### Example 3: In Jupyter Notebook
```python
from mimic_dataset.main import main
import json

# Run RAG Pipeline
result = main('{"STEP": "RAG_PIPELINE"}')
print("✅ RAG Pipeline executed")
```

### Example 4: Batch Processing
```python
import json
from mimic_dataset.main import main

# Execute multiple steps
steps = [
    "BRONZE_LOAD",
    "SILVER_TRANSFORM_LOAD",
    "QUALITY_CHECK",
    "GOLD_TRANSFORM_LOAD",
    "RAG_PIPELINE"
]

for step in steps:
    print(f"Executing: {step}")
    main(json.dumps({"STEP": step}))
    print(f"✅ {step} completed\n")
```

---

## Expected Output

### Successful Execution
```
Hello
{"STEP": "RAG_PIPELINE"}
{'STEP': 'RAG_PIPELINE'}
RAG_PIPELINE

======================================================================
🚀 MIMIC RAG PIPELINE EXECUTION
======================================================================

📄 Phase 1: Creating documents from MIMIC silver tables...
✅ Created 1234 documents in mmc.gold.llm_documents

✂️  Phase 2: Chunking documents...
✅ Created 5678 chunks in mmc.gold.llm_chunks

🔢 Phase 3: Generating embeddings...
  Processed 100/5678 chunks
  Processed 200/5678 chunks
  ...
✅ Generated embeddings for 5678 chunks in mmc.gold.llm_embeddings

🔍 Phase 4: Creating vector search index...
✅ Created Vector Search endpoint: mimic_vector_endpoint
✅ Created Vector Search index: mmc.gold.mimic_llm_index

✅ RAG Pipeline executed successfully!
======================================================================
✅ Job Completed Successfully
```

### Error Handling
```
Hello
Invalid JSON
Error: Expecting value: line 1 column 1 (char 0)

# OR

Hello
{"STEP": "INVALID_STEP"}
{'STEP': 'INVALID_STEP'}
INVALID_STEP
Invalid STEP parameter: INVALID_STEP
```

---

## Troubleshooting

### Issue: "No module named 'mimic_dataset'"
**Solution:** Install the package
```bash
cd /Users/anjeereddy/Documents/Workspace/mimic-dataset
pip install -e .
```

### Issue: "JSON decode error"
**Solution:** Ensure JSON is properly formatted
```bash
# Wrong
python -m mimic_dataset.main {STEP: RAG_PIPELINE}

# Correct
python -m mimic_dataset.main '{"STEP": "RAG_PIPELINE"}'
```

### Issue: "Spark session not initialized"
**Solution:** Ensure GlobalVariables.setup_spark() is called (done automatically in main)

### Issue: "Vector search endpoint not found"
**Solution:** Pipeline creates it automatically on first run. Give it a moment.

### Issue: Slow embedding generation
**Solution:** Use skip_embedding_generation=True on subsequent runs
```python
from mimic_dataset.gen_ai.rag_pipeline import execute_rag_pipeline
execute_rag_pipeline(skip_embedding_generation=True)
```

---

## Performance Notes

| Phase | Time | Notes |
|-------|------|-------|
| Phase 1: Documents | ~1 min | Depends on silver table size |
| Phase 2: Chunks | ~2 min | Depends on document count |
| Phase 3: Embeddings | 10-30 min | Most time-consuming, uses API |
| Phase 4: Vector Index | ~2 min | Usually quick |
| **Total First Run** | 20-40 min | Includes embedding generation |
| **Subsequent Runs** | ~2 min | With skip_embedding_generation=True |

---

## Available Steps

| Step | Description |
|------|-------------|
| `BRONZE_LOAD` | Ingest raw data to bronze layer |
| `SILVER_TRANSFORM_LOAD` | Transform and load to silver layer |
| `QUALITY_CHECK` | Run data quality checks |
| `GOLD_TRANSFORM_LOAD` | Aggregate and load to gold layer |
| `RAG_PIPELINE` | Execute RAG pipeline for AI insights |

---

## Advanced Usage

### Custom Schema
```python
from mimic_dataset.gen_ai.rag_pipeline import execute_rag_pipeline

# Use custom schema
artifacts = execute_rag_pipeline(schema_name="custom_schema")
```

### Skip Embedding Generation
```python
from mimic_dataset.gen_ai.rag_pipeline import execute_rag_pipeline

# Reuse existing embeddings
artifacts = execute_rag_pipeline(skip_embedding_generation=True)
```

### Use Existing Index
```python
from databricks.vector_search.client import VectorSearchClient

# Get existing index
vsc = VectorSearchClient()
index = vsc.get_index(
    endpoint_name="mimic_vector_endpoint",
    index_name="mmc.gold.mimic_llm_index"
)

# Use for queries
from mimic_dataset.gen_ai.rag_pipeline import ask_mimic_bot
answer = ask_mimic_bot("Question?", index)
```

---

## Next Steps

1. ✅ Verify installation: `pip install -e .`
2. ✅ Execute RAG pipeline: `python -m mimic_dataset.main '{"STEP": "RAG_PIPELINE"}'`
3. ✅ Check documentation: Read RAG_PIPELINE_QUICK_START.md
4. ✅ Try examples: Run code from RAG_PIPELINE_QUICK_START.md
5. ✅ Integrate: Use in your applications

---

Happy analyzing! 🚀

