from pyspark.sql.functions import col, floor, datediff
from mimic_dataset.utils.globals import GlobalVariables as G
from mimic_dataset.utils.file import load_config

def execute_silver():
    config, _ = load_config()
    schema_name = config['schema_name']

    spark = G.spark

    df = spark.table("""
                {schema_name}.bronze.admissions_raw    
                """.format(schema_name=schema_name))

    df_clean = df.select([col(c).alias(c.lower()) for c in df.columns])

    df_clean = (
        df_clean
            .withColumn("admittime", col("admittime").cast("timestamp"))
            .withColumn("dischtime", col("dischtime").cast("timestamp"))
            .withColumn("hospital_expire_flag", col("hospital_expire_flag").cast("int"))
    )

    df_clean = df_clean.dropDuplicates(["subject_id", "hadm_id"])

    df_pat = spark.table("""
                     {schema_name}.bronze.patients_raw
                     """.format(schema_name=schema_name))

    df_pat_clean = (
        df_pat
            .dropDuplicates(["subject_id"])
            .withColumn("dob", col("dob").cast("date"))
            .withColumn("dod", col("dod").cast("date"))
    )

    df_pat_clean.write.format("delta").mode("overwrite") \
        .saveAsTable(f"{schema_name}.silver.dim_patients")

    df_icu = spark.table("""
                     {schema_name}.bronze.icustays_raw
                     """.format(schema_name=schema_name))

    df_icu_clean = (
        df_icu
            .withColumn("intime", col("intime").cast("timestamp"))
            .withColumn("outtime", col("outtime").cast("timestamp"))
            .dropDuplicates(["icustay_id"])
    )

    df_icu_clean.write.format("delta").mode("overwrite") \
        .saveAsTable(f"{schema_name}.silver.fact_icustays")

    df_adm = spark.table("""
                     {schema_name}.bronze.admissions_raw
                     """.format(schema_name=schema_name))

    df_adm_clean = (
        df_adm
            .withColumn("admittime", col("admittime").cast("timestamp"))
            .withColumn("dischtime", col("dischtime").cast("timestamp"))
            .dropDuplicates(["hadm_id"])
    )

    df_adm_clean.write.format("delta").mode("overwrite") \
        .saveAsTable(f"{schema_name}.silver.fact_admissions")

    df_adm_clean = df_adm_clean.withColumn(
        "length_of_stay_days",
        datediff(col("dischtime"), col("admittime"))
    )

    df_age = (
        df_adm_clean
            .join(df_pat_clean, "subject_id")
            .withColumn("age", floor(datediff(col("admittime"), col("dob")) / 365.25))
    )

    df_age = (
        df_adm_clean
            .drop("row_id")
            .join(df_pat_clean.drop("row_id"), "subject_id")
            .withColumn("age", floor(datediff(col("admittime"), col("dob")) / 365.25))
    )

    df_age.write.format("delta").mode("overwrite") \
        .saveAsTable(f"{schema_name}.silver.fact_admissions_enriched")

    df_diag = spark.table(f"{schema_name}.bronze.d_icd_diagnoses_raw")

    df_diag_clean = df_diag.dropDuplicates(["icd9_code"])

    df_diag_clean.write.format("delta").mode("overwrite") \
        .saveAsTable(f"{schema_name}.silver.dim_icd_diagnoses")
