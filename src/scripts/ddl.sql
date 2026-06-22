-- =============================================================================
-- MIMIC-III  —  CREATE TABLE scripts
-- Generated from CSV schema analysis
-- Schema : mimic  (change to dbo or your preferred schema)
-- Compatible with : SQL Server / Azure SQL Database
-- =============================================================================

-- Uncomment to create schema first
-- CREATE SCHEMA mimic;
-- GO

-- =============================================================================
-- 1. ADMISSIONS
-- =============================================================================
CREATE TABLE ADMISSIONS (
                                  row_id               INT            NOT NULL,
                                  subject_id           INT            NOT NULL,
                                  hadm_id              INT            NOT NULL,
                                  admittime            DATETIME2      NOT NULL,
                                  dischtime            DATETIME2      NOT NULL,
                                  deathtime            DATETIME2      NULL,
                                  admission_type       NVARCHAR(50)   NOT NULL,
                                  admission_location   NVARCHAR(100)  NOT NULL,
                                  discharge_location   NVARCHAR(100)  NOT NULL,
                                  insurance            NVARCHAR(50)   NOT NULL,
                                  language             NVARCHAR(20)   NULL,
                                  religion             NVARCHAR(100)  NULL,
                                  marital_status       NVARCHAR(50)   NULL,
                                  ethnicity            NVARCHAR(200)  NOT NULL,
                                  edregtime            DATETIME2      NULL,
                                  edouttime            DATETIME2      NULL,
                                  diagnosis            NVARCHAR(500)  NOT NULL,
                                  hospital_expire_flag TINYINT        NOT NULL,
                                  has_chartevents_data TINYINT        NOT NULL,
                                  CONSTRAINT PK_ADMISSIONS PRIMARY KEY (row_id)
);
GO

-- =============================================================================
-- 2. PATIENTS
-- =============================================================================
CREATE TABLE PATIENTS (
                                row_id      INT          NOT NULL,
                                subject_id  INT          NOT NULL,
                                gender      CHAR(1)      NOT NULL,
                                dob         DATETIME2    NOT NULL,
                                dod         DATETIME2    NULL,
                                dod_hosp    DATETIME2    NULL,
                                dod_ssn     DATETIME2    NULL,
                                expire_flag TINYINT      NOT NULL,
                                CONSTRAINT PK_PATIENTS PRIMARY KEY (row_id)
);
GO

-- =============================================================================
-- 3. CAREGIVERS
-- =============================================================================
CREATE TABLE CAREGIVERS (
                                  row_id      INT           NOT NULL,
                                  cgid        INT           NOT NULL,
                                  label       NVARCHAR(50)  NOT NULL,
                                  description NVARCHAR(200) NULL,
                                  CONSTRAINT PK_CAREGIVERS PRIMARY KEY (row_id)
);
GO

-- =============================================================================
-- 4. TRANSFERS
-- =============================================================================
CREATE TABLE TRANSFERS (
                                 row_id         INT           NOT NULL,
                                 subject_id     INT           NOT NULL,
                                 hadm_id        INT           NOT NULL,
                                 icustay_id     INT           NULL,
                                 dbsource       NVARCHAR(20)  NOT NULL,
                                 eventtype      NVARCHAR(20)  NOT NULL,
                                 prev_careunit  NVARCHAR(50)  NULL,
                                 curr_careunit  NVARCHAR(50)  NULL,
                                 prev_wardid    SMALLINT      NULL,
                                 curr_wardid    SMALLINT      NULL,
                                 intime         DATETIME2     NOT NULL,
                                 outtime        DATETIME2     NULL,
                                 los            FLOAT         NULL,
                                 CONSTRAINT PK_TRANSFERS PRIMARY KEY (row_id)
);
GO

-- =============================================================================
-- 5. CALLOUT
-- =============================================================================
CREATE TABLE CALLOUT (
                               row_id                  INT           NOT NULL,
                               subject_id              INT           NOT NULL,
                               hadm_id                 INT           NOT NULL,
                               submit_wardid           SMALLINT      NOT NULL,
                               submit_careunit         NVARCHAR(50)  NULL,
                               curr_wardid             SMALLINT      NOT NULL,
                               curr_careunit           NVARCHAR(50)  NOT NULL,
                               callout_wardid          SMALLINT      NOT NULL,
                               callout_service         NVARCHAR(50)  NOT NULL,
                               request_tele            TINYINT       NOT NULL,
                               request_resp            TINYINT       NOT NULL,
                               request_cdiff           TINYINT       NOT NULL,
                               request_mrsa            TINYINT       NOT NULL,
                               request_vre             TINYINT       NOT NULL,
                               callout_status          NVARCHAR(50)  NOT NULL,
                               callout_outcome         NVARCHAR(50)  NOT NULL,
                               discharge_wardid        SMALLINT      NULL,
                               acknowledge_status      NVARCHAR(50)  NOT NULL,
                               createtime              DATETIME2     NOT NULL,
                               updatetime              DATETIME2     NOT NULL,
                               acknowledgetime         DATETIME2     NULL,
                               outcometime             DATETIME2     NOT NULL,
                               firstreservationtime    DATETIME2     NULL,
                               currentreservationtime  DATETIME2     NULL,
                               CONSTRAINT PK_CALLOUT PRIMARY KEY (row_id)
);
GO

-- =============================================================================
-- 6. SERVICES
-- =============================================================================
CREATE TABLE SERVICES (
                                row_id        INT          NOT NULL,
                                subject_id    INT          NOT NULL,
                                hadm_id       INT          NOT NULL,
                                transfertime  DATETIME2    NOT NULL,
                                prev_service  NVARCHAR(20) NULL,
                                curr_service  NVARCHAR(20) NOT NULL,
                                CONSTRAINT PK_SERVICES PRIMARY KEY (row_id)
);
GO

-- =============================================================================
-- 7. DIAGNOSES_ICD
-- =============================================================================
CREATE TABLE DIAGNOSES_ICD (
                                     row_id     INT          NOT NULL,
                                     subject_id INT          NOT NULL,
                                     hadm_id    INT          NOT NULL,
                                     seq_num    SMALLINT     NOT NULL,
                                     icd9_code  NVARCHAR(10) NOT NULL,
                                     CONSTRAINT PK_DIAGNOSES_ICD PRIMARY KEY (row_id)
);
GO

-- =============================================================================
-- 8. D_ICD_DIAGNOSES
-- =============================================================================
CREATE TABLE D_ICD_DIAGNOSES (
                                       row_id      INT            NOT NULL,
                                       icd9_code   NVARCHAR(10)   NOT NULL,
                                       short_title NVARCHAR(100)  NOT NULL,
                                       long_title  NVARCHAR(1000) NOT NULL,
                                       CONSTRAINT PK_D_ICD_DIAGNOSES PRIMARY KEY (row_id)
);
GO

-- =============================================================================
-- 9. PROCEDURES_ICD
-- =============================================================================
CREATE TABLE PROCEDURES_ICD (
                                      row_id     INT      NOT NULL,
                                      subject_id INT      NOT NULL,
                                      hadm_id    INT      NOT NULL,
                                      seq_num    SMALLINT NOT NULL,
                                      icd9_code  INT      NOT NULL,
                                      CONSTRAINT PK_PROCEDURES_ICD PRIMARY KEY (row_id)
);
GO

-- =============================================================================
-- 10. D_ICD_PROCEDURES
-- =============================================================================
CREATE TABLE D_ICD_PROCEDURES (
                                        row_id      INT            NOT NULL,
                                        icd9_code   INT            NOT NULL,
                                        short_title NVARCHAR(100)  NOT NULL,
                                        long_title  NVARCHAR(1000) NOT NULL,
                                        CONSTRAINT PK_D_ICD_PROCEDURES PRIMARY KEY (row_id)
);
GO

-- =============================================================================
-- 11. D_CPT
-- =============================================================================
CREATE TABLE D_CPT (
                             row_id               INT          NOT NULL,
                             category             SMALLINT     NOT NULL,
                             sectionrange         NVARCHAR(20) NOT NULL,
                             sectionheader        NVARCHAR(200)NOT NULL,
                             subsectionrange      NVARCHAR(20) NOT NULL,
                             subsectionheader     NVARCHAR(200)NOT NULL,
                             codesuffix           NVARCHAR(5)  NULL,
                             mincodeinsubsection  INT          NOT NULL,
                             maxcodeinsubsection  INT          NOT NULL,
                             CONSTRAINT PK_D_CPT PRIMARY KEY (row_id)
);
GO

-- =============================================================================
-- 12. CPTEVENTS
-- =============================================================================
CREATE TABLE CPTEVENTS (
                                 row_id            INT           NOT NULL,
                                 subject_id        INT           NOT NULL,
                                 hadm_id           INT           NOT NULL,
                                 costcenter        NVARCHAR(20)  NOT NULL,
                                 chartdate         DATE          NULL,
                                 cpt_cd            INT           NOT NULL,
                                 cpt_number        INT           NOT NULL,
                                 cpt_suffix        NVARCHAR(10)  NULL,
                                 ticket_id_seq     SMALLINT      NOT NULL,
                                 sectionheader     NVARCHAR(200) NOT NULL,
                                 subsectionheader  NVARCHAR(200) NOT NULL,
                                 description       NVARCHAR(500) NULL,
                                 CONSTRAINT PK_CPTEVENTS PRIMARY KEY (row_id)
);
GO

-- =============================================================================
-- 13. D_ITEMS
-- =============================================================================
CREATE TABLE D_ITEMS (
                               row_id       INT           NOT NULL,
                               itemid       INT           NOT NULL,
                               label        NVARCHAR(200) NOT NULL,
                               abbreviation NVARCHAR(100) NULL,
                               dbsource     NVARCHAR(20)  NOT NULL,
                               linksto      NVARCHAR(50)  NOT NULL,
                               category     NVARCHAR(100) NULL,
                               unitname     NVARCHAR(100) NULL,
                               param_type   NVARCHAR(50)  NULL,
                               conceptid    INT           NULL,
                               CONSTRAINT PK_D_ITEMS PRIMARY KEY (row_id)
);
GO

-- =============================================================================
-- 14. CHARTEVENTS
-- =============================================================================
CREATE TABLE CHARTEVENTS (
                                   row_id       INT           NOT NULL,
                                   subject_id   INT           NOT NULL,
                                   hadm_id      INT           NOT NULL,
                                   icustay_id   INT           NOT NULL,
                                   itemid       INT           NOT NULL,
                                   charttime    DATETIME2     NOT NULL,
                                   storetime    DATETIME2     NOT NULL,
                                   cgid         INT           NOT NULL,
                                   value        FLOAT         NULL,
                                   valuenum     FLOAT         NULL,
                                   valueuom     NVARCHAR(50)  NULL,
                                   warning      TINYINT       NOT NULL,
                                   error        TINYINT       NOT NULL,
                                   resultstatus NVARCHAR(50)  NULL,
                                   stopped      NVARCHAR(50)  NULL,
                                   CONSTRAINT PK_CHARTEVENTS PRIMARY KEY (row_id)
);
GO

-- =============================================================================
-- 15. DATETIMEEVENTS
-- =============================================================================
CREATE TABLE DATETIMEEVENTS (
                                      row_id       INT           NOT NULL,
                                      subject_id   INT           NOT NULL,
                                      hadm_id      INT           NOT NULL,
                                      icustay_id   INT           NOT NULL,
                                      itemid       INT           NOT NULL,
                                      charttime    DATETIME2     NOT NULL,
                                      storetime    DATETIME2     NOT NULL,
                                      cgid         INT           NOT NULL,
                                      value        DATETIME2     NULL,
                                      valueuom     NVARCHAR(50)  NOT NULL,
                                      warning      TINYINT       NULL,
                                      error        TINYINT       NULL,
                                      resultstatus NVARCHAR(50)  NULL,
                                      stopped      NVARCHAR(50)  NOT NULL,
                                      CONSTRAINT PK_DATETIMEEVENTS PRIMARY KEY (row_id)
);
GO

-- =============================================================================
-- 16. OUTPUTEVENTS
-- =============================================================================
CREATE TABLE OUTPUTEVENTS (
                                    row_id     INT          NOT NULL,
                                    subject_id INT          NOT NULL,
                                    hadm_id    INT          NOT NULL,
                                    icustay_id INT          NOT NULL,
                                    charttime  DATETIME2    NOT NULL,
                                    itemid     INT          NOT NULL,
                                    value      FLOAT        NULL,
                                    valueuom   NVARCHAR(20) NULL,
                                    storetime  DATETIME2    NOT NULL,
                                    cgid       INT          NOT NULL,
                                    stopped    NVARCHAR(50) NULL,
                                    newbottle  TINYINT      NULL,
                                    iserror    TINYINT      NULL,
                                    CONSTRAINT PK_OUTPUTEVENTS PRIMARY KEY (row_id)
);
GO

-- =============================================================================
-- 17. PROCEDUREEVENTS_MV
-- =============================================================================
CREATE TABLE PROCEDUREEVENTS_MV (
                                          row_id                     INT           NOT NULL,
                                          subject_id                 INT           NOT NULL,
                                          hadm_id                    INT           NOT NULL,
                                          icustay_id                 INT           NOT NULL,
                                          starttime                  DATETIME2     NOT NULL,
                                          endtime                    DATETIME2     NOT NULL,
                                          itemid                     INT           NOT NULL,
                                          value                      BIGINT        NOT NULL,
                                          valueuom                   NVARCHAR(20)  NULL,
                                          location                   NVARCHAR(100) NULL,
                                          locationcategory           NVARCHAR(100) NULL,
                                          storetime                  DATETIME2     NOT NULL,
                                          cgid                       INT           NOT NULL,
                                          orderid                    BIGINT        NOT NULL,
                                          linkorderid                BIGINT        NOT NULL,
                                          ordercategoryname          NVARCHAR(100) NOT NULL,
                                          secondaryordercategoryname NVARCHAR(200) NULL,
                                          ordercategorydescription   NVARCHAR(100) NOT NULL,
                                          isopenbag                  TINYINT       NOT NULL,
                                          continueinnextdept         TINYINT       NOT NULL,
                                          cancelreason               TINYINT       NOT NULL,
                                          statusdescription          NVARCHAR(50)  NOT NULL,
                                          comments_editedby          NVARCHAR(50)  NULL,
                                          comments_canceledby        NVARCHAR(50)  NULL,
                                          comments_date              DATETIME2     NULL,
                                          CONSTRAINT PK_PROCEDUREEVENTS_MV PRIMARY KEY (row_id)
);
GO

-- =============================================================================
-- 18. PRESCRIPTIONS
-- =============================================================================
CREATE TABLE PRESCRIPTIONS (
                                     row_id           INT           NOT NULL,
                                     subject_id       INT           NOT NULL,
                                     hadm_id          INT           NOT NULL,
                                     icustay_id       INT           NULL,
                                     startdate        DATETIME2     NOT NULL,
                                     enddate          DATETIME2     NOT NULL,
                                     drug_type        NVARCHAR(20)  NOT NULL,
                                     drug             NVARCHAR(200) NOT NULL,
                                     drug_name_poe    NVARCHAR(200) NULL,
                                     drug_name_generic NVARCHAR(200) NULL,
                                     formulary_drug_cd NVARCHAR(20) NOT NULL,
                                     gsn              FLOAT         NULL,
                                     ndc              BIGINT        NOT NULL,
                                     prod_strength    NVARCHAR(200) NOT NULL,
                                     dose_val_rx      NVARCHAR(100) NOT NULL,
                                     dose_unit_rx     NVARCHAR(50)  NOT NULL,
                                     form_val_disp    NVARCHAR(50)  NOT NULL,
                                     form_unit_disp   NVARCHAR(50)  NOT NULL,
                                     route            NVARCHAR(50)  NOT NULL,
                                     CONSTRAINT PK_PRESCRIPTIONS PRIMARY KEY (row_id)
);
GO

-- =============================================================================
-- 19. MICROBIOLOGYEVENTS
-- =============================================================================
CREATE TABLE MICROBIOLOGYEVENTS (
                                          row_id              INT           NOT NULL,
                                          subject_id          INT           NOT NULL,
                                          hadm_id             INT           NOT NULL,
                                          chartdate           DATETIME2     NOT NULL,
                                          charttime           DATETIME2     NULL,
                                          spec_itemid         INT           NOT NULL,
                                          spec_type_desc      NVARCHAR(100) NOT NULL,
                                          org_itemid          INT           NULL,
                                          org_name            NVARCHAR(200) NULL,
                                          isolate_num         SMALLINT      NULL,
                                          ab_itemid           INT           NULL,
                                          ab_name             NVARCHAR(100) NULL,
                                          dilution_text       NVARCHAR(20)  NULL,
                                          dilution_comparison NVARCHAR(10)  NULL,
                                          dilution_value      FLOAT         NULL,
                                          interpretation      NVARCHAR(5)   NULL,
                                          CONSTRAINT PK_MICROBIOLOGYEVENTS PRIMARY KEY (row_id)
);
GO

-- =============================================================================
-- 20. NOTEEVENTS
-- =============================================================================
CREATE TABLE NOTEEVENTS (
                                  row_id      INT            NOT NULL,
                                  subject_id  INT            NOT NULL,
                                  hadm_id     INT            NULL,
                                  chartdate   DATE           NOT NULL,
                                  charttime   DATETIME2      NULL,
                                  storetime   DATETIME2      NULL,
                                  category    NVARCHAR(100)  NOT NULL,
                                  description NVARCHAR(200)  NOT NULL,
                                  cgid        INT            NULL,
                                  iserror     NVARCHAR(5)    NULL,
                                  text        NVARCHAR(MAX)  NOT NULL,
                                  CONSTRAINT PK_NOTEEVENTS PRIMARY KEY (row_id)
);
GO

-- =============================================================================
-- FOREIGN KEY CONSTRAINTS
-- Uncomment once all tables are loaded and data integrity is confirmed
-- =============================================================================

/*
-- ADMISSIONS → PATIENTS
ALTER TABLE ADMISSIONS
    ADD CONSTRAINT FK_ADM_PATIENT
    FOREIGN KEY (subject_id) REFERENCES PATIENTS (subject_id);

-- TRANSFERS → ADMISSIONS
ALTER TABLE TRANSFERS
    ADD CONSTRAINT FK_TRN_ADMISSION
    FOREIGN KEY (hadm_id) REFERENCES ADMISSIONS (hadm_id);

-- SERVICES → ADMISSIONS
ALTER TABLE SERVICES
    ADD CONSTRAINT FK_SVC_ADMISSION
    FOREIGN KEY (hadm_id) REFERENCES ADMISSIONS (hadm_id);

-- CALLOUT → ADMISSIONS
ALTER TABLE CALLOUT
    ADD CONSTRAINT FK_COU_ADMISSION
    FOREIGN KEY (hadm_id) REFERENCES ADMISSIONS (hadm_id);

-- DIAGNOSES_ICD → ADMISSIONS
ALTER TABLE DIAGNOSES_ICD
    ADD CONSTRAINT FK_DIAG_ADMISSION
    FOREIGN KEY (hadm_id) REFERENCES ADMISSIONS (hadm_id);

-- DIAGNOSES_ICD → D_ICD_DIAGNOSES
ALTER TABLE DIAGNOSES_ICD
    ADD CONSTRAINT FK_DIAG_ICD
    FOREIGN KEY (icd9_code) REFERENCES D_ICD_DIAGNOSES (icd9_code);

-- PROCEDURES_ICD → ADMISSIONS
ALTER TABLE PROCEDURES_ICD
    ADD CONSTRAINT FK_PROC_ADMISSION
    FOREIGN KEY (hadm_id) REFERENCES ADMISSIONS (hadm_id);

-- CPTEVENTS → ADMISSIONS
ALTER TABLE CPTEVENTS
    ADD CONSTRAINT FK_CPT_ADMISSION
    FOREIGN KEY (hadm_id) REFERENCES ADMISSIONS (hadm_id);

-- CHARTEVENTS → D_ITEMS
ALTER TABLE CHARTEVENTS
    ADD CONSTRAINT FK_CHT_ITEM
    FOREIGN KEY (itemid) REFERENCES D_ITEMS (itemid);

-- CHARTEVENTS → CAREGIVERS
ALTER TABLE CHARTEVENTS
    ADD CONSTRAINT FK_CHT_CAREGIVER
    FOREIGN KEY (cgid) REFERENCES CAREGIVERS (cgid);

-- DATETIMEEVENTS → D_ITEMS
ALTER TABLE DATETIMEEVENTS
    ADD CONSTRAINT FK_DTE_ITEM
    FOREIGN KEY (itemid) REFERENCES D_ITEMS (itemid);

-- OUTPUTEVENTS → ADMISSIONS
ALTER TABLE OUTPUTEVENTS
    ADD CONSTRAINT FK_OUT_ADMISSION
    FOREIGN KEY (hadm_id) REFERENCES ADMISSIONS (hadm_id);

-- PROCEDUREEVENTS_MV → D_ITEMS
ALTER TABLE PROCEDUREEVENTS_MV
    ADD CONSTRAINT FK_PMV_ITEM
    FOREIGN KEY (itemid) REFERENCES D_ITEMS (itemid);

-- PRESCRIPTIONS → ADMISSIONS
ALTER TABLE PRESCRIPTIONS
    ADD CONSTRAINT FK_RX_ADMISSION
    FOREIGN KEY (hadm_id) REFERENCES ADMISSIONS (hadm_id);

-- MICROBIOLOGYEVENTS → ADMISSIONS
ALTER TABLE MICROBIOLOGYEVENTS
    ADD CONSTRAINT FK_MIC_ADMISSION
    FOREIGN KEY (hadm_id) REFERENCES ADMISSIONS (hadm_id);

-- NOTEEVENTS → ADMISSIONS
ALTER TABLE NOTEEVENTS
    ADD CONSTRAINT FK_NOTE_ADMISSION
    FOREIGN KEY (hadm_id) REFERENCES ADMISSIONS (hadm_id);
*/

-- =============================================================================
-- RECOMMENDED INDEXES for query performance
-- =============================================================================

-- ADMISSIONS
CREATE INDEX IX_ADM_SUBJECT    ON ADMISSIONS (subject_id);
CREATE INDEX IX_ADM_HADM       ON ADMISSIONS (hadm_id);
CREATE INDEX IX_ADM_ADMITTIME  ON ADMISSIONS (admittime);

-- PATIENTS
CREATE INDEX IX_PAT_SUBJECT    ON PATIENTS (subject_id);

-- TRANSFERS
CREATE INDEX IX_TRN_HADM       ON TRANSFERS (hadm_id);
CREATE INDEX IX_TRN_ICUSTAY    ON TRANSFERS (icustay_id);

-- CHARTEVENTS
CREATE INDEX IX_CHT_SUBJECT    ON CHARTEVENTS (subject_id);
CREATE INDEX IX_CHT_HADM       ON CHARTEVENTS (hadm_id);
CREATE INDEX IX_CHT_ICUSTAY    ON CHARTEVENTS (icustay_id);
CREATE INDEX IX_CHT_ITEMID     ON CHARTEVENTS (itemid);
CREATE INDEX IX_CHT_CHARTTIME  ON CHARTEVENTS (charttime);

-- DATETIMEEVENTS
CREATE INDEX IX_DTE_HADM       ON DATETIMEEVENTS (hadm_id);
CREATE INDEX IX_DTE_ICUSTAY    ON DATETIMEEVENTS (icustay_id);

-- OUTPUTEVENTS
CREATE INDEX IX_OUT_HADM       ON OUTPUTEVENTS (hadm_id);
CREATE INDEX IX_OUT_ICUSTAY    ON OUTPUTEVENTS (icustay_id);

-- PRESCRIPTIONS
CREATE INDEX IX_RX_HADM        ON PRESCRIPTIONS (hadm_id);
CREATE INDEX IX_RX_ICUSTAY     ON PRESCRIPTIONS (icustay_id);

-- MICROBIOLOGYEVENTS
CREATE INDEX IX_MIC_HADM       ON MICROBIOLOGYEVENTS (hadm_id);
CREATE INDEX IX_MIC_CHARTDATE  ON MICROBIOLOGYEVENTS (chartdate);

-- NOTEEVENTS
CREATE INDEX IX_NOTE_HADM      ON NOTEEVENTS (hadm_id);
CREATE INDEX IX_NOTE_CATEGORY  ON NOTEEVENTS (category);

-- DIAGNOSES_ICD
CREATE INDEX IX_DIAG_HADM      ON DIAGNOSES_ICD (hadm_id);
CREATE INDEX IX_DIAG_ICD9      ON DIAGNOSES_ICD (icd9_code);

-- PROCEDUREEVENTS_MV
CREATE INDEX IX_PMV_HADM       ON PROCEDUREEVENTS_MV (hadm_id);
CREATE INDEX IX_PMV_ICUSTAY    ON PROCEDUREEVENTS_MV (icustay_id);
GO



-- =============================================================================
-- MIMIC-III  —  CREATE TABLE scripts (batch 2)
-- Tables : LABEVENTS, INPUTEVENTS_MV, INPUTEVENTS_CV,
--          ICUSTAYS, DRGCODES, D_LABITEMS
-- Generated from CSV schema analysis
-- Schema  : mimic  (change to dbo or your preferred schema)
-- Compatible with : SQL Server / Azure SQL Database
-- =============================================================================

-- Uncomment to create schema first
-- CREATE SCHEMA mimic;
-- GO

-- =============================================================================
-- 1. D_LABITEMS
--    Reference / dictionary table — load before LABEVENTS (FK dependency)
-- =============================================================================
CREATE TABLE mimic.D_LABITEMS (
                                  row_id     INT           NOT NULL,
                                  itemid     INT           NOT NULL,
                                  label      NVARCHAR(200) NOT NULL,
                                  fluid      NVARCHAR(100) NOT NULL,
                                  category   NVARCHAR(100) NOT NULL,
                                  loinc_code NVARCHAR(20)  NULL,          -- 86 nulls; not all items have a LOINC code
                                  CONSTRAINT PK_D_LABITEMS    PRIMARY KEY (row_id),
                                  CONSTRAINT UQ_D_LABITEMS_ID UNIQUE      (itemid)
);
GO

-- =============================================================================
-- 2. ICUSTAYS
--    One row per ICU stay; bridge between ADMISSIONS and event tables
-- =============================================================================
CREATE TABLE mimic.ICUSTAYS (
                                row_id          INT           NOT NULL,
                                subject_id      INT           NOT NULL,
                                hadm_id         INT           NOT NULL,
                                icustay_id      INT           NOT NULL,
                                dbsource        NVARCHAR(20)  NOT NULL,  -- 'carevue' or 'metavision'
                                first_careunit  NVARCHAR(20)  NOT NULL,
                                last_careunit   NVARCHAR(20)  NOT NULL,
                                first_wardid    SMALLINT      NOT NULL,
                                last_wardid     SMALLINT      NOT NULL,
                                intime          DATETIME2     NOT NULL,
                                outtime         DATETIME2     NOT NULL,
                                los             FLOAT         NOT NULL,  -- length of stay in fractional days
                                CONSTRAINT PK_ICUSTAYS    PRIMARY KEY (row_id),
                                CONSTRAINT UQ_ICUSTAYS_ID UNIQUE      (icustay_id)
);
GO

-- =============================================================================
-- 3. LABEVENTS
--    Lab results; hadm_id nullable — some labs drawn outside a hospital admission
-- =============================================================================
CREATE TABLE mimic.LABEVENTS (
                                 row_id     INT            NOT NULL,
                                 subject_id INT            NOT NULL,
                                 hadm_id    INT            NULL,         -- NULL for outpatient / ED labs
                                 itemid     INT            NOT NULL,
                                 charttime  DATETIME2      NOT NULL,
                                 value      NVARCHAR(200)  NOT NULL,     -- stored as text; numeric values also in valuenum
                                 valuenum   FLOAT          NULL,         -- NULL when value is non-numeric (e.g. ">1000", "NEG")
                                 valueuom   NVARCHAR(20)   NULL,         -- NULL for dimensionless results
                                 flag       NVARCHAR(20)   NULL,         -- NULL = normal; 'abnormal' = outside range
                                 CONSTRAINT PK_LABEVENTS PRIMARY KEY (row_id)
);
GO

-- =============================================================================
-- 4. INPUTEVENTS_MV
--    Metavision input events (IV fluids, medications, nutrition)
--    Richer schema than CareVue — includes order-level detail
-- =============================================================================
CREATE TABLE mimic.INPUTEVENTS_MV (
                                      row_id                         INT           NOT NULL,
                                      subject_id                     INT           NOT NULL,
                                      hadm_id                        INT           NOT NULL,
                                      icustay_id                     INT           NOT NULL,
                                      starttime                      DATETIME2     NOT NULL,
                                      endtime                        DATETIME2     NOT NULL,
                                      itemid                         INT           NOT NULL,
                                      amount                         FLOAT         NOT NULL,
                                      amountuom                      NVARCHAR(20)  NOT NULL,
                                      rate                           FLOAT         NULL,         -- NULL for bolus inputs
                                      rateuom                        NVARCHAR(20)  NULL,         -- NULL when rate is NULL
                                      storetime                      DATETIME2     NOT NULL,
                                      cgid                           INT           NOT NULL,
                                      orderid                        BIGINT        NOT NULL,
                                      linkorderid                    BIGINT        NOT NULL,
                                      ordercategoryname              NVARCHAR(100) NOT NULL,
                                      secondaryordercategoryname     NVARCHAR(200) NULL,         -- NULL for simple orders
                                      ordercomponenttypedescription  NVARCHAR(100) NOT NULL,
                                      ordercategorydescription       NVARCHAR(100) NOT NULL,
                                      patientweight                  FLOAT         NOT NULL,     -- kg at time of order
                                      totalamount                    FLOAT         NULL,         -- NULL for bolus / drug push
                                      totalamountuom                 NVARCHAR(20)  NULL,         -- NULL when totalamount is NULL
                                      isopenbag                      TINYINT       NOT NULL,
                                      continueinnextdept             TINYINT       NOT NULL,
                                      cancelreason                   TINYINT       NOT NULL,
                                      statusdescription              NVARCHAR(50)  NOT NULL,
                                      comments_editedby              NVARCHAR(50)  NULL,         -- NULL when unedited
                                      comments_canceledby            NVARCHAR(50)  NULL,         -- NULL when not cancelled
                                      comments_date                  DATETIME2     NULL,         -- NULL when no comment
                                      originalamount                 FLOAT         NOT NULL,
                                      originalrate                   FLOAT         NOT NULL,
                                      CONSTRAINT PK_INPUTEVENTS_MV PRIMARY KEY (row_id)
);
GO

-- =============================================================================
-- 5. INPUTEVENTS_CV
--    CareVue input events — older system, simpler schema than MV
--    rate / rateuom / originalrate / originalrateuom / originalsite
--    are entirely NULL in this dataset (CareVue did not capture them)
-- =============================================================================
CREATE TABLE mimic.INPUTEVENTS_CV (
                                      row_id            INT           NOT NULL,
                                      subject_id        INT           NOT NULL,
                                      hadm_id           INT           NOT NULL,
                                      icustay_id        INT           NOT NULL,
                                      charttime         DATETIME2     NOT NULL,
                                      itemid            INT           NOT NULL,
                                      amount            FLOAT         NULL,         -- 9 nulls observed
                                      amountuom         NVARCHAR(20)  NULL,         -- 5 nulls observed
                                      rate              FLOAT         NULL,         -- entirely NULL in CareVue
                                      rateuom           NVARCHAR(20)  NULL,         -- entirely NULL in CareVue
                                      storetime         DATETIME2     NOT NULL,
                                      cgid              INT           NOT NULL,
                                      orderid           BIGINT        NOT NULL,
                                      linkorderid       BIGINT        NOT NULL,
                                      stopped           NVARCHAR(20)  NULL,         -- "D/C'd" when discontinued; else NULL
                                      newbottle         TINYINT       NULL,         -- 1 = new bottle started; NULL otherwise
                                      originalamount    FLOAT         NULL,         -- NULL for some CareVue records
                                      originalamountuom NVARCHAR(20)  NOT NULL,
                                      originalroute     NVARCHAR(50)  NOT NULL,
                                      originalrate      FLOAT         NULL,         -- entirely NULL in CareVue
                                      originalrateuom   NVARCHAR(20)  NULL,         -- entirely NULL in CareVue
                                      originalsite      NVARCHAR(100) NULL,         -- entirely NULL in CareVue
                                      CONSTRAINT PK_INPUTEVENTS_CV PRIMARY KEY (row_id)
);
GO

-- =============================================================================
-- 6. DRGCODES
--    Diagnosis-Related Group codes billed per hospital admission
--    drg_severity / drg_mortality are NULL for HCFA DRG type (APR-DRG only)
-- =============================================================================
CREATE TABLE mimic.DRGCODES (
                                row_id       INT            NOT NULL,
                                subject_id   INT            NOT NULL,
                                hadm_id      INT            NOT NULL,
                                drg_type     NVARCHAR(20)   NOT NULL,   -- 'HCFA' or 'APR'
                                drg_code     SMALLINT       NOT NULL,
                                description  NVARCHAR(500)  NOT NULL,
                                drg_severity TINYINT        NULL,        -- APR-DRG only (1-4); NULL for HCFA
                                drg_mortality TINYINT       NULL,        -- APR-DRG only (1-4); NULL for HCFA
                                CONSTRAINT PK_DRGCODES PRIMARY KEY (row_id)
);
GO

-- =============================================================================
-- FOREIGN KEY CONSTRAINTS
-- Uncomment after all tables are populated and data integrity is confirmed
-- =============================================================================

/*
-- LABEVENTS → ADMISSIONS
ALTER TABLE mimic.LABEVENTS
    ADD CONSTRAINT FK_LAB_ADMISSION
    FOREIGN KEY (hadm_id) REFERENCES mimic.ADMISSIONS (hadm_id);

-- LABEVENTS → PATIENTS
ALTER TABLE mimic.LABEVENTS
    ADD CONSTRAINT FK_LAB_PATIENT
    FOREIGN KEY (subject_id) REFERENCES mimic.PATIENTS (subject_id);

-- LABEVENTS → D_LABITEMS
ALTER TABLE mimic.LABEVENTS
    ADD CONSTRAINT FK_LAB_ITEM
    FOREIGN KEY (itemid) REFERENCES mimic.D_LABITEMS (itemid);

-- ICUSTAYS → ADMISSIONS
ALTER TABLE mimic.ICUSTAYS
    ADD CONSTRAINT FK_ICU_ADMISSION
    FOREIGN KEY (hadm_id) REFERENCES mimic.ADMISSIONS (hadm_id);

-- ICUSTAYS → PATIENTS
ALTER TABLE mimic.ICUSTAYS
    ADD CONSTRAINT FK_ICU_PATIENT
    FOREIGN KEY (subject_id) REFERENCES mimic.PATIENTS (subject_id);

-- INPUTEVENTS_MV → ICUSTAYS
ALTER TABLE mimic.INPUTEVENTS_MV
    ADD CONSTRAINT FK_INMV_ICUSTAY
    FOREIGN KEY (icustay_id) REFERENCES mimic.ICUSTAYS (icustay_id);

-- INPUTEVENTS_MV → ADMISSIONS
ALTER TABLE mimic.INPUTEVENTS_MV
    ADD CONSTRAINT FK_INMV_ADMISSION
    FOREIGN KEY (hadm_id) REFERENCES mimic.ADMISSIONS (hadm_id);

-- INPUTEVENTS_MV → D_ITEMS
ALTER TABLE mimic.INPUTEVENTS_MV
    ADD CONSTRAINT FK_INMV_ITEM
    FOREIGN KEY (itemid) REFERENCES mimic.D_ITEMS (itemid);

-- INPUTEVENTS_MV → CAREGIVERS
ALTER TABLE mimic.INPUTEVENTS_MV
    ADD CONSTRAINT FK_INMV_CAREGIVER
    FOREIGN KEY (cgid) REFERENCES mimic.CAREGIVERS (cgid);

-- INPUTEVENTS_CV → ICUSTAYS
ALTER TABLE mimic.INPUTEVENTS_CV
    ADD CONSTRAINT FK_INCV_ICUSTAY
    FOREIGN KEY (icustay_id) REFERENCES mimic.ICUSTAYS (icustay_id);

-- INPUTEVENTS_CV → ADMISSIONS
ALTER TABLE mimic.INPUTEVENTS_CV
    ADD CONSTRAINT FK_INCV_ADMISSION
    FOREIGN KEY (hadm_id) REFERENCES mimic.ADMISSIONS (hadm_id);

-- INPUTEVENTS_CV → D_ITEMS
ALTER TABLE mimic.INPUTEVENTS_CV
    ADD CONSTRAINT FK_INCV_ITEM
    FOREIGN KEY (itemid) REFERENCES mimic.D_ITEMS (itemid);

-- DRGCODES → ADMISSIONS
ALTER TABLE mimic.DRGCODES
    ADD CONSTRAINT FK_DRG_ADMISSION
    FOREIGN KEY (hadm_id) REFERENCES mimic.ADMISSIONS (hadm_id);

-- DRGCODES → PATIENTS
ALTER TABLE mimic.DRGCODES
    ADD CONSTRAINT FK_DRG_PATIENT
    FOREIGN KEY (subject_id) REFERENCES mimic.PATIENTS (subject_id);
*/

-- =============================================================================
-- RECOMMENDED INDEXES
-- =============================================================================

-- LABEVENTS  (very large table — indexes are critical)
CREATE INDEX IX_LAB_SUBJECT    ON mimic.LABEVENTS (subject_id);
CREATE INDEX IX_LAB_HADM       ON mimic.LABEVENTS (hadm_id);
CREATE INDEX IX_LAB_ITEMID     ON mimic.LABEVENTS (itemid);
CREATE INDEX IX_LAB_CHARTTIME  ON mimic.LABEVENTS (charttime);
CREATE INDEX IX_LAB_FLAG       ON mimic.LABEVENTS (flag);

-- ICUSTAYS
CREATE INDEX IX_ICU_SUBJECT    ON mimic.ICUSTAYS (subject_id);
CREATE INDEX IX_ICU_HADM       ON mimic.ICUSTAYS (hadm_id);
CREATE INDEX IX_ICU_INTIME     ON mimic.ICUSTAYS (intime);

-- INPUTEVENTS_MV
CREATE INDEX IX_INMV_SUBJECT   ON mimic.INPUTEVENTS_MV (subject_id);
CREATE INDEX IX_INMV_HADM      ON mimic.INPUTEVENTS_MV (hadm_id);
CREATE INDEX IX_INMV_ICUSTAY   ON mimic.INPUTEVENTS_MV (icustay_id);
CREATE INDEX IX_INMV_ITEMID    ON mimic.INPUTEVENTS_MV (itemid);
CREATE INDEX IX_INMV_STARTTIME ON mimic.INPUTEVENTS_MV (starttime);

-- INPUTEVENTS_CV
CREATE INDEX IX_INCV_SUBJECT   ON mimic.INPUTEVENTS_CV (subject_id);
CREATE INDEX IX_INCV_HADM      ON mimic.INPUTEVENTS_CV (hadm_id);
CREATE INDEX IX_INCV_ICUSTAY   ON mimic.INPUTEVENTS_CV (icustay_id);
CREATE INDEX IX_INCV_ITEMID    ON mimic.INPUTEVENTS_CV (itemid);
CREATE INDEX IX_INCV_CHARTTIME ON mimic.INPUTEVENTS_CV (charttime);

-- DRGCODES
CREATE INDEX IX_DRG_HADM       ON mimic.DRGCODES (hadm_id);
CREATE INDEX IX_DRG_CODE       ON mimic.DRGCODES (drg_code);
CREATE INDEX IX_DRG_TYPE       ON mimic.DRGCODES (drg_type);

-- D_LABITEMS
CREATE INDEX IX_DLAB_ITEMID    ON mimic.D_LABITEMS (itemid);
CREATE INDEX IX_DLAB_LOINC     ON mimic.D_LABITEMS (loinc_code);
GO