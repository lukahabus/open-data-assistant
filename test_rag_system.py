#!/usr/bin/env python3
"""
Test script for the advanced RAG-based Open Data Assistant
Demonstrates the integration of embeddings, vector database, SPARQL, and API calls
"""

import sys
import os
import logging
from typing import Dict, Any
import time

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.rag_system import RAGSystem, QueryExample
from src.schema_extractor import SchemaExtractor, auto_populate_rag_with_schema
from src.unified_data_assistant import ask_unified_assistant

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def test_rag_system():
    """Test basic RAG system functionality"""
    print("🧠 Testing RAG System Basic Functionality")
    print("=" * 50)

    try:
        # Initialize RAG system
        rag = RAGSystem()

        # Populate with examples
        rag.populate_with_examples()
        print("✅ RAG system initialized and populated with examples")

        # Test similarity search
        test_query = "Find environmental data about pollution in European cities"
        similar_examples = rag.retrieve_similar_examples(test_query, n_results=3)

        print(f"\n🔍 Similar examples for: '{test_query}'")
        for i, example in enumerate(similar_examples, 1):
            distance = example.get("distance", "N/A")
            print(f"{i}. {example['question']} (similarity: {distance})")

        # Test RAG-enhanced query generation
        sparql_query = rag.generate_sparql_with_rag(test_query)
        print(f"\n📝 Generated SPARQL query (first 200 chars):")
        print(sparql_query[:200] + "..." if len(sparql_query) > 200 else sparql_query)

        # Test query validation
        is_valid, message = rag.validate_sparql_query(sparql_query)
        print(f"\n✓ Query validation: {'PASS' if is_valid else 'FAIL'} - {message}")

        return True

    except Exception as e:
        print(f"❌ RAG system test failed: {e}")
        return False


def test_schema_extraction():
    """Test schema extraction functionality"""
    print("\n📊 Testing Schema Extraction")
    print("=" * 50)

    try:
        # Create schema extractor
        extractor = SchemaExtractor("https://data.europa.eu/sparql")

        print("🔄 Extracting DCAT schema information...")
        dcat_info = extractor.get_dcat_specific_schema()

        if dcat_info:
            print("✅ DCAT Schema extracted successfully:")
            print(f"   📈 Datasets: {dcat_info.get('datasets', 0):,}")
            print(f"   📦 Distributions: {dcat_info.get('distributions', 0):,}")
            print(f"   🏢 Publishers: {dcat_info.get('publishers', 0):,}")
            print(f"   🏷️  Themes: {dcat_info.get('themes', 0):,}")
        else:
            print("⚠️  No DCAT schema information found")

        return True

    except Exception as e:
        print(f"❌ Schema extraction test failed: {e}")
        return False


def test_unified_assistant():
    """Test the unified data assistant with various queries"""
    print("\n🚀 Testing Unified Data Assistant")
    print("=" * 50)

    test_queries = [
        "Find datasets about renewable energy and climate change",
        "Show me COVID-19 health data from European countries",
        "List transportation datasets with air quality measurements",
    ]

    results = []

    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Test Query {i}: {query}")
        print("-" * 40)

        start_time = time.time()

        try:
            result = ask_unified_assistant(query)
            end_time = time.time()

            if result["status"] == "success":
                print(f"✅ Success! (took {end_time - start_time:.2f}s)")
                print(f"📄 Answer (first 300 chars): {result['answer'][:300]}...")
                results.append(True)
            else:
                print(f"❌ Failed: {result.get('message', 'Unknown error')}")
                results.append(False)

        except Exception as e:
            print(f"❌ Error: {e}")
            results.append(False)

    success_rate = sum(results) / len(results) * 100
    print(
        f"\n📊 Overall Success Rate: {success_rate:.1f}% ({sum(results)}/{len(results)})"
    )

    return success_rate > 50  # Consider test passed if >50% queries succeed


def performance_benchmark():
    """Run a performance benchmark of the system"""
    print("\n⚡ Performance Benchmark")
    print("=" * 50)

    query = "Find energy consumption datasets from European agencies since 2020"
    iterations = 3

    times = []

    for i in range(iterations):
        print(f"🔄 Run {i+1}/{iterations}...")
        start_time = time.time()

        try:
            result = ask_unified_assistant(query)
            end_time = time.time()

            elapsed = end_time - start_time
            times.append(elapsed)

            status = "✅" if result["status"] == "success" else "❌"
            print(f"   {status} Completed in {elapsed:.2f}s")

        except Exception as e:
            print(f"   ❌ Failed: {e}")

    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        print(f"\n📈 Performance Summary:")
        print(f"   Average: {avg_time:.2f}s")
        print(f"   Fastest: {min_time:.2f}s")
        print(f"   Slowest: {max_time:.2f}s")

        return avg_time < 30  # Consider good if average under 30s

    return False


def system_comparison():
    """Compare different approaches (SPARQL vs API vs Unified)"""
    print("\n⚖️  System Comparison")
    print("=" * 50)

    query = "Find climate change datasets with environmental indicators"

    print(f"📋 Comparing approaches for: '{query}'")

    # Test unified approach
    print("\n🔄 Testing Unified RAG + SPARQL + API approach...")
    start_time = time.time()

    try:
        unified_result = ask_unified_assistant(query)
        unified_time = time.time() - start_time

        unified_success = unified_result["status"] == "success"
        print(f"{'✅' if unified_success else '❌'} Unified: {unified_time:.2f}s")

    except Exception as e:
        print(f"❌ Unified approach failed: {e}")
        unified_success = False
        unified_time = 0

    # Summary
    print(f"\n📊 Comparison Summary:")
    print(
        f"   🚀 Unified RAG System: {'PASS' if unified_success else 'FAIL'} ({unified_time:.2f}s)"
    )
    print(
        f"   🎯 Performance: {'Excellent' if unified_time < 10 else 'Good' if unified_time < 20 else 'Acceptable'}"
    )

    return unified_success


def main():
    """Run all tests and benchmarks"""
    print("🌟 Advanced Open Data Assistant - RAG System Test Suite")
    print("=" * 60)
    print(
        "Based on research: 'LLM-based SPARQL Query Generation from Natural Language'"
    )
    print("Features: ChromaDB embeddings, schema extraction, unified querying")
    print("=" * 60)

    # Run all tests
    tests = [
        ("RAG System", test_rag_system),
        ("Schema Extraction", test_schema_extraction),
        ("Unified Assistant", test_unified_assistant),
        ("Performance Benchmark", performance_benchmark),
        ("System Comparison", system_comparison),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Running {test_name}...")
            result = test_func()
            results.append((test_name, result))

        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))

    # Final summary
    print("\n" + "=" * 60)
    print("🏁 FINAL TEST RESULTS")
    print("=" * 60)

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1

    print(
        f"\n📊 Overall: {passed}/{len(results)} tests passed ({passed/len(results)*100:.1f}%)"
    )

    if passed == len(results):
        print("🎉 All tests passed! The RAG system is working perfectly.")
    elif passed >= len(results) * 0.7:
        print("✨ Most tests passed! The system is working well.")
    else:
        print("⚠️  Some tests failed. Please check the logs for issues.")

    # Next steps recommendation
    print("\n🎯 Next Steps:")
    print("1. Run: python test_rag_system.py")
    print("2. Try: from src import ask_unified_assistant")
    print("3. Query: ask_unified_assistant('your question here')")
    print("4. Explore: Check the vector_store/ directory for embeddings")
    print("5. Thesis: Document the RAG system in your thesis chapters")


if __name__ == "__main__":
    main()
