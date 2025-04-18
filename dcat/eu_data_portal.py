"""Module for interacting with the EU Data Portal."""

from typing import List, Dict, Any, Optional
import logging
from SPARQLWrapper import SPARQLWrapper, JSON
from .sparql_processor import SparqlQueryProcessor


class EUDataPortal:
    """Interface for EU Data Portal interaction."""

    SPARQL_ENDPOINT = "https://data.europa.eu/sparql"

    def __init__(self):
        """Initialize EU Data Portal interface."""
        self.sparql = SPARQLWrapper(self.SPARQL_ENDPOINT)
        self.sparql.setReturnFormat(JSON)
        self.query_processor = SparqlQueryProcessor()
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

    def search_datasets(self, query: str) -> List[Dict[str, Any]]:
        """Search for datasets using natural language query.

        Args:
            query: Natural language query string

        Returns:
            List of matching datasets
        """
        try:
            # Convert natural query to SPARQL
            sparql_query = self.query_processor.process_query(query)

            # Execute query
            self.sparql.setQuery(sparql_query)
            results = self.sparql.query().convert()

            # Process results
            datasets = []
            for binding in results.get("results", {}).get("bindings", []):
                dataset = self._process_binding(binding)
                if dataset:
                    datasets.append(dataset)

            self.logger.info(f"Found {len(datasets)} datasets matching query: {query}")
            return datasets

        except Exception as e:
            self.logger.error(f"Error searching datasets: {str(e)}")
            return []

    def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific dataset.

        Args:
            dataset_id: Dataset identifier

        Returns:
            Dataset metadata or None if not found
        """
        try:
            query = f"""
                {self.query_processor.DEFAULT_PREFIXES}
                
                SELECT ?title ?description ?publisher ?modified ?theme ?format
                WHERE {{
                    <{dataset_id}> a dcat:Dataset ;
                        dct:title ?title ;
                        dct:description ?description .
                    
                    OPTIONAL {{ <{dataset_id}> dct:publisher/foaf:name ?publisher }}
                    OPTIONAL {{ <{dataset_id}> dct:modified ?modified }}
                    OPTIONAL {{ <{dataset_id}> dcat:theme/skos:prefLabel ?theme }}
                    OPTIONAL {{ 
                        <{dataset_id}> dcat:distribution ?distribution .
                        ?distribution dct:format/rdfs:label ?format
                    }}
                    
                    FILTER(LANG(?title) = "en" || LANG(?title) = "")
                    FILTER(LANG(?description) = "en" || LANG(?description) = "")
                }}
            """

            self.sparql.setQuery(query)
            results = self.sparql.query().convert()

            if results.get("results", {}).get("bindings"):
                return self._process_binding(results["results"]["bindings"][0])
            return None

        except Exception as e:
            self.logger.error(f"Error getting dataset {dataset_id}: {str(e)}")
            return None

    def get_distributions(self, dataset_id: str) -> List[Dict[str, Any]]:
        """Get distribution information for a dataset.

        Args:
            dataset_id: Dataset identifier

        Returns:
            List of dataset distributions
        """
        try:
            query = f"""
                {self.query_processor.DEFAULT_PREFIXES}
                
                SELECT ?url ?format ?description ?size
                WHERE {{
                    <{dataset_id}> dcat:distribution ?distribution .
                    ?distribution dcat:accessURL ?url .
                    OPTIONAL {{ ?distribution dct:format/rdfs:label ?format }}
                    OPTIONAL {{ ?distribution dct:description ?description }}
                    OPTIONAL {{ ?distribution dcat:byteSize ?size }}
                }}
            """

            self.sparql.setQuery(query)
            results = self.sparql.query().convert()

            distributions = []
            for binding in results.get("results", {}).get("bindings", []):
                distribution = {
                    "url": binding.get("url", {}).get("value"),
                    "format": binding.get("format", {}).get("value"),
                    "description": binding.get("description", {}).get("value"),
                    "size": binding.get("size", {}).get("value"),
                }
                distributions.append(distribution)

            return distributions

        except Exception as e:
            self.logger.error(f"Error getting distributions for {dataset_id}: {str(e)}")
            return []

    def _process_binding(self, binding: Dict[str, Any]) -> Dict[str, Any]:
        """Process a SPARQL result binding into dataset metadata.

        Args:
            binding: SPARQL result binding

        Returns:
            Processed dataset metadata
        """
        dataset = {}

        # Map SPARQL variables to metadata fields
        field_mappings = {
            "dataset": "@id",
            "title": "dct:title",
            "description": "dct:description",
            "publisher": "dct:publisher",
            "modified": "dct:modified",
            "theme": "dcat:theme",
        }

        for sparql_var, metadata_field in field_mappings.items():
            if sparql_var in binding:
                value = binding[sparql_var]["value"]
                if sparql_var == "publisher":
                    dataset[metadata_field] = {"foaf:name": value}
                else:
                    dataset[metadata_field] = value

        return dataset
