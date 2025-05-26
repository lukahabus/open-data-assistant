"""
Main module for implementing Linked Data Based Exploratory Search.

This module will contain the components and logic inspired by the PhD thesis
"Linked data based exploratory search" by Nicolas Marie.
(Ref: https://inria.hal.science/tel-01130622v1)

Components might include:
-   Data structures for typed graphs.
-   Spreading activation algorithms or similar associative retrieval mechanisms.
-   Querying modules for interacting with SPARQL endpoints.
-   Result presentation and exploration logic (conceptual).
"""

import requests
import json
import logging
from typing import Dict, List, Union, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("exploratory_search.log")],
)


class ExploratorySearchEngine:
    """
    A class to encapsulate the linked data exploratory search functionalities.
    """

    def __init__(self, sparql_endpoint: str, timeout: int = 30, max_retries: int = 3):
        """
        Initializes the search engine.

        Args:
            sparql_endpoint (str): The SPARQL endpoint to query.
            timeout (int): Timeout in seconds for SPARQL queries.
            max_retries (int): Maximum number of retries for failed queries.
        """
        self.sparql_endpoint = sparql_endpoint
        self.timeout = timeout

        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        # Create a session with retry strategy
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        logging.info(
            f"ExploratorySearchEngine initialized with endpoint: {self.sparql_endpoint}"
        )

    def execute_sparql_query(self, query: str) -> Union[Dict, str]:
        """
        Executes a SPARQL query against the configured endpoint.

        Args:
            query (str): The SPARQL query string.

        Returns:
            Union[Dict, str]: The JSON results if successful, or an error message string.
        """
        logging.info(f"Executing SPARQL query:\n{query}")
        headers = {
            "Accept": "application/sparql-results+json",
            "User-Agent": "LinkedDataExploratorySearch/1.0",
        }
        params = {"query": query}

        try:
            start_time = time.time()
            response = self.session.get(
                self.sparql_endpoint,
                headers=headers,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            results = response.json()

            execution_time = time.time() - start_time
            logging.info(
                f"SPARQL query successful in {execution_time:.2f}s, "
                f"{len(results.get('results', {}).get('bindings', []))} bindings returned."
            )
            return results

        except requests.exceptions.Timeout:
            error_msg = (
                f"Error: SPARQL query execution timed out after {self.timeout}s."
            )
            logging.error(error_msg)
            return error_msg

        except requests.exceptions.RequestException as e:
            error_msg = f"Error: SPARQL query execution failed. Request Error: {str(e)}"
            logging.error(error_msg, exc_info=True)
            return error_msg

        except json.JSONDecodeError as e:
            error_msg = (
                f"Error: SPARQL query execution failed. Response not valid JSON. "
                f"Error: {str(e)}. Response Text (first 200 chars): {response.text[:200]}"
            )
            logging.error(error_msg, exc_info=True)
            return error_msg

        except Exception as e:
            error_msg = f"Error: An unexpected error occurred: {str(e)}"
            logging.error(error_msg, exc_info=True)
            return error_msg

    def associative_retrieval(self, seed_entities: List[str]) -> Dict:
        """
        Performs associative retrieval by fetching direct outgoing properties and
        their objects for a list of seed entities.

        Args:
            seed_entities (List[str]): A list of initial entity URIs to start the exploration.

        Returns:
            Dict: A dictionary where keys are seed entity URIs and values are lists
                  of dictionaries, each representing a property-object pair.
        """
        logging.info(
            f"Performing associative retrieval for {len(seed_entities)} entities"
        )
        all_related_data = {}

        # Process entities in smaller batches to avoid overwhelming the endpoint
        batch_size = 5
        for i in range(0, len(seed_entities), batch_size):
            batch = seed_entities[i : i + batch_size]

            for entity_uri in batch:
                query = f"""
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                
                SELECT DISTINCT ?predicate ?object ?objectLabel
                WHERE {{
                  <{entity_uri}> ?predicate ?object .
                  OPTIONAL {{
                    ?object rdfs:label|skos:prefLabel ?objectLabel .
                    FILTER(LANGMATCHES(LANG(?objectLabel), "en") || LANG(?objectLabel) = "")
                  }}
                }}
                LIMIT 50
                """

                results = self.execute_sparql_query(query)
                entity_relations = []

                if isinstance(results, dict) and "results" in results:
                    bindings = results["results"].get("bindings", [])
                    for binding in bindings:
                        relation = {
                            "predicate": binding["predicate"]["value"],
                            "object": binding["object"]["value"],
                            "object_type": binding["object"]["type"],
                        }
                        if "objectLabel" in binding:
                            relation["object_label"] = binding["objectLabel"]["value"]
                        entity_relations.append(relation)
                elif isinstance(results, str):
                    logging.warning(
                        f"Could not retrieve relations for {entity_uri}: {results}"
                    )

                all_related_data[entity_uri] = entity_relations

                # Add a small delay between queries to be nice to the endpoint
                time.sleep(0.5)

        logging.info(
            f"Associative retrieval completed. Found related data for {len(all_related_data)} entities."
        )
        return all_related_data

    def find_exploratory_paths(
        self, query: str, depth: int = 1, limit: int = 10
    ) -> Dict:
        """
        Main method to perform an exploratory search.

        Args:
            query (str): The user's natural language query or initial search terms.
            depth (int): The depth of exploration (currently 1 level).
            limit (int): Maximum number of seed entities to retrieve.

        Returns:
            Dict: A structured representation of the exploration results.
        """
        logging.info(
            f"Starting exploratory search for query: '{query}' with depth {depth}"
        )

        # Optimize the initial query with better filtering and indexing hints
        initial_sparql_query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT DISTINCT ?seedEntity ?label ?type
        WHERE {{
          {{
            ?seedEntity rdfs:label ?label .
            FILTER(CONTAINS(LCASE(STR(?label)), LCASE("{query}")))
            FILTER(LANGMATCHES(LANG(?label), "en") || LANG(?label) = "")
          }}
          UNION
          {{
            ?seedEntity dct:title|skos:prefLabel ?label .
            FILTER(CONTAINS(LCASE(STR(?label)), LCASE("{query}")))
            FILTER(LANGMATCHES(LANG(?label), "en") || LANG(?label) = "")
          }}
          OPTIONAL {{ ?seedEntity rdf:type ?type . }}
        }}
        LIMIT {limit}
        """

        initial_results = self.execute_sparql_query(initial_sparql_query)

        if isinstance(initial_results, str):
            return {
                "error": "Failed to get initial seed entities",
                "details": initial_results,
                "query_used": initial_sparql_query,
            }

        seed_entities_bindings = initial_results.get("results", {}).get("bindings", [])
        seed_entities = [
            binding["seedEntity"]["value"] for binding in seed_entities_bindings
        ]

        if not seed_entities:
            return {
                "message": "No initial seed entities found for the query.",
                "query_used": initial_sparql_query,
                "results_received": initial_results,
            }

        logging.info(f"Found {len(seed_entities)} seed entities")
        related_concepts_data = self.associative_retrieval(seed_entities)

        exploration_results = {
            "query": query,
            "seed_entities_details": seed_entities_bindings,
            "related_concepts": related_concepts_data,
            "paths_explored": [],
            "message": "Exploratory search completed successfully.",
            "metadata": {
                "depth": depth,
                "seed_entities_count": len(seed_entities),
                "related_concepts_count": len(related_concepts_data),
            },
        }
        return exploration_results


if __name__ == "__main__":
    logging.info("--- Initializing Linked Data Exploratory Search ---")

    # Example: Using DBpedia endpoint
    dbpedia_endpoint = "https://dbpedia.org/sparql"
    engine = ExploratorySearchEngine(
        sparql_endpoint=dbpedia_endpoint, timeout=45, max_retries=3  # Increased timeout
    )

    # Example query
    test_query = "machine learning"
    results = engine.find_exploratory_paths(
        test_query, limit=5
    )  # Reduced limit for testing

    logging.info("\n--- Exploratory Search Results ---")
    if isinstance(results, str):
        print(results)
    else:
        print(json.dumps(results, indent=2))
    logging.info("------------------------------------")

    # Example direct SPARQL query (if needed for testing the connection)
    # sample_query = """
    # SELECT ?label
    # WHERE {
    #  <http://dbpedia.org/resource/Linked_Data> rdfs:label ?label .
    #  FILTER (LANG(?label) = 'en')
    # }
    # LIMIT 1
    # """
    # direct_results = engine.execute_sparql_query(sample_query)
    # logging.info("\n--- Direct SPARQL Test ---")
    # print(json.dumps(direct_results, indent=2))
    # logging.info("--------------------------")
