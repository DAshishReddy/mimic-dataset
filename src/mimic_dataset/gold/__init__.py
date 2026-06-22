"""
Gold Layer - Analytics and Aggregation

Creates aggregate analytics tables from silver data for reporting
and downstream analytics (icu_visits_per_patient, readmissions, etc.).

Functions:
    - execute_gold(): Main entry point for gold layer aggregation
"""

from mimic_dataset.gold.load_to_gold import execute_gold  # noqa: F401

__all__ = ["execute_gold"]

