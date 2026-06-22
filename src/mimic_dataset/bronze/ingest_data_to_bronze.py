from mimic_dataset.utils.globals import GlobalVariables as G
from mimic_dataset.utils.file import load_config


def ingest():
    config, _ = load_config()
    schema_name = config['schema_name']
    raw_data_location = config['raw_data_location']
    spark = G.spark

    spark.sql("""
            CREATE DATABASE IF NOT EXISTS {schema_name}.bronze
            """.format(schema_name=schema_name))
    spark.sql("""
            CREATE DATABASE IF NOT EXISTS {schema_name}.silver
            """.format(schema_name=schema_name))
    spark.sql("""
            CREATE DATABASE IF NOT EXISTS {schema_name}.gold
            """.format(schema_name=schema_name))

    # Drop table if exists
    spark.sql("""
              DROP TABLE IF EXISTS {schema_name}.bronze.raw_data
              """.format(schema_name=schema_name))

    # Create managed table using Delta format
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {schema_name}.bronze.raw_data
        USING DELTA
    """)

    files = [
        "ADMISSIONS.csv", "ICUSTAYS.csv", "PATIENTS.csv", "LABEVENTS.csv",
        "CALLOUT.csv", "CAREGIVERS.csv", "CHARTEVENTS.csv", "CPTEVENTS.csv",
        "DATETIMEEVENTS.csv", "DIAGNOSES_ICD.csv", "DRGCODES.csv",
        "D_CPT.csv", "D_ICD_DIAGNOSES.csv", "D_ICD_PROCEDURES.csv",
        "D_ITEMS.csv", "D_LABITEMS.csv", "INPUTEVENTS_CV.csv",
        "INPUTEVENTS_MV.csv", "MICROBIOLOGYEVENTS.csv", "NOTEEVENTS.csv",
        "OUTPUTEVENTS.csv", "PRESCRIPTIONS.csv", "PROCEDUREEVENTS_MV.csv",
        "PROCEDURES_ICD.csv", "SERVICES.csv", "TRANSFERS.csv"
    ]

    print("Current User:", spark.sql("SELECT current_user()").collect())

    for f in files:
        table_name = f.replace(".csv", "").lower() + "_raw"

        df = (spark.read
              .option("header", "true")
              .option("inferSchema", "true")
              .csv(f"{raw_data_location}/{f}"))

        (df.write
         .format("delta")
         .mode("overwrite")
         .saveAsTable(f"{schema_name}.bronze.{table_name}"))

        print(f"✅ Ingested: {f} -> bd_mimic.bronze.{table_name}")
