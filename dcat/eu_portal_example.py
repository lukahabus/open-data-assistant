"""Example script demonstrating EU Data Portal integration."""
import json
from .eu_data_portal import EUDataPortal
from typing import Dict, Any
import re


def natural_to_sparql(query: str) -> str:
    """Convert natural language query to SPARQL query."""
    # Basic patterns to detect query intent
    temporal_pattern = (
        r"\b(from|after|before|between)\s+(\d{4}(?:-\d{2})?(?:-\d{2})?)\b"
    )
    keyword_pattern = r"about|related to|containing|with|about|on\s+(\w+)"
    format_pattern = r"\b(format|type)\s+(is|in)\s+(\w+)\b"

    # Default prefixes
    sparql_query = """
    PREFIX dcat: <http://www.w3.org/ns/dcat#>
    PREFIX dct: <http://purl.org/dc/terms/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    
    SELECT DISTINCT ?dataset ?title ?description ?publisher ?modified WHERE {
        ?dataset a dcat:Dataset ;
                dct:title ?title ;
                dct:description ?description ;
                dct:publisher ?publisherURI ;
                dct:modified ?modified .
        
        ?publisherURI foaf:name ?publisher .
    """

    # Add filters based on query analysis
    filters = []

    # Check for temporal constraints
    temporal_matches = re.findall(temporal_pattern, query.lower())
    if temporal_matches:
        for prep, date in temporal_matches:
            if prep == "after":
                filters.append(f'FILTER(?modified >= "{date}"^^xsd:date)')
            elif prep == "before":
                filters.append(f'FILTER(?modified <= "{date}"^^xsd:date)')

    # Check for keywords/themes
    keyword_matches = re.findall(keyword_pattern, query.lower())
    if keyword_matches:
        keyword_filters = []
        for keyword in keyword_matches:
            keyword_filters.append(
                f'CONTAINS(LCASE(STR(?title)), "{keyword}") || CONTAINS(LCASE(STR(?description)), "{keyword}")'
            )
        if keyword_filters:
            filters.append("FILTER(" + " || ".join(keyword_filters) + ")")

    # Check for format constraints
    format_matches = re.findall(format_pattern, query.lower())
    if format_matches:
        for _, _, format_type in format_matches:
            sparql_query += """
        ?dataset dcat:distribution ?distribution .
        ?distribution dct:format ?format .
        """
            filters.append(f'FILTER(CONTAINS(LCASE(STR(?format)), "{format_type}"))')

    # Add all filters
    if filters:
        sparql_query += "\n    " + "\n    " + "\n    ".join(filters)

    # Close query
    sparql_query += """
}
ORDER BY DESC(?modified)
LIMIT 10
    """

    return sparql_query


def main():
    """Run EU Data Portal examples."""
    portal = EUDataPortal()

    # Example 1: Search for datasets about climate change
    print("\n=== Example 1: Climate Change Datasets ===")
    query = "Show me datasets about climate change from 2023"
    
    print("Executing query:", query)
    datasets = portal.search_datasets(query)
    
    print(f"\nFound {len(datasets)} datasets")
    for dataset in datasets[:3]:  # Show first 3 results
        print(f"\nTitle: {dataset.get('dct:title', 'N/A')}")
        publisher = dataset.get('dct:publisher', {}).get('foaf:name', 'N/A')
        print(f"Publisher: {publisher}")
        print(f"Modified: {dataset.get('dct:modified', 'N/A')}")

    # Example 2: Get CSV datasets about education
    print("\n=== Example 2: Education CSV Datasets ===")
    query = "Find datasets about education in CSV format"
    
    print("Executing query:", query)
    datasets = portal.search_datasets(query)
    
    print(f"\nFound {len(datasets)} datasets")
    for dataset in datasets[:3]:
        print(f"\nTitle: {dataset.get('dct:title', 'N/A')}")
        publisher = dataset.get('dct:publisher', {}).get('foaf:name', 'N/A')
        print(f"Publisher: {publisher}")
        
        # Get distribution information if available
        dataset_id = dataset.get('@id')
        if dataset_id:
            distributions = portal.get_distributions(dataset_id)
            if distributions:
                print("\nDistributions:")
                for dist in distributions:
                    print(f"- Format: {dist.get('format', 'N/A')}")
                    print(f"  URL: {dist.get('url', 'N/A')}")

if __name__ == "__main__":
    main()
