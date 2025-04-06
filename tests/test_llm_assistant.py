"""Tests for the LLM Assistant."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from dcat.metadata.base import (
    DCATDataset,
    DCATCatalog,
    DCATIdentifier,
    DCATPublisher,
    LangString,
    TemporalCoverage,
    SpatialCoverage,
)
from dcat.semantic.analyzer import SemanticAnalyzer, SemanticRelation
from dcat.assistant.llm_assistant import (
    LLMAssistant,
    DatasetSuggestion,
    MetadataInsight,
    AssistantResponse,
)


@pytest.fixture
def mock_semantic_analyzer():
    """Create a mock semantic analyzer."""
    analyzer = Mock(spec=SemanticAnalyzer)

    # Mock semantic search results
    analyzer.embedding_engine.semantic_search.return_value = [
        ("dataset-1", 0.9, {"title": "Test Dataset 1"}),
        ("dataset-2", 0.8, {"title": "Test Dataset 2"}),
    ]

    # Mock related datasets
    analyzer.find_related_datasets.return_value = [
        ("dataset-3", 0.85, ["dataset-1", "dataset-3"]),
        ("dataset-4", 0.75, ["dataset-1", "dataset-4"]),
    ]

    # Mock clusters
    analyzer.get_dataset_clusters.return_value = [
        {"dataset-1", "dataset-3", "dataset-5"},
        {"dataset-2", "dataset-4"},
    ]

    return analyzer


@pytest.fixture
def assistant(mock_semantic_analyzer):
    """Create an LLM assistant for testing."""
    with patch("langchain.chat_models.ChatOpenAI"):
        return LLMAssistant(mock_semantic_analyzer)


@pytest.fixture
def test_dataset():
    """Create a test dataset."""
    return DCATDataset(
        identifier=DCATIdentifier(id="test-dataset", source_id="test-source"),
        title={"en": LangString("Test Dataset")},
        description={"en": LangString("A dataset for testing")},
        keywords=[LangString("test"), LangString("data")],
        themes=[LangString("testing")],
        temporal_coverage=TemporalCoverage(
            start_date=datetime(2023, 1, 1), end_date=datetime(2023, 12, 31)
        ),
    )


def test_assistant_init(assistant):
    """Test assistant initialization."""
    assert assistant.semantic_analyzer is not None
    assert assistant.max_suggestions == 5
    assert hasattr(assistant, "query_prompt")
    assert hasattr(assistant, "explanation_prompt")
    assert hasattr(assistant, "response_parser")


@patch("langchain.chat_models.ChatOpenAI")
def test_analyze_query(mock_llm, assistant, mock_semantic_analyzer):
    """Test query analysis."""
    # Mock LLM response
    mock_response = Mock()
    mock_response.content = """
    {
        "answer": "Here are some relevant datasets about testing.",
        "suggestions": [
            {
                "dataset_id": "dataset-1",
                "relevance_score": 0.9,
                "explanation": "This dataset contains test data."
            }
        ],
        "insights": [
            {
                "insight_type": "quality",
                "description": "High quality metadata",
                "confidence": 0.95,
                "affected_datasets": ["dataset-1"]
            }
        ],
        "next_steps": ["Explore related datasets"]
    }
    """
    mock_llm.return_value.predict_messages.return_value = mock_response

    # Test query analysis
    response = assistant.analyze_query(
        "Find datasets about testing", context={"current_dataset_id": "dataset-1"}
    )

    assert isinstance(response, AssistantResponse)
    assert "relevant datasets" in response.answer.lower()
    assert len(response.suggestions) > 0
    assert len(response.insights) > 0
    assert len(response.next_steps) > 0

    # Verify semantic analyzer calls
    mock_semantic_analyzer.embedding_engine.semantic_search.assert_called_once()
    mock_semantic_analyzer.find_related_datasets.assert_called_once()
    mock_semantic_analyzer.get_dataset_clusters.assert_called_once()


def test_suggest_datasets(assistant, mock_semantic_analyzer):
    """Test dataset suggestions."""
    suggestions = assistant.suggest_datasets(
        "Find test data", filters={"theme": ["testing"]}
    )

    assert len(suggestions) > 0
    for suggestion in suggestions:
        assert isinstance(suggestion, DatasetSuggestion)
        assert suggestion.dataset_id in ["dataset-1", "dataset-2"]
        assert suggestion.relevance_score > 0
        assert suggestion.explanation != ""


def test_analyze_metadata(assistant, test_dataset, mock_semantic_analyzer):
    """Test metadata analysis."""
    # Mock dataset relations
    mock_semantic_analyzer.analyze_dataset.return_value = [
        SemanticRelation(
            source_id="test-dataset",
            target_id="dataset-1",
            relation_type="similar",
            confidence=0.85,
            metadata={},
        )
    ]

    insights = assistant.analyze_metadata(test_dataset)

    assert len(insights) > 0
    for insight in insights:
        assert isinstance(insight, MetadataInsight)
        assert insight.insight_type in ["quality", "relationship", "coverage"]
        assert insight.confidence > 0
        assert len(insight.affected_datasets) > 0


def test_metadata_quality_analysis(assistant, test_dataset):
    """Test metadata quality analysis."""
    # Test with complete metadata
    quality_insight = assistant._analyze_metadata_quality(test_dataset)
    assert quality_insight is None

    # Test with incomplete metadata
    incomplete_dataset = DCATDataset(
        identifier=DCATIdentifier(id="incomplete", source_id="test"),
        title={},  # Missing title
        description={"en": LangString("Test")},
    )

    quality_insight = assistant._analyze_metadata_quality(incomplete_dataset)
    assert quality_insight is not None
    assert quality_insight.insight_type == "quality"
    assert "missing English title" in quality_insight.description.lower()


def test_relationship_analysis(assistant, test_dataset):
    """Test relationship analysis."""
    relations = [
        SemanticRelation(
            source_id="test-dataset",
            target_id="dataset-1",
            relation_type="similar",
            confidence=0.9,
            metadata={},
        )
    ]
    cluster = {"test-dataset", "dataset-1", "dataset-2"}

    insight = assistant._analyze_relationships(test_dataset, relations, cluster)

    assert insight is not None
    assert insight.insight_type == "relationship"
    assert "cluster" in insight.description.lower()
    assert insight.confidence > 0


def test_coverage_analysis(assistant, test_dataset):
    """Test coverage analysis."""
    # Test with complete coverage
    cluster = {"test-dataset", "dataset-1"}
    coverage_insight = assistant._analyze_coverage(test_dataset, cluster)
    assert coverage_insight is None

    # Test with missing coverage
    incomplete_dataset = DCATDataset(
        identifier=DCATIdentifier(id="incomplete", source_id="test"),
        title={"en": LangString("Test")},
        description={"en": LangString("Test")},
        temporal_coverage=None,  # Missing temporal coverage
    )

    coverage_insight = assistant._analyze_coverage(incomplete_dataset, cluster)
    assert coverage_insight is not None
    assert coverage_insight.insight_type == "coverage"
    assert "temporal coverage" in coverage_insight.description.lower()


def test_filter_application(assistant):
    """Test filter application to candidates."""
    candidates = [
        ("dataset-1", 0.9, {"theme": "testing", "format": "CSV"}),
        ("dataset-2", 0.8, {"theme": "analysis", "format": "JSON"}),
        ("dataset-3", 0.7, {"theme": "testing", "format": "XML"}),
    ]

    # Test theme filter
    filtered = assistant._apply_filters(candidates, filters={"theme": "testing"})
    assert len(filtered) == 2
    assert all(c[2]["theme"] == "testing" for c in filtered)

    # Test format filter
    filtered = assistant._apply_filters(candidates, filters={"format": "CSV"})
    assert len(filtered) == 1
    assert filtered[0][0] == "dataset-1"

    # Test multiple filters
    filtered = assistant._apply_filters(
        candidates, filters={"theme": "testing", "format": "CSV"}
    )
    assert len(filtered) == 1
    assert filtered[0][0] == "dataset-1"
