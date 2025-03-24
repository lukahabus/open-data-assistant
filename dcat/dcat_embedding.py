"""
DCAT Embedding - A module for embedding DCAT metadata using LangChain.

This module provides functions for embedding DCAT metadata using LangChain,
which can be used for semantic search and retrieval of datasets.
"""

import os
import json
import faiss
import pickle
from typing import List, Dict, Any, Optional, Tuple, Union
import numpy as np
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter

from dcat.dcat_metadata import (
    Catalog,
    Dataset,
    Distribution,
    DataService,
    load_catalog_from_json,
)

# Load environment variables
load_dotenv()


class DCATEmbedder:
    """Class for embedding DCAT metadata."""

    def __init__(self, embedding_model: Optional[Any] = None):
        """Initialize the DCATEmbedder.

        Args:
            embedding_model: The embedding model to use. Defaults to OpenAIEmbeddings.
        """
        self.embedding_model = embedding_model or OpenAIEmbeddings()
        self.vector_store = None

    def prepare_dataset_document(self, dataset: Dataset) -> Document:
        """Prepare a document for a dataset.

        Args:
            dataset: The dataset to prepare a document for.

        Returns:
            A document containing the dataset metadata.
        """
        # Create a comprehensive metadata representation
        content = f"Dataset: {dataset.title}\n"
        content += f"Description: {dataset.description}\n"

        if dataset.keywords:
            content += f"Keywords: {', '.join(dataset.keywords)}\n"

        if dataset.themes:
            content += f"Themes: {', '.join(dataset.themes)}\n"

        if dataset.temporal_coverage:
            start = dataset.temporal_coverage.get("start_date", "Unknown")
            end = dataset.temporal_coverage.get("end_date", "Unknown")
            content += f"Temporal Coverage: {start} to {end}\n"

        if dataset.spatial_coverage:
            content += f"Spatial Coverage: {str(dataset.spatial_coverage)}\n"

        if dataset.publisher:
            publisher_name = dataset.publisher.get("name", "Unknown")
            content += f"Publisher: {publisher_name}\n"

        if dataset.distributions:
            content += "Distributions:\n"
            for dist in dataset.distributions:
                content += f"  - {dist.title} (Format: {dist.format or 'Unknown'})\n"

        # Create the document with appropriate metadata
        metadata = {
            "id": dataset.id,
            "title": dataset.title,
            "description": dataset.description,
            "type": "dataset",
            "keywords": dataset.keywords,
            "themes": dataset.themes,
            "issued": dataset.issued,
            "modified": dataset.modified,
        }

        return Document(page_content=content, metadata=metadata)

    def prepare_dataset_collection_documents(
        self, datasets: List[Dataset]
    ) -> List[Document]:
        """Prepare documents for a collection of datasets.

        Args:
            datasets: The datasets to prepare documents for.

        Returns:
            A list of documents containing the dataset metadata.
        """
        documents = []
        for dataset in datasets:
            documents.append(self.prepare_dataset_document(dataset))
        return documents

    def prepare_catalog_documents(self, catalog: Catalog) -> List[Document]:
        """Prepare documents for a catalog.

        Args:
            catalog: The catalog to prepare documents for.

        Returns:
            A list of documents containing the catalog metadata.
        """
        documents = []

        # Add catalog information
        catalog_content = f"Catalog: {catalog.title}\n"
        catalog_content += f"Description: {catalog.description}\n"

        if catalog.keywords:
            catalog_content += f"Keywords: {', '.join(catalog.keywords)}\n"

        if catalog.themes:
            catalog_content += f"Themes: {', '.join(catalog.themes)}\n"

        if catalog.publisher:
            publisher_name = catalog.publisher.get("name", "Unknown")
            catalog_content += f"Publisher: {publisher_name}\n"

        catalog_metadata = {
            "id": catalog.id,
            "title": catalog.title,
            "description": catalog.description,
            "type": "catalog",
            "keywords": catalog.keywords,
            "themes": catalog.themes,
            "issued": catalog.issued,
            "modified": catalog.modified,
        }

        documents.append(
            Document(page_content=catalog_content, metadata=catalog_metadata)
        )

        # Add dataset documents
        for dataset in catalog.datasets:
            documents.append(self.prepare_dataset_document(dataset))

        # Add service documents
        for service in catalog.services:
            service_content = f"Data Service: {service.title}\n"
            service_content += f"Description: {service.description}\n"
            service_content += f"Endpoint URL: {service.endpoint_url}\n"

            if service.keywords:
                service_content += f"Keywords: {', '.join(service.keywords)}\n"

            if service.themes:
                service_content += f"Themes: {', '.join(service.themes)}\n"

            if service.serves_dataset:
                service_content += (
                    f"Serves Datasets: {', '.join(service.serves_dataset)}\n"
                )

            service_metadata = {
                "id": service.id,
                "title": service.title,
                "description": service.description,
                "type": "service",
                "keywords": service.keywords,
                "themes": service.themes,
                "endpoint_url": service.endpoint_url,
                "issued": service.issued,
                "modified": service.modified,
            }

            documents.append(
                Document(page_content=service_content, metadata=service_metadata)
            )

        return documents

    def create_vector_store(self, documents: List[Document]) -> FAISS:
        """Create a vector store from a list of documents.

        Args:
            documents: The documents to create a vector store from.

        Returns:
            A FAISS vector store containing the documents.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=100
        )
        split_docs = text_splitter.split_documents(documents)
        vector_store = FAISS.from_documents(split_docs, self.embedding_model)
        self.vector_store = vector_store
        return vector_store

    def embed_catalog(self, catalog: Catalog) -> FAISS:
        """Embed a catalog into a vector store.

        Args:
            catalog: The catalog to embed.

        Returns:
            A FAISS vector store containing the embedded catalog.
        """
        documents = self.prepare_catalog_documents(catalog)
        return self.create_vector_store(documents)

    def save_vector_store(self, vector_store: FAISS, directory: str):
        """Save a vector store to disk.

        Args:
            vector_store: The vector store to save.
            directory: The directory to save the vector store to.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)
        vector_store.save_local(directory)

    def load_vector_store(self, directory: str) -> FAISS:
        """Load a vector store from disk.

        Args:
            directory: The directory to load the vector store from.

        Returns:
            A FAISS vector store loaded from disk.
        """
        vector_store = FAISS.load_local(
            directory, self.embedding_model, allow_dangerous_deserialization=True
        )
        self.vector_store = vector_store
        return vector_store

    def semantic_search(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """Perform semantic search on the vector store.

        Args:
            query: The query to search for.
            k: The number of results to return. Defaults to 5.

        Returns:
            A list of tuples containing the document and its similarity score.
        """
        if not self.vector_store:
            raise ValueError(
                "Vector store has not been created. Please create a vector store first."
            )

        return self.vector_store.similarity_search_with_score(query, k=k)

    def get_dataset_by_id(self, dataset_id: str) -> Optional[Document]:
        """Get a dataset by its ID.

        Args:
            dataset_id: The ID of the dataset to get.

        Returns:
            The dataset document, or None if not found.
        """
        if not self.vector_store:
            raise ValueError(
                "Vector store has not been created. Please create a vector store first."
            )

        # Search all documents to find the one with matching ID and type
        all_docs = self.vector_store.similarity_search("", k=100)

        # Filter manually
        for doc in all_docs:
            if (
                doc.metadata.get("id") == dataset_id
                and doc.metadata.get("type") == "dataset"
            ):
                return doc

        return None

    def find_related_datasets(self, dataset_id: str, k: int = 5) -> List[Document]:
        """Find datasets related to a specific dataset.

        Args:
            dataset_id: The ID of the dataset to find related datasets for.
            k: The number of results to return. Defaults to 5.

        Returns:
            A list of documents containing related datasets.
        """
        dataset = self.get_dataset_by_id(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset with ID {dataset_id} not found.")

        # Use the dataset content as a query to find similar datasets
        results = self.vector_store.similarity_search(
            dataset.page_content,
            k=k + 20,  # Get more results than needed to allow for filtering
        )

        # Filter manually to find datasets only, and exclude the query dataset
        dataset_results = [
            doc
            for doc in results
            if doc.metadata.get("type") == "dataset"
            and doc.metadata.get("id") != dataset_id
        ]

        # Return only k results
        return dataset_results[:k]
