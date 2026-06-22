from pyspark.sql import functions as F
from mimic_dataset.utils.globals import GlobalVariables as G
from mimic_dataset.utils.file import load_config


def execute_gold():
    config, _ = load_config()
    schema_name = config['schema_name']

    spark = G.spark

    # ICU visits per patient
    icu_visits_per_patient_df = (
        spark.table(f"{schema_name}.silver.fact_icustays")
        .groupBy("subject_id")
        .count()
        .withColumnRenamed("count", "icu_visits")
    )

    icu_visits_per_patient_df.write.mode("overwrite") \
        .saveAsTable(f"{schema_name}.gold.icu_visits_per_patient")

    # Readmissions by insurance
    readmissions_by_insurance_df = (
        spark.table(f"{schema_name}.silver.fact_admissions_enriched")
        .groupBy("insurance", "admission_type")
        .count()
        .withColumnRenamed("count", "total_admissions")
    )

    readmissions_by_insurance_df.write.mode("overwrite") \
        .saveAsTable(f"{schema_name}.gold.readmissions_by_insurance")

    # ICU visit distribution
    icu_visits_dist_df = (
        icu_visits_per_patient_df
        .groupBy("icu_visits")
        .agg(F.count("*").alias("patient_count"))
    )

    # Calculate total patient count separately
    total_patients_df = (
        icu_visits_dist_df
        .agg(F.sum("patient_count").alias("total_patients"))
    )

    # Add percentage without window function
    icu_visits_dist_df = (
        icu_visits_dist_df
        .crossJoin(total_patients_df)
        .withColumn(
            "percentage",
            F.round(
                (F.col("patient_count") * 100.0) / F.col("total_patients"),
                2
            ).cast("decimal(27,2)")
        )
        .drop("total_patients")
    )

    icu_visits_dist_df.write.mode("overwrite") \
        .saveAsTable(f"{schema_name}.gold.icu_visit_distribution")

    # ICU admissions trend
    icu_admissions_trend_df = (
        spark.table(f"{schema_name}.silver.fact_icustays")
        .withColumn("admission_year", F.year("intime"))
        .groupBy("admission_year")
        .count()
        .withColumnRenamed("count", "total_admissions")
        .orderBy("admission_year")
    )

    icu_admissions_trend_df.write.mode("overwrite") \
        .saveAsTable(f"{schema_name}.gold.icu_admissions_trend")