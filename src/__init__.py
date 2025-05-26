# Open Data Assistant - Advanced RAG System for EU Open Data Portal
# Combines SPARQL queries, API calls, and vector similarity search

from .rag_system import RAGSystem, QueryExample, SchemaInfo
from .schema_extractor import SchemaExtractor, auto_populate_rag_with_schema
from .unified_data_assistant import UnifiedDataAssistant, ask_unified_assistant

__version__ = "1.0.0"
__author__ = "Open Data Assistant Team"

__all__ = [
    "RAGSystem",
    "QueryExample",
    "SchemaInfo",
    "SchemaExtractor",
    "auto_populate_rag_with_schema",
    "UnifiedDataAssistant",
    "ask_unified_assistant",
]
