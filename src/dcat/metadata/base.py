"""
Base DCAT metadata classes with enhanced functionality for CKAN integration and dataset linking.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Union
from uuid import UUID, uuid4


@dataclass
class DCATProperty:
    """Base class for DCAT properties with enhanced metadata."""

    value: str
    language: Optional[str] = None
    datatype: Optional[str] = None
    source: Optional[str] = None
    last_modified: datetime = field(default_factory=datetime.now)
    confidence: float = 1.0


@dataclass
class DCATIdentifier:
    """Unique identifier for DCAT resources."""

    id: UUID = field(default_factory=uuid4)
    uri: Optional[str] = None
    source_id: Optional[str] = None  # Original ID from source system (e.g., CKAN)


@dataclass
class DCATResource:
    """Base class for all DCAT resources."""

    identifier: DCATIdentifier = field(default_factory=DCATIdentifier)
    title: Dict[str, DCATProperty] = field(default_factory=dict)
    description: Dict[str, DCATProperty] = field(default_factory=dict)
    issued: Optional[datetime] = None
    modified: Optional[datetime] = None
    keywords: List[DCATProperty] = field(default_factory=list)
    landing_page: Optional[str] = None
    metadata: Dict[str, Union[str, int, float, bool]] = field(default_factory=dict)


@dataclass
class DCATDataset(DCATResource):
    """Enhanced DCAT Dataset class with additional metadata for analysis."""

    distributions: List["DCATDistribution"] = field(default_factory=list)
    temporal_coverage: Optional[Dict[str, datetime]] = None
    spatial_coverage: Optional[Dict[str, float]] = None
    themes: List[DCATProperty] = field(default_factory=list)
    publisher: Optional["DCATAgent"] = None
    contact_point: Optional["DCATAgent"] = None
    frequency: Optional[str] = None
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    related_resources: List[UUID] = field(default_factory=list)
    similarity_scores: Dict[UUID, float] = field(default_factory=dict)


@dataclass
class DCATDistribution(DCATResource):
    """DCAT Distribution class for dataset access information."""

    download_url: Optional[str] = None
    access_url: Optional[str] = None
    format: Optional[str] = None
    media_type: Optional[str] = None
    byte_size: Optional[int] = None
    schema: Optional[str] = None
    compression_format: Optional[str] = None
    packaging_format: Optional[str] = None


@dataclass
class DCATAgent:
    """DCAT Agent class for organizations and contacts."""

    identifier: DCATIdentifier = field(default_factory=DCATIdentifier)
    name: Dict[str, DCATProperty] = field(default_factory=dict)
    type: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    homepage: Optional[str] = None


@dataclass
class DCATCatalog(DCATResource):
    """DCAT Catalog class with enhanced dataset management."""

    datasets: List[DCATDataset] = field(default_factory=list)
    homepage: Optional[str] = None
    language: List[str] = field(default_factory=list)
    license: Optional[str] = None
    publisher: Optional[DCATAgent] = None
    spatial: Optional[str] = None
    themes_taxonomy: Optional[str] = None

    def add_dataset(self, dataset: DCATDataset) -> None:
        """Add a dataset to the catalog."""
        self.datasets.append(dataset)

    def remove_dataset(self, dataset_id: UUID) -> None:
        """Remove a dataset from the catalog."""
        self.datasets = [d for d in self.datasets if d.identifier.id != dataset_id]

    def get_dataset(self, dataset_id: UUID) -> Optional[DCATDataset]:
        """Get a dataset by its identifier."""
        for dataset in self.datasets:
            if dataset.identifier.id == dataset_id:
                return dataset
        return None

    def update_dataset(self, dataset: DCATDataset) -> bool:
        """Update an existing dataset in the catalog."""
        for i, existing_dataset in enumerate(self.datasets):
            if existing_dataset.identifier.id == dataset.identifier.id:
                self.datasets[i] = dataset
                return True
        return False

    def find_datasets_by_theme(self, theme: str) -> List[DCATDataset]:
        """Find datasets by theme."""
        return [
            dataset
            for dataset in self.datasets
            if any(t.value.lower() == theme.lower() for t in dataset.themes)
        ]

    def find_related_datasets(
        self, dataset_id: UUID, min_similarity: float = 0.5
    ) -> List[DCATDataset]:
        """Find datasets related to a given dataset based on similarity scores."""
        source_dataset = self.get_dataset(dataset_id)
        if not source_dataset:
            return []

        return [
            dataset
            for dataset in self.datasets
            if dataset.identifier.id != dataset_id
            and dataset.identifier.id in source_dataset.similarity_scores
            and source_dataset.similarity_scores[dataset.identifier.id]
            >= min_similarity
        ]

    def get_datasets_by_publisher(self, publisher_id: UUID) -> List[DCATDataset]:
        """Get all datasets from a specific publisher."""
        return [
            dataset
            for dataset in self.datasets
            if dataset.publisher and dataset.publisher.identifier.id == publisher_id
        ]

    def get_datasets_by_format(self, format: str) -> List[DCATDataset]:
        """Get all datasets that have distributions in a specific format."""
        return [
            dataset
            for dataset in self.datasets
            if any(
                d.format and d.format.lower() == format.lower()
                for d in dataset.distributions
            )
        ]
