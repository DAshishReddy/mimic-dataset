# RAG Pipeline Module Documentation

## Overview

The `rag_pipeline.py` module implements a **Retrieval-Augmented Generation (RAG)** pipeline for generating AI-powered clinical insights and prescription recommendations using the MIMIC-III hospital dataset on Databricks.

## Architecture

The pipeline consists of 6 phases:

### Phase 1: Data Foundation
**Function:** `create_llm_documents(schema_name: str = "mmc")`

Loads patient admissions from the MIMIC silver layer and creates unified text documents by concatenating clinical fields (subject_id, admission_type, diagnosis).

**Output Table:** `{schema_name}.gold.llm_documents`

### Phase 2: Intelligent Chunking
**Function:** `chunk_documents(schema_name: str = "mmc", chunk_size: int = 200, chunk_overlap: int = 20)`

Uses LangChain's `RecursiveCharacterTextSplitter` to break documents into manageable chunks with configurable overlap to preserve context at boundaries.

**Output Table:** `{schema_name}.gold.llm_chunks`

**Parameters:**
- `chunk_size` (default: 200): Size of each chunk in characters
- `chunk_overlap` (default: 20): Overlap between chunks to maintain context

### Phase 3: Vector Embeddings
**Function:** `generate_embeddings(schema_name: str = "mmc", model: str = "databricks-bge-large-en", batch_size: int = 20, rate_limit_sleep: float = 1.0)`

Converts text chunks into 1024-dimensional vectors using Databricks' BGE-Large-EN embedding model. Processes in batches with rate-limiting to avoid API throttling.

**Output Table:** `{schema_name}.gold.llm_embeddings`

**Parameters:**
- `batch_size` (default: 20): Number of chunks to embed in one API call
- `rate_limit_sleep` (default: 1.0): Sleep duration between batches

### Phase 4: Vector Search Index
**Function:** `create_vector_search_index(schema_name: str = "mmc", endpoint_name: str = "mimic_vector_endpoint", index_name: str = None)`

Creates a Databricks Vector Search index with Delta Sync that automatically stays in sync with the embeddings table.

**Returns:** `VectorSearchClient` object

**Index Name:** `{schema_name}.gold.mimic_llm_index`

### Phase 5: RAG Chatbot Variations

#### 1. Simple Bot
**Function:** `ask_mimic_bot(question: str, index: Any, model: str = "databricks-meta-llama-3-3-70b-instruct")`

Simple RAG function: embeds question → retrieves context → generates answer

**Returns:** str (LLM response)

#### 2. Table Bot
**Function:** `ask_mimic_bot_table(question: str, index: Any, model: str = "databricks-meta-llama-3-3-70b-instruct")`

Enhanced RAG with JSON-formatted responses for tabular data display

**Returns:** pd.DataFrame (structured results)

#### 3. Conversational Bot
**Class:** `MimicChatbot`

Full conversational chatbot with memory that maintains conversation history:

```python
bot = MimicChatbot(index=index_object)
response = bot.ask("What diagnoses lead to emergency admission?")
follow_up = bot.ask("Tell me more about those cases")  # Maintains context
bot.reset()  # Clear history
```

**Methods:**
- `ask(question: str)`: Ask a question with memory
- `reset()`: Clear conversation history

### Phase 6: Patient Lookup & Clinical Insights

#### Get Patient Summary
**Function:** `get_patient_summary(subject_id: int, schema_name: str = "mmc")`

Fetches patient admissions and ICU stays from MIMIC silver tables

**Returns:** Tuple[pd.DataFrame, pd.DataFrame] (admissions_df, icu_df)

#### Generate Patient Insights
**Function:** `generate_patient_insights(admissions_df: pd.DataFrame, icu_df: pd.DataFrame, subject_id: int, index: Any)`

Uses RAG to analyze patient diagnoses, ICU history, and LOS to provide:
- Clinical summary
- Key risk factors
- Recommended areas for monitoring

**Returns:** str (clinical insights text)

#### Generate Prescription
**Function:** `generate_prescription(admissions_df: pd.DataFrame, icu_df: pd.DataFrame, subject_id: int, index: Any)`

Uses RAG to recommend:
- Primary medications (name, dosage, frequency, route)
- Supportive medications
- Monitoring instructions
- Special precautions

**Returns:** str (prescription recommendations)

### Phase 6: Email Delivery

#### Build Email HTML
**Function:** `build_prescription_email_html(subject_id: int, admissions_df: pd.DataFrame, icu_df: pd.DataFrame, prescription_text: str, doctor_name: str)`

Generates professional HTML email body with patient information and prescription details

**Returns:** str (HTML formatted email body)

#### Send Email
**Function:** `send_prescription_email(recipient_email: str, subject_id: int, admissions_df: pd.DataFrame, icu_df: pd.DataFrame, prescription_text: str, doctor_name: str, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587, sender_email: str = None, sender_password: str = None)`

Sends or previews prescription email

**Returns:** Tuple[bool, str] (success status, message or HTML preview)

## Main Execution Function

**Function:** `execute_rag_pipeline(schema_name: str = "mmc", skip_embedding_generation: bool = False)`

Orchestrates the entire RAG pipeline end-to-end:
1. Creates documents from MIMIC silver tables
2. Chunks documents into manageable pieces
3. Generates embeddings (or skips if already done)
4. Creates vector search index

**Returns:** Dict with pipeline artifacts:
```python
{
    'vsc': VectorSearchClient,
    'index': Vector search index object,
    'schema_name': str
}
```

**Example Usage:**
```python
from mimic_dataset.gen_ai.rag_pipeline import execute_rag_pipeline

artifacts = execute_rag_pipeline()
index = artifacts['index']
```

## Integration with main.py

The RAG pipeline is integrated into the main ETL orchestrator. To execute from `main.py`:

```python
python -m mimic_dataset.main '{"STEP": "RAG_PIPELINE"}'
```

## Helper Functions

### _retrieve_rag_context
Internal function that embeds a question and retrieves similar chunks from the vector index.

### _build_patient_context
Internal function that extracts diagnoses, ICU units, and average length of stay from patient dataframes.

## Dependencies

Required packages:
- `databricks-genai-inference`: For embeddings and LLM access
- `databricks-vectorsearch`: For vector index management
- `langchain-text-splitters`: For document chunking
- `pandas`: For dataframe manipulation
- `pyspark`: For distributed data processing

Add to `requirements.txt`:
```txt
databricks-genai-inference>=0.1.0
databricks-vectorsearch>=0.1.0
langchain-text-splitters>=0.1.0
pandas>=1.0.0
pyspark>=3.0.0
```

## Configuration

The pipeline uses the default Databricks workspace configuration through `GlobalVariables` for Spark access.

Default schema name: `mmc` (can be customized per function call)

## Usage Examples

### Example 1: Run Full Pipeline
```python
from mimic_dataset.gen_ai.rag_pipeline import execute_rag_pipeline

# Run full pipeline
artifacts = execute_rag_pipeline(schema_name="mmc")
index = artifacts['index']
```

### Example 2: Ask Questions
```python
from mimic_dataset.gen_ai.rag_pipeline import ask_mimic_bot

answer = ask_mimic_bot(
    question="What are common emergency diagnoses?",
    index=index
)
print(answer)
```

### Example 3: Patient Lookup and Prescription
```python
from mimic_dataset.gen_ai.rag_pipeline import (
    get_patient_summary,
    generate_prescription,
    send_prescription_email
)

admissions_df, icu_df = get_patient_summary(subject_id=10029)

prescription = generate_prescription(
    admissions_df=admissions_df,
    icu_df=icu_df,
    subject_id=10029,
    index=index
)

success, result = send_prescription_email(
    recipient_email="doctor@hospital.com",
    subject_id=10029,
    admissions_df=admissions_df,
    icu_df=icu_df,
    prescription_text=prescription,
    doctor_name="Smith",
    sender_email="sender@gmail.com",
    sender_password="app_password"
)
```

### Example 4: Conversational Bot
```python
from mimic_dataset.gen_ai.rag_pipeline import MimicChatbot

bot = MimicChatbot(index=index)

q1 = bot.ask("What diagnoses require ICU admission?")
print(q1)

q2 = bot.ask("What medications are typically prescribed?")
print(q2)

q3 = bot.ask("Tell me more about the first one")  # Maintains context
print(q3)
```

## Notes

- All functions designed to be Databricks-aware using SparkSession
- Email functionality returns HTML preview if SMTP credentials not provided
- For Gmail: Use App Password (not regular password)
- Embeddings generation is compute-intensive; use `skip_embedding_generation=True` if already completed
- RAG context limited to top-5 most similar chunks by default (configurable)
- All recommendations are for educational/demonstration purposes with synthetic MIMIC data

## Error Handling

All functions include proper error handling:
- Vector search endpoint/index: Checks for existing resources before creation
- Email sending: Returns error message on failure
- RAG retrieval: Validates presence of index and embeddings

## Performance Considerations

- Embedding generation: Batch size of 20 with 1-second rate limiting
- Vector search: Returns top-5 results by default
- Conversational memory: Limited to last 6 messages to manage context window
- Chunk overlap: 20 characters to preserve context at boundaries

