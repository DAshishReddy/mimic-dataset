# RAG Pipeline Quick Start Guide

## Installation

### 1. Install Dependencies
```bash
cd /Users/anjeereddy/Documents/Workspace/mimic-dataset
pip install -e .
```

Or manually install required packages:
```bash
pip install databricks-genai-inference databricks-vectorsearch langchain-text-splitters pandas pyspark
```

## Quick Examples

### Example 1: Execute Full RAG Pipeline

```python
from mimic_dataset.gen_ai.rag_pipeline import execute_rag_pipeline

# Run the complete pipeline
artifacts = execute_rag_pipeline(schema_name="mmc")

# Extract the vector search index for later use
index = artifacts['index']
print("✅ Pipeline executed successfully!")
```

### Example 2: Ask Simple Questions

```python
from mimic_dataset.gen_ai.rag_pipeline import ask_mimic_bot, execute_rag_pipeline

# Get the index
artifacts = execute_rag_pipeline()
index = artifacts['index']

# Ask a question
question = "What are common emergency diagnoses?"
answer = ask_mimic_bot(question, index)
print(f"Q: {question}")
print(f"A: {answer}")
```

### Example 3: Get Structured Results

```python
from mimic_dataset.gen_ai.rag_pipeline import ask_mimic_bot_table, execute_rag_pipeline

artifacts = execute_rag_pipeline()
index = artifacts['index']

# Get results as a DataFrame
question = "What infections are common in emergency admissions?"
results_df = ask_mimic_bot_table(question, index)
print(results_df)
```

### Example 4: Conversational Chat

```python
from mimic_dataset.gen_ai.rag_pipeline import MimicChatbot, execute_rag_pipeline

artifacts = execute_rag_pipeline()
index = artifacts['index']

# Create chatbot with memory
bot = MimicChatbot(index=index)

# First question
print(bot.ask("What diagnoses require ICU admission?"))

# Follow-up (maintains context)
print(bot.ask("What medications are used for those?"))

# Another follow-up
print(bot.ask("Tell me more about the most common one"))

# Reset if needed
bot.reset()
```

### Example 5: Patient Lookup and Clinical Insights

```python
from mimic_dataset.gen_ai.rag_pipeline import (
    execute_rag_pipeline,
    get_patient_summary,
    generate_patient_insights
)

artifacts = execute_rag_pipeline()
index = artifacts['index']

# Get patient data
subject_id = 10029
admissions_df, icu_df = get_patient_summary(subject_id)

print(f"Patient {subject_id} Summary:")
print(f"- Admissions: {len(admissions_df)}")
print(f"- ICU Stays: {len(icu_df)}")

# Generate AI insights
insights = generate_patient_insights(admissions_df, icu_df, subject_id, index)
print("\nClinical Insights:")
print(insights)
```

### Example 6: Generate Prescription

```python
from mimic_dataset.gen_ai.rag_pipeline import (
    execute_rag_pipeline,
    get_patient_summary,
    generate_prescription
)

artifacts = execute_rag_pipeline()
index = artifacts['index']

# Get patient
subject_id = 10029
admissions_df, icu_df = get_patient_summary(subject_id)

# Generate prescription
prescription = generate_prescription(admissions_df, icu_df, subject_id, index)
print("Prescription Recommendations:")
print(prescription)
```

### Example 7: Send Prescription Email

```python
from mimic_dataset.gen_ai.rag_pipeline import (
    execute_rag_pipeline,
    get_patient_summary,
    generate_prescription,
    send_prescription_email
)

artifacts = execute_rag_pipeline()
index = artifacts['index']

# Get patient and generate prescription
subject_id = 10029
admissions_df, icu_df = get_patient_summary(subject_id)
prescription = generate_prescription(admissions_df, icu_df, subject_id, index)

# Send email (or get preview)
success, result = send_prescription_email(
    recipient_email="doctor@hospital.com",
    subject_id=subject_id,
    admissions_df=admissions_df,
    icu_df=icu_df,
    prescription_text=prescription,
    doctor_name="Smith",
    # For actual sending (Gmail requires app password):
    # sender_email="your_email@gmail.com",
    # sender_password="your_app_password"
)

if success:
    print(f"✅ {result}")
else:
    # If SMTP not configured, result contains HTML preview
    print("📧 Email Preview:")
    print(result[:500] + "...")  # First 500 chars
```

### Example 8: Integration with Main ETL

```python
import json
from mimic_dataset.main import main

# Call RAG pipeline as part of main ETL
main(json.dumps({"STEP": "RAG_PIPELINE"}))
```

Or from command line:
```bash
python -m mimic_dataset.main '{"STEP": "RAG_PIPELINE"}'
```

## Common Workflows

### Workflow 1: One-Time Setup
```python
from mimic_dataset.gen_ai.rag_pipeline import execute_rag_pipeline

# Setup once
artifacts = execute_rag_pipeline()
# Store or save artifacts for reuse
```

### Workflow 2: Reuse Index
```python
from mimic_dataset.gen_ai.rag_pipeline import execute_rag_pipeline, ask_mimic_bot
from databricks.vector_search.client import VectorSearchClient

# Get existing index instead of regenerating
vsc = VectorSearchClient()
index = vsc.get_index(
    endpoint_name="mimic_vector_endpoint", 
    index_name="mmc.gold.mimic_llm_index"
)

# Use for multiple queries
for question in ["What is common?", "What is rare?"]:
    answer = ask_mimic_bot(question, index)
    print(f"Q: {question}")
    print(f"A: {answer}\n")
```

### Workflow 3: Batch Patient Processing
```python
from mimic_dataset.gen_ai.rag_pipeline import (
    execute_rag_pipeline,
    get_patient_summary,
    generate_prescription
)

artifacts = execute_rag_pipeline()
index = artifacts['index']

# Process multiple patients
patient_ids = [10029, 10030, 10031]

for patient_id in patient_ids:
    try:
        admissions_df, icu_df = get_patient_summary(patient_id)
        if not admissions_df.empty:
            prescription = generate_prescription(admissions_df, icu_df, patient_id, index)
            print(f"✅ Patient {patient_id}: Prescription generated")
    except Exception as e:
        print(f"❌ Patient {patient_id}: Error - {e}")
```

## Configuration Options

### Customize Chunking
```python
from mimic_dataset.gen_ai.rag_pipeline import chunk_documents

# Larger chunks with more overlap for better context
chunk_documents(
    schema_name="mmc",
    chunk_size=500,
    chunk_overlap=100
)
```

### Customize Embedding
```python
from mimic_dataset.gen_ai.rag_pipeline import generate_embeddings

# Larger batch size (faster) or smaller (more conservative)
generate_embeddings(
    schema_name="mmc",
    batch_size=50,
    rate_limit_sleep=0.5
)
```

### Skip Expensive Operations
```python
from mimic_dataset.gen_ai.rag_pipeline import execute_rag_pipeline

# Skip embedding generation if already done
artifacts = execute_rag_pipeline(skip_embedding_generation=True)
```

## Troubleshooting

### Issue: "Module not found" errors
**Solution:** Install dependencies
```bash
pip install -e .
```

### Issue: Spark session issues
**Solution:** Make sure you have spark configured in `globals.py`
```python
from mimic_dataset.utils.globals import GlobalVariables as G
G.setup_spark()
```

### Issue: Vector search endpoint not found
**Solution:** The pipeline creates endpoints automatically on first run
```python
from mimic_dataset.gen_ai.rag_pipeline import create_vector_search_index
vsc = create_vector_search_index("mmc")
```

### Issue: Email not sending
**Solution:** For Gmail, use app-specific password (not regular login password)
1. Go to https://myaccount.google.com/apppasswords
2. Generate an App Password
3. Use that in `send_prescription_email()`

### Issue: Slow embedding generation
**Solution:** Reduce batch size or skip if already done
```python
execute_rag_pipeline(skip_embedding_generation=True)
```

## Best Practices

1. **Cache the index** - Don't recreate it every time
```python
index = artifacts['index']
# Reuse index multiple times
```

2. **Use conversational bot** for multi-turn interactions
```python
bot = MimicChatbot(index)
# Maintains context automatically
```

3. **Handle errors gracefully**
```python
try:
    insights = generate_patient_insights(...)
except Exception as e:
    print(f"Could not generate insights: {e}")
    # Fallback logic
```

4. **Use schema_name parameter** for different environments
```python
execute_rag_pipeline(schema_name="dev")  # Development
execute_rag_pipeline(schema_name="prod") # Production
```

5. **Review email previews** before sending
```python
success, result = send_prescription_email(...)
if not success and "<html>" in result:
    print("Email preview:", result)
    # Review before adding credentials
```

## Performance Notes

- **First run:** Full pipeline takes 10-30 minutes (embedding generation)
- **Subsequent runs:** Queries typically take 2-5 seconds
- **Batch processing:** Multiple patient lookups are I/O bound, not CPU bound

Enjoy using the MIMIC RAG Pipeline! 🚀

