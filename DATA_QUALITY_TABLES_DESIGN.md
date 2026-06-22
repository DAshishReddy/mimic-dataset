# Data Quality Tables Design

## Overview
This document defines the Delta table structures for storing data quality check results in the `data_quality` schema.

---

## Table 1: `data_quality.quality_check_results`

Stores the results of data quality checks (Checks 1-12).

### Schema

| Column Name | Data Type | Description | Example |
|-------------|-----------|-------------|---------|
| check_id | INT | Unique identifier for the check | 1 |
| check_name | STRING | Name of the quality check | `null_hadm_id` |
| check_category | STRING | Category of the check | `ICU_STAYS`, `ADMISSIONS`, `PATIENTS`, `DIAGNOSES` |
| table_name | STRING | Source table being checked | `mimic_catalog.silver.fact_icustays` |
| check_description | STRING | Detailed description of what's checked | `Check for NULL values in hadm_id column` |
| issue_count | LONG | Number of issues/anomalies found | 0 |
| threshold_value | STRING | Optional threshold used in check | `365` (for LOS check) |
| check_status | STRING | Status of check | `PASS`, `WARN`, `FAIL` |
| execution_timestamp | TIMESTAMP | When the check was run | `2026-05-09 10:30:45.123` |
| execution_date | DATE | Date of execution (for partitioning) | `2026-05-09` |

### Primary Key
- `check_id` + `execution_timestamp`

### Partitioning
- `PARTITIONED BY (execution_date)`

### Sample Data

| check_id | check_name | check_category | table_name | check_description | issue_count | threshold_value | check_status | execution_timestamp | execution_date |
|----------|-----------|----------------|-----------|-------------------|-------------|-----------------|--------------|---------------------|----------------|
| 1 | null_hadm_id | ICU_STAYS | mimic_catalog.silver.fact_icustays | Check for NULL values in hadm_id | 0 | NULL | PASS | 2026-05-09 10:30:45 | 2026-05-09 |
| 2 | null_outtime | ICU_STAYS | mimic_catalog.silver.fact_icustays | Check for NULL values in outtime | 5 | NULL | WARN | 2026-05-09 10:30:46 | 2026-05-09 |
| 3 | extreme_los | ICU_STAYS | mimic_catalog.silver.fact_icustays | Check for LOS > 365 days | 12 | 365 | WARN | 2026-05-09 10:30:47 | 2026-05-09 |
| 9 | negative_admission_duration | ADMISSIONS | mimic_catalog.silver.fact_admissions | Check for admittime > dischtime | 0 | NULL | PASS | 2026-05-09 10:30:50 | 2026-05-09 |
| 10 | invalid_gender | PATIENTS | mimic_catalog.silver.dim_patients | Check for invalid gender values | 3 | M,F | WARN | 2026-05-09 10:30:51 | 2026-05-09 |

---

## Table 2: `data_quality.icu_admissions_trends`

Stores ICU admissions analytics by year and month (Analytics 1 & 2).

### Schema

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| year | INT | Year of admission |
| month | INT | Month of admission (optional) |
| icu_admissions | LONG | Count of ICU admissions |
| execution_timestamp | TIMESTAMP | When the analytics was run |
| execution_date | DATE | Date of execution (for partitioning) |

### Partitioning
- `PARTITIONED BY (execution_date)`

### Sample Data

| year | month | icu_admissions | execution_timestamp | execution_date |
|------|-------|----------------|---------------------|----------------|
| 2100 | NULL | 45231 | 2026-05-09 10:30:45 | 2026-05-09 |
| 2101 | 1 | 3890 | 2026-05-09 10:30:45 | 2026-05-09 |
| 2101 | 2 | 4120 | 2026-05-09 10:30:45 | 2026-05-09 |

---

## Table 3: `data_quality.patient_icu_visits`

Stores patient-level ICU visit analytics (Analytics 3).

### Schema

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| subject_id | INT | Patient identifier |
| icu_visits | LONG | Number of ICU visits by patient |
| execution_timestamp | TIMESTAMP | When the analytics was run |
| execution_date | DATE | Date of execution (for partitioning) |

### Partitioning
- `PARTITIONED BY (execution_date)`

### Sample Data

| subject_id | icu_visits | execution_timestamp | execution_date |
|------------|------------|---------------------|----------------|
| 100 | 5 | 2026-05-09 10:30:45 | 2026-05-09 |
| 200 | 3 | 2026-05-09 10:30:45 | 2026-05-09 |
| 300 | 2 | 2026-05-09 10:30:45 | 2026-05-09 |

---

## Table 4: `data_quality.icu_readmissions_by_insurance`

Stores readmission analytics by insurance and admission type (Analytics 4).

### Schema

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| insurance | STRING | Insurance type |
| admission_type | STRING | Type of admission |
| total_icu_readmissions | LONG | Count of ICU readmissions |
| execution_timestamp | TIMESTAMP | When the analytics was run |
| execution_date | DATE | Date of execution (for partitioning) |

### Partitioning
- `PARTITIONED BY (execution_date)`

### Sample Data

| insurance | admission_type | total_icu_readmissions | execution_timestamp | execution_date |
|-----------|----------------|----------------------|---------------------|----------------|
| Medicare | URGENT | 1250 | 2026-05-09 10:30:45 | 2026-05-09 |
| Medicaid | EMERGENCY | 890 | 2026-05-09 10:30:45 | 2026-05-09 |

---

## Table 5: `data_quality.elderly_icu_admissions`

Stores elderly patient (age >= 65) ICU admissions by year (Analytics 5).

### Schema

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| year | INT | Year of admission |
| elderly_icu_admissions | LONG | Count of elderly patients admitted to ICU |
| execution_timestamp | TIMESTAMP | When the analytics was run |
| execution_date | DATE | Date of execution (for partitioning) |

### Partitioning
- `PARTITIONED BY (execution_date)`

### Sample Data

| year | elderly_icu_admissions | execution_timestamp | execution_date |
|------|------------------------|---------------------|----------------|
| 2100 | 35000 | 2026-05-09 10:30:45 | 2026-05-09 |
| 2101 | 38000 | 2026-05-09 10:30:45 | 2026-05-09 |

---

## Table 6: `data_quality.mortality_by_admission_type`

Stores mortality analytics by admission type (Analytics 6).

### Schema

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| admission_type | STRING | Type of admission |
| total_cases | LONG | Total number of cases |
| deaths | LONG | Number of deaths |
| mortality_rate | DECIMAL(5,2) | Mortality rate (0-1) |
| execution_timestamp | TIMESTAMP | When the analytics was run |
| execution_date | DATE | Date of execution (for partitioning) |

### Partitioning
- `PARTITIONED BY (execution_date)`

### Sample Data

| admission_type | total_cases | deaths | mortality_rate | execution_timestamp | execution_date |
|----------------|-------------|--------|----------------|---------------------|----------------|
| EMERGENCY | 50000 | 5200 | 0.10 | 2026-05-09 10:30:45 | 2026-05-09 |
| URGENT | 30000 | 2100 | 0.07 | 2026-05-09 10:30:45 | 2026-05-09 |
| ELECTIVE | 20000 | 400 | 0.02 | 2026-05-09 10:30:45 | 2026-05-09 |

---

## Table 7: `data_quality.quality_check_summary`

Stores a summary of each quality check run for reporting and monitoring.

### Schema

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| run_id | STRING | Unique identifier for the run (UUID) |
| execution_timestamp | TIMESTAMP | When the check run started |
| execution_date | DATE | Date of execution |
| total_checks_executed | INT | Total number of checks run |
| passed_checks | INT | Number of checks that passed |
| warning_checks | INT | Number of checks with warnings |
| failed_checks | INT | Number of failed checks |
| total_issues_found | LONG | Total issues across all checks |
| execution_duration_seconds | INT | Duration of check execution |
| run_status | STRING | Overall status: `SUCCESS`, `PARTIAL_SUCCESS`, `FAILED` |

### Partitioning
- `PARTITIONED BY (execution_date)`

### Sample Data

| run_id | execution_timestamp | execution_date | total_checks_executed | passed_checks | warning_checks | failed_checks | total_issues_found | execution_duration_seconds | run_status |
|--------|---------------------|----------------|----------------------|---------------|----------------|--------------|--------------------|----------------------------|------------|
| run_20260509_001 | 2026-05-09 10:30:45 | 2026-05-09 | 12 | 9 | 3 | 0 | 20 | 45 | SUCCESS |

---

## Column Definitions

| Check ID | Check Name | Category | Table Name | Description |
|----------|-----------|----------|-----------|-------------|
| 1 | null_hadm_id | ICU_STAYS | fact_icustays | Checks for NULL hadm_id values |
| 2 | null_outtime | ICU_STAYS | fact_icustays | Checks for NULL outtime values |
| 3 | extreme_los | ICU_STAYS | fact_icustays | Checks for LOS > 365 days |
| 4 | future_intime | ICU_STAYS | fact_icustays | Checks for intime > current_date |
| 5 | future_outtime | ICU_STAYS | fact_icustays | Checks for outtime > current_date |
| 6 | dob_after_admission | ICU_STAYS | fact_icustays, dim_patients | Checks for DOB > intime |
| 7 | missing_patient_reference | ICU_STAYS | fact_icustays, dim_patients | Checks for referential integrity |
| 8 | missing_admission_reference | ICU_STAYS | fact_icustays, fact_admissions | Checks for referential integrity |
| 9 | negative_admission_duration | ADMISSIONS | fact_admissions | Checks for admittime > dischtime |
| 10 | invalid_gender | PATIENTS | dim_patients | Checks for invalid gender values |
| 11 | duplicate_subject_id | PATIENTS | dim_patients | Checks for duplicates |
| 12 | null_icd_code | DIAGNOSES | diagnoses_icd_raw | Checks for NULL icd9_code |

---

## SQL to Create Tables

```sql
-- Create data_quality schema
CREATE SCHEMA IF NOT EXISTS mimic_catalog.data_quality;

-- Table 1: Quality Check Results
CREATE TABLE IF NOT EXISTS mimic_catalog.data_quality.quality_check_results (
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
)
USING DELTA
PARTITIONED BY (execution_date);

-- Table 2: ICU Admissions Trends
CREATE TABLE IF NOT EXISTS mimic_catalog.data_quality.icu_admissions_trends (
    year INT,
    month INT,
    icu_admissions LONG,
    execution_timestamp TIMESTAMP,
    execution_date DATE
)
USING DELTA
PARTITIONED BY (execution_date);

-- Table 3: Patient ICU Visits
CREATE TABLE IF NOT EXISTS mimic_catalog.data_quality.patient_icu_visits (
    subject_id INT,
    icu_visits LONG,
    execution_timestamp TIMESTAMP,
    execution_date DATE
)
USING DELTA
PARTITIONED BY (execution_date);

-- Table 4: ICU Readmissions by Insurance
CREATE TABLE IF NOT EXISTS mimic_catalog.data_quality.icu_readmissions_by_insurance (
    insurance STRING,
    admission_type STRING,
    total_icu_readmissions LONG,
    execution_timestamp TIMESTAMP,
    execution_date DATE
)
USING DELTA
PARTITIONED BY (execution_date);

-- Table 5: Elderly ICU Admissions
CREATE TABLE IF NOT EXISTS mimic_catalog.data_quality.elderly_icu_admissions (
    year INT,
    elderly_icu_admissions LONG,
    execution_timestamp TIMESTAMP,
    execution_date DATE
)
USING DELTA
PARTITIONED BY (execution_date);

-- Table 6: Mortality by Admission Type
CREATE TABLE IF NOT EXISTS mimic_catalog.data_quality.mortality_by_admission_type (
    admission_type STRING,
    total_cases LONG,
    deaths LONG,
    mortality_rate DECIMAL(5,2),
    execution_timestamp TIMESTAMP,
    execution_date DATE
)
USING DELTA
PARTITIONED BY (execution_date);

-- Table 7: Quality Check Summary
CREATE TABLE IF NOT EXISTS mimic_catalog.data_quality.quality_check_summary (
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
)
USING DELTA
PARTITIONED BY (execution_date);
```

---

## Benefits

✅ **Time-series tracking** - Partitioned by execution_date for fast querying and archival  
✅ **Historical analysis** - Track data quality trends over time  
✅ **Automated monitoring** - Detect anomalies and quality regressions  
✅ **Reporting** - Generate dashboards and reports from stored results  
✅ **Alerting** - Set up alerts based on check failures/warnings  
✅ **Compliance** - Maintain audit trail of data quality checks  

---

## Query Examples

### Get all failed checks from past 7 days
```sql
SELECT * FROM mimic_catalog.data_quality.quality_check_results
WHERE execution_date >= current_date() - 7
  AND check_status = 'FAIL'
ORDER BY execution_timestamp DESC;
```

### Compare mortality rate trends
```sql
SELECT execution_date, admission_type, mortality_rate
FROM mimic_catalog.data_quality.mortality_by_admission_type
WHERE execution_date >= current_date() - 30
ORDER BY execution_date, admission_type;
```

### Check highest issue counts
```sql
SELECT check_name, check_category, SUM(issue_count) as total_issues
FROM mimic_catalog.data_quality.quality_check_results
WHERE execution_date >= current_date() - 7
GROUP BY check_name, check_category
ORDER BY total_issues DESC;
```

