"""
MIMIC Dataset ETL Pipeline

A comprehensive ETL pipeline for MIMIC-III clinical dataset processing
with data quality assurance and AI-powered insights using RAG.

Modules:
    - bronze: Raw data ingestion layer
    - silver: Data transformation and standardization layer
    - gold: Analytics and aggregation layer
    - data_quality: Data quality validation framework
    - gen_ai: Gen-AI and RAG pipeline integration
    - utils: Shared utilities (config, globals, etc.)

Main Entry Point:
    python -m mimic_dataset.main '{"STEP": "BRONZE_LOAD"}'
"""

__version__ = "0.1.2"
__author__ = "Anji"

from mimic_dataset.utils.globals import GlobalVariables  # noqa: F401
from mimic_dataset.utils.file import load_config  # noqa: F401

