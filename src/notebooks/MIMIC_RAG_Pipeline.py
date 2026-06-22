# Databricks notebook source
# MAGIC %md
# MAGIC %md
# MAGIC # Building an AI-Powered Clinical Intelligence System
# MAGIC ### A RAG Pipeline on MIMIC-III Hospital Data
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## The Story: From Raw Hospital Records to AI-Driven Patient Insights
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### WHY — The Problem We Set Out to Solve
# MAGIC
# MAGIC Hospitals generate **massive volumes of patient data** every day — admissions, diagnoses, ICU stays, lab results, medications, and discharge summaries. Yet when a doctor needs a quick, holistic view of a patient's clinical profile, they often have to **manually sift through dozens of records** across multiple systems.
# MAGIC
# MAGIC **The questions we asked:**
# MAGIC - *What if a doctor could type a patient ID and instantly see their full clinical story — enriched with AI-powered insights?*
# MAGIC - *What if the system could recommend prescriptions based on the patient's specific diagnoses and history?*
# MAGIC - *What if those recommendations could be emailed directly to the attending physician — formatted, professional, and ready for review?*
# MAGIC
# MAGIC This project was born from a simple belief: **AI should augment clinical decision-making, not replace it.** We wanted to build a system that turns raw hospital data into actionable intelligence — in seconds, not hours.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### HOW — The Journey of Implementation
# MAGIC
# MAGIC We built this system as a **Retrieval-Augmented Generation (RAG) pipeline** on **Databricks**, using real-world hospital data from the **MIMIC-III** clinical database. Here's how we did it, step by step:
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC #### Phase 1: Data Foundation (Cells 1–5)
# MAGIC **"First, understand the data."**
# MAGIC
# MAGIC We started by exploring the **MIMIC silver layer** — curated tables containing patient admissions (`fact_admissions_enriched`) and ICU stays (`fact_icustays`). Each record tells a piece of a patient's story: their diagnosis, how they arrived, how long they stayed, and whether they survived.
# MAGIC
# MAGIC We then **concatenated key fields** — `subject_id`, `admission_type`, and `diagnosis` — into unified text documents and saved them as `bd_mimic.gold.llm_documents`. This became the raw material for our AI to learn from.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC #### Phase 2: Intelligent Chunking (Cells 6–13)
# MAGIC **"Break the data into digestible pieces."**
# MAGIC
# MAGIC Large language models can't process entire databases at once. So we used **LangChain's `RecursiveCharacterTextSplitter`** to break our documents into **200-character chunks with 20-character overlap** — ensuring no context is lost at boundaries.
# MAGIC
# MAGIC This produced thousands of focused text chunks, each carrying a meaningful snippet of clinical information. These were stored as `bd_mimic.gold.llm_chunks`.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC #### Phase 3: Vector Embeddings (Cells 14–21)
# MAGIC **"Teach the machine to understand meaning, not just words."**
# MAGIC
# MAGIC Using Databricks' **`databricks-bge-large-en`** embedding model, we converted every text chunk into a **1024-dimensional vector** — a mathematical representation of its semantic meaning. The phrase "patient admitted with chest pain" and "emergency cardiac admission" now live close together in vector space.
# MAGIC
# MAGIC We processed embeddings in **batches of 20** (with rate-limit handling) and saved the results as `bd_mimic.gold.llm_embeddings`.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC #### Phase 4: Vector Search Index (Cells 22–24)
# MAGIC **"Build the retrieval engine."**
# MAGIC
# MAGIC We created a **Databricks Vector Search endpoint** (`mimic_vector_endpoint`) and a **Delta Sync index** (`bd_mimic.gold.mimic_llm_index`). This index automatically stays in sync with our embeddings table — any new data flows through seamlessly.
# MAGIC
# MAGIC Now, when someone asks a question, the system:
# MAGIC 1. Converts the question into a vector
# MAGIC 2. Finds the **top 5 most similar chunks** from the index
# MAGIC 3. Returns them as context for the LLM
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC #### Phase 5: RAG Chatbot (Cells 25–40)
# MAGIC **"Give the data a voice."**
# MAGIC
# MAGIC We built the intelligence layer in **three iterations**:
# MAGIC
# MAGIC **v1 — `ask_mimic_bot()`**: A simple function that embeds a question, retrieves context from vector search, and sends it to **Meta Llama 3.3 70B** to generate an answer. We tested it with questions like *"What are common emergency diagnoses?"* and *"What is the average ICU stay for sepsis patients?"*
# MAGIC
# MAGIC **v2 — `ask_mimic_bot_table()`**: Enhanced the bot to return **structured JSON output** that gets rendered as clean Pandas DataFrames — turning free-text answers into tabular insights.
# MAGIC
# MAGIC **v3 — `MimicChatbot` class**: A full conversational chatbot with **memory** — it tracks the last 6 messages, enabling follow-up questions like *"Tell me more about that"* without losing context.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC #### Phase 6: Patient Lookup UI with Prescription & Email (Cells 41–43)
# MAGIC **"Put it all together — one click, full intelligence."**
# MAGIC
# MAGIC The final phase brought everything together into an **interactive user interface** built with `ipywidgets`:
# MAGIC
# MAGIC **Step 1 — Patient Lookup:** Enter any `subject_id` → instantly see demographics, admission history, ICU stays, and **AI-generated clinical insights** from the RAG pipeline.
# MAGIC
# MAGIC **Step 2 — Prescription Generation:** Click one button → the system generates **structured prescription recommendations** using the patient's actual diagnoses + RAG-retrieved medical context. Includes primary medications, supportive drugs, monitoring instructions, and precautions.
# MAGIC
# MAGIC **Step 3 — Email Delivery:** Enter a doctor's name and email → the system generates a **professional HTML prescription report** and sends it via SMTP. Complete with patient summary, prescriptions, and a medical disclaimer.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### WHAT — What This System Achieves
# MAGIC
# MAGIC | Capability | Description |
# MAGIC | --- | --- |
# MAGIC | **Instant Patient Profiles** | Full demographic + clinical history in one view |
# MAGIC | **AI Clinical Insights** | RAG-powered analysis of risk factors and monitoring needs |
# MAGIC | **Smart Prescriptions** | Context-aware medication recommendations |
# MAGIC | **Email Reports** | Professional HTML emails sent directly to physicians |
# MAGIC | **Conversational AI** | Multi-turn chatbot with memory for follow-up questions |
# MAGIC | **Scalable Architecture** | Delta Sync keeps the vector index always up-to-date |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### The Architecture at a Glance
# MAGIC
# MAGIC ```
# MAGIC  MIMIC Silver Tables
# MAGIC  |
# MAGIC  [Concatenate Fields → Gold Documents]
# MAGIC  |
# MAGIC  [LangChain Text Splitter → Gold Chunks]
# MAGIC  |
# MAGIC  [BGE-Large-EN Embeddings → Gold Embeddings]
# MAGIC  |
# MAGIC  [Delta Sync → Vector Search Index]
# MAGIC  |
# MAGIC  [Question] → [Embed] → [Vector Search] → [Top-5 Chunks]
# MAGIC  |
# MAGIC  [Patient Data + RAG Context] → [Llama 3.3 70B]
# MAGIC  |
# MAGIC  [Clinical Insights / Prescriptions]
# MAGIC  |
# MAGIC  [Interactive UI → Email to Doctor]
# MAGIC ```
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### Key Technologies Used
# MAGIC - **Databricks Lakehouse** — Unity Catalog, Delta Lake, Medallion Architecture
# MAGIC - **LangChain** — Text splitting and chunking
# MAGIC - **Databricks BGE-Large-EN** — Embedding model (1024-dim vectors)
# MAGIC - **Databricks Vector Search** — Delta Sync index for semantic retrieval
# MAGIC - **Meta Llama 3.3 70B Instruct** — Large language model for generation
# MAGIC - **ipywidgets** — Interactive notebook UI
# MAGIC - **Python smtplib** — Email delivery
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC > *"This project demonstrates that with the right architecture, raw hospital data can be transformed into a real-time clinical intelligence system — one that doesn't just store information, but understands it."*
# MAGIC
# MAGIC ---
# MAGIC **Let's begin. Scroll down to see each phase in action.** ↓

# COMMAND ----------

# DBTITLE 1,Cell 2
spark.sql("SHOW TABLES IN mimic_catalog.silver").show()

# COMMAND ----------

# DBTITLE 1,Cell 3
df = spark.read.table("mimic_catalog.silver.fact_admissions_enriched")

display(df)

# COMMAND ----------

# DBTITLE 1,Cell 4
from pyspark.sql.functions import concat_ws

df = spark.read.table("mimic_catalog.silver.fact_admissions_enriched")

documents = df.select(
    concat_ws(
        " ",
        "subject_id",
        "admission_type",
        "diagnosis"
    ).alias("text")
)

display(documents)

# COMMAND ----------

# DBTITLE 1,Cell 5
documents.write.mode("overwrite").saveAsTable("mimic_catalog.gold.llm_documents")

# COMMAND ----------

# DBTITLE 1,Cell 6
spark.read.table("mimic_catalog.gold.llm_documents").show()

# COMMAND ----------

# MAGIC %pip install langchain langchain-text-splitters

# COMMAND ----------

# DBTITLE 1,Cell 8
docs = spark.read.table("mimic_catalog.gold.llm_documents")

display(docs)

# COMMAND ----------

docs_pd = docs.toPandas()

texts = docs_pd["text"].tolist()

# COMMAND ----------

# DBTITLE 1,Cell 10
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=20
)

chunks = []

for t in texts:
    chunks.extend(splitter.split_text(t))

# COMMAND ----------

chunk_df = spark.createDataFrame([(c,) for c in chunks], ["chunk_text"])

display(chunk_df)

# COMMAND ----------

# DBTITLE 1,Cell 12
chunk_df.write.mode("overwrite").saveAsTable("mimic_catalog.gold.llm_chunks")

# COMMAND ----------

# DBTITLE 1,Cell 13
spark.read.table("mimic_catalog.gold.llm_chunks").show()

# COMMAND ----------

# MAGIC %pip install databricks-genai-inference

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# DBTITLE 1,Cell 16
chunks_df = spark.read.table("mimic_catalog.gold.llm_chunks")

display(chunks_df)

# COMMAND ----------

chunks_pd = chunks_df.toPandas()

texts = chunks_pd["chunk_text"].tolist()

# COMMAND ----------

from databricks_genai_inference import Embedding
import time

batch_size = 20
all_embeddings = []

for i in range(0, len(texts), batch_size):
    
    batch = texts[i:i+batch_size]
    
    response = Embedding.create(
        model="databricks-bge-large-en",
        input=batch
    )
    
    all_embeddings.extend(response.embeddings)
    
    time.sleep(1)   # prevents hitting rate limit

# COMMAND ----------

chunks_pd["embedding"] = all_embeddings

# COMMAND ----------

# DBTITLE 1,Cell 20
embeddings_df = spark.createDataFrame(chunks_pd)

embeddings_df.write.mode("overwrite").saveAsTable(
    "mimic_catalog.gold.llm_embeddings"
)

# COMMAND ----------

# DBTITLE 1,Cell 21
spark.read.table("mimic_catalog.gold.llm_embeddings").show()

# COMMAND ----------

# MAGIC %pip install databricks-vectorsearch
# MAGIC
# MAGIC from databricks.vector_search.client import VectorSearchClient
# MAGIC
# MAGIC vsc = VectorSearchClient()
# MAGIC
# MAGIC # List existing vector search endpoints
# MAGIC endpoints = vsc.list_endpoints()
# MAGIC print(endpoints)

# COMMAND ----------

# DBTITLE 1,Cell 23
spark.sql("""
    ALTER TABLE mimic_catalog.gold.llm_embeddings
    SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")

try:
    vsc.create_endpoint(name="mimic_vector_endpoint")
    print("Endpoint created successfully.")
except Exception as e:
    if "already exists" in str(e) or "exceeded quota" in str(e):
        print("Endpoint already exists, skipping creation.")
    else:
        raise

try:
    vsc.create_delta_sync_index(
        endpoint_name="mimic_vector_endpoint",
        source_table_name="mimic_catalog.gold.llm_embeddings",
        index_name="mimic_catalog.gold.mimic_llm_index",
        primary_key="chunk_text",
        pipeline_type="TRIGGERED",
        embedding_dimension=1024,
        embedding_vector_column="embedding"
    )
except Exception as e:
    if "already exists" in str(e):
        print("Index already exists, skipping creation.")
    else:
        raise

# COMMAND ----------

# DBTITLE 1,Cell 24
from databricks_genai_inference import ChatCompletion, Embedding

question = "What diagnoses lead to emergency admission?"

query_embedding = Embedding.create(
    model="databricks-bge-large-en",
    input=[question]
).embeddings[0]

index = vsc.get_index("mimic_vector_endpoint", "mimic_catalog.gold.mimic_llm_index")
index.wait_until_ready()
results = index.similarity_search(
    query_vector=query_embedding,
    columns=["chunk_text"],
    num_results=5
)

context = "\n".join([r[0] for r in results['result']['data_array']])

prompt = f"""
Answer the question using the context.

Context:
{context}

Question:
{question}
"""

response = ChatCompletion.create(
    model="databricks-meta-llama-3-3-70b-instruct",
    messages=[{"role":"user","content":prompt}]
)

print(response.message)

# COMMAND ----------

from databricks_genai_inference import ChatCompletion

context = "\n".join([r[0] for r in results['result']['data_array']])

prompt = f"""
Answer the question using the context.

Context:
{context}

Question:
What diagnoses lead to emergency admission?
"""

response = ChatCompletion.create(
    model="databricks-meta-llama-3-3-70b-instruct",
    messages=[{"role":"user","content":prompt}]
)

print(response.message)

# COMMAND ----------

def ask_mimic_bot(question):

    # create embedding for the question
    query_response = Embedding.create(
        model="databricks-bge-large-en",
        input=[question]
    )

    query_vector = query_response.embeddings[0]

    # retrieve similar records
    results = index.similarity_search(
        query_vector=query_vector,
        columns=["chunk_text"],
        num_results=5
    )

    # build context
    context = "\n".join([r[0] for r in results['result']['data_array']])

    prompt = f"""
    Answer the question using the context.

    Context:
    {context}

    Question:
    {question}
    """

    response = ChatCompletion.create(
        model="databricks-meta-llama-3-3-70b-instruct",
        messages=[{"role":"user","content":prompt}]
    )

    return response.message

# COMMAND ----------

ask_mimic_bot("What are common emergency diagnoses?")

# COMMAND ----------

# DBTITLE 1,Cell 28
# MAGIC %sql
# MAGIC SELECT AVG(los) AS avg_icu_stay
# MAGIC FROM mimic_catalog.silver.fact_icustays
# MAGIC WHERE subject_id IN (
# MAGIC     SELECT subject_id
# MAGIC     FROM mimic_catalog.silver.fact_admissions_enriched
# MAGIC     WHERE diagnosis LIKE '%SEPSIS%'
# MAGIC )

# COMMAND ----------

import pandas as pd
import re

text = ask_mimic_bot("What diseases are frequently seen in emergency admissions?")

# extract numbered list items
diseases = re.findall(r'\d+\.\s*(.*)', text)

df = pd.DataFrame(diseases, columns=["Common Emergency Diagnoses"])

display(df)

# COMMAND ----------

clean = [d.split("(")[0].strip() for d in diseases]

df = pd.DataFrame(clean, columns=["Disease"])

display(df)

# COMMAND ----------

def ask_mimic_bot_table(question):
    answer = ask_mimic_bot(question)

    diseases = re.findall(r'\d+\.\s*(.*)', answer)

    df = pd.DataFrame(diseases, columns=["Result"])

    display(df)

# COMMAND ----------

ask_mimic_bot_table("what diseases are frequently seen in emergency admissions?")

# COMMAND ----------

from databricks_genai_inference import ChatCompletion
import pandas as pd
import json

def ask_mimic_bot_table(question):

    query_response = Embedding.create(
        model="databricks-bge-large-en",
        input=[question]
    )

    query_vector = query_response.embeddings[0]

    results = index.similarity_search(
        query_vector=query_vector,
        columns=["chunk_text"],
        num_results=5
    )

    context = "\n".join([r[0] for r in results['result']['data_array']])

    prompt = f"""
    Answer the question using the context.

    Context:
    {context}

    Question:
    {question}

    IMPORTANT:
    Return the answer ONLY in JSON format like this:

    {{
      "results": [
        {{"item": "value"}}
      ]
    }}
    """

    response = ChatCompletion.create(
        model="databricks-meta-llama-3-3-70b-instruct",
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.message

    data = json.loads(text)

    df = pd.DataFrame(data["results"])

    display(df)

# COMMAND ----------

ask_mimic_bot_table("What infections are common in emergency hospital admissions?")

# COMMAND ----------

class MimicChatbot:
    def __init__(self, index):
        self.index = index
        self.chat_history = []

    def ask(self, question):
        self.chat_history.append({"role": "user", "content": question})

        # 1. Embed query
        query_vec = Embedding.create(
            model="databricks-bge-large-en",
            input=[question]
        ).embeddings[0]

        # 2. Retrieve context
        results = self.index.similarity_search(
            query_vector=query_vec,
            columns=["chunk_text"],
            num_results=5
        )

        context = "\n".join(
            [r[0] for r in results["result"]["data_array"]]
        )

        # 3. Build conversational prompt
        prompt = f"""
You are a medical data assistant.
Use the context below and conversation history.

Context:
{context}

Conversation:
{self._format_history()}

Answer clearly.
"""

        response = ChatCompletion.create(
            model="databricks-meta-llama-3-3-70b-instruct",
            messages=[{"role": "user", "content": prompt}]
        )

        answer = response.message
        self.chat_history.append({"role": "assistant", "content": answer})
        return answer

    def _format_history(self):
        return "\n".join(
            [f"{m['role']}: {m['content']}" for m in self.chat_history[-6:]]
        )

# COMMAND ----------

# DBTITLE 1,Cell 36
from databricks_genai_inference import Embedding, ChatCompletion
from databricks.vector_search.client import VectorSearchClient
import pandas as pd
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# Ensure vector index is loaded
try:
    vsc = VectorSearchClient()
    index = vsc.get_index(index_name="mimic_catalog.gold.mimic_llm_index")
except Exception:
    pass  # index already loaded from earlier cells


def get_patient_summary(subject_id: int):
    """Fetch patient admissions and ICU stays from MIMIC tables."""
    admissions_df = spark.sql(f"""
        SELECT a.subject_id, a.hadm_id, a.diagnosis, a.admission_type, a.admission_location,
               a.discharge_location, a.insurance, p.gender,
               FLOOR(DATEDIFF(a.admittime, p.dob) / 365.25) AS age,
               DATEDIFF(a.dischtime, a.admittime) AS length_of_stay_days,
               a.admittime, a.dischtime, a.hospital_expire_flag, a.marital_status, a.ethnicity
        FROM mimic_catalog.silver.fact_admissions a
        JOIN mimic_catalog.silver.dim_patients p ON a.subject_id = p.subject_id
        WHERE a.subject_id = {subject_id}
        ORDER BY a.admittime
    """).toPandas()

    icu_df = spark.sql(f"""
        SELECT icustay_id, hadm_id, first_careunit, last_careunit, los,
               intime, outtime
        FROM mimic_catalog.silver.fact_icustays
        WHERE subject_id = {subject_id}
        ORDER BY intime
    """).toPandas()

    return admissions_df, icu_df


def _build_patient_context(admissions_df, icu_df, subject_id):
    """Build patient context string for LLM prompts."""
    diagnoses = admissions_df["diagnosis"].tolist()
    diagnosis_str = ", ".join(diagnoses) if diagnoses else "No diagnoses found"
    icu_units = icu_df["first_careunit"].unique().tolist() if not icu_df.empty else []
    avg_los = round(icu_df["los"].mean(), 2) if not icu_df.empty else "N/A"
    return diagnosis_str, icu_units, avg_los


def _retrieve_rag_context(question):
    """Embed question and retrieve context from vector index."""
    query_vec = Embedding.create(
        model="databricks-bge-large-en",
        input=[question]
    ).embeddings[0]

    results = index.similarity_search(
        query_vector=query_vec,
        columns=["chunk_text"],
        num_results=5
    )
    return "\n".join([r[0] for r in results["result"]["data_array"]])


def generate_patient_insights(admissions_df, icu_df, subject_id: int):
    """Use RAG to generate AI insights about the patient."""
    diagnosis_str, icu_units, avg_los = _build_patient_context(admissions_df, icu_df, subject_id)

    question = (
        f"Patient {subject_id} has the following diagnoses: {diagnosis_str}. "
        f"They had {len(icu_df)} ICU stay(s) in units: {', '.join(icu_units) if icu_units else 'none'}. "
        f"Average ICU length of stay: {avg_los} days. "
        f"Provide a clinical summary and key risk factors for this patient."
    )

    context = _retrieve_rag_context(question)

    prompt = f"""
You are a medical data assistant analyzing a patient record.

Patient Context:
{context}

Patient Details:
- Subject ID: {subject_id}
- Diagnoses: {diagnosis_str}
- ICU Stays: {len(icu_df)} (Units: {', '.join(icu_units) if icu_units else 'none'})
- Avg ICU LOS: {avg_los} days

Provide:
1. A brief clinical summary
2. Key risk factors based on their diagnoses
3. Recommended areas for monitoring
"""

    response = ChatCompletion.create(
        model="databricks-meta-llama-3-3-70b-instruct",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.message


def generate_prescription(admissions_df, icu_df, subject_id: int):
    """Use RAG to generate prescription recommendations for the patient."""
    diagnosis_str, icu_units, avg_los = _build_patient_context(admissions_df, icu_df, subject_id)

    question = (
        f"What medications and prescriptions are recommended for a patient with: {diagnosis_str}? "
        f"Consider ICU stay history and post-discharge care."
    )

    context = _retrieve_rag_context(question)

    row = admissions_df.iloc[0]
    prompt = f"""
You are a clinical pharmacist assistant reviewing a patient record.

Medical Context:
{context}

Patient Details:
- Subject ID: {subject_id}
- Age: {row.get('age', 'N/A')} | Gender: {row.get('gender', 'N/A')}
- Diagnoses: {diagnosis_str}
- ICU Stays: {len(icu_df)} (Units: {', '.join(icu_units) if icu_units else 'none'})
- Avg ICU LOS: {avg_los} days
- Insurance: {row.get('insurance', 'N/A')}

Provide a structured prescription recommendation:
1. **Primary Medications** — Drug name, dosage, frequency, route
2. **Supportive Medications** — Supplements, pain management, etc.
3. **Monitoring Instructions** — Lab tests, vitals to track
4. **Special Precautions** — Drug interactions, contraindications, allergies to check

IMPORTANT: This is for educational/demo purposes using synthetic MIMIC data.
"""

    response = ChatCompletion.create(
        model="databricks-meta-llama-3-3-70b-instruct",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.message


def build_prescription_email_html(subject_id, admissions_df, icu_df, prescription_text, doctor_name):
    """Build a professional HTML email body for the prescription."""
    row = admissions_df.iloc[0]
    diagnosis_str = ", ".join(admissions_df["diagnosis"].tolist())
    now = datetime.now().strftime("%B %d, %Y %I:%M %p")

    prescription_html = prescription_text.replace("\n", "<br>")

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; max-width: 700px; margin: auto;">
        <div style="background: #0073e6; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
            <h2 style="margin:0;">🏥 MIMIC Clinical Prescription Report</h2>
            <p style="margin:5px 0 0 0;">Generated: {now}</p>
        </div>
        <div style="padding: 20px; border: 1px solid #ddd; border-top: none;">
            <h3>Patient Information</h3>
            <table style="border-collapse:collapse; width:100%;">
                <tr><td style="padding:8px; border:1px solid #ddd; width:30%;"><b>Patient ID</b></td>
                    <td style="padding:8px; border:1px solid #ddd;">{subject_id}</td></tr>
                <tr><td style="padding:8px; border:1px solid #ddd;"><b>Gender / Age</b></td>
                    <td style="padding:8px; border:1px solid #ddd;">{row.get('gender', 'N/A')} / {row.get('age', 'N/A')} years</td></tr>
                <tr><td style="padding:8px; border:1px solid #ddd;"><b>Diagnoses</b></td>
                    <td style="padding:8px; border:1px solid #ddd;">{diagnosis_str}</td></tr>
                <tr><td style="padding:8px; border:1px solid #ddd;"><b>ICU Stays</b></td>
                    <td style="padding:8px; border:1px solid #ddd;">{len(icu_df)}</td></tr>
                <tr><td style="padding:8px; border:1px solid #ddd;"><b>Attending Doctor</b></td>
                    <td style="padding:8px; border:1px solid #ddd;">Dr. {doctor_name}</td></tr>
            </table>

            <h3 style="margin-top:20px;">💊 Prescription Recommendations</h3>
            <div style="background:#f8f9fa; padding:15px; border-radius:8px; border-left:4px solid #28a745;">
                {prescription_html}
            </div>

            <hr style="margin-top:25px;">
            <p style="font-size:11px; color:#999;">⚠️ <b>Disclaimer:</b> This prescription report is generated by an AI system using 
            synthetic MIMIC-III data for educational/demo purposes only. It is NOT a substitute for professional medical advice. 
            Always consult a licensed healthcare provider before making clinical decisions.</p>
        </div>
    </body>
    </html>
    """
    return html


def send_prescription_email(recipient_email, subject_id, admissions_df, icu_df, prescription_text, doctor_name,
                            smtp_server="smtp.gmail.com", smtp_port=587, sender_email=None, sender_password=None):
    """Send prescription email. Returns (success: bool, message: str)."""
    html_body = build_prescription_email_html(subject_id, admissions_df, icu_df, prescription_text, doctor_name)
    subject = f"Prescription Report — Patient {subject_id} | Dr. {doctor_name}"

    if not sender_email or not sender_password:
        # Return the HTML for preview when SMTP credentials are not configured
        return False, html_body

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())

        return True, f"Email sent successfully to {recipient_email}"
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"


print("✅ Patient lookup, prescription, and email functions loaded.")

# COMMAND ----------

import ipywidgets as widgets
from IPython.display import display, HTML, clear_output

# --- State to hold current patient data ---
_state = {"admissions_df": None, "icu_df": None, "subject_id": None, "prescription": None}

# ===================== WIDGETS =====================

# Patient Input Section
patient_id_input = widgets.Text(
    value="10029",
    placeholder="Enter Patient ID (subject_id)",
    description="Patient ID:",
    style={"description_width": "100px"},
    layout=widgets.Layout(width="350px")
)

lookup_button = widgets.Button(
    description="\U0001f50d Lookup Patient",
    button_style="primary",
    layout=widgets.Layout(width="200px", height="38px")
)

# Doctor / Email Section
doctor_name_input = widgets.Text(
    value="",
    placeholder="Enter doctor's name",
    description="Doctor Name:",
    style={"description_width": "120px"},
    layout=widgets.Layout(width="350px")
)

recipient_email_input = widgets.Text(
    value="",
    placeholder="Recipient email address",
    description="Send Email To:",
    style={"description_width": "120px"},
    layout=widgets.Layout(width="400px")
)

smtp_server_input = widgets.Text(
    value="smtp.gmail.com",
    description="SMTP Server:",
    style={"description_width": "120px"},
    layout=widgets.Layout(width="350px")
)

smtp_port_input = widgets.IntText(
    value=587,
    description="SMTP Port:",
    style={"description_width": "120px"},
    layout=widgets.Layout(width="220px")
)

sender_email_input = widgets.Text(
    value="",
    placeholder="Your Gmail address (sender)",
    description="Sender Email:",
    style={"description_width": "120px"},
    layout=widgets.Layout(width="400px")
)

sender_password_input = widgets.Password(
    value="",
    placeholder="App password (not your login password)",
    description="App Password:",
    style={"description_width": "120px"},
    layout=widgets.Layout(width="400px")
)

generate_rx_button = widgets.Button(
    description="\U0001f48a Generate Prescription",
    button_style="info",
    layout=widgets.Layout(width="250px", height="38px"),
    disabled=True
)

send_email_button = widgets.Button(
    description="\U0001f4e7 Send Prescription Email",
    button_style="success",
    layout=widgets.Layout(width="270px", height="38px"),
    disabled=True
)

# Output areas
output_area = widgets.Output(
    layout=widgets.Layout(border="1px solid #ddd", padding="15px", margin="10px 0", width="100%", min_height="200px")
)

rx_output_area = widgets.Output(
    layout=widgets.Layout(border="1px solid #ddd", padding="15px", margin="10px 0", width="100%", min_height="100px")
)

email_output_area = widgets.Output(
    layout=widgets.Layout(border="1px solid #ddd", padding="15px", margin="10px 0", width="100%", min_height="100px")
)

# SMTP config toggle
smtp_toggle = widgets.ToggleButton(
    value=False,
    description="Show SMTP Settings",
    button_style="",
    icon="cog",
    layout=widgets.Layout(width="200px")
)

smtp_box = widgets.VBox(
    [smtp_server_input, smtp_port_input, sender_email_input, sender_password_input],
    layout=widgets.Layout(display="none", padding="10px", border="1px dashed #ccc", margin="5px 0")
)

def toggle_smtp(change):
    smtp_box.layout.display = "block" if change["new"] else "none"

smtp_toggle.observe(toggle_smtp, names="value")

# ===================== CALLBACKS =====================

def on_lookup_click(btn):
    output_area.clear_output()
    rx_output_area.clear_output()
    email_output_area.clear_output()
    generate_rx_button.disabled = True
    send_email_button.disabled = True
    _state["prescription"] = None

    with output_area:
        try:
            sid = int(patient_id_input.value.strip())
        except ValueError:
            display(HTML("<p style='color:red;'>\u274c Please enter a valid numeric Patient ID.</p>"))
            return

        display(HTML(f"<h3>\u23f3 Loading data for Patient {sid}...</h3>"))

        admissions_df, icu_df = get_patient_summary(sid)
        clear_output(wait=True)

        if admissions_df.empty:
            display(HTML(f"<p style='color:red;'>\u274c No records found for Patient ID <b>{sid}</b>. Try another ID.</p>"))
            return

        # Save state
        _state["admissions_df"] = admissions_df
        _state["icu_df"] = icu_df
        _state["subject_id"] = sid

        # Patient Demographics
        row = admissions_df.iloc[0]
        demo_html = f"""
        <h3>\U0001f464 Patient {sid} \u2014 Overview</h3>
        <table style='border-collapse:collapse; width:60%;'>
            <tr><td style='padding:6px; border:1px solid #ddd;'><b>Gender</b></td>
                <td style='padding:6px; border:1px solid #ddd;'>{row.get('gender', 'N/A')}</td></tr>
            <tr><td style='padding:6px; border:1px solid #ddd;'><b>Age</b></td>
                <td style='padding:6px; border:1px solid #ddd;'>{row.get('age', 'N/A')}</td></tr>
            <tr><td style='padding:6px; border:1px solid #ddd;'><b>Ethnicity</b></td>
                <td style='padding:6px; border:1px solid #ddd;'>{row.get('ethnicity', 'N/A')}</td></tr>
            <tr><td style='padding:6px; border:1px solid #ddd;'><b>Marital Status</b></td>
                <td style='padding:6px; border:1px solid #ddd;'>{row.get('marital_status', 'N/A')}</td></tr>
            <tr><td style='padding:6px; border:1px solid #ddd;'><b>Insurance</b></td>
                <td style='padding:6px; border:1px solid #ddd;'>{row.get('insurance', 'N/A')}</td></tr>
            <tr><td style='padding:6px; border:1px solid #ddd;'><b>Total Admissions</b></td>
                <td style='padding:6px; border:1px solid #ddd;'>{len(admissions_df)}</td></tr>
            <tr><td style='padding:6px; border:1px solid #ddd;'><b>Total ICU Stays</b></td>
                <td style='padding:6px; border:1px solid #ddd;'>{len(icu_df)}</td></tr>
        </table>
        """
        display(HTML(demo_html))

        # Admission History
        display(HTML("<h3>\U0001f3e5 Admission History</h3>"))
        adm_display = admissions_df[[
            "hadm_id", "diagnosis", "admission_type", "admittime",
            "dischtime", "length_of_stay_days", "hospital_expire_flag"
        ]].copy()
        adm_display.columns = ["Admission ID", "Diagnosis", "Type", "Admitted", "Discharged", "LOS (days)", "Expired"]
        display(adm_display)

        # ICU Stays
        if not icu_df.empty:
            display(HTML("<h3>\U0001f6cf\ufe0f ICU Stay History</h3>"))
            icu_display = icu_df[[
                "icustay_id", "hadm_id", "first_careunit", "last_careunit", "los", "intime", "outtime"
            ]].copy()
            icu_display.columns = ["ICU Stay ID", "Admission ID", "First Unit", "Last Unit", "LOS (days)", "ICU In", "ICU Out"]
            display(icu_display)

        # AI Clinical Insights
        display(HTML("<h3>\U0001f916 AI Clinical Insights</h3>"))
        display(HTML("<p><i>Generating insights using RAG pipeline...</i></p>"))
        try:
            insights = generate_patient_insights(admissions_df, icu_df, sid)
            formatted = insights.replace("\n", "<br>")
            display(HTML(f"<div style='background:#f8f9fa; padding:15px; border-radius:8px; border-left:4px solid #0073e6;'>{formatted}</div>"))
        except Exception as e:
            display(HTML(f"<p style='color:orange;'>\u26a0\ufe0f Could not generate AI insights: {e}</p>"))

        # Enable prescription button
        generate_rx_button.disabled = False


def on_generate_rx_click(btn):
    rx_output_area.clear_output()
    email_output_area.clear_output()
    send_email_button.disabled = True

    with rx_output_area:
        if _state["admissions_df"] is None:
            display(HTML("<p style='color:red;'>\u274c Please lookup a patient first.</p>"))
            return

        display(HTML("<h3>\U0001f48a Generating Prescription Recommendations...</h3>"))
        display(HTML("<p><i>Analyzing patient data with RAG pipeline...</i></p>"))

        try:
            rx = generate_prescription(_state["admissions_df"], _state["icu_df"], _state["subject_id"])
            _state["prescription"] = rx
            clear_output(wait=True)

            display(HTML("<h3>\U0001f48a Prescription Recommendations</h3>"))
            rx_html = rx.replace("\n", "<br>")
            display(HTML(f"<div style='background:#f0fff0; padding:15px; border-radius:8px; border-left:4px solid #28a745;'>{rx_html}</div>"))
            display(HTML("<p style='color:#28a745;'>\u2705 Prescription ready. Fill in doctor name and email below, then click <b>Send Prescription Email</b>.</p>"))

            send_email_button.disabled = False
        except Exception as e:
            clear_output(wait=True)
            display(HTML(f"<p style='color:red;'>\u274c Error generating prescription: {e}</p>"))


def on_send_email_click(btn):
    email_output_area.clear_output()

    with email_output_area:
        if _state["prescription"] is None:
            display(HTML("<p style='color:red;'>\u274c Please generate a prescription first.</p>"))
            return

        doctor = doctor_name_input.value.strip()
        recipient = recipient_email_input.value.strip()

        if not doctor:
            display(HTML("<p style='color:red;'>\u274c Please enter the doctor's name.</p>"))
            return
        if not recipient or "@" not in recipient:
            display(HTML("<p style='color:red;'>\u274c Please enter a valid recipient email address.</p>"))
            return

        sender = sender_email_input.value.strip() or None
        password = sender_password_input.value.strip() or None
        smtp_srv = smtp_server_input.value.strip()
        smtp_prt = smtp_port_input.value

        display(HTML("<h3>\U0001f4e7 Sending Prescription Email...</h3>"))

        success, result = send_prescription_email(
            recipient_email=recipient,
            subject_id=_state["subject_id"],
            admissions_df=_state["admissions_df"],
            icu_df=_state["icu_df"],
            prescription_text=_state["prescription"],
            doctor_name=doctor,
            smtp_server=smtp_srv,
            smtp_port=smtp_prt,
            sender_email=sender,
            sender_password=password
        )

        clear_output(wait=True)

        if success:
            display(HTML(f"<p style='color:#28a745; font-size:16px;'>\u2705 <b>{result}</b></p>"))
        else:
            if "<html>" in result:
                # No SMTP configured — show email preview
                display(HTML("<h3>\U0001f4e7 Email Preview</h3>"))
                display(HTML("<p style='color:#e67300;'>\u26a0\ufe0f SMTP credentials not configured. Showing email preview below. "
                             "To send emails, click <b>Show SMTP Settings</b> and fill in your credentials.</p>"))
                display(HTML(f"<p><b>To:</b> {recipient} | <b>Subject:</b> Prescription Report \u2014 Patient {_state['subject_id']} | Dr. {doctor}</p>"))
                display(HTML(f"<div style='border:2px solid #ddd; border-radius:8px; margin-top:10px;'>{result}</div>"))
            else:
                display(HTML(f"<p style='color:red;'>\u274c {result}</p>"))


# ===================== BIND CALLBACKS =====================
lookup_button.on_click(on_lookup_click)
generate_rx_button.on_click(on_generate_rx_click)
send_email_button.on_click(on_send_email_click)

# ===================== LAYOUT =====================
header = HTML("<h2>\U0001f3e5 MIMIC Patient Lookup \u2014 RAG Pipeline</h2>")
step1_label = HTML("<b>Step 1:</b> Enter Patient ID and click Lookup")
step2_label = HTML("<b>Step 2:</b> Review data, then generate prescription")
step3_label = HTML("<b>Step 3:</b> Enter doctor info and send email")

display(header)
display(step1_label)
display(widgets.HBox([patient_id_input, lookup_button]))
display(output_area)

display(HTML("<hr>"))
display(step2_label)
display(generate_rx_button)
display(rx_output_area)

display(HTML("<hr>"))
display(step3_label)
display(widgets.HBox([doctor_name_input, recipient_email_input]))
display(widgets.HBox([send_email_button, smtp_toggle]))
display(smtp_box)
display(email_output_area)

# COMMAND ----------

# DBTITLE 1,Cell 38
from databricks_genai_inference import Embedding, ChatCompletion
from databricks.vector_search.client import VectorSearchClient
import pandas as pd
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# Ensure vector index is loaded
try:
    vsc = VectorSearchClient()
    index = vsc.get_index(index_name="mimic_catalog.gold.mimic_llm_index")
except Exception:
    pass  # index already loaded from earlier cells


def get_patient_summary(subject_id: int):
    """Fetch patient admissions and ICU stays from MIMIC tables."""
    admissions_df = spark.sql(f"""
        SELECT subject_id, hadm_id, diagnosis, admission_type, admission_location,
               discharge_location, insurance, gender, age, length_of_stay_days,
               admittime, dischtime, hospital_expire_flag, marital_status, ethnicity
        FROM mimic_catalog.silver.fact_admissions_enriched
        WHERE subject_id = {subject_id}
        ORDER BY admittime
    """).toPandas()

    icu_df = spark.sql(f"""
        SELECT icustay_id, hadm_id, first_careunit, last_careunit, los,
               intime, outtime
        FROM mimic_catalog.silver.fact_icustays
        WHERE subject_id = {subject_id}
        ORDER BY intime
    """).toPandas()

    return admissions_df, icu_df


def _build_patient_context(admissions_df, icu_df, subject_id):
    """Build patient context string for LLM prompts."""
    diagnoses = admissions_df["diagnosis"].tolist()
    diagnosis_str = ", ".join(diagnoses) if diagnoses else "No diagnoses found"
    icu_units = icu_df["first_careunit"].unique().tolist() if not icu_df.empty else []
    avg_los = round(icu_df["los"].mean(), 2) if not icu_df.empty else "N/A"
    return diagnosis_str, icu_units, avg_los


def _retrieve_rag_context(question):
    """Embed question and retrieve context from vector index."""
    query_vec = Embedding.create(
        model="databricks-bge-large-en",
        input=[question]
    ).embeddings[0]

    results = index.similarity_search(
        query_vector=query_vec,
        columns=["chunk_text"],
        num_results=5
    )
    return "\n".join([r[0] for r in results["result"]["data_array"]])


def generate_patient_insights(admissions_df, icu_df, subject_id: int):
    """Use RAG to generate AI insights about the patient."""
    diagnosis_str, icu_units, avg_los = _build_patient_context(admissions_df, icu_df, subject_id)

    question = (
        f"Patient {subject_id} has the following diagnoses: {diagnosis_str}. "
        f"They had {len(icu_df)} ICU stay(s) in units: {', '.join(icu_units) if icu_units else 'none'}. "
        f"Average ICU length of stay: {avg_los} days. "
        f"Provide a clinical summary and key risk factors for this patient."
    )

    context = _retrieve_rag_context(question)

    prompt = f"""
You are a medical data assistant analyzing a patient record.

Patient Context:
{context}

Patient Details:
- Subject ID: {subject_id}
- Diagnoses: {diagnosis_str}
- ICU Stays: {len(icu_df)} (Units: {', '.join(icu_units) if icu_units else 'none'})
- Avg ICU LOS: {avg_los} days

Provide:
1. A brief clinical summary
2. Key risk factors based on their diagnoses
3. Recommended areas for monitoring
"""

    response = ChatCompletion.create(
        model="databricks-meta-llama-3-3-70b-instruct",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.message


def generate_prescription(admissions_df, icu_df, subject_id: int):
    """Use RAG to generate prescription recommendations for the patient."""
    diagnosis_str, icu_units, avg_los = _build_patient_context(admissions_df, icu_df, subject_id)

    question = (
        f"What medications and prescriptions are recommended for a patient with: {diagnosis_str}? "
        f"Consider ICU stay history and post-discharge care."
    )

    context = _retrieve_rag_context(question)

    row = admissions_df.iloc[0]
    prompt = f"""
You are a clinical pharmacist assistant reviewing a patient record.

Medical Context:
{context}

Patient Details:
- Subject ID: {subject_id}
- Age: {row.get('age', 'N/A')} | Gender: {row.get('gender', 'N/A')}
- Diagnoses: {diagnosis_str}
- ICU Stays: {len(icu_df)} (Units: {', '.join(icu_units) if icu_units else 'none'})
- Avg ICU LOS: {avg_los} days
- Insurance: {row.get('insurance', 'N/A')}

Provide a structured prescription recommendation:
1. **Primary Medications** - Drug name, dosage, frequency, route
2. **Supportive Medications** - Supplements, pain management, etc.
3. **Monitoring Instructions** - Lab tests, vitals to track
4. **Special Precautions** - Drug interactions, contraindications, allergies to check

IMPORTANT: This is for educational/demo purposes using synthetic MIMIC data.
"""

    response = ChatCompletion.create(
        model="databricks-meta-llama-3-3-70b-instruct",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.message


def build_prescription_email_html(subject_id, admissions_df, icu_df, prescription_text, doctor_name):
    """Build a professional HTML email body for the prescription."""
    row = admissions_df.iloc[0]
    diagnosis_str = ", ".join(admissions_df["diagnosis"].tolist())
    now = datetime.now().strftime("%B %d, %Y %I:%M %p")

    prescription_html = prescription_text.replace("\n", "<br>")

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; max-width: 700px; margin: auto;">
        <div style="background: #0073e6; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
            <h2 style="margin:0;">🏥 MIMIC Clinical Prescription Report</h2>
            <p style="margin:5px 0 0 0;">Generated: {now}</p>
        </div>
        <div style="padding: 20px; border: 1px solid #ddd; border-top: none;">
            <h3>Patient Information</h3>
            <table style="border-collapse:collapse; width:100%;">
                <tr><td style="padding:8px; border:1px solid #ddd; width:30%;"><b>Patient ID</b></td>
                    <td style="padding:8px; border:1px solid #ddd;">{subject_id}</td></tr>
                <tr><td style="padding:8px; border:1px solid #ddd;"><b>Gender / Age</b></td>
                    <td style="padding:8px; border:1px solid #ddd;">{row.get('gender', 'N/A')} / {row.get('age', 'N/A')} years</td></tr>
                <tr><td style="padding:8px; border:1px solid #ddd;"><b>Diagnoses</b></td>
                    <td style="padding:8px; border:1px solid #ddd;">{diagnosis_str}</td></tr>
                <tr><td style="padding:8px; border:1px solid #ddd;"><b>ICU Stays</b></td>
                    <td style="padding:8px; border:1px solid #ddd;">{len(icu_df)}</td></tr>
                <tr><td style="padding:8px; border:1px solid #ddd;"><b>Attending Doctor</b></td>
                    <td style="padding:8px; border:1px solid #ddd;">Dr. {doctor_name}</td></tr>
            </table>

            <h3 style="margin-top:20px;">Prescription Recommendations</h3>
            <div style="background:#f8f9fa; padding:15px; border-radius:8px; border-left:4px solid #28a745;">
                {prescription_html}
            </div>

            <hr style="margin-top:25px;">
            <p style="font-size:11px; color:#999;"><b>Disclaimer:</b> This prescription report is generated by an AI system using 
            synthetic MIMIC-III data for educational/demo purposes only. It is NOT a substitute for professional medical advice. 
            Always consult a licensed healthcare provider before making clinical decisions.</p>
        </div>
    </body>
    </html>
    """
    return html


def send_prescription_email(recipient_email, subject_id, admissions_df, icu_df, prescription_text, doctor_name,
                            smtp_server="smtp.gmail.com", smtp_port=587, sender_email=None, sender_password=None):
    """Send prescription email. Returns (success: bool, message: str)."""
    html_body = build_prescription_email_html(subject_id, admissions_df, icu_df, prescription_text, doctor_name)
    subject = f"Prescription Report - Patient {subject_id} | Dr. {doctor_name}"

    if not sender_email or not sender_password:
        return False, html_body

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())

        return True, f"Email sent successfully to {recipient_email}"
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"


print("Patient lookup, prescription, and email functions loaded.")

# COMMAND ----------

# Step 1: Patient Lookup & AI Insights
# Change the Patient ID in the widget at the top of the notebook, then re-run this cell.

dbutils.widgets.text("patient_id", "10029", "Patient ID")
subject_id = int(dbutils.widgets.get("patient_id").strip())

from IPython.display import display, HTML

display(HTML(f"<h2>\U0001f3e5 MIMIC Patient Lookup — RAG Pipeline</h2>"))
display(HTML(f"<h3>\u23f3 Loading data for Patient {subject_id}...</h3>"))

admissions_df, icu_df = get_patient_summary(subject_id)

if admissions_df.empty:
    display(HTML(f"<p style='color:red;'>\u274c No records found for Patient ID <b>{subject_id}</b>. Try another ID.</p>"))
else:
    # Save state for subsequent cells
    _state = {"admissions_df": admissions_df, "icu_df": icu_df, "subject_id": subject_id, "prescription": None}

    # Patient Demographics
    row = admissions_df.iloc[0]
    demo_html = f"""
    <h3>\U0001f464 Patient {subject_id} — Overview</h3>
    <table style='border-collapse:collapse; width:60%;'>
        <tr><td style='padding:6px; border:1px solid #ddd;'><b>Gender</b></td>
            <td style='padding:6px; border:1px solid #ddd;'>{row.get('gender', 'N/A')}</td></tr>
        <tr><td style='padding:6px; border:1px solid #ddd;'><b>Age</b></td>
            <td style='padding:6px; border:1px solid #ddd;'>{row.get('age', 'N/A')}</td></tr>
        <tr><td style='padding:6px; border:1px solid #ddd;'><b>Ethnicity</b></td>
            <td style='padding:6px; border:1px solid #ddd;'>{row.get('ethnicity', 'N/A')}</td></tr>
        <tr><td style='padding:6px; border:1px solid #ddd;'><b>Marital Status</b></td>
            <td style='padding:6px; border:1px solid #ddd;'>{row.get('marital_status', 'N/A')}</td></tr>
        <tr><td style='padding:6px; border:1px solid #ddd;'><b>Insurance</b></td>
            <td style='padding:6px; border:1px solid #ddd;'>{row.get('insurance', 'N/A')}</td></tr>
        <tr><td style='padding:6px; border:1px solid #ddd;'><b>Total Admissions</b></td>
            <td style='padding:6px; border:1px solid #ddd;'>{len(admissions_df)}</td></tr>
        <tr><td style='padding:6px; border:1px solid #ddd;'><b>Total ICU Stays</b></td>
            <td style='padding:6px; border:1px solid #ddd;'>{len(icu_df)}</td></tr>
    </table>
    """
    display(HTML(demo_html))

    # Admission History
    display(HTML("<h3>\U0001f3e5 Admission History</h3>"))
    adm_display = admissions_df[[
        "hadm_id", "diagnosis", "admission_type", "admittime",
        "dischtime", "length_of_stay_days", "hospital_expire_flag"
    ]].copy()
    adm_display.columns = ["Admission ID", "Diagnosis", "Type", "Admitted", "Discharged", "LOS (days)", "Expired"]
    display(adm_display)

    # ICU Stays
    if not icu_df.empty:
        display(HTML("<h3>\U0001f6cf\ufe0f ICU Stay History</h3>"))
        icu_display = icu_df[[
            "icustay_id", "hadm_id", "first_careunit", "last_careunit", "los", "intime", "outtime"
        ]].copy()
        icu_display.columns = ["ICU Stay ID", "Admission ID", "First Unit", "Last Unit", "LOS (days)", "ICU In", "ICU Out"]
        display(icu_display)

    # AI Clinical Insights
    display(HTML("<h3>\U0001f916 AI Clinical Insights</h3>"))
    display(HTML("<p><i>Generating insights using RAG pipeline...</i></p>"))
    try:
        insights = generate_patient_insights(admissions_df, icu_df, subject_id)
        formatted = insights.replace("\n", "<br>")
        display(HTML(f"<div style='background:#f8f9fa; padding:15px; border-radius:8px; border-left:4px solid #0073e6;'>{formatted}</div>"))
    except Exception as e:
        display(HTML(f"<p style='color:orange;'>\u26a0\ufe0f Could not generate AI insights: {e}</p>"))

    display(HTML("<br><p style='color:#0073e6;'>\u2705 <b>Patient loaded.</b> Run the next cell to generate a prescription.</p>"))

# COMMAND ----------

# DBTITLE 1,Step 2: Generate Prescription
# Step 2: Generate Prescription
# Run this cell after the patient lookup above completes.

from IPython.display import display, HTML

if _state.get("admissions_df") is None:
    display(HTML("<p style='color:red;'>\u274c Please run the Patient Lookup cell (Step 1) first.</p>"))
else:
    sid = _state["subject_id"]
    display(HTML(f"<h3>\U0001f48a Generating Prescription for Patient {sid}...</h3>"))
    display(HTML("<p><i>Analyzing patient data with RAG pipeline...</i></p>"))

    try:
        rx = generate_prescription(_state["admissions_df"], _state["icu_df"], sid)
        _state["prescription"] = rx

        display(HTML("<h3>\U0001f48a Prescription Recommendations</h3>"))
        rx_html = rx.replace("\n", "<br>")
        display(HTML(f"<div style='background:#f0fff0; padding:15px; border-radius:8px; border-left:4px solid #28a745;'>{rx_html}</div>"))
        display(HTML("<br><p style='color:#28a745;'>\u2705 <b>Prescription ready.</b> Run the next cell to preview/send email.</p>"))
    except Exception as e:
        display(HTML(f"<p style='color:red;'>\u274c Error generating prescription: {e}</p>"))

# COMMAND ----------

# DBTITLE 1,Step 3: Email Prescription
# Step 3: Email Prescription
# Fill in ALL widgets at the top of the notebook, then run this cell.
# For Gmail: use an App Password (https://myaccount.google.com/apppasswords), not your regular password.

dbutils.widgets.text("doctor_name", "", "Doctor Name")
dbutils.widgets.text("recipient_email", "", "Recipient Email")
dbutils.widgets.text("sender_email", "", "Sender Email (Gmail)")
dbutils.widgets.text("sender_password", "", "Sender App Password")

from IPython.display import display, HTML

doctor_name = dbutils.widgets.get("doctor_name").strip()
recipient_email = dbutils.widgets.get("recipient_email").strip()
sender_email = dbutils.widgets.get("sender_email").strip()
sender_password = dbutils.widgets.get("sender_password").strip()

if _state.get("prescription") is None:
    display(HTML("<p style='color:red;'>\u274c Please run the Prescription cell (Step 2) first.</p>"))
elif not doctor_name:
    display(HTML("<p style='color:red;'>\u274c Please enter a Doctor Name in the widget at the top of the notebook.</p>"))
elif not recipient_email or "@" not in recipient_email:
    display(HTML("<p style='color:red;'>\u274c Please enter a valid Recipient Email in the widget at the top of the notebook.</p>"))
elif not sender_email or not sender_password:
    display(HTML("<p style='color:orange;'>\u26a0\ufe0f To send the email, fill in <b>Sender Email</b> and <b>Sender App Password</b> widgets at the top.</p>"))
    display(HTML("<p style='color:orange;'>For Gmail, generate an App Password at: <a href='https://myaccount.google.com/apppasswords' target='_blank'>https://myaccount.google.com/apppasswords</a></p>"))
    # Show preview anyway
    html_body = build_prescription_email_html(_state["subject_id"], _state["admissions_df"], _state["icu_df"], _state["prescription"], doctor_name)
    display(HTML("<h3>\U0001f4e7 Email Preview</h3>"))
    display(HTML(f"<p><b>To:</b> {recipient_email} | <b>Subject:</b> Prescription Report - Patient {_state['subject_id']} | Dr. {doctor_name}</p>"))
    display(HTML(f"<div style='border:2px solid #ddd; border-radius:8px; margin-top:10px;'>{html_body}</div>"))
else:
    display(HTML(f"<h3>\U0001f4e7 Sending Prescription Email for Patient {_state['subject_id']}...</h3>"))

    success, result = send_prescription_email(
        recipient_email=recipient_email,
        subject_id=_state["subject_id"],
        admissions_df=_state["admissions_df"],
        icu_df=_state["icu_df"],
        prescription_text=_state["prescription"],
        doctor_name=doctor_name,
        sender_email=sender_email,
        sender_password=sender_password
    )

    if success:
        display(HTML(f"<p style='color:#28a745; font-size:16px;'>\u2705 <b>{result}</b></p>"))
    else:
        display(HTML(f"<p style='color:red;'>\u274c {result}</p>"))