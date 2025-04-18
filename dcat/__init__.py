"""
DCAT Package - A collection of tools for working with DCAT (Data Catalog Vocabulary) metadata.

This package provides tools for working with DCAT metadata, including:
- Data models for DCAT catalogs, datasets, distributions, and services
- Embedding and semantic search capabilities for DCAT metadata
- A LangChain-based assistant for interacting with DCAT metadata
- SQL-like querying and comparison with LLM-based querying
"""

# Import key classes and functions for easy access
from dcat.dcat_metadata import (
    Catalog,
    Dataset,
    Distribution,
    DataService,
    load_catalog_from_json,
)
from dcat.dcat_embedding import DCATEmbedder
from dcat.dcat_assistant import DCATAssistant

"""DCAT metadata analysis and EU Data Portal integration."""
from .eu_data_portal import EUDataPortal
from .sparql_processor import SparqlQueryProcessor

__all__ = ['EUDataPortal', 'SparqlQueryProcessor']
