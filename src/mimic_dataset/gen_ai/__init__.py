"""
Gen-AI Module - Retrieval-Augmented Generation (RAG) Pipeline

Implements RAG pipeline for AI-powered clinical insights:
- Document creation from silver tables
- Text chunking and embedding generation
- Vector search index creation
- LLM-based QA and chatbot capabilities
- Patient insights and prescription generation

Functions:
    - execute_rag_pipeline(): Main entry point for RAG pipeline
    - ask_mimic_bot(): Query the MIMIC RAG chatbot
    - get_patient_summary(): Fetch patient clinical context
    - generate_patient_insights(): Generate AI-powered clinical insights
    - generate_prescription(): Generate prescription recommendations
"""

from mimic_dataset.gen_ai.rag_pipeline import (  # noqa: F401
    execute_rag_pipeline,
    ask_mimic_bot,
    get_patient_summary,
    generate_patient_insights,
    generate_prescription,
    MimicChatbot
)

__all__ = [
    "execute_rag_pipeline",
    "ask_mimic_bot",
    "get_patient_summary",
    "generate_patient_insights",
    "generate_prescription",
    "MimicChatbot"
]

