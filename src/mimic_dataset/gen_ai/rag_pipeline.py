"""
RAG Pipeline for MIMIC-III Clinical Intelligence System

This module implements a Retrieval-Augmented Generation (RAG) pipeline
for generating AI-powered clinical insights and prescription recommendations
using the MIMIC-III hospital dataset.

Architecture Flow:
1. Load MIMIC silver tables (patient admissions, ICU stays)
2. Create documents by concatenating clinical fields
3. Split documents into chunks using LangChain
4. Generate embeddings using Databricks BGE-Large-EN model
5. Create Vector Search index for similarity retrieval
6. Use Llama 3.3 70B for RAG-powered generation
7. Generate patient insights and prescriptions
8. Format and email reports

Dependencies:
- databricks-genai-inference: For embeddings and LLM access
- databricks-vectorsearch: For vector index management
- langchain-text-splitters: For document chunking
- pandas: For dataframe manipulation
- pyspark: For distributed data processing
"""

import json
import smtplib
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Tuple, Dict, Any, List, Optional

import pandas as pd
from pyspark.sql.functions import concat_ws

from databricks_genai_inference import ChatCompletion, Embedding
from databricks.vector_search.client import VectorSearchClient
from langchain_text_splitters import RecursiveCharacterTextSplitter

from mimic_dataset.utils.globals import GlobalVariables as G
from mimic_dataset.utils.file import load_config


# ============================================================================
# PHASE 1: DATA FOUNDATION - Create Documents from MIMIC Silver Tables
# ============================================================================

def create_llm_documents(schema_name: Optional[str] = None) -> None:
    """
    Load patient admissions from MIMIC silver layer and create documents.

    Concatenates key clinical fields (subject_id, admission_type, diagnosis)
    into unified text documents. Saves to gold layer as llm_documents table.

    Args:
        schema_name (str): Database schema name (default: "mmc")

    Returns:
        None

    Raises:
        Exception: If Spark tables are not accessible
    """
    # get schema from config if not provided
    if not schema_name:
        config, _ = load_config()
        schema_name = config["schema_name"]

    spark = G.spark

    # Read fact admissions table from silver layer
    df = spark.read.table(f"{schema_name}.silver.fact_admissions_enriched")

    # Concatenate clinical fields into text documents
    documents = df.select(
        concat_ws(
            " ",
            "subject_id",
            "admission_type",
            "diagnosis"
        ).alias("text")
    )

    # Save to gold layer
    documents.write.mode("overwrite").saveAsTable(f"{schema_name}.gold.llm_documents")
    print(f"✅ Created {documents.count()} documents in {schema_name}.gold.llm_documents")


# ============================================================================
# PHASE 2: INTELLIGENT CHUNKING - Split Documents into Chunks
# ============================================================================

def chunk_documents(schema_name: Optional[str] = None, chunk_size: int = 200, chunk_overlap: int = 20) -> None:
    """
    Split documents into manageable chunks using LangChain.

    Uses RecursiveCharacterTextSplitter to break documents into smaller pieces
    with configurable overlap to preserve context at boundaries.

    Args:
        schema_name (str): Database schema name (default: "mmc")
        chunk_size (int): Size of each chunk in characters (default: 200)
        chunk_overlap (int): Overlap between chunks in characters (default: 20)

    Returns:
        None

    Raises:
        Exception: If llm_documents table doesn't exist
    """
    # get schema from config if not provided
    if not schema_name:
        config, _ = load_config()
        schema_name = config["schema_name"]

    spark = G.spark

    # Read documents from gold layer
    docs_df = spark.read.table(f"{schema_name}.gold.llm_documents")
    docs_pd = docs_df.toPandas()
    texts = docs_pd["text"].tolist()

    # Initialize text splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    # Split all texts into chunks
    chunks = []
    for text in texts:
        chunks.extend(splitter.split_text(text))

    # Create dataframe and save to gold layer
    chunk_df = spark.createDataFrame([(c,) for c in chunks], ["chunk_text"])
    chunk_df.write.mode("overwrite").saveAsTable(f"{schema_name}.gold.llm_chunks")
    print(f"✅ Created {len(chunks)} chunks in {schema_name}.gold.llm_chunks")


# ============================================================================
# PHASE 3: VECTOR EMBEDDINGS - Generate Embeddings for Chunks
# ============================================================================

def generate_embeddings(
    schema_name: Optional[str] = None,
    model: str = "databricks-bge-large-en",
    batch_size: int = 20,
    rate_limit_sleep: float = 1.0
) -> None:
    """
    Generate vector embeddings for all text chunks.

    Uses Databricks BGE-Large-EN embedding model to convert chunks into
    1024-dimensional vectors. Processes in batches with rate-limiting.

    Args:
        schema_name (str): Database schema name (default: "mmc")
        model (str): Embedding model name (default: "databricks-bge-large-en")
        batch_size (int): Batch size for embedding API calls (default: 20)
        rate_limit_sleep (float): Sleep time between batches in seconds (default: 1.0)

    Returns:
        None

    Raises:
        Exception: If embedding API is not accessible
    """
    # get schema from config if not provided
    if not schema_name:
        config, _ = load_config()
        schema_name = config["schema_name"]

    spark = G.spark

    # Read chunks from gold layer
    chunks_df = spark.read.table(f"{schema_name}.gold.llm_chunks")
    chunks_pd = chunks_df.toPandas()
    texts = chunks_pd["chunk_text"].tolist()

    # Generate embeddings in batches
    all_embeddings = []
    total_chunks = len(texts)

    for i in range(0, total_chunks, batch_size):
        batch = texts[i:i + batch_size]

        response = Embedding.create(
            model=model,
            input=batch
        )

        all_embeddings.extend(response.embeddings)

        # Rate limiting
        if i + batch_size < total_chunks:
            time.sleep(rate_limit_sleep)

        print(f"  Processed {min(i + batch_size, total_chunks)}/{total_chunks} chunks")

    # Add embeddings to dataframe
    chunks_pd["embedding"] = all_embeddings

    # Convert to Spark dataframe and save
    embeddings_df = spark.createDataFrame(chunks_pd)
    embeddings_df.write.mode("overwrite").saveAsTable(f"{schema_name}.gold.llm_embeddings")
    print(f"✅ Generated embeddings for {len(all_embeddings)} chunks in {schema_name}.gold.llm_embeddings")


# ============================================================================
# PHASE 4: VECTOR SEARCH INDEX - Create Retrieval Index
# ============================================================================

def create_vector_search_index(
    schema_name: Optional[str] = None,
    endpoint_name: str = "mimic_vector_endpoint",
    index_name: str = None
) -> VectorSearchClient:
    """
    Create or retrieve a Databricks Vector Search index.

    Sets up a Delta Sync index that automatically stays in sync with
    the embeddings table. Used for semantic similarity search.

    Args:
        schema_name (str): Database schema name (default: "mmc")
        endpoint_name (str): Vector search endpoint name (default: "mimic_vector_endpoint")
        index_name (str): Full index name (default: "{schema_name}.gold.mimic_llm_index")

    Returns:
        VectorSearchClient: Initialized vector search client

    Raises:
        Exception: If vector search service is unavailable
    """
    # get schema from config if not provided
    if not schema_name:
        config, _ = load_config()
        schema_name = config["schema_name"]

    if index_name is None:
        index_name = f"{schema_name}.gold.mimic_llm_index"

    spark = G.spark
    vsc = VectorSearchClient()

    # Enable Change Data Feed on embeddings table
    spark.sql(f"""
        ALTER TABLE {schema_name}.gold.llm_embeddings
        SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
    """)

    # Create vector search endpoint
    try:
        vsc.create_endpoint(name=endpoint_name)
        print(f"✅ Created Vector Search endpoint: {endpoint_name}")
    except Exception as e:
        if "already exists" in str(e) or "exceeded quota" in str(e):
            print(f"ℹ️  Vector Search endpoint already exists: {endpoint_name}")
        else:
            raise

    # Create Delta Sync index
    try:
        vsc.create_delta_sync_index(
            endpoint_name=endpoint_name,
            source_table_name=f"{schema_name}.gold.llm_embeddings",
            index_name=index_name,
            primary_key="chunk_text",
            pipeline_type="TRIGGERED",
            embedding_dimension=1024,
            embedding_vector_column="embedding"
        )
        print(f"✅ Created Vector Search index: {index_name}")
    except Exception as e:
        if "already exists" in str(e):
            print(f"ℹ️  Vector Search index already exists: {index_name}")
        else:
            raise

    return vsc


# ============================================================================
# PHASE 5: RAG PIPELINE UTILITIES - RAG Context Retrieval & Generation
# ============================================================================

def _retrieve_rag_context(
    question: str,
    index: Any,
    num_results: int = 5,
    model: str = "databricks-bge-large-en"
) -> str:
    """
    Embed question and retrieve similar chunks from vector index.

    Args:
        question (str): User question or query
        index: Vector search index object
        num_results (int): Number of top results to retrieve (default: 5)
        model (str): Embedding model to use (default: "databricks-bge-large-en")

    Returns:
        str: Concatenated context from retrieved chunks
    """
    # Embed the question
    query_vec = Embedding.create(
        model=model,
        input=[question]
    ).embeddings[0]

    # Retrieve similar chunks
    results = index.similarity_search(
        query_vector=query_vec,
        columns=["chunk_text"],
        num_results=num_results
    )

    # Format context
    context = "\n".join([r[0] for r in results["result"]["data_array"]])
    return context


def _build_patient_context(
    admissions_df: pd.DataFrame,
    icu_df: pd.DataFrame,
    subject_id: int
) -> Tuple[str, List[str], float]:
    """
    Build clinical context from patient admission and ICU data.

    Args:
        admissions_df (pd.DataFrame): Patient admission records
        icu_df (pd.DataFrame): Patient ICU stay records
        subject_id (int): Patient ID

    Returns:
        Tuple[str, List[str], float]: (diagnoses_string, icu_units_list, avg_los)
    """
    diagnoses = admissions_df["diagnosis"].tolist()
    diagnosis_str = ", ".join(diagnoses) if diagnoses else "No diagnoses found"

    icu_units = icu_df["first_careunit"].unique().tolist() if not icu_df.empty else []
    avg_los = round(icu_df["los"].mean(), 2) if not icu_df.empty else "N/A"

    return diagnosis_str, icu_units, avg_los


# ============================================================================
# PHASE 5: RAG CHATBOT VARIATIONS
# ============================================================================

def ask_mimic_bot(
    question: str,
    index: Any,
    model: str = "databricks-meta-llama-3-3-70b-instruct"
) -> str:
    """
    Ask the MIMIC RAG bot a question and get LLM-generated answer.

    Simple RAG function: embed question, retrieve context, generate answer.

    Args:
        question (str): Question about MIMIC clinical data
        index: Vector search index object
        model (str): LLM model to use (default: Meta Llama 3.3 70B)

    Returns:
        str: LLM-generated answer
    """
    # Retrieve context
    context = _retrieve_rag_context(question, index)

    # Build prompt
    prompt = f"""
Answer the question using the context provided.

Context:
{context}

Question:
{question}
"""

    # Generate answer
    response = ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.message


def ask_mimic_bot_table(
    question: str,
    index: Any,
    model: str = "databricks-meta-llama-3-3-70b-instruct"
) -> pd.DataFrame:
    """
    Ask the MIMIC RAG bot a question and return structured JSON as DataFrame.

    Enhanced RAG function with JSON-formatted responses for tabular display.

    Args:
        question (str): Question about MIMIC clinical data
        index: Vector search index object
        model (str): LLM model to use (default: Meta Llama 3.3 70B)

    Returns:
        pd.DataFrame: Structured results as DataFrame

    Raises:
        json.JSONDecodeError: If LLM response is not valid JSON
    """
    # Retrieve context
    context = _retrieve_rag_context(question, index)

    # Build prompt requesting JSON format
    prompt = f"""
Answer the question using the context provided.

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

    # Generate answer
    response = ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse JSON and convert to DataFrame
    data = json.loads(response.message)
    df = pd.DataFrame(data["results"])

    return df


class MimicChatbot:
    """
    Conversational chatbot with memory for multi-turn interactions.

    Maintains conversation history to enable follow-up questions
    while maintaining context from previous exchanges.

    Attributes:
        index: Vector search index for RAG retrieval
        chat_history (list): List of message dicts with 'role' and 'content'
        model (str): LLM model name
    """

    def __init__(
        self,
        index: Any,
        model: str = "databricks-meta-llama-3-3-70b-instruct",
        max_history: int = 6
    ):
        """
        Initialize the chatbot.

        Args:
            index: Vector search index object
            model (str): LLM model to use
            max_history (int): Maximum messages to keep in history (default: 6)
        """
        self.index = index
        self.chat_history = []
        self.model = model
        self.max_history = max_history

    def ask(self, question: str) -> str:
        """
        Ask a question and get a response with conversation memory.

        Args:
            question (str): User question

        Returns:
            str: LLM-generated response
        """
        # Add user message to history
        self.chat_history.append({"role": "user", "content": question})

        # Retrieve RAG context
        context = _retrieve_rag_context(question, self.index)

        # Build conversational prompt
        prompt = f"""
You are a medical data assistant.
Use the context below and conversation history to answer.

Context:
{context}

Conversation:
{self._format_history()}

Answer clearly and helpfully.
"""

        # Generate response
        response = ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )

        answer = response.message

        # Add assistant response to history
        self.chat_history.append({"role": "assistant", "content": answer})

        return answer

    def _format_history(self) -> str:
        """Format conversation history for prompt inclusion."""
        return "\n".join(
            [f"{m['role']}: {m['content']}" for m in self.chat_history[-self.max_history:]]
        )

    def reset(self) -> None:
        """Clear conversation history."""
        self.chat_history = []


# ============================================================================
# PHASE 6: PATIENT LOOKUP & CLINICAL INSIGHTS
# ============================================================================

def get_patient_summary(
    subject_id: int,
    schema_name: Optional[str] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Fetch patient admissions and ICU stays from MIMIC silver tables.

    Args:
        subject_id (int): Patient ID (subject_id from MIMIC)
        schema_name (str): Database schema name (default: "mmc")

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (admissions_df, icu_df)

    Raises:
        Exception: If patient not found or tables inaccessible
    """
    # get schema from config if not provided
    if not schema_name:
        config, _ = load_config()
        schema_name = config["schema_name"]

    spark = G.spark

    # Query admissions
    admissions_df = spark.sql(f"""
        SELECT a.subject_id, a.hadm_id, a.diagnosis, a.admission_type, 
               a.admission_location, a.discharge_location, a.insurance, 
               p.gender, FLOOR(DATEDIFF(a.admittime, p.dob) / 365.25) AS age,
               DATEDIFF(a.dischtime, a.admittime) AS length_of_stay_days,
               a.admittime, a.dischtime, a.hospital_expire_flag, 
               a.marital_status, a.ethnicity
        FROM {schema_name}.silver.fact_admissions a
        JOIN {schema_name}.silver.dim_patients p ON a.subject_id = p.subject_id
        WHERE a.subject_id = {subject_id}
        ORDER BY a.admittime
    """).toPandas()

    # Query ICU stays
    icu_df = spark.sql(f"""
        SELECT icustay_id, hadm_id, first_careunit, last_careunit, los,
               intime, outtime
        FROM {schema_name}.silver.fact_icustays
        WHERE subject_id = {subject_id}
        ORDER BY intime
    """).toPandas()

    return admissions_df, icu_df


def generate_patient_insights(
    admissions_df: pd.DataFrame,
    icu_df: pd.DataFrame,
    subject_id: int,
    index: Any
) -> str:
    """
    Generate AI-powered clinical insights using RAG for a patient.

    Analyzes patient diagnoses, ICU history, and LOS to provide
    clinical summary and risk assessment.

    Args:
        admissions_df (pd.DataFrame): Patient admission records
        icu_df (pd.DataFrame): Patient ICU stay records
        subject_id (int): Patient ID
        index: Vector search index

    Returns:
        str: LLM-generated clinical insights
    """
    diagnosis_str, icu_units, avg_los = _build_patient_context(admissions_df, icu_df, subject_id)

    # Build RAG question
    question = (
        f"Patient {subject_id} has the following diagnoses: {diagnosis_str}. "
        f"They had {len(icu_df)} ICU stay(s) in units: {', '.join(icu_units) if icu_units else 'none'}. "
        f"Average ICU length of stay: {avg_los} days. "
        f"Provide a clinical summary and key risk factors for this patient."
    )

    # Retrieve context
    context = _retrieve_rag_context(question, index)

    # Build prompt
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


def generate_prescription(
    admissions_df: pd.DataFrame,
    icu_df: pd.DataFrame,
    subject_id: int,
    index: Any
) -> str:
    """
    Generate prescription recommendations using RAG for a patient.

    Uses patient diagnoses, age, gender, and medical context to recommend
    primary medications, supportive drugs, monitoring, and precautions.

    Args:
        admissions_df (pd.DataFrame): Patient admission records
        icu_df (pd.DataFrame): Patient ICU stay records
        subject_id (int): Patient ID
        index: Vector search index

    Returns:
        str: LLM-generated prescription recommendations

    Note:
        This is for educational/demonstration purposes using synthetic MIMIC data.
    """
    diagnosis_str, icu_units, avg_los = _build_patient_context(admissions_df, icu_df, subject_id)

    # Build RAG question
    question = (
        f"What medications and prescriptions are recommended for a patient with: {diagnosis_str}? "
        f"Consider ICU stay history and post-discharge care."
    )

    # Retrieve context
    context = _retrieve_rag_context(question, index)

    # Get patient demographics
    row = admissions_df.iloc[0]

    # Build prompt
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


# ============================================================================
# PHASE 6: EMAIL DELIVERY
# ============================================================================

def build_prescription_email_html(
    subject_id: int,
    admissions_df: pd.DataFrame,
    icu_df: pd.DataFrame,
    prescription_text: str,
    doctor_name: str
) -> str:
    """
    Build professional HTML email body for prescription report.

    Args:
        subject_id (int): Patient ID
        admissions_df (pd.DataFrame): Patient admission records
        icu_df (pd.DataFrame): Patient ICU stay records
        prescription_text (str): Prescription recommendations text
        doctor_name (str): Attending physician name

    Returns:
        str: HTML formatted email body
    """
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


def send_prescription_email(
    recipient_email: str,
    subject_id: int,
    admissions_df: pd.DataFrame,
    icu_df: pd.DataFrame,
    prescription_text: str,
    doctor_name: str,
    smtp_server: str = "smtp.gmail.com",
    smtp_port: int = 587,
    sender_email: str = None,
    sender_password: str = None
) -> Tuple[bool, str]:
    """
    Send prescription report email to recipient.

    Args:
        recipient_email (str): Recipient email address
        subject_id (int): Patient ID
        admissions_df (pd.DataFrame): Patient admission records
        icu_df (pd.DataFrame): Patient ICU stay records
        prescription_text (str): Prescription recommendations
        doctor_name (str): Attending physician name
        smtp_server (str): SMTP server address (default: smtp.gmail.com)
        smtp_port (int): SMTP port (default: 587)
        sender_email (str): Sender email address (optional)
        sender_password (str): Sender app password (optional)

    Returns:
        Tuple[bool, str]: (success, message)
            - If sender credentials provided: (bool, email_status_message)
            - If credentials missing: (False, html_preview)
    """
    html_body = build_prescription_email_html(
        subject_id, admissions_df, icu_df, prescription_text, doctor_name
    )
    subject = f"Prescription Report — Patient {subject_id} | Dr. {doctor_name}"

    # Return HTML preview if SMTP credentials not provided
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


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def execute_rag_pipeline(
    schema_name: Optional[str] = None,
    skip_embedding_generation: bool = False
) -> Dict[str, Any]:
    """
    Execute the complete RAG pipeline end-to-end.

    Orchestrates all phases: document creation, chunking, embedding generation,
    vector index creation, and initializaton of RAG components.

    Args:
        schema_name (str): Database schema name (default: "mmc")
        skip_embedding_generation (bool): Skip expensive embedding generation if true

    Returns:
        Dict[str, Any]: Pipeline artifacts including vector search client and index
        {
            'vsc': VectorSearchClient,
            'index': Vector search index object,
            'schema_name': str
        }

    Raises:
        Exception: If any phase fails
    """
    print("\n" + "="*70)
    print("🚀 MIMIC RAG PIPELINE EXECUTION")
    print("="*70)

    # get schema from config if not provided
    if not schema_name:
        config, _ = load_config()
        schema_name = config["schema_name"]

    try:
        # Phase 1: Create documents
        print("\n📄 Phase 1: Creating documents from MIMIC silver tables...")
        create_llm_documents(schema_name)

        # Phase 2: Chunk documents
        print("\n✂️  Phase 2: Chunking documents...")
        chunk_documents(schema_name)

        # Phase 3: Generate embeddings
        if not skip_embedding_generation:
            print("\n🔢 Phase 3: Generating embeddings...")
            generate_embeddings(schema_name)
        else:
            print("\n⏭️  Phase 3: Skipping embedding generation (already completed)")

        # Phase 4: Create vector search index
        print("\n🔍 Phase 4: Creating vector search index...")
        vsc = create_vector_search_index(schema_name)
        index = vsc.get_index(
            endpoint_name="mimic_vector_endpoint",
            index_name=f"{schema_name}.gold.mimic_llm_index"
        )

        print("\n✅ RAG Pipeline executed successfully!")
        print("="*70)

        return {
            'vsc': vsc,
            'index': index,
            'schema_name': schema_name
        }

    except Exception as e:
        print(f"\n❌ RAG Pipeline execution failed: {str(e)}")
        raise


if __name__ == "__main__":
    # For debugging/testing purposes
    print("RAG Pipeline module loaded successfully.")
    print("Call execute_rag_pipeline() to run the full pipeline.")


