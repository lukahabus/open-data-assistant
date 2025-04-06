"""
Embedding engine for semantic analysis of DCAT metadata.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

from ..metadata.base import DCATDataset, DCATCatalog
from ..metadata.validators import DCATValidator


class EmbeddingEngine:
    """Engine for generating and managing embeddings of DCAT metadata."""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        collection_name: str = "dcat_embeddings",
        persist_directory: str = "./vector_store",
    ):
        """Initialize the embedding engine.

        Args:
            model_name: Name of the sentence transformer model to use
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist embeddings
        """
        self.model = SentenceTransformer(model_name)
        self.chroma_client = chromadb.PersistentClient(
            path=persist_directory, settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name
        )

    def _prepare_metadata_text(self, dataset: DCATDataset) -> str:
        """Prepare metadata text for embedding.

        Args:
            dataset: DCAT dataset

        Returns:
            Concatenated metadata text
        """
        text_parts = []

        # Add title
        if dataset.title.get("en"):
            text_parts.append(f"Title: {dataset.title['en'].value}")

        # Add description
        if dataset.description.get("en"):
            text_parts.append(f"Description: {dataset.description['en'].value}")

        # Add keywords
        if dataset.keywords:
            keywords = [kw.value for kw in dataset.keywords]
            text_parts.append(f"Keywords: {', '.join(keywords)}")

        # Add themes
        if dataset.themes:
            themes = [theme.value for theme in dataset.themes]
            text_parts.append(f"Themes: {', '.join(themes)}")

        # Add distributions
        if dataset.distributions:
            formats = [d.format for d in dataset.distributions if d.format]
            if formats:
                text_parts.append(f"Formats: {', '.join(formats)}")

        # Add publisher
        if dataset.publisher and dataset.publisher.name.get("en"):
            text_parts.append(f"Publisher: {dataset.publisher.name['en'].value}")

        return " | ".join(text_parts)

    def embed_dataset(self, dataset: DCATDataset) -> np.ndarray:
        """Generate embeddings for a dataset.

        Args:
            dataset: DCAT dataset

        Returns:
            Embedding vector
        """
        text = self._prepare_metadata_text(dataset)
        return self.model.encode(text)

    def add_dataset(self, dataset: DCATDataset) -> None:
        """Add a dataset to the vector store.

        Args:
            dataset: DCAT dataset
        """
        text = self._prepare_metadata_text(dataset)
        embedding = self.embed_dataset(dataset)

        self.collection.add(
            documents=[text],
            embeddings=[embedding.tolist()],
            ids=[str(dataset.identifier.id)],
            metadatas=[
                {
                    "title": (
                        dataset.title.get("en", "").value
                        if dataset.title.get("en")
                        else ""
                    ),
                    "source_id": dataset.identifier.source_id or "",
                }
            ],
        )

    def update_dataset(self, dataset: DCATDataset) -> None:
        """Update a dataset in the vector store.

        Args:
            dataset: DCAT dataset
        """
        text = self._prepare_metadata_text(dataset)
        embedding = self.embed_dataset(dataset)

        self.collection.update(
            documents=[text],
            embeddings=[embedding.tolist()],
            ids=[str(dataset.identifier.id)],
            metadatas=[
                {
                    "title": (
                        dataset.title.get("en", "").value
                        if dataset.title.get("en")
                        else ""
                    ),
                    "source_id": dataset.identifier.source_id or "",
                }
            ],
        )

    def find_similar_datasets(
        self, dataset: DCATDataset, n_results: int = 5, min_similarity: float = 0.5
    ) -> List[Tuple[str, float]]:
        """Find similar datasets based on embedding similarity.

        Args:
            dataset: Query dataset
            n_results: Number of results to return
            min_similarity: Minimum similarity threshold

        Returns:
            List of (dataset_id, similarity_score) tuples
        """
        query_embedding = self.embed_dataset(dataset)

        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results + 1,  # Add 1 to account for self-match
        )

        similar_datasets = []
        for i, (doc_id, distance) in enumerate(
            zip(results["ids"][0], results["distances"][0])
        ):
            # Skip self-match
            if doc_id == str(dataset.identifier.id):
                continue

            # Convert distance to similarity (1 - distance)
            similarity = 1 - distance

            if similarity >= min_similarity:
                similar_datasets.append((doc_id, similarity))

        return similar_datasets[:n_results]

    def semantic_search(
        self, query: str, n_results: int = 5, min_similarity: float = 0.3
    ) -> List[Tuple[str, float, Dict]]:
        """Search for datasets using semantic similarity.

        Args:
            query: Search query
            n_results: Number of results to return
            min_similarity: Minimum similarity threshold

        Returns:
            List of (dataset_id, similarity_score, metadata) tuples
        """
        query_embedding = self.model.encode(query)

        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            include=["metadatas"],
        )

        search_results = []
        for doc_id, distance, metadata in zip(
            results["ids"][0], results["distances"][0], results["metadatas"][0]
        ):
            similarity = 1 - distance
            if similarity >= min_similarity:
                search_results.append((doc_id, similarity, metadata))

        return search_results

    def process_catalog(self, catalog: DCATCatalog) -> None:
        """Process all datasets in a catalog.

        Args:
            catalog: DCAT catalog
        """
        # Validate catalog first
        validator = DCATValidator()
        errors, quality_score = validator.validate_and_score(catalog)

        if quality_score < 0.5:
            raise ValueError(f"Catalog quality score too low: {quality_score}")

        # Process each dataset
        for dataset in catalog.datasets:
            try:
                if self.collection.get(ids=[str(dataset.identifier.id)]):
                    self.update_dataset(dataset)
                else:
                    self.add_dataset(dataset)
            except Exception as e:
                print(f"Error processing dataset {dataset.identifier.id}: {str(e)}")
                continue

        # Update similarity scores
        self._update_similarity_scores(catalog)

    def _update_similarity_scores(self, catalog: DCATCatalog) -> None:
        """Update similarity scores between datasets in a catalog.

        Args:
            catalog: DCAT catalog
        """
        for dataset in catalog.datasets:
            similar_datasets = self.find_similar_datasets(
                dataset, n_results=10, min_similarity=0.5
            )

            # Update similarity scores in the dataset
            dataset.similarity_scores = {
                dataset_id: score for dataset_id, score in similar_datasets
            }
