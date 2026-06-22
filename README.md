# MIMIC Dataset - AI-Powered Clinical Intelligence System

A comprehensive **Medallion Architecture** ETL pipeline for the MIMIC-III hospital dataset with integrated Retrieval-Augmented Generation (RAG) chatbot for clinical insights, prescription recommendations, and automated email delivery.

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![Databricks](https://img.shields.io/badge/Databricks-Ready-brightgreen)](https://databricks.com/)
[![Status](https://img.shields.io/badge/status-Active-green)](https://github.com)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Data Flow](#data-flow)
- [Configuration](#configuration)
- [Usage](#usage)
- [Modules](#modules)
- [RAG Pipeline](#rag-pipeline)

---

## Overview

**MIMIC Dataset** is a production-ready data pipeline that transforms raw hospital patient data into actionable clinical intelligence using AI. The system:

- **Ingests** raw MIMIC-III data from cloud storage (Azure Data Lake)
- **Transforms** data through a medallion architecture (Bronze → Silver → Gold)
- **Validates** data quality at each layer
- **Enriches** data with AI-powered clinical insights
- **Generates** intelligent prescription recommendations
- **Delivers** formatted reports via email

### Key Features

✅ **Medallion Architecture** - Structured data transformation across 3 layers  
✅ **Data Quality Validation** - Comprehensive quality checks at Silver layer  
✅ **Vector Search** - Semantic similarity search using embeddings  
✅ **RAG Chatbot** - Multi-turn conversational AI with memory  
✅ **Email Reports** - Professional HTML prescription delivery  
✅ **Automated CI/CD** - GitHub Actions for build and Databricks deployment  
✅ **Configuration Management** - YAML-based environment configs  
✅ **Type-Safe** - Full type hints and docstrings  

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    MIMIC Dataset Pipeline                        │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                      LANDING LAYER                               │
│  (Azure Data Lake: abfss://trainingmimicds@.../landing)         │
│  Raw CSV files: ADMISSIONS, PATIENTS, ICUSTAYS, LABEVENTS, etc  │
└─────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼ INGEST
┌──────────────────────────────────────────────────────────────────┐
│                      BRONZE LAYER                                │
│              (Raw Ingestion - Delta Tables)                      │
│  admissions_raw, patients_raw, icustays_raw, labevents_raw, ... │
└─────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼ TRANSFORM
┌──────────────────────────────────────────────────────────────────┐
│                      SILVER LAYER                                │
│        (Cleaned & Standardized - Delta Tables)                   │
│  dim_patients, fact_admissions, fact_icustays,                  │
│  fact_admissions_enriched                                        │
│                          │                                       │
│          ┌───────────────▼────────────────┐                      │
│          │   QUALITY CHECKS               │                      │
│          │  - Null/Duplicate Detection    │                      │
│          │  - Data Type Validation        │                      │
│          │  - Range & Business Logic      │                      │
│          └───────────────┬────────────────┘                      │
└─────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼ AGGREGATE
┌──────────────────────────────────────────────────────────────────┐
│                      GOLD LAYER                                  │
│         (Analytics-Ready - Delta Tables)                         │
│  icu_visits_per_patient, readmissions_by_insurance,             │
│  icu_visit_distribution, icu_admissions_trend,                  │
│  LLM documents, chunks, embeddings, vector index                │
└─────────────────────────┬──────────────────────────────────────┘
                          │
                ┌─────────┴──────────┐
                │                    │
                ▼ ANALYTICS         ▼ GEN-AI
            ┌──────────────┐    ┌──────────────────────┐
            │  BI/Reports  │    │   RAG PIPELINE       │
            │  Dashboards  │    │                      │
            └──────────────┘    │ 1. Doc Creation      │
                                │ 2. Text Chunking     │
                                │ 3. Embeddings        │
                                │ 4. Vector Index      │
                                │ 5. RAG Chatbot       │
                                │ 6. Prescriptions     │
                                │ 7. Email Delivery    │
                                └──────────────────────┘
```

### Technology Stack

| Component | Technology |
|-----------|-----------|
| **Data Lake** | Azure Data Lake Storage (ADLS) |
| **Data Warehouse** | Databricks Lakehouse |
| **Data Format** | Delta Lake |
| **Orchestration** | Python + PySpark |
| **LLM** | Meta Llama 3.3 70B Instruct |
| **Embeddings** | Databricks BGE-Large-EN (1024-dim) |
| **Vector Search** | Databricks Vector Search |
| **Chunking** | LangChain RecursiveCharacterTextSplitter |
| **Configuration** | YAML |
| **CI/CD** | GitHub Actions |
| **Deployment** | Databricks Workspace + Volumes |

---

## Installation

### Prerequisites

- Python 3.9+
- Databricks workspace with Unity Catalog enabled
- Azure storage account (for landing zone)

### Setup Steps

```bash
# 1. Clone repository
git clone https://github.com/yourusername/mimic-dataset.git
cd mimic-dataset

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install package
pip install -e .

# 4. Configure Databricks
databricks configure --token

# 5. Verify installation
python -c "from mimic_dataset.main import main; print('✅ Installation successful')"
```

---

## Project Structure

```
mimic-dataset/
├── src/mimic_dataset/
│   ├── main.py                              # ETL orchestrator
│   ├── bronze/
│   │   └── ingest_data_to_bronze.py         # Landing → Bronze
│   ├── silver/
│   │   └── transform_and_load_to_silver.py  # Bronze → Silver
│   ├── gold/
│   │   └── load_to_gold.py                  # Silver → Gold
│   ├── data_quality/
│   │   └── quality_check.py                 # Data validation
│   ├── gen_ai/
│   │   └── rag_pipeline.py                  # RAG chatbot pipeline
│   ├── utils/
│   │   ├── globals.py                       # Spark session
│   │   └── file.py                          # Config loading
│   └── resources/configs/dev/
│       └── config.yaml                      # Configuration
├── .github/workflows/
│   └── ci_cd.yml                            # GitHub Actions
└── pyproject.toml                           # Dependencies
```

---

## Data Flow

### 1️⃣ Landing → Bronze Layer (Ingestion)

**Source**: Azure Data Lake (ADLS)

**Files Processed**:
- ADMISSIONS.csv - Patient admissions
- PATIENTS.csv - Demographics
- ICUSTAYS.csv - ICU stays
- LABEVENTS.csv - Laboratory results
- +20 more MIMIC-III tables

**Process** (`bronze/ingest_data_to_bronze.py`):
```
Landing CSV Files
    ↓
PySpark Read (with schema inference)
    ↓
Delta Format Conversion
    ↓
Bronze Schema:
  - Database: training_catalog.bronze
  - Tables: *_raw (25 tables)
```

---

### 2️⃣ Bronze → Silver Layer (Transformation)

**Transformation** (`silver/transform_and_load_to_silver.py`):

**Dimension Tables**:
```
PATIENTS_raw
    ↓ (Select, Rename, Clean)
    → dim_patients
```

**Fact Tables**:
```
ADMISSIONS_raw + PATIENTS_raw
    ↓ (Join, Enrich, Calculate)
    → fact_admissions_enriched
       (subject_id, hadm_id, diagnosis, age, ...)

ICUSTAYS_raw
    ↓ (Transform)
    → fact_icustays
```

**Process**:
1. Filter invalid records
2. Calculate derived fields (age from DOB)
3. Standardize data types
4. Handle null values
5. Remove duplicates

**Output**:
- Database: `training_catalog.silver`
- Tables: `dim_patients`, `fact_admissions`, `fact_icustays`, `fact_admissions_enriched`

---

### 3️⃣ Data Quality Checks (Silver Layer)

**Validation** (`data_quality/quality_check.py`):

| Check | Description |
|-------|-------------|
| **Completeness** | NULL detection in key columns |
| **Uniqueness** | Duplicate record identification |
| **Validity** | Data type compliance |
| **Consistency** | Foreign key relationships |
| **Range Checks** | Business logic validation |

**Output**: HTML report with quality metrics

---

### 4️⃣ Silver → Gold Layer (Aggregation)

**Aggregation** (`gold/load_to_gold.py`):

```
Silver Tables
    ↓
Aggregate & Summarize
    ↓
├─ icu_visits_per_patient (Ranked by visit count)
├─ readmissions_by_insurance (Readmission rates)
├─ icu_visit_distribution (Historical trends)
└─ icu_admissions_trend (Time-series)
```

**Output**:
- Database: `training_catalog.gold`
- Pre-aggregated tables for analytics

---

### 5️⃣ Gold Layer → RAG Pipeline (Gen-AI)

**RAG Pipeline** (`gen_ai/rag_pipeline.py`):

```
Phase 1: DOCUMENT CREATION
├─ Read Silver Tables
├─ Concatenate: subject_id + diagnosis + admission_type
└─ Output: gold.llm_documents

Phase 2: TEXT CHUNKING
├─ RecursiveCharacterTextSplitter
├─ Chunk Size: 200 chars
├─ Overlap: 20 chars
└─ Output: gold.llm_chunks (~5,000+)

Phase 3: EMBEDDINGS
├─ BGE-Large-EN Model
├─ 1024-dimensional vectors
├─ Batch Processing (20 chunks/batch)
└─ Output: gold.llm_embeddings

Phase 4: VECTOR INDEX
├─ Databricks Vector Search
├─ Delta Sync (auto-update)
├─ Endpoint: mimic_vector_endpoint
└─ Index: mmc.gold.mimic_llm_index

Phase 5: RAG CHATBOT
├─ User Question
│  ↓ Embed
├─ Vector Search (Top-5)
│  ↓ Context Retrieval
├─ LLM Prompt
│  ↓ Generate
└─ AI-Powered Answer
```

---

## Configuration

### Config File

**Location**: `src/mimic_dataset/resources/configs/dev/config.yaml`

```yaml
schema_name: 'training_catalog'
raw_data_location: 'abfss://trainingmimicds@trainingstrgnew.dfs.core.windows.net/landing'
```

### Environment Variables

```bash
export DATABRICKS_HOST=https://your-workspace.databricks.com
export DATABRICKS_TOKEN=dapi...
```

---

## Usage

### Execute ETL Steps

```bash
# Bronze ingest
python -m mimic_dataset.main '{"STEP": "BRONZE_LOAD"}'

# Silver transformation
python -m mimic_dataset.main '{"STEP": "SILVER_TRANSFORM_LOAD"}'

# Quality checks
python -m mimic_dataset.main '{"STEP": "QUALITY_CHECK"}'

# Gold aggregation
python -m mimic_dataset.main '{"STEP": "GOLD_TRANSFORM_LOAD"}'

# RAG pipeline
python -m mimic_dataset.main '{"STEP": "RAG_PIPELINE"}'
```

### Use RAG Chatbot

```python
from mimic_dataset.gen_ai.rag_pipeline import execute_rag_pipeline, ask_mimic_bot

# Initialize
artifacts = execute_rag_pipeline()
index = artifacts['index']

# Ask question
answer = ask_mimic_bot("What diagnoses lead to emergency admission?", index)
print(answer)
```

### Get Patient Insights

```python
from mimic_dataset.gen_ai.rag_pipeline import (
    execute_rag_pipeline,
    get_patient_summary,
    generate_patient_insights,
    generate_prescription
)

artifacts = execute_rag_pipeline()
index = artifacts['index']

# Patient lookup
admissions_df, icu_df = get_patient_summary(subject_id=10029)

# Clinical insights
insights = generate_patient_insights(admissions_df, icu_df, 10029, index)

# Prescription recommendations
prescription = generate_prescription(admissions_df, icu_df, 10029, index)
```

### Send Email Report

```python
from mimic_dataset.gen_ai.rag_pipeline import send_prescription_email

success, result = send_prescription_email(
    recipient_email="doctor@hospital.com",
    subject_id=10029,
    admissions_df=admissions_df,
    icu_df=icu_df,
    prescription_text=prescription,
    doctor_name="Smith",
    sender_email="your@gmail.com",
    sender_password="app_password"
)
```

---

## Modules

| Module | Purpose |
|--------|---------|
| `bronze/ingest_data_to_bronze.py` | Ingest landing CSV to bronze tables |
| `silver/transform_and_load_to_silver.py` | Transform bronze to silver (cleaned) |
| `gold/load_to_gold.py` | Aggregate silver to gold analytics tables |
| `data_quality/quality_check.py` | Validate data quality at silver layer |
| `gen_ai/rag_pipeline.py` | RAG pipeline: embeddings, search, chatbot |
| `utils/globals.py` | Global Spark session management |
| `utils/file.py` | YAML config loading |

---

## RAG Pipeline

### How It Works

1. **Document Creation** - Extract clinical narratives from Silver
2. **Chunking** - Split into semantically meaningful pieces
3. **Embeddings** - Convert to vector representations
4. **Vector Index** - Create searchable index
5. **Query** - User question embedded and searched
6. **Context** - Top-5 similar chunks retrieved
7. **Generation** - LLM generates answer with context
8. **Memory** - Multi-turn conversations tracked

### Use Cases

| Use Case | Function | Output |
|----------|----------|--------|
| Q&A | `ask_mimic_bot()` | Text answer |
| Structured | `ask_mimic_bot_table()` | JSON DataFrame |
| Conversational | `MimicChatbot` | Multi-turn chat |
| Patient Lookup | `get_patient_summary()` | Demographics |
| Clinical Insights | `generate_patient_insights()` | Risk factors |
| Prescriptions | `generate_prescription()` | Drug recommendations |
| Email Reports | `send_prescription_email()` | HTML email |

### Performance

| Operation | Time |
|-----------|------|
| First run (with embeddings) | 20-40 min |
| Subsequent runs | ~2 min |
| Single question | 2-3 sec |
| Patient lookup | 1-2 sec |

---

## Documentation

Additional documentation files:

- **RAG_PIPELINE_DOCUMENTATION.md** - Technical API reference
- **RAG_PIPELINE_QUICK_START.md** - 8 working code examples
- **EXECUTION_GUIDE.md** - Step-by-step execution
- **RAG_DOCUMENTATION_INDEX.md** - Documentation index

---

## CI/CD

### GitHub Actions

**Trigger**: Push to `main` branch

**Pipeline**:
1. Build wheel package
2. Upload to Databricks Volume
3. Deploy to workspace

**Secrets Required**:
- `DATABRICKS_HOST`
- `DATABRICKS_TOKEN`

---

## Status

- ✅ Bronze Layer
- ✅ Silver Layer
- ✅ Data Quality Checks
- ✅ Gold Layer
- ✅ RAG Pipeline
- ✅ CI/CD
- 🔄 Production Deployment

---

## Support

For issues or questions:
- Check documentation files
- Review quick-start guide
- Enable debug logging

---

**Version**: 0.1.2  
**Last Updated**: May 10, 2026  
**Status**: Active Development

