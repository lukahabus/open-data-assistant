#!/usr/bin/env python3
"""Demo script showing how simple queries work better"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from interactive_dataset_assistant import (
    extract_semantic_concepts,
    generate_semantic_search_queries,
    query_eu_api_robust,
    rank_datasets_by_relevance,
)


def demo_simple_vs_complex():
    """Demonstrate the difference between complex and simple queries"""

    print("DEMO: Simple vs Complex Queries for EU Open Data Portal")
    print("=" * 70)

    # Complex query that returns 0 results
    complex_query = '"electricity consumption GDP per capita correlation"'
    print(f"\n1. COMPLEX QUERY: {complex_query}")
    print("   (This is what the old system would generate)")

    results = query_eu_api_robust(complex_query, 5)
    print(f"   Results: {len(results)} datasets found")
    if results:
        for r in results[:3]:
            print(f"   - {r.get('title', '')[:60]}...")

    # Simple queries that work better
    print("\n2. SIMPLE QUERIES (New Approach):")
    simple_queries = ["electricity", "GDP", "energy", "economic"]

    all_results = []
    seen_titles = set()

    for query in simple_queries:
        print(f"\n   Query: '{query}'")
        results = query_eu_api_robust(query, 5)
        print(f"   Results: {len(results)} datasets found")

        # Add unique results
        for dataset in results:
            title = dataset.get("title", "")
            if title and title not in seen_titles:
                seen_titles.add(title)
                dataset["search_query"] = query
                all_results.append(dataset)

        # Show first few titles
        for r in results[:2]:
            print(f"     - {r.get('title', '')[:50]}...")

    # Now rank the combined results
    print(f"\n3. RANKING COMBINED RESULTS:")
    print(f"   Total unique datasets found: {len(all_results)}")

    # Extract concepts for ranking
    test_query = "electricity and GDP per capita"
    concepts = extract_semantic_concepts(test_query)

    # Rank results
    ranked_results = rank_datasets_by_relevance(all_results, test_query, concepts)

    print(f"\n   TOP RANKED RESULTS (by relevance to '{test_query}'):")
    for i, dataset in enumerate(ranked_results[:5], 1):
        print(f"\n   {i}. {dataset.get('title', 'No title')}")
        print(f"      Score: {dataset.get('semantic_relevance_score', 0)}")
        print(f"      Found with: '{dataset.get('search_query', '')}'")
        desc = dataset.get("dataset_description", "")[:100]
        if desc:
            print(f"      Description: {desc}...")

    print("\n" + "=" * 70)
    print("CONCLUSION: Simple queries find more datasets, then ranking")
    print("identifies the most relevant ones based on semantic analysis!")


if __name__ == "__main__":
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable not set")
        sys.exit(1)

    demo_simple_vs_complex()
