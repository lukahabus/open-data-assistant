"""
Open Data Assistant - A tool for working with open data.

This is the main entry point for the Open Data Assistant application, which
provides various tools for working with open data, including:
- DCAT metadata processing and searching
- Data visualization and analysis
- Natural language querying of datasets
"""

import os
import argparse
from dotenv import load_dotenv

# Import DCAT package
from dcat import (
    Catalog,
    Dataset,
    Distribution,
    DataService,
    load_catalog_from_json,
    DCATEmbedder,
    DCATAssistant,
)

# Load environment variables
load_dotenv()


def main():
    """Main entry point for the Open Data Assistant application."""
    parser = argparse.ArgumentParser(
        description="Open Data Assistant - A tool for working with open data."
    )

    # Add subparsers for different functionalities
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # DCAT assistant subcommand
    dcat_parser = subparsers.add_parser("dcat", help="Run the DCAT assistant")
    dcat_parser.add_argument(
        "--catalog",
        default="dcat/sample_dcat_catalog.json",
        help="Path to the DCAT catalog JSON file",
    )
    dcat_parser.add_argument("--query", help="Query to process")

    # Parse arguments
    args = parser.parse_args()

    # Handle commands
    if args.command == "dcat":
        # Run DCAT assistant
        run_dcat_assistant(args.catalog, args.query)
    else:
        parser.print_help()


def run_dcat_assistant(catalog_path: str, query: str = None):
    """Run the DCAT assistant with the given catalog and query.

    Args:
        catalog_path: Path to the DCAT catalog JSON file.
        query: Optional query to process.
    """
    print(f"Loading catalog from {catalog_path}...")

    # Initialize the DCAT assistant
    catalog = load_catalog_from_json(catalog_path)
    embedder = DCATEmbedder()

    # Check if vector store already exists
    vector_store_dir = "vector_store"
    if os.path.exists(vector_store_dir):
        print("Loading existing vector store...")
        embedder.load_vector_store(vector_store_dir)
    else:
        print("Creating new vector store...")
        embedder.embed_catalog(catalog)
        os.makedirs(vector_store_dir, exist_ok=True)
        embedder.save_vector_store(embedder.vector_store, vector_store_dir)

    assistant = DCATAssistant(embedder)

    if query:
        # Process the provided query
        result = assistant.process_query(query)
        print("\nAnswer:")
        print(result["answer"])
    else:
        # Interactive mode
        print("\nDCAT Assistant initialized. Type 'exit' to quit.")
        while True:
            user_input = input("\nYour question: ")
            if user_input.lower() in ["exit", "quit", "q"]:
                break

            result = assistant.process_query(user_input)
            print("\nAnswer:")
            print(result["answer"])


if __name__ == "__main__":
    main()
