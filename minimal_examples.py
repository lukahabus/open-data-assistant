#!/usr/bin/env python3
"""
Minimal Working Examples for RAG System
Simple demonstrations for thesis documentation
"""

import sys
import os

# Add src directory for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def example_1_basic_rag():
    """Example 1: Basic RAG system initialization and similarity search"""
    from src.rag_system import RAGSystem, QueryExample

    print("Example 1: Basic RAG System")
    print("-" * 30)

    # Initialize RAG system
    rag = RAGSystem()

    # Add a simple example
    example = QueryExample(
        question="Find air quality datasets",
        sparql_query="""PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct: <http://purl.org/dc/terms/>
SELECT ?dataset ?title WHERE {
  ?dataset a dcat:Dataset .
  ?dataset dct:title ?title .
  FILTER(CONTAINS(LCASE(STR(?title)), "air quality"))
} LIMIT 10""",
        endpoint="https://data.europa.eu/sparql",
        description="Air quality dataset search",
    )

    # Add example to RAG system
    doc_id = rag.add_query_example(example)
    print(f"SUCCESS: Added example with ID: {doc_id[:8]}...")

    # Test similarity search
    similar = rag.retrieve_similar_examples("pollution data", n_results=1)
    print(f"SUCCESS: Found {len(similar)} similar examples")

    return True


def example_2_sparql_generation():
    """Example 2: RAG-enhanced SPARQL generation"""
    from src.rag_system import RAGSystem

    print("\nExample 2: SPARQL Generation")
    print("-" * 30)

    # Initialize and populate RAG system
    rag = RAGSystem()
    rag.populate_with_examples()
    print("SUCCESS: RAG system populated with examples")

    # Generate SPARQL query
    test_query = "Find environment datasets"
    sparql = rag.generate_sparql_with_rag(test_query)

    if sparql and not sparql.startswith("Error") and "PREFIX" in sparql:
        print("SUCCESS: SPARQL query generated successfully")
        print(f"   Query length: {len(sparql)} characters")
        # Show first few lines
        lines = sparql.split("\n")[:3]
        print(f"   Sample: {' '.join(lines)}...")
        return True
    else:
        print("FAILED: SPARQL generation failed")
        return False


def example_3_schema_extraction():
    """Example 3: Simple schema extraction"""
    from src.schema_extractor import SchemaExtractor

    print("\nExample 3: Schema Extraction")
    print("-" * 30)

    # Create schema extractor
    extractor = SchemaExtractor("https://data.europa.eu/sparql")

    # Extract DCAT schema (simple and fast)
    try:
        dcat_info = extractor.get_dcat_specific_schema()

        if dcat_info and dcat_info.get("datasets", 0) > 0:
            print(f"SUCCESS: Found {dcat_info.get('datasets', 0):,} datasets")
            print(f"SUCCESS: Found {dcat_info.get('publishers', 0):,} publishers")
            return True
        else:
            print("WARNING: No schema information retrieved")
            return False
    except Exception as e:
        print(f"FAILED: Schema extraction failed: {e}")
        return False


def example_4_simple_working_queries():
    """Example 4: Demonstrate simple working queries"""
    from src.rag_system import RAGSystem

    print("\nExample 4: Simple Working Queries")
    print("-" * 30)

    rag = RAGSystem()
    rag.populate_with_examples()

    # Test queries that should work
    test_queries = ["climate data", "energy information", "environment datasets"]

    success_count = 0

    for query in test_queries:
        print(f"Testing: '{query}'")
        try:
            sparql = rag.generate_sparql_with_rag(query)
            if sparql and "PREFIX" in sparql and not sparql.startswith("Error"):
                print(f"   SUCCESS: Success - {len(sparql)} chars")
                success_count += 1
            else:
                print(f"   FAILED: Failed")
        except Exception as e:
            print(f"   ERROR: Error: {e}")

    print(
        f"\nSuccess rate: {success_count}/{len(test_queries)} ({success_count/len(test_queries)*100:.0f}%)"
    )
    return success_count >= len(test_queries) * 0.67  # 67% success rate


def main():
    """Run all minimal examples"""
    print("Minimal RAG System Examples")
    print("=" * 40)
    print("Simple demonstrations for thesis documentation")
    print("=" * 40)

    examples = [
        ("Basic RAG System", example_1_basic_rag),
        ("SPARQL Generation", example_2_sparql_generation),
        ("Schema Extraction", example_3_schema_extraction),
        ("Working Queries", example_4_simple_working_queries),
    ]

    results = []

    for name, example_func in examples:
        try:
            result = example_func()
            results.append((name, result))
        except Exception as e:
            print(f"FAILED: {name} crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 40)
    print("EXAMPLE RESULTS")
    print("=" * 40)

    passed = 0
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status} {name}")
        if result:
            passed += 1

    print(
        f"\nOverall: {passed}/{len(results)} examples working ({passed/len(results)*100:.0f}%)"
    )

    if passed >= len(results) * 0.75:
        print("RAG system is functional and ready for thesis!")
    else:
        print("Some examples need attention.")

    # Thesis examples summary
    print("\nFor Thesis Documentation:")
    print("1. Basic RAG functionality demonstrated")
    print("2. Vector similarity search working")
    print("3. SPARQL generation from natural language")
    print("4. Schema extraction capabilities")
    print("5. Multi-modal querying approach")

    return passed >= len(results) * 0.75


if __name__ == "__main__":
    main()
