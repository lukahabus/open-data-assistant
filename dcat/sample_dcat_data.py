"""
Sample DCAT Data - Generates sample DCAT metadata for testing.

This module provides functions for generating sample DCAT metadata, including
catalogs, datasets, distributions, and services.
"""

import pandas as pd
import numpy as np
import uuid
from datetime import datetime
import pytz
import json
import os
import sys
from typing import List, Dict, Any

# Handle imports to work when run directly or as a module
try:
    from .dcat_metadata import (
        Catalog,
        Dataset,
        Distribution,
        DataService,
        DatasetSeries,
        CatalogRecord,
        DCATResource,
        save_catalog_to_json,
    )
except ImportError:
    from dcat_metadata import (
        Catalog,
        Dataset,
        Distribution,
        DataService,
        DatasetSeries,
        CatalogRecord,
        DCATResource,
        save_catalog_to_json,
    )


def create_sample_catalog():
    """Create a sample catalog with datasets from the original project."""
    # Set up paths to data files
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    edu_csv_path = os.path.join(
        root_dir, "data", "Geoportal_visokoskolske_ustanove.csv"
    )
    streets_csv_path = os.path.join(root_dir, "data", "ulicegz.csv")

    # Create the catalog
    catalog = Catalog(
        id="catalog-001",
        title="Open Data Zagreb Catalog",
        description="A catalog of open datasets from the City of Zagreb",
        keywords=["zagreb", "open data", "geospatial", "education", "streets"],
        themes=["education", "geography", "infrastructure"],
        issued="2023-01-16",
        modified="2023-01-30",
        publisher={"name": "City of Zagreb", "url": "https://www.zagreb.hr"},
    )

    # Create the visokoskolske ustanove dataset
    try:
        edu_df = pd.read_csv(edu_csv_path)
        edu_dataset_description = f"""Dataset containing the locations of higher education institutions in Zagreb.
        Contains {len(edu_df)} institutions with their geographical coordinates and metadata.
        The dataset includes the name of each institution, its address, and precise coordinates."""
    except Exception as e:
        print(f"Warning: Could not read {edu_csv_path}: {e}")
        edu_df = pd.DataFrame()
        edu_dataset_description = "Dataset containing the locations of higher education institutions in Zagreb."

    edu_distribution = Distribution(
        id="distribution-001",
        title="Geoportal visokoskolske ustanove CSV",
        description="CSV file containing data on higher education institutions in Zagreb",
        keywords=["education", "geospatial", "zagreb", "institutions"],
        access_url="https://geoportal.zagreb.hr/Public/Datasets/Download/135",
        download_url="https://geoportal.zagreb.hr/Public/Datasets/Download/135",
        media_type="text/csv",
        format="CSV",
        license="https://data.gov.hr/otvorena-dozvola",
    )

    edu_dataset = Dataset(
        id="dataset-001",
        title="Geoportal visokoskolske ustanove",
        description=edu_dataset_description,
        keywords=["education", "university", "college", "zagreb", "geospatial"],
        themes=["education", "geography"],
        issued="2023-01-16",
        modified="2023-01-30",
        distributions=[edu_distribution],
        spatial_coverage={
            "type": "Point",
            "coordinates": [15.97, 45.81],  # Zagreb coordinates
        },
        publisher={
            "name": "City of Zagreb - Geoportal",
            "url": "https://geoportal.zagreb.hr",
        },
    )

    # Create the streets dataset
    try:
        streets_df = pd.read_csv(streets_csv_path, delimiter=";")
        streets_dataset_description = f"""Dataset containing information about streets in Zagreb.
        Contains {len(streets_df)} streets with detailed information about each street,
        including the street name, the person or entity it was named after, and historical information."""
    except Exception as e:
        print(f"Warning: Could not read {streets_csv_path}: {e}")
        streets_df = pd.DataFrame()
        streets_dataset_description = (
            "Dataset containing information about streets in Zagreb."
        )

    streets_distribution = Distribution(
        id="distribution-002",
        title="Zagreb Streets CSV",
        description="CSV file containing data on streets in Zagreb",
        keywords=["streets", "zagreb", "urban"],
        access_url="https://data.gov.hr/dataset/zagrebačke-ulice",
        download_url="https://data.gov.hr/dataset/zagrebačke-ulice/resource/download",
        media_type="text/csv",
        format="CSV",
        license="https://data.gov.hr/otvorena-dozvola",
    )

    streets_dataset = Dataset(
        id="dataset-002",
        title="Zagreb Streets Dataset",
        description=streets_dataset_description,
        keywords=["streets", "zagreb", "urban", "city", "infrastructure"],
        themes=["infrastructure", "urban planning"],
        issued="2023-01-16",
        modified="2023-01-30",
        distributions=[streets_distribution],
        spatial_coverage={
            "type": "Point",
            "coordinates": [15.97, 45.81],  # Zagreb coordinates
        },
        publisher={"name": "City of Zagreb", "url": "https://www.zagreb.hr"},
    )

    # Create a data service for the datasets
    mapping_service = DataService(
        id="service-001",
        title="Zagreb Open Data Mapping Service",
        description="A service that provides geospatial mapping capabilities for Zagreb open datasets",
        endpoint_url="https://geoportal.zagreb.hr/Public/Map/Default",
        serves_dataset=["dataset-001", "dataset-002"],
        service_type="WMS",
    )

    # Create a dataset series for related datasets
    zagreb_geo_series = DatasetSeries(
        id="series-001",
        title="Zagreb Geospatial Datasets",
        description="A series of geospatial datasets for the City of Zagreb",
        keywords=["zagreb", "geospatial", "geography"],
        themes=["geography", "urban planning"],
        datasets=["dataset-001", "dataset-002"],
    )

    # Add catalog records
    edu_record = CatalogRecord(
        id="record-001",
        primary_topic="dataset-001",
        title="Catalog Record for Geoportal visokoskolske ustanove",
        description="Metadata record for the Geoportal visokoskolske ustanove dataset",
        issued="2023-01-16",
        modified="2023-01-30",
    )

    streets_record = CatalogRecord(
        id="record-002",
        primary_topic="dataset-002",
        title="Catalog Record for Zagreb Streets Dataset",
        description="Metadata record for the Zagreb Streets dataset",
        issued="2023-01-16",
        modified="2023-01-30",
    )

    # Add everything to the catalog
    catalog.add_dataset(edu_dataset)
    catalog.add_dataset(streets_dataset)
    catalog.add_service(mapping_service)
    catalog.add_dataset_series(zagreb_geo_series)
    catalog.add_record(edu_record)
    catalog.add_record(streets_record)

    return catalog


def main():
    """Create sample data and save it to a JSON file."""
    catalog = create_sample_catalog()

    # Use os.path.join for cross-platform compatibility
    script_dir = os.path.dirname(os.path.abspath(__file__))
    catalog_path = os.path.join(script_dir, "sample_dcat_catalog.json")

    save_catalog_to_json(catalog, catalog_path)
    print(f"Sample DCAT catalog created and saved to {catalog_path}")


if __name__ == "__main__":
    main()
