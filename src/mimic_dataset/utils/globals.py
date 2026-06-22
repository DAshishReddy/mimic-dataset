"""
Global Variables and Spark Session Management

Provides centralized Spark session initialization and management
for use across all ETL pipeline modules.
"""

import logging
from pyspark.sql import SparkSession

logger = logging.getLogger(__name__)


class GlobalVariables:
    """
    Singleton class for managing global Spark session and resources.

    Attributes:
        spark (SparkSession): Shared Spark session instance
    """
    spark: SparkSession = None

    @classmethod
    def setup_spark(cls) -> SparkSession:
        """
        Initialize or retrieve the shared Spark session.

        Creates a new SparkSession if one doesn't exist, or returns
        the existing instance if already initialized.

        Returns:
            SparkSession: The initialized Spark session

        Raises:
            Exception: If Spark initialization fails
        """
        if cls.spark is None:
            try:
                logger.info("Initializing new Spark session...")
                cls.spark = SparkSession.builder \
                    .appName("mimic-dataset-etl") \
                    .getOrCreate()
                logger.info("✓ Spark session initialized successfully")
                logger.debug(f"Spark version: {cls.spark.version}")
                logger.debug(f"Spark catalog: {cls.spark.catalog.currentDatabase()}")
            except Exception as e:
                logger.error(f"Failed to initialize Spark session: {e}", exc_info=True)
                raise
        else:
            logger.debug("Using existing Spark session")

        return cls.spark

    @classmethod
    def get_spark(cls) -> SparkSession:
        """
        Get the current Spark session.

        Returns:
            SparkSession: The current Spark session

        Raises:
            RuntimeError: If Spark session has not been initialized
        """
        if cls.spark is None:
            raise RuntimeError("Spark session not initialized. Call setup_spark() first.")
        return cls.spark
