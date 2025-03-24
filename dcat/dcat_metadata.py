"""
DCAT Metadata Module - Utilities for working with DCAT metadata.

This module provides functions and classes for working with DCAT (Data Catalog Vocabulary)
metadata, including parsing, validation, and analysis.

Key DCAT classes implemented:
- Catalog: Represents a catalog of datasets
- Dataset: Represents a collection of data
- Distribution: Represents an accessible form of a dataset
- DataService: Represents a service that provides access to datasets
- DatasetSeries: Represents a collection of datasets with shared characteristics
- CatalogRecord: Represents a metadata record in a catalog
"""

import json
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field, asdict
import os
from datetime import datetime


@dataclass
class DCATResource:
    """Base class for DCAT resources."""

    id: str
    title: str
    description: str
    keywords: List[str] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    issued: Optional[str] = None
    modified: Optional[str] = None
    landing_page: Optional[str] = None
    language: List[str] = field(default_factory=list)
    publisher: Optional[Dict[str, str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class Distribution(DCATResource):
    """A specific representation of a dataset."""

    access_url: Optional[str] = None
    download_url: Optional[str] = None
    media_type: Optional[str] = None
    format: Optional[str] = None
    byte_size: Optional[int] = None
    checksum: Optional[Dict[str, str]] = None
    license: Optional[str] = None


@dataclass
class Dataset(DCATResource):
    """A collection of data, published or curated by a single agent."""

    distributions: List[Distribution] = field(default_factory=list)
    temporal_coverage: Optional[Dict[str, str]] = None
    spatial_coverage: Optional[Dict[str, Any]] = None
    accrual_periodicity: Optional[str] = None
    version: Optional[str] = None
    version_notes: Optional[str] = None
    is_version_of: Optional[str] = None
    has_version: List[str] = field(default_factory=list)
    source_dataset: List[str] = field(default_factory=list)
    contact_point: Optional[Dict[str, str]] = None


@dataclass
class DataService(DCATResource):
    """A collection of operations that provides access to datasets."""

    endpoint_url: Optional[str] = None
    serves_dataset: List[str] = field(default_factory=list)
    endpoint_description: Optional[str] = None
    service_type: Optional[str] = None

    def __post_init__(self):
        """Validate the DataService after initialization."""
        if self.endpoint_url is None:
            raise ValueError("endpoint_url must be provided for DataService")


@dataclass
class DatasetSeries(DCATResource):
    """A collection of datasets sharing common characteristics."""

    datasets: List[str] = field(default_factory=list)
    temporal_coverage: Optional[Dict[str, str]] = None
    spatial_coverage: Optional[Dict[str, Any]] = None


@dataclass
class CatalogRecord:
    """A record in a data catalog, describing a single dataset or data service."""

    id: str
    primary_topic: str  # ID of the described resource
    title: Optional[str] = None
    description: Optional[str] = None
    issued: Optional[str] = None
    modified: Optional[str] = None
    conforms_to: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Catalog(DCATResource):
    """A curated collection of metadata about resources (e.g., datasets and data services)."""

    datasets: List[Dataset] = field(default_factory=list)
    services: List[DataService] = field(default_factory=list)
    records: List[CatalogRecord] = field(default_factory=list)
    dataset_series: List[DatasetSeries] = field(default_factory=list)

    def add_dataset(self, dataset: Dataset):
        """Add a dataset to the catalog."""
        self.datasets.append(dataset)

    def add_service(self, service: DataService):
        """Add a data service to the catalog."""
        self.services.append(service)

    def add_record(self, record: CatalogRecord):
        """Add a catalog record to the catalog."""
        self.records.append(record)

    def add_dataset_series(self, series: DatasetSeries):
        """Add a dataset series to the catalog."""
        self.dataset_series.append(series)


def load_catalog_from_json(file_path: str) -> Catalog:
    """Load a catalog from a JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Create the catalog
    catalog = Catalog(
        id=data.get("id", ""),
        title=data.get("title", ""),
        description=data.get("description", ""),
        keywords=data.get("keywords", []),
        themes=data.get("themes", []),
        issued=data.get("issued"),
        modified=data.get("modified"),
        landing_page=data.get("landing_page"),
        language=data.get("language", []),
        publisher=data.get("publisher"),
    )

    # Add datasets
    for dataset_data in data.get("datasets", []):
        distributions = []
        for dist_data in dataset_data.get("distributions", []):
            distribution = Distribution(
                id=dist_data.get("id", ""),
                title=dist_data.get("title", ""),
                description=dist_data.get("description", ""),
                keywords=dist_data.get("keywords", []),
                themes=dist_data.get("themes", []),
                issued=dist_data.get("issued"),
                modified=dist_data.get("modified"),
                landing_page=dist_data.get("landing_page"),
                language=dist_data.get("language", []),
                publisher=dist_data.get("publisher"),
                access_url=dist_data.get("access_url"),
                download_url=dist_data.get("download_url"),
                media_type=dist_data.get("media_type"),
                format=dist_data.get("format"),
                byte_size=dist_data.get("byte_size"),
                checksum=dist_data.get("checksum"),
                license=dist_data.get("license"),
            )
            distributions.append(distribution)

        dataset = Dataset(
            id=dataset_data.get("id", ""),
            title=dataset_data.get("title", ""),
            description=dataset_data.get("description", ""),
            keywords=dataset_data.get("keywords", []),
            themes=dataset_data.get("themes", []),
            issued=dataset_data.get("issued"),
            modified=dataset_data.get("modified"),
            landing_page=dataset_data.get("landing_page"),
            language=dataset_data.get("language", []),
            publisher=dataset_data.get("publisher"),
            distributions=distributions,
            temporal_coverage=dataset_data.get("temporal_coverage"),
            spatial_coverage=dataset_data.get("spatial_coverage"),
            accrual_periodicity=dataset_data.get("accrual_periodicity"),
            version=dataset_data.get("version"),
            version_notes=dataset_data.get("version_notes"),
            is_version_of=dataset_data.get("is_version_of"),
            has_version=dataset_data.get("has_version", []),
            source_dataset=dataset_data.get("source_dataset", []),
            contact_point=dataset_data.get("contact_point"),
        )
        catalog.add_dataset(dataset)

    # Add services
    for service_data in data.get("services", []):
        service = DataService(
            id=service_data.get("id", ""),
            title=service_data.get("title", ""),
            description=service_data.get("description", ""),
            keywords=service_data.get("keywords", []),
            themes=service_data.get("themes", []),
            issued=service_data.get("issued"),
            modified=service_data.get("modified"),
            landing_page=service_data.get("landing_page"),
            language=service_data.get("language", []),
            publisher=service_data.get("publisher"),
            endpoint_url=service_data.get("endpoint_url"),
            serves_dataset=service_data.get("serves_dataset", []),
            endpoint_description=service_data.get("endpoint_description"),
            service_type=service_data.get("service_type"),
        )
        catalog.add_service(service)

    return catalog


def save_catalog_to_json(catalog: Catalog, file_path: str):
    """Save a catalog to a JSON file."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(catalog.to_dict(), f, indent=2)
