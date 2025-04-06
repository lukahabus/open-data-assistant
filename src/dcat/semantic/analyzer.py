"""
Semantic analyzer for discovering and analyzing relationships between datasets.
"""

from typing import Dict, List, Optional, Set, Tuple
import networkx as nx
from dataclasses import dataclass
import numpy as np

from ..metadata.base import DCATDataset, DCATCatalog
from ..embedding.engine import EmbeddingEngine


@dataclass
class SemanticRelation:
    """Represents a semantic relationship between datasets."""

    source_id: str
    target_id: str
    relation_type: str
    confidence: float
    metadata: Dict


class SemanticAnalyzer:
    """Analyzer for discovering semantic relationships between datasets."""

    def __init__(
        self,
        embedding_engine: EmbeddingEngine,
        min_similarity: float = 0.7,
        max_relations: int = 10,
    ):
        """Initialize the semantic analyzer.

        Args:
            embedding_engine: Engine for generating and comparing embeddings
            min_similarity: Minimum similarity threshold for relationships
            max_relations: Maximum number of relations per dataset
        """
        self.embedding_engine = embedding_engine
        self.min_similarity = min_similarity
        self.max_relations = max_relations
        self.graph = nx.DiGraph()

    def analyze_dataset(self, dataset: DCATDataset) -> List[SemanticRelation]:
        """Analyze a dataset to discover its relationships with others.

        Args:
            dataset: Dataset to analyze

        Returns:
            List of discovered semantic relations
        """
        relations = []

        # Find similar datasets
        similar_datasets = self.embedding_engine.find_similar_datasets(
            dataset, n_results=self.max_relations, min_similarity=self.min_similarity
        )

        # Create relations for similar datasets
        for target_id, similarity in similar_datasets:
            relation = SemanticRelation(
                source_id=str(dataset.identifier.id),
                target_id=target_id,
                relation_type="similar",
                confidence=similarity,
                metadata={
                    "source_title": (
                        dataset.title.get("en", "").value
                        if dataset.title.get("en")
                        else ""
                    ),
                    "similarity_score": similarity,
                    "themes_overlap": self._calculate_theme_overlap(dataset, target_id),
                },
            )
            relations.append(relation)

            # Update graph
            self._update_graph(relation)

        return relations

    def analyze_catalog(self, catalog: DCATCatalog) -> List[SemanticRelation]:
        """Analyze all datasets in a catalog to discover relationships.

        Args:
            catalog: Catalog to analyze

        Returns:
            List of all discovered semantic relations
        """
        all_relations = []

        # First ensure all datasets are in the embedding store
        self.embedding_engine.process_catalog(catalog)

        # Analyze each dataset
        for dataset in catalog.datasets:
            try:
                relations = self.analyze_dataset(dataset)
                all_relations.extend(relations)
            except Exception as e:
                print(f"Error analyzing dataset {dataset.identifier.id}: {str(e)}")
                continue

        return all_relations

    def find_related_datasets(
        self, dataset_id: str, max_depth: int = 2, min_confidence: float = 0.5
    ) -> List[Tuple[str, float, List[str]]]:
        """Find related datasets through graph traversal.

        Args:
            dataset_id: ID of the source dataset
            max_depth: Maximum path length to consider
            min_confidence: Minimum confidence threshold

        Returns:
            List of (dataset_id, confidence, path) tuples
        """
        if not self.graph.has_node(dataset_id):
            return []

        related = []
        visited = {dataset_id}

        def dfs(current_id: str, depth: int, path: List[str], confidence: float):
            if depth >= max_depth:
                return

            for neighbor in self.graph.neighbors(current_id):
                if neighbor not in visited:
                    edge_confidence = self.graph[current_id][neighbor]["confidence"]
                    new_confidence = confidence * edge_confidence

                    if new_confidence >= min_confidence:
                        visited.add(neighbor)
                        new_path = path + [neighbor]
                        related.append((neighbor, new_confidence, new_path))
                        dfs(neighbor, depth + 1, new_path, new_confidence)

        dfs(dataset_id, 0, [dataset_id], 1.0)
        return sorted(related, key=lambda x: x[1], reverse=True)

    def get_dataset_clusters(
        self, min_cluster_size: int = 3, min_similarity: float = 0.6
    ) -> List[Set[str]]:
        """Find clusters of related datasets.

        Args:
            min_cluster_size: Minimum number of datasets in a cluster
            min_similarity: Minimum similarity threshold for cluster edges

        Returns:
            List of dataset clusters (sets of dataset IDs)
        """
        # Create subgraph with edges above similarity threshold
        filtered_graph = nx.Graph()
        for u, v, data in self.graph.edges(data=True):
            if data["confidence"] >= min_similarity:
                filtered_graph.add_edge(u, v)

        # Find connected components (clusters)
        clusters = []
        for component in nx.connected_components(filtered_graph):
            if len(component) >= min_cluster_size:
                clusters.append(component)

        return sorted(clusters, key=len, reverse=True)

    def get_central_datasets(self, top_k: int = 10) -> List[Tuple[str, float]]:
        """Find the most central datasets based on graph metrics.

        Args:
            top_k: Number of datasets to return

        Returns:
            List of (dataset_id, centrality_score) tuples
        """
        if not self.graph:
            return []

        # Calculate eigenvector centrality
        try:
            centrality = nx.eigenvector_centrality_numpy(self.graph)
        except:
            # Fallback to degree centrality if eigenvector centrality fails
            centrality = nx.degree_centrality(self.graph)

        # Sort by centrality score
        central_datasets = sorted(centrality.items(), key=lambda x: x[1], reverse=True)

        return central_datasets[:top_k]

    def _update_graph(self, relation: SemanticRelation) -> None:
        """Update the relationship graph with a new relation.

        Args:
            relation: Semantic relation to add
        """
        self.graph.add_edge(
            relation.source_id,
            relation.target_id,
            type=relation.relation_type,
            confidence=relation.confidence,
            metadata=relation.metadata,
        )

    def _calculate_theme_overlap(self, dataset: DCATDataset, target_id: str) -> float:
        """Calculate theme overlap between two datasets.

        Args:
            dataset: Source dataset
            target_id: ID of target dataset

        Returns:
            Theme overlap score
        """
        # Get target dataset from embedding engine
        target_results = self.embedding_engine.semantic_search(
            " ".join([theme.value for theme in dataset.themes]), n_results=1
        )

        if not target_results or target_results[0][0] != target_id:
            return 0.0

        return target_results[0][1]  # Return similarity score as theme overlap
