"""Module for finding datasets in the EU Open Data Portal."""
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import requests
import json

class EUDatasetFinder:
    """Interface for finding datasets in the EU Open Data Portal."""
    
    def __init__(self, endpoint: str = "https://data.europa.eu/api/hub/repo/query"):
        """Initialize the dataset finder.
        
        Args:
            endpoint: SPARQL endpoint URL
        """
        self.endpoint = endpoint
        self._setup_logging()

    def _setup_logging(self):
        """Set up logging configuration."""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def find_recent_datasets(
        self,
        keywords: List[str],
        days_back: int = 180,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Find recent datasets matching keywords.
        
        Args:
            keywords: List of search keywords
            days_back: How many days back to search
            limit: Maximum number of results
            
        Returns:
            List of matching datasets
        """
        cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        # Build keyword filter
        keyword_filters = []
        for keyword in keywords:
            keyword_filters.append(f'CONTAINS(LCASE(STR(?title)), "{keyword.lower()}")')
        keyword_filter = " || ".join(keyword_filters)
        
        query = f"""
        SELECT DISTINCT ?dataset ?title ?modified ?publisher ?description
        WHERE {{
            ?dataset a dcat:Dataset ;
                    dct:title ?title ;
                    dct:modified ?modified .
            OPTIONAL {{ 
                ?dataset dct:publisher ?pub .
                ?pub foaf:name ?publisher 
            }}
            OPTIONAL {{
                ?dataset dct:description ?description
            }}
            
            FILTER({keyword_filter})
            FILTER(LANG(?title) = "en" || LANG(?title) = "")
            FILTER(?modified >= "{cutoff_date}"^^xsd:date)
        }}
        ORDER BY DESC(?modified)
        LIMIT {limit}
        """
        
        results = self._execute_query(query)
        return self._process_results(results)

    def find_datasets_by_format(
        self,
        format: str,
        keywords: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Find datasets in a specific format.
        
        Args:
            format: File format to search for (e.g., "csv", "json")
            keywords: Optional list of keywords to filter by
            limit: Maximum number of results
            
        Returns:
            List of matching datasets
        """
        # Build keyword filter if provided
        keyword_filter = ""
        if keywords:
            keyword_filters = []
            for keyword in keywords:
                keyword_filters.append(f'CONTAINS(LCASE(STR(?title)), "{keyword.lower()}")')
            keyword_filter = f"FILTER({' || '.join(keyword_filters)})"
        
        query = f"""
        SELECT DISTINCT ?dataset ?title ?distribution ?format ?description
        WHERE {{
            ?dataset a dcat:Dataset ;
                    dct:title ?title ;
                    dcat:distribution ?distribution .
            ?distribution dct:format ?format .
            OPTIONAL {{
                ?dataset dct:description ?description
            }}
            
            FILTER(CONTAINS(LCASE(STR(?format)), "{format.lower()}"))
            FILTER(LANG(?title) = "en" || LANG(?title) = "")
            {keyword_filter}
        }}
        LIMIT {limit}
        """
        
        results = self._execute_query(query)
        return self._process_results(results)

    def find_datasets_by_publisher(
        self,
        publisher_name: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Find datasets from a specific publisher.
        
        Args:
            publisher_name: Name of the publisher to search for
            limit: Maximum number of results
            
        Returns:
            List of matching datasets
        """
        query = f"""
        SELECT DISTINCT ?dataset ?title ?publisher ?modified ?description
        WHERE {{
            ?dataset a dcat:Dataset ;
                    dct:title ?title ;
                    dct:publisher ?pub .
            ?pub foaf:name ?publisher .
            OPTIONAL {{
                ?dataset dct:modified ?modified
            }}
            OPTIONAL {{
                ?dataset dct:description ?description
            }}
            
            FILTER(CONTAINS(LCASE(STR(?publisher)), "{publisher_name.lower()}"))
            FILTER(LANG(?title) = "en" || LANG(?title) = "")
        }}
        ORDER BY DESC(?modified)
        LIMIT {limit}
        """
        
        results = self._execute_query(query)
        return self._process_results(results)

    def get_dataset_details(self, dataset_uri: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific dataset.
        
        Args:
            dataset_uri: URI of the dataset
            
        Returns:
            Dataset details or None if not found
        """
        query = f"""
        SELECT DISTINCT ?title ?description ?modified ?publisher ?theme ?format
        WHERE {{
            <{dataset_uri}> a dcat:Dataset ;
                          dct:title ?title .
            OPTIONAL {{ <{dataset_uri}> dct:description ?description }}
            OPTIONAL {{ <{dataset_uri}> dct:modified ?modified }}
            OPTIONAL {{ 
                <{dataset_uri}> dct:publisher ?pub .
                ?pub foaf:name ?publisher 
            }}
            OPTIONAL {{ 
                <{dataset_uri}> dcat:theme ?themeUri .
                ?themeUri skos:prefLabel ?theme 
            }}
            OPTIONAL {{
                <{dataset_uri}> dcat:distribution ?dist .
                ?dist dct:format ?format
            }}
            
            FILTER(LANG(?title) = "en" || LANG(?title) = "")
        }}
        """
        
        results = self._execute_query(query)
        processed = self._process_results(results)
        return processed[0] if processed else None

    def _execute_query(self, query: str) -> dict:
        """Execute a SPARQL query.
        
        Args:
            query: SPARQL query string
            
        Returns:
            Query results
        """
        # Add common prefixes
        prefixed_query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        """ + query
        
        headers = {
            'Accept': 'application/sparql-results+json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(
                self.endpoint,
                headers=headers,
                data={'query': prefixed_query}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Query execution failed: {str(e)}")
            return {"error": str(e)}

    def _process_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process SPARQL query results.
        
        Args:
            results: Raw query results
            
        Returns:
            List of processed dataset dictionaries
        """
        processed = []
        
        if "error" in results:
            self.logger.error(f"Error in results: {results['error']}")
            return processed
            
        bindings = results.get("results", {}).get("bindings", [])
        
        for binding in bindings:
            dataset = {}
            for key, value in binding.items():
                # Extract simple value from SPARQL result format
                dataset[key] = value.get("value")
            processed.append(dataset)
            
        return processed