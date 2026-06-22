"""
Silver Layer - Data Transformation and Standardization

Transforms and cleans raw bronze data into standardized silver tables.
Creates dimension and fact tables with calculated fields (age, LOS, etc.).

Functions:
    - execute_silver(): Main entry point for silver layer transformation
"""

from mimic_dataset.silver.transform_and_load_to_silver import execute_silver  # noqa: F401

__all__ = ["execute_silver"]

