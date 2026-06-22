"""
Bronze Layer - Raw Data Ingestion

Handles ingestion of raw MIMIC-III CSV files from Azure Data Lake
into Delta tables in the bronze schema.

Functions:
    - ingest(): Main entry point for bronze layer ingestion
"""

from mimic_dataset.bronze.ingest_data_to_bronze import ingest  # noqa: F401

__all__ = ["ingest"]

