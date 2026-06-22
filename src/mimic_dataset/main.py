"""
MIMIC Dataset ETL Pipeline Orchestrator

Main entry point for executing MIMIC dataset ETL pipeline steps:
- BRONZE_LOAD: Ingest raw MIMIC data into Bronze layer
- SILVER_TRANSFORM_LOAD: Transform and load data to Silver layer
- QUALITY_CHECK: Perform data quality validation
- GOLD_TRANSFORM_LOAD: Aggregate and load data to Gold layer
- RAG_PIPELINE: Initialize RAG pipeline for Gen-AI capabilities

Usage:
    python -m mimic_dataset.main --STEP BRONZE_LOAD
    python -m mimic_dataset.main --STEP SILVER_TRANSFORM_LOAD
    python -m mimic_dataset.main --STEP QUALITY_CHECK
    python -m mimic_dataset.main --STEP GOLD_TRANSFORM_LOAD
    python -m mimic_dataset.main --STEP RAG_PIPELINE

    From Databricks Jobs:
    ["--STEP","BRONZE_LOAD"]
    ["--STEP","SILVER_TRANSFORM_LOAD"]
    ["--STEP","QUALITY_CHECK"]
    ["--STEP","GOLD_TRANSFORM_LOAD"]
    ["--STEP","RAG_PIPELINE"]
"""

import sys
import argparse
import logging
from typing import Optional

from mimic_dataset.bronze.ingest_data_to_bronze import ingest
from mimic_dataset.utils.globals import GlobalVariables as G
from mimic_dataset.utils.file import load_config
from mimic_dataset.silver.transform_and_load_to_silver import execute_silver as silver
from mimic_dataset.gold.load_to_gold import execute_gold as gold
from mimic_dataset.data_quality.quality_check import execute_quality_check as quality_check
from mimic_dataset.gen_ai.rag_pipeline import execute_rag_pipeline as rag_pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define valid pipeline steps
VALID_STEPS = {
    "BRONZE_LOAD": ingest,
    "SILVER_TRANSFORM_LOAD": silver,
    "QUALITY_CHECK": quality_check,
    "GOLD_TRANSFORM_LOAD": gold,
    "RAG_PIPELINE": rag_pipeline
}


def validate_parameters(step: str) -> str:
    """
    Validate STEP parameter.

    Args:
        step (str): STEP parameter value

    Returns:
        str: Validated STEP parameter

    Raises:
        ValueError: If STEP value is invalid
    """

    if step not in VALID_STEPS:
        raise ValueError(
            f"Invalid STEP: '{step}'. "
            f"Valid steps are: {', '.join(VALID_STEPS.keys())}"
        )

    return step


def main(step: Optional[str] = None) -> None:
    """
    Orchestrate MIMIC ETL pipeline execution.

    Args:
        step (Optional[str]): STEP parameter value.
                             If not provided, parses from command-line arguments.

    Raises:
        SystemExit: On validation errors or execution failures
    """
    try:
        logger.info("=" * 80)
        logger.info("🚀 MIMIC DATASET ETL PIPELINE ORCHESTRATOR")
        logger.info("=" * 80)

        # Initialize Spark session
        logger.info("📌 Initializing Spark session...")
        G.setup_spark()
        logger.info("✓ Spark session initialized")

        # Load and display configuration
        logger.info("📌 Loading configuration...")
        config, config_json = load_config()
        logger.info(f"✓ Schema: {config.get('schema_name')}")
        logger.info(f"✓ Data location: {config.get('raw_data_location')}")

        # Parse command-line arguments
        logger.info("📌 Parsing execution parameters...")
        parser = argparse.ArgumentParser(
            description="MIMIC Dataset ETL Pipeline Orchestrator",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python -m mimic_dataset.main --STEP BRONZE_LOAD
  python -m mimic_dataset.main --STEP SILVER_TRANSFORM_LOAD
  python -m mimic_dataset.main --STEP QUALITY_CHECK
  python -m mimic_dataset.main --STEP GOLD_TRANSFORM_LOAD
  python -m mimic_dataset.main --STEP RAG_PIPELINE
            """
        )
        parser.add_argument(
            "--STEP",
            type=str,
            required=step is None,
            help="Pipeline step to execute (BRONZE_LOAD, SILVER_TRANSFORM_LOAD, QUALITY_CHECK, GOLD_TRANSFORM_LOAD, RAG_PIPELINE)"
        )

        # Parse arguments if step not provided
        if step is None:
            args = parser.parse_args()
            step = args.STEP

        logger.info(f"✓ Parameters received: STEP={step}")

        # Validate and extract step
        validated_step = validate_parameters(step)
        logger.info(f"📌 Executing step: {validated_step}")

        # Execute the requested step
        logger.info("📌 Starting pipeline step execution...")
        VALID_STEPS[validated_step]()

        logger.info("=" * 80)
        logger.info("✅ Job Completed Successfully")
        logger.info("=" * 80)

    except ValueError as e:
        logger.error(f"❌ Invalid parameter value: {e}")
        sys.exit(1)

    except SystemExit as e:
        # argparse calls sys.exit on error, re-raise it
        if e.code != 0:
            logger.error(f"❌ Argument parsing failed")
        raise

    except Exception as e:
        logger.error(f"❌ Pipeline execution failed: {type(e).__name__}: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
