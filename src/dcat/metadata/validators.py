"""
Validators for DCAT metadata to ensure data quality and consistency.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from .base import DCATCatalog, DCATDataset, DCATDistribution, DCATProperty


class ValidationError:
    """Represents a validation error in DCAT metadata."""

    def __init__(self, field: str, message: str, severity: str = "error"):
        self.field = field
        self.message = message
        self.severity = severity  # "error", "warning", or "info"

    def __str__(self) -> str:
        return f"{self.severity.upper()}: {self.field} - {self.message}"


class DCATValidator:
    """Validator for DCAT metadata."""

    @staticmethod
    def validate_property(
        prop: Optional[Dict[str, DCATProperty]], field_name: str
    ) -> List[ValidationError]:
        """Validate a DCAT property."""
        errors = []

        if not prop:
            errors.append(
                ValidationError(field_name, "Property is required but missing", "error")
            )
            return errors

        for lang, value in prop.items():
            if not value.value.strip():
                errors.append(
                    ValidationError(
                        f"{field_name}.{lang}",
                        f"Value for language '{lang}' is empty",
                        "error",
                    )
                )

            if value.confidence < 0 or value.confidence > 1:
                errors.append(
                    ValidationError(
                        f"{field_name}.{lang}",
                        f"Confidence score must be between 0 and 1, got {value.confidence}",
                        "error",
                    )
                )

        return errors

    @staticmethod
    def validate_url(url: Optional[str], field_name: str) -> List[ValidationError]:
        """Validate a URL field."""
        errors = []

        if url:
            if not url.startswith(("http://", "https://", "ftp://")):
                errors.append(
                    ValidationError(field_name, f"Invalid URL format: {url}", "error")
                )

        return errors

    @staticmethod
    def validate_date(
        date: Optional[datetime], field_name: str
    ) -> List[ValidationError]:
        """Validate a date field."""
        errors = []

        if date:
            if date > datetime.now():
                errors.append(
                    ValidationError(
                        field_name, f"Date cannot be in the future: {date}", "warning"
                    )
                )

        return errors

    @classmethod
    def validate_distribution(
        cls, distribution: DCATDistribution
    ) -> List[ValidationError]:
        """Validate a DCAT Distribution."""
        errors = []

        # Validate required fields
        errors.extend(cls.validate_property(distribution.title, "distribution.title"))

        # Validate URLs
        errors.extend(
            cls.validate_url(distribution.download_url, "distribution.download_url")
        )
        errors.extend(
            cls.validate_url(distribution.access_url, "distribution.access_url")
        )

        # Validate format
        if not distribution.format and not distribution.media_type:
            errors.append(
                ValidationError(
                    "distribution.format",
                    "Either format or media_type must be specified",
                    "warning",
                )
            )

        # Validate byte size
        if distribution.byte_size is not None and distribution.byte_size < 0:
            errors.append(
                ValidationError(
                    "distribution.byte_size",
                    f"Byte size cannot be negative: {distribution.byte_size}",
                    "error",
                )
            )

        return errors

    @classmethod
    def validate_dataset(cls, dataset: DCATDataset) -> List[ValidationError]:
        """Validate a DCAT Dataset."""
        errors = []

        # Validate required fields
        errors.extend(cls.validate_property(dataset.title, "dataset.title"))
        errors.extend(cls.validate_property(dataset.description, "dataset.description"))

        # Validate dates
        errors.extend(cls.validate_date(dataset.issued, "dataset.issued"))
        errors.extend(cls.validate_date(dataset.modified, "dataset.modified"))

        # Validate distributions
        if not dataset.distributions:
            errors.append(
                ValidationError(
                    "dataset.distributions",
                    "Dataset should have at least one distribution",
                    "warning",
                )
            )

        for i, distribution in enumerate(dataset.distributions):
            dist_errors = cls.validate_distribution(distribution)
            for error in dist_errors:
                error.field = f"dataset.distributions[{i}].{error.field}"
                errors.append(error)

        # Validate keywords and themes
        if not dataset.keywords and not dataset.themes:
            errors.append(
                ValidationError(
                    "dataset.keywords",
                    "Dataset should have either keywords or themes",
                    "warning",
                )
            )

        # Validate similarity scores
        for dataset_id, score in dataset.similarity_scores.items():
            if score < 0 or score > 1:
                errors.append(
                    ValidationError(
                        f"dataset.similarity_scores[{dataset_id}]",
                        f"Similarity score must be between 0 and 1, got {score}",
                        "error",
                    )
                )

        return errors

    @classmethod
    def validate_catalog(cls, catalog: DCATCatalog) -> List[ValidationError]:
        """Validate a DCAT Catalog."""
        errors = []

        # Validate required fields
        errors.extend(cls.validate_property(catalog.title, "catalog.title"))

        # Validate homepage
        errors.extend(cls.validate_url(catalog.homepage, "catalog.homepage"))

        # Validate datasets
        if not catalog.datasets:
            errors.append(
                ValidationError(
                    "catalog.datasets",
                    "Catalog should have at least one dataset",
                    "warning",
                )
            )

        # Validate each dataset
        for i, dataset in enumerate(catalog.datasets):
            dataset_errors = cls.validate_dataset(dataset)
            for error in dataset_errors:
                error.field = f"catalog.datasets[{i}].{error.field}"
                errors.append(error)

        # Check for duplicate dataset IDs
        dataset_ids = [d.identifier.id for d in catalog.datasets]
        duplicate_ids = {id_ for id_ in dataset_ids if dataset_ids.count(id_) > 1}
        if duplicate_ids:
            errors.append(
                ValidationError(
                    "catalog.datasets",
                    f"Duplicate dataset IDs found: {duplicate_ids}",
                    "error",
                )
            )

        return errors

    @classmethod
    def validate_and_score(
        cls, catalog: DCATCatalog
    ) -> Tuple[List[ValidationError], float]:
        """Validate a catalog and return a quality score."""
        errors = cls.validate_catalog(catalog)

        # Calculate quality score based on errors
        total_weight = 0
        error_weight = 0

        for error in errors:
            if error.severity == "error":
                weight = 1.0
            elif error.severity == "warning":
                weight = 0.5
            else:  # info
                weight = 0.1

            total_weight += weight
            error_weight += weight

        # Perfect score is 1.0, worst is 0.0
        if total_weight == 0:
            quality_score = 1.0
        else:
            quality_score = 1.0 - (error_weight / (total_weight * 2))

        return errors, quality_score
