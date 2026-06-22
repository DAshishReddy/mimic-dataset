from mimic_dataset.utils.globals import GlobalVariables as G
from mimic_dataset.utils.file import load_config
from pyspark.sql.functions import (
    col, count, sum as spark_sum, year, month, floor, datediff,
    round as spark_round, when, current_timestamp, current_date,
    lit
)
from pyspark.sql.types import IntegerType
from datetime import datetime
import uuid
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def execute_quality_check():
    try:
        logger.info("=" * 80)
        logger.info("🔍 DATA QUALITY CHECKS - STARTING")
        logger.info("=" * 80)

        # Load configuration
        logger.info("Loading configuration...")
        config, _ = load_config()
        schema_name = config['schema_name']
        spark = G.spark
        logger.info(f"✓ Configuration loaded: schema_name={schema_name}")

        # Initialize run metadata
        run_id = str(uuid.uuid4())
        run_start_time = datetime.now()
        logger.info(f"✓ Run ID generated: {run_id}")
        logger.info(f"✓ Run start time: {run_start_time}")

        # Create data_quality schema
        logger.info(f"Creating data_quality schema in {schema_name}...")
        spark.sql(f"CREATE SCHEMA IF NOT EXISTS {schema_name}.data_quality")
        logger.info(f"✓ Data quality schema created/verified")

        # Create tables
        logger.info("Creating data quality tables...")
        _create_data_quality_tables(spark, schema_name)
        logger.info("✓ All data quality tables created/verified")

        # Initialize counters
        quality_checks = []
        passed_checks = 0
        warning_checks = 0
        failed_checks = 0
        total_issues = 0

        logger.info("\n" + "=" * 80)
        logger.info("📋 SECTION 1: ICU STAYS DATA QUALITY CHECKS")
        logger.info("=" * 80)

        # Load tables for reuse
        icu_stays = spark.table(f"{schema_name}.silver.fact_icustays")
        patients = spark.table(f"{schema_name}.silver.dim_patients")
        admissions = spark.table(f"{schema_name}.silver.fact_admissions")

        # Check 1: NULL hadm_id
        logger.info("Executing Check 1: NULL hadm_id in fact_icustays")
        df_check1 = icu_stays.filter(col("hadm_id").isNull()).count()
        status1 = "PASS" if df_check1 == 0 else "WARN" if df_check1 < 100 else "FAIL"
        quality_checks.append({"check_id": 1, "check_name": "null_hadm_id", "check_category": "ICU_STAYS", "table_name": f"{schema_name}.silver.fact_icustays", "check_description": "Check for NULL values in hadm_id column", "issue_count": df_check1, "threshold_value": None, "check_status": status1})
        passed_checks += 1 if status1 == "PASS" else 0
        warning_checks += 1 if status1 == "WARN" else 0
        failed_checks += 1 if status1 == "FAIL" else 0
        total_issues += df_check1
        logger.info(f"✓ Check 1: Issue Count={df_check1}, Status={status1}")

        # Check 2: NULL outtime
        logger.info("Executing Check 2: NULL outtime in fact_icustays")
        df_check2 = icu_stays.filter(col("outtime").isNull()).count()
        status2 = "PASS" if df_check2 == 0 else "WARN" if df_check2 < 100 else "FAIL"
        quality_checks.append({"check_id": 2, "check_name": "null_outtime", "check_category": "ICU_STAYS", "table_name": f"{schema_name}.silver.fact_icustays", "check_description": "Check for NULL values in outtime column", "issue_count": df_check2, "threshold_value": None, "check_status": status2})
        passed_checks += 1 if status2 == "PASS" else 0
        warning_checks += 1 if status2 == "WARN" else 0
        failed_checks += 1 if status2 == "FAIL" else 0
        total_issues += df_check2
        logger.info(f"✓ Check 2: Issue Count={df_check2}, Status={status2}")

        # Check 3: Extreme Length of Stay
        logger.info("Executing Check 3: Extreme Length of Stay (LOS > 365 days)")
        df_check3 = icu_stays.filter(col("los") > 365).count()
        status3 = "PASS" if df_check3 == 0 else "WARN" if df_check3 < 50 else "FAIL"
        quality_checks.append({"check_id": 3, "check_name": "extreme_los", "check_category": "ICU_STAYS", "table_name": f"{schema_name}.silver.fact_icustays", "check_description": "Check for LOS > 365 days", "issue_count": df_check3, "threshold_value": "365", "check_status": status3})
        passed_checks += 1 if status3 == "PASS" else 0
        warning_checks += 1 if status3 == "WARN" else 0
        failed_checks += 1 if status3 == "FAIL" else 0
        total_issues += df_check3
        logger.info(f"✓ Check 3: Issue Count={df_check3}, Status={status3}")

        # Check 4: Future intime
        logger.info("Executing Check 4: Future intime")
        df_check4 = icu_stays.filter(col("intime") > current_date()).count()
        status4 = "PASS" if df_check4 == 0 else "FAIL"
        quality_checks.append({"check_id": 4, "check_name": "future_intime", "check_category": "ICU_STAYS", "table_name": f"{schema_name}.silver.fact_icustays", "check_description": "Check for intime > current_date", "issue_count": df_check4, "threshold_value": None, "check_status": status4})
        passed_checks += 1 if status4 == "PASS" else 0
        failed_checks += 1 if status4 == "FAIL" else 0
        total_issues += df_check4
        logger.info(f"✓ Check 4: Issue Count={df_check4}, Status={status4}")

        # Check 5: Future outtime
        logger.info("Executing Check 5: Future outtime")
        df_check5 = icu_stays.filter(col("outtime") > current_date()).count()
        status5 = "PASS" if df_check5 == 0 else "FAIL"
        quality_checks.append({"check_id": 5, "check_name": "future_outtime", "check_category": "ICU_STAYS", "table_name": f"{schema_name}.silver.fact_icustays", "check_description": "Check for outtime > current_date", "issue_count": df_check5, "threshold_value": None, "check_status": status5})
        passed_checks += 1 if status5 == "PASS" else 0
        failed_checks += 1 if status5 == "FAIL" else 0
        total_issues += df_check5
        logger.info(f"✓ Check 5: Issue Count={df_check5}, Status={status5}")

        # Check 6: DOB after admission
        logger.info("Executing Check 6: DOB after admission")
        df_check6 = icu_stays.join(patients, "subject_id").filter(col("dob") > col("intime")).count()
        status6 = "PASS" if df_check6 == 0 else "FAIL"
        quality_checks.append({"check_id": 6, "check_name": "dob_after_admission", "check_category": "ICU_STAYS", "table_name": f"{schema_name}.silver.fact_icustays", "check_description": "Check for DOB > intime", "issue_count": df_check6, "threshold_value": None, "check_status": status6})
        passed_checks += 1 if status6 == "PASS" else 0
        failed_checks += 1 if status6 == "FAIL" else 0
        total_issues += df_check6
        logger.info(f"✓ Check 6: Issue Count={df_check6}, Status={status6}")

        # Check 7: Missing patient reference
        logger.info("Executing Check 7: Missing patient reference")
        patients_alias = patients.withColumnRenamed("subject_id", "patient_subject_id").withColumnRenamed("dob", "patient_dob")
        df_check7 = icu_stays.join(patients_alias, icu_stays["subject_id"] == patients_alias["patient_subject_id"], "left").filter(col("patient_dob").isNull()).count()
        status7 = "PASS" if df_check7 == 0 else "FAIL"
        quality_checks.append({"check_id": 7, "check_name": "missing_patient_reference", "check_category": "ICU_STAYS", "table_name": f"{schema_name}.silver.fact_icustays", "check_description": "Check for missing patient references", "issue_count": df_check7, "threshold_value": None, "check_status": status7})
        passed_checks += 1 if status7 == "PASS" else 0
        failed_checks += 1 if status7 == "FAIL" else 0
        total_issues += df_check7
        logger.info(f"✓ Check 7: Issue Count={df_check7}, Status={status7}")

        # Check 8: Missing admission reference
        logger.info("Executing Check 8: Missing admission reference")
        admissions_alias = admissions.withColumnRenamed("hadm_id", "admission_hadm_id").withColumnRenamed("admittime", "admission_admittime")
        df_check8 = icu_stays.join(admissions_alias, icu_stays["hadm_id"] == admissions_alias["admission_hadm_id"], "left").filter(col("admission_admittime").isNull()).count()
        status8 = "PASS" if df_check8 == 0 else "FAIL"
        quality_checks.append({"check_id": 8, "check_name": "missing_admission_reference", "check_category": "ICU_STAYS", "table_name": f"{schema_name}.silver.fact_icustays", "check_description": "Check for missing admission references", "issue_count": df_check8, "threshold_value": None, "check_status": status8})
        passed_checks += 1 if status8 == "PASS" else 0
        failed_checks += 1 if status8 == "FAIL" else 0
        total_issues += df_check8
        logger.info(f"✓ Check 8: Issue Count={df_check8}, Status={status8}")

        # SECTION 2: ADMISSIONS CHECKS
        logger.info("\n" + "=" * 80)
        logger.info("📋 SECTION 2: ADMISSIONS DATA QUALITY CHECKS")
        logger.info("=" * 80)

        # Check 9: Negative admission duration
        logger.info("Executing Check 9: Negative admission duration")
        df_check9 = admissions.filter(col("admittime") > col("dischtime")).count()
        status9 = "PASS" if df_check9 == 0 else "FAIL"
        quality_checks.append({"check_id": 9, "check_name": "negative_admission_duration", "check_category": "ADMISSIONS", "table_name": f"{schema_name}.silver.fact_admissions", "check_description": "Check for admittime > dischtime", "issue_count": df_check9, "threshold_value": None, "check_status": status9})
        passed_checks += 1 if status9 == "PASS" else 0
        failed_checks += 1 if status9 == "FAIL" else 0
        total_issues += df_check9
        logger.info(f"✓ Check 9: Issue Count={df_check9}, Status={status9}")

        # SECTION 3: PATIENTS CHECKS
        logger.info("\n" + "=" * 80)
        logger.info("📋 SECTION 3: PATIENTS DATA QUALITY CHECKS")
        logger.info("=" * 80)

        # Check 10: Invalid gender
        logger.info("Executing Check 10: Invalid gender")
        df_check10 = patients.filter(~col("gender").isin(['M', 'F'])).count()
        status10 = "PASS" if df_check10 == 0 else "WARN" if df_check10 < 10 else "FAIL"
        quality_checks.append({"check_id": 10, "check_name": "invalid_gender", "check_category": "PATIENTS", "table_name": f"{schema_name}.silver.dim_patients", "check_description": "Check for invalid gender values", "issue_count": df_check10, "threshold_value": "M,F", "check_status": status10})
        passed_checks += 1 if status10 == "PASS" else 0
        warning_checks += 1 if status10 == "WARN" else 0
        failed_checks += 1 if status10 == "FAIL" else 0
        total_issues += df_check10
        logger.info(f"✓ Check 10: Issue Count={df_check10}, Status={status10}")

        # Check 11: Duplicate subject_id
        logger.info("Executing Check 11: Duplicate subject_id")
        df_check11 = patients.groupBy("subject_id").agg(count("*").alias("cnt")).filter(col("cnt") > 1).count()
        status11 = "PASS" if df_check11 == 0 else "FAIL"
        quality_checks.append({"check_id": 11, "check_name": "duplicate_subject_id", "check_category": "PATIENTS", "table_name": f"{schema_name}.silver.dim_patients", "check_description": "Check for duplicate subject_id values", "issue_count": df_check11, "threshold_value": None, "check_status": status11})
        passed_checks += 1 if status11 == "PASS" else 0
        failed_checks += 1 if status11 == "FAIL" else 0
        total_issues += df_check11
        logger.info(f"✓ Check 11: Issue Count={df_check11}, Status={status11}")

        # SECTION 4: DIAGNOSES CHECKS
        logger.info("\n" + "=" * 80)
        logger.info("📋 SECTION 4: DIAGNOSES DATA QUALITY CHECKS")
        logger.info("=" * 80)

        # Check 12: NULL icd9_code
        logger.info("Executing Check 12: NULL icd9_code")
        diagnoses = spark.table(f"{schema_name}.bronze.diagnoses_icd_raw")
        df_check12 = diagnoses.filter(col("icd9_code").isNull()).count()
        status12 = "PASS" if df_check12 == 0 else "FAIL"
        quality_checks.append({"check_id": 12, "check_name": "null_icd_code", "check_category": "DIAGNOSES", "table_name": f"{schema_name}.bronze.diagnoses_icd_raw", "check_description": "Check for NULL icd9_code values", "issue_count": df_check12, "threshold_value": None, "check_status": status12})
        passed_checks += 1 if status12 == "PASS" else 0
        failed_checks += 1 if status12 == "FAIL" else 0
        total_issues += df_check12
        logger.info(f"✓ Check 12: Issue Count={df_check12}, Status={status12}")

        # Write quality check results (enforce schema to avoid Delta merge conflicts)
        logger.info("\nWriting quality check results to table...")
        df_quality_checks = spark.createDataFrame(quality_checks)
        # Cast columns explicitly to match target table schema
        df_quality_checks = (df_quality_checks
                             .withColumn("check_id", col("check_id").cast("int"))
                             .withColumn("check_name", col("check_name").cast("string"))
                             .withColumn("check_category", col("check_category").cast("string"))
                             .withColumn("table_name", col("table_name").cast("string"))
                             .withColumn("check_description", col("check_description").cast("string"))
                             .withColumn("issue_count", col("issue_count").cast("long"))
                             .withColumn("threshold_value", col("threshold_value").cast("string"))
                             .withColumn("check_status", col("check_status").cast("string"))
                             .withColumn("execution_timestamp", current_timestamp())
                             .withColumn("execution_date", current_date()))
        df_quality_checks = df_quality_checks.select("check_id", "check_name", "check_category", "table_name", "check_description", "issue_count", "threshold_value", "check_status", "execution_timestamp", "execution_date")
        df_quality_checks.write.format("delta").mode("append").option("mergeSchema", "true").saveAsTable(f"{schema_name}.data_quality.quality_check_results")
        logger.info(f"✓ Wrote {len(quality_checks)} quality check results to table")

        # SECTION 5: ANALYTICS
        logger.info("\n" + "=" * 80)
        logger.info("📊 SECTION 5: ANALYTICS - ICU ADMISSIONS TRENDS")
        logger.info("=" * 80)

        icustays_raw = spark.table(f"{schema_name}.bronze.icustays_raw")
        logger.info("Computing ICU admissions trends...")
        df_analytics1 = icustays_raw.withColumn("admission_year", year(col("intime"))).groupBy("admission_year").agg(count("*").alias("icu_admissions")).orderBy("admission_year")
        df_analytics1_write = (df_analytics1
                               .withColumn("month", lit(None).cast(IntegerType()))
                               .withColumn("admission_year", col("admission_year").cast("int"))
                               .withColumn("icu_admissions", col("icu_admissions").cast("long"))
                               .withColumn("execution_timestamp", current_timestamp())
                               .withColumn("execution_date", current_date())
                               .select("admission_year", "month", "icu_admissions", "execution_timestamp", "execution_date"))
        df_analytics1_write.write.format("delta").mode("append").option("mergeSchema", "true").saveAsTable(f"{schema_name}.data_quality.icu_admissions_trends")
        logger.info("✓ Analytics 1 written to icu_admissions_trends table")

        df_analytics2 = icustays_raw.withColumn("year", year(col("intime"))).withColumn("month", month(col("intime"))).groupBy("year", "month").agg(count("*").alias("icu_admissions")).orderBy(col("icu_admissions").desc())
        df_analytics2_write = (df_analytics2
                               .withColumn("year", col("year").cast("int"))
                               .withColumn("month", col("month").cast("int"))
                               .withColumn("icu_admissions", col("icu_admissions").cast("long"))
                               .withColumn("execution_timestamp", current_timestamp())
                               .withColumn("execution_date", current_date())
                               .select("year", "month", "icu_admissions", "execution_timestamp", "execution_date"))
        df_analytics2_write.write.format("delta").mode("append").option("mergeSchema", "true").saveAsTable(f"{schema_name}.data_quality.icu_admissions_trends")
        logger.info("✓ Analytics 2 written to icu_admissions_trends table")

        # SECTION 6-9: More Analytics
        logger.info("\n" + "=" * 80)
        logger.info("📊 SECTION 6: ANALYTICS - PATIENT-LEVEL")
        logger.info("=" * 80)

        df_analytics3 = spark.table(f"{schema_name}.silver.fact_icustays").groupBy("subject_id").agg(count("*").alias("icu_visits")).filter(col("icu_visits") > 1).orderBy(col("icu_visits").desc())
        df_analytics3_write = (df_analytics3
                               .withColumn("subject_id", col("subject_id").cast("int"))
                               .withColumn("icu_visits", col("icu_visits").cast("long"))
                               .withColumn("execution_timestamp", current_timestamp())
                               .withColumn("execution_date", current_date()))
        df_analytics3_write.write.format("delta").mode("append").option("mergeSchema", "true").saveAsTable(f"{schema_name}.data_quality.patient_icu_visits")
        logger.info(f"✓ Analytics 3 ({df_analytics3.count()} records) written to patient_icu_visits table")

        logger.info("\n" + "=" * 80)
        logger.info("📊 SECTION 7: ANALYTICS - ICU READMISSIONS BY INSURANCE")
        logger.info("=" * 80)

        df_analytics4 = admissions.join(spark.table(f"{schema_name}.silver.fact_icustays"), "hadm_id").groupBy("insurance", "admission_type").agg(count("*").alias("total_icu_readmissions")).orderBy(col("total_icu_readmissions").desc())
        df_analytics4_write = (df_analytics4
                               .withColumn("insurance", col("insurance").cast("string"))
                               .withColumn("admission_type", col("admission_type").cast("string"))
                               .withColumn("total_icu_readmissions", col("total_icu_readmissions").cast("long"))
                               .withColumn("execution_timestamp", current_timestamp())
                               .withColumn("execution_date", current_date()))
        df_analytics4_write.write.format("delta").mode("append").option("mergeSchema", "true").saveAsTable(f"{schema_name}.data_quality.icu_readmissions_by_insurance")
        logger.info("✓ Analytics 4 written to icu_readmissions_by_insurance table")

        logger.info("\n" + "=" * 80)
        logger.info("📊 SECTION 8: ANALYTICS - ELDERLY ICU ADMISSIONS")
        logger.info("=" * 80)

        patients_raw = spark.table(f"{schema_name}.bronze.patients_raw")
        df_analytics5 = (icustays_raw.join(patients_raw, "subject_id")
            .withColumn("age", floor(datediff(col("intime"), col("dob")) / 365.25))
            .filter(col("age") >= 65).withColumn("year", year(col("intime")))
            .groupBy("year").agg(count("*").alias("elderly_icu_admissions")).orderBy("year"))
        df_analytics5_write = (df_analytics5
                               .withColumn("year", col("year").cast("int"))
                               .withColumn("elderly_icu_admissions", col("elderly_icu_admissions").cast("long"))
                               .withColumn("execution_timestamp", current_timestamp())
                               .withColumn("execution_date", current_date()))
        df_analytics5_write.write.format("delta").mode("append").option("mergeSchema", "true").saveAsTable(f"{schema_name}.data_quality.elderly_icu_admissions")
        logger.info("✓ Analytics 5 written to elderly_icu_admissions table")

        logger.info("\n" + "=" * 80)
        logger.info("📊 SECTION 9: ANALYTICS - MORTALITY RATES")
        logger.info("=" * 80)

        admissions_raw = spark.table(f"{schema_name}.bronze.admissions_raw")
        df_analytics6 = (admissions_raw.groupBy("admission_type")
            .agg(count("*").alias("total_cases"), spark_sum("hospital_expire_flag").alias("deaths"))
            .withColumn("mortality_rate", spark_round(col("deaths") / col("total_cases"), 2))
            .orderBy(col("mortality_rate").desc()))
        df_analytics6_write = (df_analytics6
                               .withColumn("admission_type", col("admission_type").cast("string"))
                               .withColumn("total_cases", col("total_cases").cast("long"))
                               .withColumn("deaths", col("deaths").cast("long"))
                               .withColumn("mortality_rate", col("mortality_rate").cast("decimal(5,2)"))
                               .withColumn("execution_timestamp", current_timestamp())
                               .withColumn("execution_date", current_date())
                               .select("admission_type", "total_cases", "deaths", "mortality_rate", "execution_timestamp", "execution_date"))
        df_analytics6_write.write.format("delta").mode("append").option("mergeSchema", "true").saveAsTable(f"{schema_name}.data_quality.mortality_by_admission_type")
        logger.info("✓ Analytics 6 written to mortality_by_admission_type table")

        # Write summary
        logger.info("\n" + "=" * 80)
        logger.info("💾 WRITING QUALITY CHECK SUMMARY")
        logger.info("=" * 80)

        total_checks_executed = 12
        run_end_time = datetime.now()
        execution_duration_seconds = int((run_end_time - run_start_time).total_seconds())
        run_status = "SUCCESS" if failed_checks == 0 else "PARTIAL_SUCCESS" if warning_checks >= 0 else "FAILED"

        summary_data = [{
            "run_id": run_id,
            "execution_timestamp": run_end_time,
            "execution_date": run_end_time.date(),
            "total_checks_executed": total_checks_executed,
            "passed_checks": passed_checks,
            "warning_checks": warning_checks,
            "failed_checks": failed_checks,
            "total_issues_found": total_issues,
            "execution_duration_seconds": execution_duration_seconds,
            "run_status": run_status
        }]

        df_summary = spark.createDataFrame(summary_data)
        # Enforce schema types for summary table
        df_summary = (df_summary
                      .withColumn("run_id", col("run_id").cast("string"))
                      .withColumn("execution_timestamp", col("execution_timestamp").cast("timestamp"))
                      .withColumn("execution_date", col("execution_date").cast("date"))
                      .withColumn("total_checks_executed", col("total_checks_executed").cast("int"))
                      .withColumn("passed_checks", col("passed_checks").cast("int"))
                      .withColumn("warning_checks", col("warning_checks").cast("int"))
                      .withColumn("failed_checks", col("failed_checks").cast("int"))
                      .withColumn("total_issues_found", col("total_issues_found").cast("long"))
                      .withColumn("execution_duration_seconds", col("execution_duration_seconds").cast("int"))
                      .withColumn("run_status", col("run_status").cast("string")))
        df_summary.write.format("delta").mode("append").option("mergeSchema", "true").saveAsTable(f"{schema_name}.data_quality.quality_check_summary")

        logger.info(f"\n{'='*80}")
        logger.info("FINAL QUALITY CHECK SUMMARY:")
        logger.info(f"{'='*80}")
        logger.info(f"Run ID: {run_id}")
        logger.info(f"Total Checks Executed: {total_checks_executed}")
        logger.info(f"Passed Checks: {passed_checks}")
        logger.info(f"Warning Checks: {warning_checks}")
        logger.info(f"Failed Checks: {failed_checks}")
        logger.info(f"Total Issues Found: {total_issues}")
        logger.info(f"Execution Duration: {execution_duration_seconds} seconds")
        logger.info(f"Run Status: {run_status}")
        logger.info(f"{'='*80}")
        logger.info("✅ DATA QUALITY CHECKS COMPLETED SUCCESSFULLY")
        logger.info(f"{'='*80}\n")

    except Exception as e:
        logger.error("=" * 80)
        logger.error("✗ CRITICAL ERROR IN DATA QUALITY CHECKS")
        logger.error("=" * 80)
        logger.error(f"Error: {str(e)}", exc_info=True)
        raise


def _create_data_quality_tables(spark, schema_name):
    """Create data quality tables if they don't exist"""

    tables = [
        ("quality_check_results", """
            check_id INT,
            check_name STRING,
            check_category STRING,
            table_name STRING,
            check_description STRING,
            issue_count LONG,
            threshold_value STRING,
            check_status STRING,
            execution_timestamp TIMESTAMP,
            execution_date DATE
        """),
        ("icu_admissions_trends", """
            year INT,
            month INT,
            icu_admissions LONG,
            execution_timestamp TIMESTAMP,
            execution_date DATE
        """),
        ("patient_icu_visits", """
            subject_id INT,
            icu_visits LONG,
            execution_timestamp TIMESTAMP,
            execution_date DATE
        """),
        ("icu_readmissions_by_insurance", """
            insurance STRING,
            admission_type STRING,
            total_icu_readmissions LONG,
            execution_timestamp TIMESTAMP,
            execution_date DATE
        """),
        ("elderly_icu_admissions", """
            year INT,
            elderly_icu_admissions LONG,
            execution_timestamp TIMESTAMP,
            execution_date DATE
        """),
        ("mortality_by_admission_type", """
            admission_type STRING,
            total_cases LONG,
            deaths LONG,
            mortality_rate DECIMAL(5,2),
            execution_timestamp TIMESTAMP,
            execution_date DATE
        """),
        ("quality_check_summary", """
            run_id STRING,
            execution_timestamp TIMESTAMP,
            execution_date DATE,
            total_checks_executed INT,
            passed_checks INT,
            warning_checks INT,
            failed_checks INT,
            total_issues_found LONG,
            execution_duration_seconds INT,
            run_status STRING
        """)
    ]

    for table_name, schema_def in tables:
        try:
            logger.info(f"Creating table: {table_name}")
            spark.sql(f"""
                CREATE TABLE IF NOT EXISTS {schema_name}.data_quality.{table_name} (
                    {schema_def}
                )
                USING DELTA
                PARTITIONED BY (execution_date)
            """)
            logger.info(f"✓ Table {table_name} created/verified")
        except Exception as e:
            logger.error(f"✗ Failed to create {table_name} table: {str(e)}", exc_info=True)
            raise

    logger.info("✓ All data quality tables successfully created/verified")

