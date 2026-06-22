"""
Utilities Module - Shared Utilities and Helpers

Provides common utilities for the ETL pipeline:
- Configuration management
- Global variables and Spark session management
- File operations
"""

from mimic_dataset.utils.file import load_config  # noqa: F401
from mimic_dataset.utils.globals import GlobalVariables  # noqa: F401

__all__ = ["load_config", "GlobalVariables"]

