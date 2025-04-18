from typing import List, Dict, Any
import logging
from dcat.eu_data_portal import EUDataPortal
from dcat.sparql_processor import SparqlQueryProcessor


def run_example_queries():
    """Run example natural language queries against the EU Data Portal."""

    # Initialize components
    portal = EUDataPortal()
    processor = SparqlQueryProcessor()

    # Example queries showing different capabilities
    example_queries = [
        "Show me the latest environmental datasets",
        "Find datasets about education published in the last 6 months",
        "Get health datasets in CSV format from 2023",
        "Show me transportation datasets with JSON or XML format",
        "Find datasets about climate change published after 2020",
        "Get statistical data about employment from the last 2 years",
    ]

    print("Running natural language SPARQL query examples...")
    print("=" * 80)

    for query in example_queries:
        print(f"\nProcessing query: '{query}'")

        # Convert natural language to SPARQL
        sparql_query = processor.process_query(query)
        print("\nGenerated SPARQL query:")
        print(sparql_query)

        # Execute the query
        results = portal.execute_sparql_query(sparql_query)
        print("\nResults:")
        if isinstance(results, dict) and "error" in results:
            print(f"Error: {results['error']}")
        else:
            bindings = results.get("results", {}).get("bindings", [])
            if not bindings:
                print("No results found.")
            else:
                for item in bindings:
                    print("\nDataset:")
                    print(f"Title: {item.get('title', {}).get('value', 'N/A')}")
                    desc = item.get("description", {}).get("value", "N/A")
                    print(
                        f"Description: {desc[:200]}..."
                        if len(desc) > 200
                        else f"Description: {desc}"
                    )
                    print(f"Publisher: {item.get('publisher', {}).get('value', 'N/A')}")
                    print(f"Modified: {item.get('modified', {}).get('value', 'N/A')}")

        print("\n" + "=" * 80)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_example_queries()
