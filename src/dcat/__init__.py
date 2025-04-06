"""
DCAT Metadata Analysis Package
"""

from .metadata.base import DCATDataset, DCATCatalog
from .semantic.analyzer import SemanticAnalyzer
from .embedding.engine import EmbeddingEngine
from .assistant.llm_assistant import LLMAssistant

__version__ = "0.1.0"
