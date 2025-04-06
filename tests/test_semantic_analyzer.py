"""Tests for the semantic analyzer."""

import pytest
from datetime import datetime
import networkx as nx

from dcat.metadata.base import (
    DCATDataset,
    DCATCatalog,
    DCATIdentifier,
    DCATPublisher,
    LangString,
)
from dcat.embedding.engine import EmbeddingEngine
from dcat.semantic.analyzer import SemanticAnalyzer, SemanticRelation


@pytest.fixture
def embedding_engine(temp_vector_store):
    """Create an embedding engine for testing."""
    return EmbeddingEngine(persist_directory=temp_vector_store)


@pytest.fixture
def analyzer(embedding_engine):
    """Create a semantic analyzer for testing."""
    return SemanticAnalyzer(embedding_engine)


@pytest.fixture
def related_datasets():
    """Create a set of related datasets for testing."""
    datasets = []

    # Create environmental datasets
    for i in range(3):
        datasets.append(
            DCATDataset(
                identifier=DCATIdentifier(
                    id=f"env-dataset-{i}", source_id="test-source"
                ),
                title={"en": LangString(f"Environmental Dataset {i}")},
                description={
                    "en": LangString(f"Dataset about environmental measurements {i}")
                },
                keywords=[LangString("environment"), LangString("measurements")],
                themes=[LangString("environment")],
            )
        )

    # Create health datasets
    for i in range(3):
        datasets.append(
            DCATDataset(
                identifier=DCATIdentifier(
                    id=f"health-dataset-{i}", source_id="test-source"
                ),
                title={"en": LangString(f"Health Dataset {i}")},
                description={"en": LangString(f"Dataset about health statistics {i}")},
                keywords=[LangString("health"), LangString("statistics")],
                themes=[LangString("health")],
            )
        )

    return datasets


@pytest.fixture
def test_catalog(related_datasets):
    """Create a test catalog with related datasets."""
    return DCATCatalog(
        identifier=DCATIdentifier(id="test-catalog", source_id="test-source"),
        title={"en": LangString("Test Catalog")},
        description={"en": LangString("A catalog for testing")},
        datasets=related_datasets,
    )


def test_analyzer_init(analyzer):
    """Test analyzer initialization."""
    assert analyzer.embedding_engine is not None
    assert isinstance(analyzer.graph, nx.DiGraph)
    assert analyzer.min_similarity == 0.7
    assert analyzer.max_relations == 10


def test_analyze_dataset(analyzer, related_datasets):
    """Test dataset analysis."""
    # Add datasets to embedding engine
    for dataset in related_datasets:
        analyzer.embedding_engine.add_dataset(dataset)

    # Analyze first environmental dataset
    relations = analyzer.analyze_dataset(related_datasets[0])

    assert len(relations) > 0
    for relation in relations:
        assert isinstance(relation, SemanticRelation)
        assert relation.source_id == "env-dataset-0"
        assert relation.confidence >= analyzer.min_similarity
        assert "similarity_score" in relation.metadata
        assert "themes_overlap" in relation.metadata


def test_analyze_catalog(analyzer, test_catalog):
    """Test catalog analysis."""
    relations = analyzer.analyze_catalog(test_catalog)

    assert len(relations) > 0
    # Should find more relations between similar datasets
    env_relations = [
        r
        for r in relations
        if r.source_id.startswith("env") and r.target_id.startswith("env")
    ]
    health_relations = [
        r
        for r in relations
        if r.source_id.startswith("health") and r.target_id.startswith("health")
    ]

    assert len(env_relations) > 0
    assert len(health_relations) > 0


def test_find_related_datasets(analyzer, test_catalog):
    """Test finding related datasets through graph traversal."""
    # First analyze catalog to build graph
    analyzer.analyze_catalog(test_catalog)

    # Find related datasets for first environmental dataset
    related = analyzer.find_related_datasets("env-dataset-0")

    assert len(related) > 0
    # Should find other environmental datasets
    env_related = [r for r, _, _ in related if r.startswith("env")]
    assert len(env_related) > 0


def test_get_dataset_clusters(analyzer, test_catalog):
    """Test finding dataset clusters."""
    # First analyze catalog to build graph
    analyzer.analyze_catalog(test_catalog)

    clusters = analyzer.get_dataset_clusters(min_cluster_size=2)

    assert len(clusters) > 0
    # Should find at least environmental and health clusters
    for cluster in clusters:
        assert len(cluster) >= 2
        # Datasets in cluster should be either all env or all health
        cluster_type = next(iter(cluster)).split("-")[0]
        assert all(d.split("-")[0] == cluster_type for d in cluster)


def test_get_central_datasets(analyzer, test_catalog):
    """Test finding central datasets."""
    # First analyze catalog to build graph
    analyzer.analyze_catalog(test_catalog)

    central = analyzer.get_central_datasets(top_k=3)

    assert len(central) > 0
    assert len(central) <= 3
    for dataset_id, score in central:
        assert isinstance(score, float)
        assert score > 0


def test_theme_overlap(analyzer, related_datasets):
    """Test theme overlap calculation."""
    # Add datasets to embedding engine
    for dataset in related_datasets:
        analyzer.embedding_engine.add_dataset(dataset)

    # Calculate overlap between two environmental datasets
    overlap = analyzer._calculate_theme_overlap(
        related_datasets[0], "env-dataset-1"  # env dataset  # another env dataset
    )

    assert isinstance(overlap, float)
    assert overlap >= 0.0

    # Calculate overlap between environmental and health datasets
    cross_overlap = analyzer._calculate_theme_overlap(
        related_datasets[0], "health-dataset-0"  # env dataset  # health dataset
    )

    # Cross-domain overlap should be lower
    assert cross_overlap < overlap
