from typing import List, Dict, Any, Optional
import logging
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, DCTERMS
from SPARQLWrapper import SPARQLWrapper, JSON
import requests
import json
from datetime import datetime
from pathlib import Path


class DCATHarvester:
    """Harvests DCAT metadata from various sources."""

    DCAT = URIRef("http://www.w3.org/ns/dcat#")
    FORMATS = {
        "application/rdf+xml": "xml",
        "text/turtle": "turtle",
        "application/ld+json": "json-ld",
        "application/n-triples": "nt",
    }

    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize the harvester.

        Args:
            cache_dir: Directory to cache harvested metadata
        """
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.graph = Graph()
        self._setup_logging()

    def _setup_logging(self):
        """Set up logging configuration."""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def harvest_sparql(self, endpoint_url: str, query: str) -> List[Dict[str, Any]]:
        """Harvest DCAT metadata using SPARQL.

        Args:
            endpoint_url: SPARQL endpoint URL
            query: SPARQL query string

        Returns:
            List of harvested dataset metadata
        """
        sparql = SPARQLWrapper(endpoint_url)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)

        try:
            results = sparql.query().convert()
            self.logger.info(f"Successfully harvested from {endpoint_url}")
            return self._process_sparql_results(results)
        except Exception as e:
            self.logger.error(f"Error harvesting from {endpoint_url}: {str(e)}")
            return []

    def harvest_rdf(self, url: str, format: str = None) -> List[Dict[str, Any]]:
        """Harvest DCAT metadata from an RDF document.

        Args:
            url: URL of the RDF document
            format: RDF format (if None, will be guessed from Content-Type)

        Returns:
            List of harvested dataset metadata
        """
        try:
            response = requests.get(url)
            response.raise_for_status()

            if not format:
                content_type = response.headers.get("content-type", "").split(";")[0]
                format = self.FORMATS.get(content_type, "xml")

            self.graph.parse(data=response.text, format=format)
            self.logger.info(f"Successfully harvested from {url}")
            return self._process_graph()
        except Exception as e:
            self.logger.error(f"Error harvesting from {url}: {str(e)}")
            return []

    def harvest_ckan(
        self, portal_url: str, api_key: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Harvest DCAT metadata from a CKAN portal.

        Args:
            portal_url: CKAN portal URL
            api_key: Optional API key for authentication

        Returns:
            List of harvested dataset metadata
        """
        headers = {"Authorization": api_key} if api_key else {}

        try:
            # Get package list
            response = requests.get(
                f"{portal_url}/api/3/action/package_list", headers=headers
            )
            response.raise_for_status()
            packages = response.json()["result"]

            datasets = []
            for package_name in packages:
                # Get detailed package info
                response = requests.get(
                    f"{portal_url}/api/3/action/package_show",
                    params={"id": package_name},
                    headers=headers,
                )
                response.raise_for_status()
                package = response.json()["result"]
                datasets.append(self._convert_ckan_to_dcat(package))

            self.logger.info(f"Successfully harvested from {portal_url}")
            return datasets
        except Exception as e:
            self.logger.error(f"Error harvesting from {portal_url}: {str(e)}")
            return []

    def _process_sparql_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process SPARQL query results into DCAT metadata."""
        datasets = []
        for binding in results.get("results", {}).get("bindings", []):
            dataset = {}
            for var, value in binding.items():
                if value["type"] == "uri":
                    dataset[var] = {"@id": value["value"]}
                else:
                    dataset[var] = value["value"]
            datasets.append(dataset)
        return datasets

    def _process_graph(self) -> List[Dict[str, Any]]:
        """Process RDF graph into DCAT metadata."""
        datasets = []
        for subject in self.graph.subjects(RDF.type, self.DCAT.Dataset):
            dataset = {"@id": str(subject)}

            # Get basic metadata
            for predicate, obj in self.graph.predicate_objects(subject):
                if isinstance(obj, Literal):
                    dataset[str(predicate)] = str(obj)
                elif isinstance(obj, URIRef):
                    dataset[str(predicate)] = {"@id": str(obj)}

            datasets.append(dataset)
        return datasets

    def _convert_ckan_to_dcat(self, package: Dict[str, Any]) -> Dict[str, Any]:
        """Convert CKAN package metadata to DCAT format."""
        return {
            "@type": "dcat:Dataset",
            "@id": package.get("id"),
            "dct:title": package.get("title"),
            "dct:description": package.get("notes"),
            "dct:identifier": package.get("name"),
            "dct:modified": package.get("metadata_modified"),
            "dct:publisher": {
                "@type": "foaf:Organization",
                "foaf:name": package.get("organization", {}).get("title"),
            },
            "dcat:distribution": [
                {
                    "@type": "dcat:Distribution",
                    "dct:title": res.get("name"),
                    "dcat:accessURL": res.get("url"),
                    "dct:format": res.get("format"),
                    "dct:description": res.get("description"),
                }
                for res in package.get("resources", [])
            ],
        }

    def save_cache(self, datasets: List[Dict[str, Any]], source_id: str):
        """Cache harvested datasets.

        Args:
            datasets: List of dataset metadata
            source_id: Identifier for the source
        """
        if not self.cache_dir:
            return

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = (
            self.cache_dir / f"{source_id}_{datetime.now().strftime('%Y%m%d')}.json"
        )

        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(datasets, f, ensure_ascii=False, indent=2)

        self.logger.info(f"Cached {len(datasets)} datasets to {cache_file}")

    def load_cache(self, source_id: str) -> List[Dict[str, Any]]:
        """Load cached datasets.

        Args:
            source_id: Identifier for the source

        Returns:
            List of cached dataset metadata
        """
        if not self.cache_dir:
            return []

        cache_files = list(self.cache_dir.glob(f"{source_id}_*.json"))
        if not cache_files:
            return []

        # Get most recent cache file
        cache_file = max(cache_files)

        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                datasets = json.load(f)
            self.logger.info(f"Loaded {len(datasets)} datasets from cache {cache_file}")
            return datasets
        except Exception as e:
            self.logger.error(f"Error loading cache {cache_file}: {str(e)}")
            return []
