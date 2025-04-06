"""
LLM-powered assistant for metadata analysis and dataset discovery.
"""

from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
import json
from datetime import datetime

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from ..metadata.base import DCATDataset, DCATCatalog
from ..semantic.analyzer import SemanticAnalyzer
from ..embedding.engine import EmbeddingEngine


class DatasetSuggestion(BaseModel):
    """Suggestion for a relevant dataset."""

    dataset_id: str = Field(description="Identifier of the suggested dataset")
    relevance_score: float = Field(
        description="Score indicating relevance to the query"
    )
    explanation: str = Field(description="Explanation of why this dataset is relevant")


class MetadataInsight(BaseModel):
    """Insight about dataset metadata."""

    insight_type: str = Field(
        description="Type of insight (e.g., 'quality', 'coverage', 'relationship')"
    )
    description: str = Field(description="Description of the insight")
    confidence: float = Field(description="Confidence score for the insight")
    affected_datasets: List[str] = Field(
        description="List of dataset IDs affected by this insight"
    )


class AssistantResponse(BaseModel):
    """Structured response from the assistant."""

    answer: str = Field(description="Natural language answer to the user's query")
    suggestions: List[DatasetSuggestion] = Field(
        description="Relevant dataset suggestions"
    )
    insights: List[MetadataInsight] = Field(description="Metadata insights")
    next_steps: List[str] = Field(description="Suggested next steps for the user")


class LLMAssistant:
    """LLM-powered assistant for metadata analysis."""

    def __init__(
        self,
        semantic_analyzer: SemanticAnalyzer,
        model_name: str = "gpt-4",
        temperature: float = 0.7,
        max_suggestions: int = 5,
    ):
        """Initialize the LLM assistant.

        Args:
            semantic_analyzer: Analyzer for discovering dataset relationships
            model_name: Name of the LLM model to use
            temperature: Temperature for LLM responses
            max_suggestions: Maximum number of dataset suggestions
        """
        self.semantic_analyzer = semantic_analyzer
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.max_suggestions = max_suggestions
        self._setup_prompts()
        self._setup_parsers()

    def analyze_query(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> AssistantResponse:
        """Analyze a user query and provide relevant insights.

        Args:
            query: User's natural language query
            context: Additional context (e.g., current dataset, filters)

        Returns:
            Structured response with answer, suggestions, and insights
        """
        # Get relevant datasets through semantic search
        search_results = self.semantic_analyzer.embedding_engine.semantic_search(
            query, n_results=self.max_suggestions
        )

        # Find related datasets if context includes a current dataset
        related_datasets = []
        if context and context.get("current_dataset_id"):
            related_datasets = self.semantic_analyzer.find_related_datasets(
                context["current_dataset_id"]
            )

        # Get dataset clusters for broader context
        clusters = self.semantic_analyzer.get_dataset_clusters()

        # Prepare prompt context
        prompt_context = {
            "query": query,
            "search_results": search_results,
            "related_datasets": related_datasets,
            "clusters": clusters,
            "user_context": context or {},
        }

        # Generate LLM response
        response = self._generate_response(prompt_context)
        return response

    def suggest_datasets(
        self, query: str, filters: Optional[Dict[str, Any]] = None
    ) -> List[DatasetSuggestion]:
        """Suggest relevant datasets based on a query.

        Args:
            query: Search query or description of needed data
            filters: Optional filters (e.g., themes, formats)

        Returns:
            List of dataset suggestions
        """
        # Get initial candidates through semantic search
        candidates = self.semantic_analyzer.embedding_engine.semantic_search(
            query, n_results=self.max_suggestions * 2  # Get more for filtering
        )

        # Apply filters if provided
        if filters:
            filtered_candidates = self._apply_filters(candidates, filters)
            candidates = filtered_candidates[: self.max_suggestions]
        else:
            candidates = candidates[: self.max_suggestions]

        # Generate suggestions with explanations
        suggestions = []
        for dataset_id, score, metadata in candidates:
            # Get dataset relationships
            relations = self.semantic_analyzer.find_related_datasets(dataset_id)

            # Prepare context for explanation
            context = {
                "query": query,
                "dataset_id": dataset_id,
                "score": score,
                "metadata": metadata,
                "relations": relations,
            }

            # Generate explanation
            explanation = self._generate_suggestion_explanation(context)

            suggestion = DatasetSuggestion(
                dataset_id=dataset_id, relevance_score=score, explanation=explanation
            )
            suggestions.append(suggestion)

        return suggestions

    def analyze_metadata(self, dataset: DCATDataset) -> List[MetadataInsight]:
        """Analyze dataset metadata to generate insights.

        Args:
            dataset: Dataset to analyze

        Returns:
            List of metadata insights
        """
        insights = []

        # Get dataset relationships
        relations = self.semantic_analyzer.analyze_dataset(dataset)

        # Find dataset cluster
        clusters = self.semantic_analyzer.get_dataset_clusters()
        dataset_cluster = next(
            (c for c in clusters if dataset.identifier.id in c), set()
        )

        # Analyze metadata quality
        quality_insight = self._analyze_metadata_quality(dataset)
        if quality_insight:
            insights.append(quality_insight)

        # Analyze relationships
        relationship_insight = self._analyze_relationships(
            dataset, relations, dataset_cluster
        )
        if relationship_insight:
            insights.append(relationship_insight)

        # Analyze coverage
        coverage_insight = self._analyze_coverage(dataset, dataset_cluster)
        if coverage_insight:
            insights.append(coverage_insight)

        return insights

    def _setup_prompts(self) -> None:
        """Set up prompt templates."""
        self.query_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an expert data analyst helping users discover and understand datasets.",
                ),
                ("user", "{query}"),
                (
                    "system",
                    "Context:\nSearch Results: {search_results}\nRelated Datasets: {related_datasets}\nClusters: {clusters}\nUser Context: {user_context}",
                ),
            ]
        )

        self.explanation_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Generate a concise explanation for why this dataset is relevant:",
                ),
                (
                    "user",
                    "Query: {query}\nDataset: {dataset_id}\nScore: {score}\nMetadata: {metadata}\nRelations: {relations}",
                ),
            ]
        )

    def _setup_parsers(self) -> None:
        """Set up output parsers."""
        self.response_parser = PydanticOutputParser(pydantic_object=AssistantResponse)

    def _generate_response(self, context: Dict[str, Any]) -> AssistantResponse:
        """Generate a structured response using the LLM.

        Args:
            context: Context for the prompt

        Returns:
            Structured assistant response
        """
        # Format prompt
        prompt = self.query_prompt.format_messages(**context)

        # Get LLM response
        response = self.llm.predict_messages(prompt)

        # Parse response
        try:
            structured_response = self.response_parser.parse(response.content)
        except Exception as e:
            # Fallback to basic response if parsing fails
            structured_response = AssistantResponse(
                answer="I apologize, but I couldn't generate a complete response. "
                + str(e),
                suggestions=[],
                insights=[],
                next_steps=["Please try rephrasing your query"],
            )

        return structured_response

    def _generate_suggestion_explanation(self, context: Dict[str, Any]) -> str:
        """Generate an explanation for a dataset suggestion.

        Args:
            context: Context for the explanation

        Returns:
            Generated explanation
        """
        # Format prompt
        prompt = self.explanation_prompt.format_messages(**context)

        # Get explanation
        response = self.llm.predict_messages(prompt)
        return response.content

    def _apply_filters(
        self, candidates: List[Tuple[str, float, Dict]], filters: Dict[str, Any]
    ) -> List[Tuple[str, float, Dict]]:
        """Apply filters to dataset candidates.

        Args:
            candidates: List of (dataset_id, score, metadata) tuples
            filters: Filters to apply

        Returns:
            Filtered list of candidates
        """
        filtered = []

        for dataset_id, score, metadata in candidates:
            matches_filters = True

            # Apply each filter
            for key, value in filters.items():
                if key in metadata:
                    if isinstance(value, list):
                        if not any(v in metadata[key] for v in value):
                            matches_filters = False
                            break
                    elif metadata[key] != value:
                        matches_filters = False
                        break

            if matches_filters:
                filtered.append((dataset_id, score, metadata))

        return filtered

    def _analyze_metadata_quality(
        self, dataset: DCATDataset
    ) -> Optional[MetadataInsight]:
        """Analyze metadata quality.

        Args:
            dataset: Dataset to analyze

        Returns:
            Quality insight if issues found
        """
        issues = []

        # Check title
        if not dataset.title.get("en"):
            issues.append("missing English title")

        # Check description
        if not dataset.description.get("en"):
            issues.append("missing English description")

        # Check keywords
        if not dataset.keywords:
            issues.append("no keywords")

        # Check themes
        if not dataset.themes:
            issues.append("no themes")

        if issues:
            return MetadataInsight(
                insight_type="quality",
                description=f"Metadata quality issues found: {', '.join(issues)}",
                confidence=1.0,
                affected_datasets=[dataset.identifier.id],
            )

        return None

    def _analyze_relationships(
        self, dataset: DCATDataset, relations: List, cluster: Set[str]
    ) -> Optional[MetadataInsight]:
        """Analyze dataset relationships.

        Args:
            dataset: Dataset to analyze
            relations: Dataset relations
            cluster: Dataset's cluster

        Returns:
            Relationship insight if patterns found
        """
        if not relations:
            return None

        # Analyze relationship patterns
        strong_relations = [r for r in relations if r.confidence > 0.8]
        cluster_size = len(cluster)

        if strong_relations and cluster_size > 1:
            return MetadataInsight(
                insight_type="relationship",
                description=(
                    f"Dataset belongs to a cluster of {cluster_size} related datasets "
                    f"with {len(strong_relations)} strong relationships"
                ),
                confidence=0.9,
                affected_datasets=list(cluster),
            )

        return None

    def _analyze_coverage(
        self, dataset: DCATDataset, cluster: Set[str]
    ) -> Optional[MetadataInsight]:
        """Analyze metadata coverage within a cluster.

        Args:
            dataset: Dataset to analyze
            cluster: Dataset's cluster

        Returns:
            Coverage insight if gaps found
        """
        if not cluster:
            return None

        # Compare metadata coverage with cluster
        coverage_gaps = []

        # Check temporal coverage
        if not dataset.temporal_coverage and any(
            d.temporal_coverage for d in cluster if d != dataset.identifier.id
        ):
            coverage_gaps.append("temporal coverage")

        # Check spatial coverage
        if not dataset.spatial_coverage and any(
            d.spatial_coverage for d in cluster if d != dataset.identifier.id
        ):
            coverage_gaps.append("spatial coverage")

        if coverage_gaps:
            return MetadataInsight(
                insight_type="coverage",
                description=f"Missing metadata coverage: {', '.join(coverage_gaps)}",
                confidence=0.8,
                affected_datasets=[dataset.identifier.id],
            )

        return None
