"""
Data Quality Module - Data Validation Framework

Performs comprehensive data quality checks including completeness,
uniqueness, validity, and cross-table consistency validation.
Generates HTML quality reports and metadata tracking.

Functions:
    - execute_quality_check(): Main entry point for data quality validation
"""

from mimic_dataset.data_quality.quality_check import execute_quality_check  # noqa: F401

__all__ = ["execute_quality_check"]

