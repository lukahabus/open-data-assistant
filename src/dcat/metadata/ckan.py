"""
CKAN-specific adapter for DCAT metadata.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from .base import (
    DCATAgent,
    DCATCatalog,
    DCATDataset,
    DCATDistribution,
    DCATIdentifier,
    DCATProperty,
)


class CKANAdapter:
    """Adapter class for converting between CKAN and DCAT metadata formats."""

    @staticmethod
    def _parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime from CKAN string format."""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            return None

    @staticmethod
    def _create_property(value: str, language: Optional[str] = None) -> DCATProperty:
        """Create a DCAT property from a value."""
        return DCATProperty(value=value, language=language, source="ckan")

    @classmethod
    def create_agent_from_ckan(cls, org_dict: Dict[str, Any]) -> DCATAgent:
        """Create a DCAT Agent from CKAN organization data."""
        agent = DCATAgent()
        agent.identifier.source_id = org_dict.get("id")
        agent.name = {"en": cls._create_property(org_dict.get("title", ""))}
        agent.type = "organization"
        agent.homepage = org_dict.get("url")
        agent.email = org_dict.get("email")

        return agent

    @classmethod
    def create_distribution_from_ckan(
        cls, resource_dict: Dict[str, Any]
    ) -> DCATDistribution:
        """Create a DCAT Distribution from CKAN resource data."""
        distribution = DCATDistribution()
        distribution.identifier.source_id = resource_dict.get("id")
        distribution.title = {"en": cls._create_property(resource_dict.get("name", ""))}
        distribution.description = {
            "en": cls._create_property(resource_dict.get("description", ""))
        }
        distribution.download_url = resource_dict.get("url")
        distribution.access_url = resource_dict.get("url")
        distribution.format = resource_dict.get("format")
        distribution.media_type = resource_dict.get("mimetype")
        distribution.byte_size = resource_dict.get("size")

        return distribution

    @classmethod
    def create_dataset_from_ckan(cls, package_dict: Dict[str, Any]) -> DCATDataset:
        """Create a DCAT Dataset from CKAN package data."""
        dataset = DCATDataset()
        dataset.identifier.source_id = package_dict.get("id")
        dataset.title = {"en": cls._create_property(package_dict.get("title", ""))}
        dataset.description = {
            "en": cls._create_property(package_dict.get("notes", ""))
        }

        # Temporal metadata
        dataset.issued = cls._parse_datetime(package_dict.get("metadata_created"))
        dataset.modified = cls._parse_datetime(package_dict.get("metadata_modified"))

        # Keywords and themes
        dataset.keywords = [
            cls._create_property(tag["name"]) for tag in package_dict.get("tags", [])
        ]

        # Add groups as themes
        dataset.themes = [
            cls._create_property(group["title"])
            for group in package_dict.get("groups", [])
        ]

        # Organization as publisher
        if "organization" in package_dict and package_dict["organization"]:
            dataset.publisher = cls.create_agent_from_ckan(package_dict["organization"])

        # Resources as distributions
        dataset.distributions = [
            cls.create_distribution_from_ckan(resource)
            for resource in package_dict.get("resources", [])
        ]

        # Additional metadata
        dataset.metadata.update(
            {
                "ckan_name": package_dict.get("name"),
                "ckan_url": package_dict.get("url"),
                "ckan_version": package_dict.get("version"),
                "ckan_state": package_dict.get("state"),
                "ckan_type": package_dict.get("type"),
            }
        )

        return dataset

    @classmethod
    def create_catalog_from_ckan(
        cls, org_dict: Dict[str, Any], packages: List[Dict[str, Any]]
    ) -> DCATCatalog:
        """Create a DCAT Catalog from CKAN organization and its packages."""
        catalog = DCATCatalog()
        catalog.identifier.source_id = org_dict.get("id")
        catalog.title = {"en": cls._create_property(org_dict.get("title", ""))}
        catalog.description = {
            "en": cls._create_property(org_dict.get("description", ""))
        }
        catalog.homepage = org_dict.get("url")
        catalog.publisher = cls.create_agent_from_ckan(org_dict)

        # Add all datasets
        for package in packages:
            dataset = cls.create_dataset_from_ckan(package)
            catalog.add_dataset(dataset)

        return catalog

    @classmethod
    def to_ckan_package_dict(cls, dataset: DCATDataset) -> Dict[str, Any]:
        """Convert a DCAT Dataset to CKAN package dictionary."""
        package_dict = {
            "id": dataset.identifier.source_id,
            "name": dataset.metadata.get("ckan_name", ""),
            "title": dataset.title.get("en", DCATProperty("")).value,
            "notes": dataset.description.get("en", DCATProperty("")).value,
            "url": dataset.metadata.get("ckan_url"),
            "version": dataset.metadata.get("ckan_version"),
            "state": dataset.metadata.get("ckan_state", "active"),
            "type": dataset.metadata.get("ckan_type", "dataset"),
            "tags": [{"name": kw.value} for kw in dataset.keywords],
            "groups": [{"title": theme.value} for theme in dataset.themes],
            "resources": [
                {
                    "id": dist.identifier.source_id,
                    "name": dist.title.get("en", DCATProperty("")).value,
                    "description": dist.description.get("en", DCATProperty("")).value,
                    "url": dist.download_url or dist.access_url,
                    "format": dist.format,
                    "mimetype": dist.media_type,
                    "size": dist.byte_size,
                }
                for dist in dataset.distributions
            ],
        }

        if dataset.publisher:
            package_dict["organization"] = {
                "id": dataset.publisher.identifier.source_id,
                "title": dataset.publisher.name.get("en", DCATProperty("")).value,
                "url": dataset.publisher.homepage,
                "email": dataset.publisher.email,
            }

        return package_dict
