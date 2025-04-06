"""Tests for the embedding engine."""

import pytest
import numpy as np
from datetime import datetime
from pathlib import Path
import tempfile
import shutil

from dcat.metadata.base import (
    DCATDataset,
    DCATCatalog,
    DCATDistribution,
    DCATIdentifier,
    DCATPublisher,
    LangString,
)
from dcat.embedding.engine import EmbeddingEngine


@pytest.fixture
def temp_vector_store():
    """Create a temporary directory for vector store."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_dataset():
    """Create a sample dataset for testing."""
    return DCATDataset(
        identifier=DCATIdentifier(id="test-dataset-1", source_id="test-source"),
        title={
            "en": LangString("Test Dataset 1"),
            "hr": LangString("Testni Skup Podataka 1"),
        },
        description={
            "en": LangString("A dataset about air quality measurements."),
            "hr": LangString("Skup podataka o mjerenjima kvalitete zraka."),
        },
        keywords=[
            LangString("air quality"),
            LangString("environment"),
            LangString("measurements"),
        ],
        themes=[LangString("environment"), LangString("science")],
        publisher=DCATPublisher(name={"en": LangString("Test Organization")}),
        distributions=[
            DCATDistribution(format="CSV", url="http://example.com/data.csv")
        ],
        issued=datetime.now(),
        modified=datetime.now(),
    )


@pytest.fixture
def sample_catalog(sample_dataset):
    """Create a sample catalog for testing."""
    return DCATCatalog(
        identifier=DCATIdentifier(id="test-catalog", source_id="test-source"),
        title={"en": LangString("Test Catalog")},
        description={"en": LangString("A test catalog")},
        datasets=[sample_dataset],
    )


def test_embedding_engine_init(temp_vector_store):
    """Test embedding engine initialization."""
    engine = EmbeddingEngine(persist_directory=temp_vector_store)
    assert engine.model is not None
    assert engine.collection is not None


def test_prepare_metadata_text(temp_vector_store, sample_dataset):
    """Test metadata text preparation."""
    engine = EmbeddingEngine(persist_directory=temp_vector_store)
    text = engine._prepare_metadata_text(sample_dataset)

    assert "Test Dataset 1" in text
    assert "air quality measurements" in text
    assert "air quality" in text
    assert "environment" in text
    assert "CSV" in text
    assert "Test Organization" in text


def test_embed_dataset(temp_vector_store, sample_dataset):
    """Test dataset embedding generation."""
    engine = EmbeddingEngine(persist_directory=temp_vector_store)
    embedding = engine.embed_dataset(sample_dataset)

    assert isinstance(embedding, np.ndarray)
    assert embedding.shape[0] > 0


def test_add_and_find_similar_datasets(temp_vector_store, sample_dataset):
    """Test adding datasets and finding similar ones."""
    engine = EmbeddingEngine(persist_directory=temp_vector_store)

    # Create a similar dataset
    similar_dataset = DCATDataset(
        identifier=DCATIdentifier(id="test-dataset-2", source_id="test-source"),
        title={"en": LangString("Test Dataset 2")},
        description={
            "en": LangString(
                "Another dataset about environmental measurements and air quality."
            )
        },
        keywords=[LangString("air quality"), LangString("environment")],
    )

    # Add both datasets
    engine.add_dataset(sample_dataset)
    engine.add_dataset(similar_dataset)

    # Find similar datasets
    similar = engine.find_similar_datasets(sample_dataset, n_results=1)
    assert len(similar) == 1
    assert similar[0][0] == "test-dataset-2"
    assert similar[0][1] > 0.5  # Similarity score should be high


def test_semantic_search(temp_vector_store, sample_dataset):
    """Test semantic search functionality."""
    engine = EmbeddingEngine(persist_directory=temp_vector_store)
    engine.add_dataset(sample_dataset)

    # Search for relevant datasets
    results = engine.semantic_search("air quality data", n_results=1)
    assert len(results) == 1
    assert results[0][0] == "test-dataset-1"
    assert results[0][1] > 0.3  # Similarity score should be above threshold
    assert "title" in results[0][2]


def test_process_catalog(temp_vector_store, sample_catalog):
    """Test catalog processing."""
    engine = EmbeddingEngine(persist_directory=temp_vector_store)
    engine.process_catalog(sample_catalog)

    # Verify dataset was added
    results = engine.semantic_search("Test Dataset 1", n_results=1)
    assert len(results) == 1
    assert results[0][0] == "test-dataset-1"


def test_update_dataset(temp_vector_store, sample_dataset):
    """Test dataset updating."""
    engine = EmbeddingEngine(persist_directory=temp_vector_store)

    # Add initial dataset
    engine.add_dataset(sample_dataset)

    # Update dataset with new description
    updated_dataset = sample_dataset
    updated_dataset.description["en"] = LangString(
        "Updated description about air quality."
    )
    engine.update_dataset(updated_dataset)

    # Verify update
    results = engine.semantic_search("Updated description", n_results=1)
    assert len(results) == 1
    assert results[0][0] == "test-dataset-1"
