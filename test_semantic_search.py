#!/usr/bin/env python3
"""Test script to demonstrate semantic search improvements"""

import os
import sys

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from interactive_dataset_assistant import (
    extract_semantic_concepts,
    generate_semantic_search_queries,
    find_relevant_datasets,
    analyze_user_query,
)


def test_semantic_analysis():
    """Test the semantic analysis functionality"""

    # Test query about electricity and GDP
    test_query = (
        "give me all datasets about how electricity and GDP per capita are related"
    )

    print("=" * 80)
    print(f"TEST QUERY: {test_query}")
    print("=" * 80)

    # Step 1: Extract semantic concepts
    print("\n1. EXTRACTING SEMANTIC CONCEPTS:")
    concepts = extract_semantic_concepts(test_query)

    print(f"   Main Topics: {concepts.get('main_topics', [])}")
    print(f"   Variables: {concepts.get('variables', [])}")
    print(f"   Geographic: {concepts.get('geographic', [])}")
    print(f"   Related Terms: {concepts.get('related_terms', [])}")

    # Step 2: Generate search queries
    print("\n2. GENERATING SEARCH QUERIES:")
    search_queries = generate_semantic_search_queries(test_query, concepts)

    for i, query in enumerate(search_queries, 1):
        print(f"   Query {i}: {query}")

    # Step 3: Show how this is different from old approach
    print("\n3. COMPARISON WITH OLD APPROACH:")
    analysis = analyze_user_query(test_query)
    print(
        f"   Old approach would search for: '{analysis.location}' (because location was detected as 'global')"
    )
    print(f"   New approach uses {len(search_queries)} targeted semantic queries")

    print("\n" + "=" * 80)
    print("The new semantic approach will:")
    print("1. Search for electricity-related datasets")
    print("2. Search for GDP and economic indicator datasets")
    print("3. Look for datasets that combine both concepts")
    print("4. Rank results by relevance to the original query")
    print("5. Return datasets that actually match the user's intent")

    # Test another query
    print("\n" + "=" * 80)
    test_query2 = "Find datasets about COVID-19 vaccination rates in European countries"
    print(f"TEST QUERY 2: {test_query2}")
    print("=" * 80)

    concepts2 = extract_semantic_concepts(test_query2)
    print("\nSEMANTIC CONCEPTS:")
    print(f"   Main Topics: {concepts2.get('main_topics', [])}")
    print(f"   Variables: {concepts2.get('variables', [])}")
    print(f"   Geographic: {concepts2.get('geographic', [])}")

    search_queries2 = generate_semantic_search_queries(test_query2, concepts2)
    print("\nGENERATED QUERIES:")
    for i, query in enumerate(search_queries2[:5], 1):
        print(f"   {i}. {query}")


if __name__ == "__main__":
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key to test semantic analysis")
        sys.exit(1)

    test_semantic_analysis()
