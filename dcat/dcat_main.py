"""
DCAT Main - Main entry point for the DCAT assistant.

This script provides a command-line interface for interacting with the DCAT
assistant, allowing users to search for datasets, ask questions about datasets,
and learn about the DCAT metadata model.
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Add the parent directory to sys.path to allow importing dcat modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Now import the modules
from dcat.dcat_metadata import load_catalog_from_json
from dcat.dcat_embedding import DCATEmbedder
from dcat.dcat_assistant import DCATAssistant
from dcat import sample_dcat_data

# Load environment variables
load_dotenv()


def check_environment():
    """Check that the environment is properly set up."""
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
        print(
            "Please create a .env file with your OpenAI API key or set it in your environment."
        )
        print("Format: OPENAI_API_KEY=sk-...")
        sys.exit(1)


def initialize_dcat_assistant():
    """Initialize the DCAT Assistant."""
    # Set up paths using absolute paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    catalog_path = os.path.join(script_dir, "sample_dcat_catalog.json")
    vector_store_dir = os.path.join(os.path.dirname(script_dir), "vector_store")

    # Check if sample catalog exists, if not create it
    if not os.path.exists(catalog_path):
        print("Sample DCAT catalog not found. Creating...")
        sample_dcat_data.main()

    # Load the catalog
    print("Loading DCAT catalog...")
    catalog = load_catalog_from_json(catalog_path)

    # Create the embedder
    print("Creating DCAT embedder...")
    embedder = DCATEmbedder()

    # Check if vector store exists
    if os.path.exists(vector_store_dir):
        print("Loading existing vector store...")
        embedder.load_vector_store(vector_store_dir)
    else:
        print("Embedding catalog...")
        embedder.embed_catalog(catalog)
        os.makedirs(vector_store_dir, exist_ok=True)
        print("Saving vector store...")
        embedder.save_vector_store(embedder.vector_store, vector_store_dir)

    # Create the assistant
    print("Creating DCAT assistant...")
    assistant = DCATAssistant(embedder)

    return assistant


def run_interactive_mode(assistant):
    """Run the DCAT Assistant in interactive mode."""
    print("\nWelcome to the DCAT Assistant!")
    print("You can ask questions about the datasets in the catalog.")
    print("Type 'quit' or 'exit' to exit.")

    while True:
        # Get user input
        user_input = input("\nYou: ")

        # Check if user wants to exit
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        # Process the query
        try:
            result = assistant.process_query(user_input)
            print(f"\nAssistant: {result['answer']}")
        except Exception as e:
            print(f"\nError: {e}")


def demonstrate_functionality(assistant):
    """Demonstrate the key functionality of the DCAT Assistant."""
    print("\n=== DCAT Assistant Demonstration ===")

    # Demonstration 1: Basic dataset search
    print("\n1. Dataset Search")
    print("Query: 'Find datasets about education'")
    results = assistant.search_datasets("Find datasets about education", k=1)
    if results:
        doc, score = results[0]
        print(f"Top result (score: {score:.2f}):")
        print(doc.page_content)

    # Demonstration 2: Question answering
    print("\n2. Question Answering")
    print("Question: 'What datasets are available about streets in Zagreb?'")
    result = assistant.process_query(
        "What datasets are available about streets in Zagreb?"
    )
    print(f"Answer: {result['answer']}")

    # Demonstration 3: Related datasets
    print("\n3. Related Datasets")
    print(
        "Finding datasets related to 'dataset-001' (Geoportal visokoskolske ustanove)"
    )
    related = assistant.suggest_related_datasets("dataset-001", k=1)
    if related:
        print("Related dataset:")
        print(related[0])

    # Demonstration 4: Dataset-specific questions
    print("\n4. Dataset-specific Questions")
    print(
        "Question about dataset-002: 'What information does this dataset contain about streets?'"
    )
    answer = assistant.answer_question_about_dataset(
        "dataset-002", "What information does this dataset contain about streets?"
    )
    print(f"Answer: {answer}")


def main():
    """Main function to run the DCAT Assistant."""
    # Check environment
    check_environment()

    # Initialize DCAT Assistant
    assistant = initialize_dcat_assistant()

    # Ask user for mode
    print("\nHow would you like to use the DCAT Assistant?")
    print("1. Interactive mode")
    print("2. Demonstration mode")

    choice = input("Enter your choice (1 or 2): ")

    if choice == "1":
        run_interactive_mode(assistant)
    elif choice == "2":
        demonstrate_functionality(assistant)
    else:
        print("Invalid choice. Please enter 1 or 2.")
        main()


if __name__ == "__main__":
    main()
