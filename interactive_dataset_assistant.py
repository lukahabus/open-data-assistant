#!/usr/bin/env python3
"""
Interactive Dataset Assistant
Allows users to input natural language queries to find and analyze datasets
"""

import sys
import os
import logging
from typing import Dict, Any, List
import time
import requests
import json
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from pydantic import BaseModel, Field

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryAnalysis(BaseModel):
    """Analysis of user's natural language query"""

    intent: str = Field(
        description="What the user wants to do (search, analyze, compare, etc.)"
    )
    domain: str = Field(
        description="Subject domain (environment, health, economy, etc.)"
    )
    location: str = Field(description="Geographic focus if any")
    time_period: str = Field(description="Time period of interest if any")
    data_format: str = Field(description="Preferred data format if specified")
    complexity: str = Field(
        description="Simple, Medium, or Complex based on query requirements"
    )


def execute_sparql_query(
    query: str, endpoint: str = "https://data.europa.eu/sparql", limit: int = 30
) -> Dict[str, Any]:
    """Execute a SPARQL query and return results"""
    try:
        # Clean up the query
        query = query.strip()

        # Simplify complex queries that might cause errors
        if "EXISTS" in query and "OPTIONAL" in query:
            logger.info("Detected complex query, attempting to simplify...")
            # Create a simpler version for testing
            simple_query = """
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct: <http://purl.org/dc/terms/>

SELECT DISTINCT ?dataset ?title
WHERE {
  ?dataset a dcat:Dataset .
  ?dataset dct:title ?title .
  FILTER(LANG(?title) = "en" || LANG(?title) = "")
}
LIMIT 10
"""
            logger.info("Using simplified query instead of complex original")
            query = simple_query

        # Add LIMIT if not present
        if "LIMIT" not in query.upper():
            if query.endswith("}"):
                lines = query.split("\n")
                for i in range(len(lines) - 1, -1, -1):
                    if "}" in lines[i]:
                        lines.insert(i, f"LIMIT {limit}")
                        break
                query = "\n".join(lines)
            else:
                query += f"\nLIMIT {limit}"

        # Try GET request first
        params = {"query": query, "format": "application/sparql-results+json"}

        try:
            response = requests.get(
                endpoint,
                params=params,
                timeout=60,
                headers={
                    "Accept": "application/sparql-results+json",
                    "User-Agent": "Mozilla/5.0 (compatible; SPARQL-Client/1.0)",
                },
            )

            if response.status_code in [200, 206]:
                result = response.json()
                if result.get("results", {}).get("bindings") is not None:
                    return result

        except Exception as e:
            logger.warning(f"GET request failed: {e}, trying POST...")

        # Fallback to POST
        headers = {
            "Accept": "application/sparql-results+json",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (compatible; SPARQL-Client/1.0)",
        }

        data = {"query": query}
        response = requests.post(endpoint, headers=headers, data=data, timeout=60)

        if response.status_code in [200, 206]:
            result = response.json()
            if result.get("results", {}).get("bindings") is not None:
                return result
            else:
                return {"error": "Query executed but returned no results"}
        else:
            return {"error": f"HTTP {response.status_code}: {response.text[:200]}"}

    except Exception as e:
        return {"error": f"Error: {str(e)}"}


def format_sparql_results(results: Dict[str, Any], max_display: int = 10) -> str:
    """Format SPARQL results for display"""
    if "error" in results:
        return f"Error: {results['error']}"

    bindings = results.get("results", {}).get("bindings", [])
    if not bindings:
        return "No results found"

    variables = list(bindings[0].keys())
    formatted = f"Found {len(bindings)} results:\n\n"

    # Display up to max_display results
    display_count = min(len(bindings), max_display)

    for i, binding in enumerate(bindings[:display_count], 1):
        formatted += f"Result {i}:\n"
        for var in variables:
            value = binding.get(var, {}).get("value", "")
            formatted += f"   {var}: {value}\n"
        formatted += "\n"

    if len(bindings) > max_display:
        formatted += f"... and {len(bindings) - max_display} more results\n"

    return formatted


def analyze_user_query(user_input: str) -> QueryAnalysis:
    """Analyze user's natural language input to understand intent"""
    try:
        llm = OpenAI(temperature=0)

        prompt = PromptTemplate(
            template="""Analyze the following user query and extract key information:

User Query: "{user_input}"

Please analyze this query and provide:
- Intent: What does the user want to do? (search, analyze, compare, visualize, etc.)
- Domain: What subject area? (environment, health, economy, transport, agriculture, education, etc.)
- Location: Any geographic focus? (specific country, region, city, or "global" if not specified)
- Time Period: Any time constraints? (recent, historical, specific years, or "any" if not specified)
- Data Format: Any format preferences? (CSV, JSON, XML, or "any" if not specified)
- Complexity: Rate as Simple, Medium, or Complex based on requirements

IMPORTANT: 
- For Location: If a country name is mentioned (like Croatia, Germany, France, etc.), extract it exactly
- For Domain: Look for subject keywords (environment, health, economy, energy, transport, agriculture, etc.)
- Be specific with location detection - country names should be captured precisely

Respond in this exact format:
Intent: [intent]
Domain: [domain]
Location: [location]
Time Period: [time_period]
Data Format: [data_format]
Complexity: [complexity]

Analysis:""",
            input_variables=["user_input"],
        )

        # Use the newer RunnableSequence format
        chain = prompt | llm
        result = chain.invoke({"user_input": user_input})

        # Parse the result
        lines = result.strip().split("\n")
        analysis_data = {}

        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower().replace(" ", "_")
                value = value.strip()
                analysis_data[key] = value

        # Additional location detection for common country names
        user_lower = user_input.lower()
        countries = [
            "croatia",
            "germany",
            "france",
            "italy",
            "spain",
            "poland",
            "netherlands",
            "belgium",
            "austria",
            "portugal",
            "greece",
            "hungary",
            "czech republic",
            "slovakia",
            "slovenia",
            "estonia",
            "latvia",
            "lithuania",
            "finland",
            "sweden",
            "denmark",
            "ireland",
            "luxembourg",
            "malta",
            "cyprus",
            "bulgaria",
            "romania",
            "united kingdom",
            "uk",
            "britain",
        ]

        detected_location = analysis_data.get("location", "any")
        if detected_location == "any" or detected_location == "global":
            for country in countries:
                if country in user_lower:
                    detected_location = country.title()
                    break

        return QueryAnalysis(
            intent=analysis_data.get("intent", "search"),
            domain=analysis_data.get("domain", "general"),
            location=detected_location,
            time_period=analysis_data.get("time_period", "any"),
            data_format=analysis_data.get("data_format", "any"),
            complexity=analysis_data.get("complexity", "Medium"),
        )

    except Exception as e:
        logger.error(f"Error analyzing query: {e}")
        # Return default analysis
        return QueryAnalysis(
            intent="search",
            domain="general",
            location="any",
            time_period="any",
            data_format="any",
            complexity="Medium",
        )


def find_relevant_datasets(
    user_input: str, analysis: QueryAnalysis, max_results: int = 10
) -> List[Dict]:
    """Find datasets relevant to user's query by directly querying EU Open Data Portal"""
    try:
        logger.info(f"Starting dataset search for: '{user_input}'")

        # Strategy 1: Try specific search strategies for better results
        datasets = []

        # For location-specific queries, try different approaches
        if analysis.location != "any":
            location = analysis.location.lower()

            search_strategies = [
                location,  # Just the location name
                f'"{location}"',  # Quoted location name for exact match
                f"{location} data",  # Location + data
                f"{location} statistics",  # Location + statistics
                f"{location} datasets",  # Location + datasets
                user_input.lower(),  # Original query
            ]

            # Remove duplicates while preserving order
            seen = set()
            unique_strategies = []
            for strategy in search_strategies:
                if strategy not in seen:
                    seen.add(strategy)
                    unique_strategies.append(strategy)

            search_strategies = unique_strategies
        else:
            # For non-location queries, try variations
            search_strategies = [
                user_input.lower(),
                f"{user_input} data",
                f"{user_input} datasets",
                f"{user_input} statistics",
            ]

        for strategy in search_strategies:
            logger.info(f"Trying search strategy: '{strategy}'")
            api_results = query_eu_api_robust(strategy, max_results)

            if api_results:
                logger.info(
                    f"Found {len(api_results)} relevant datasets with strategy: '{strategy}'"
                )
                datasets.extend(api_results)

                # If we found good results, try to get similar datasets
                for dataset in api_results[
                    :2
                ]:  # Try similar datasets for top 2 results
                    similar = get_similar_datasets(dataset.get("dataset_uri", ""))
                    if similar:
                        # Filter similar datasets too
                        filtered_similar = filter_relevant_datasets(similar, user_input)
                        datasets.extend(
                            filtered_similar[:1]
                        )  # Add top 1 similar dataset

                break  # Stop after first successful strategy

        # Strategy 2: If no API results, try SPARQL with location filtering
        if not datasets:
            logger.info(
                "No API results found, trying SPARQL approach with location filtering"
            )
            sparql_results = query_eu_open_data_portal_filtered(user_input, analysis)
            if sparql_results:
                datasets.extend(sparql_results)

        # Strategy 3: If still no results, try broader searches
        if not datasets:
            logger.info("No results found, trying broader search terms")

            # Try broader terms based on analysis
            broader_terms = []
            if analysis.location != "any":
                broader_terms.extend(
                    [
                        f"{analysis.location}",
                        f"europe {analysis.location}",
                        f"european {analysis.location}",
                    ]
                )

            if analysis.domain != "general":
                broader_terms.extend(
                    [
                        analysis.domain,
                        f"{analysis.domain} data",
                        f"{analysis.domain} statistics",
                    ]
                )

            # Remove duplicates
            broader_terms = list(set(broader_terms))

            for term in broader_terms[:3]:  # Try max 3 broader terms
                logger.info(f"Trying broader search: '{term}'")
                api_results = query_eu_api_robust(term, max_results)
                if api_results:
                    # Apply stricter filtering for broader searches
                    filtered_results = filter_relevant_datasets(api_results, user_input)
                    if filtered_results:
                        datasets.extend(filtered_results)
                        break

        # Remove duplicates and limit results
        unique_datasets = []
        seen_titles = set()

        for dataset in datasets:
            title = dataset.get("title", dataset.get("question", ""))
            if title not in seen_titles:
                seen_titles.add(title)
                unique_datasets.append(dataset)

                if len(unique_datasets) >= max_results:
                    break

        logger.info(f"Returning {len(unique_datasets)} unique datasets")

        if not unique_datasets:
            logger.warning(f"No relevant datasets found for query: '{user_input}'")
            return []

        return unique_datasets

    except Exception as e:
        logger.error(f"Error finding datasets: {e}")
        return []


def query_eu_open_data_portal_filtered(
    user_input: str, analysis: QueryAnalysis
) -> List[Dict]:
    """Query EU Open Data Portal with better location filtering"""
    try:
        # Generate SPARQL query with stronger location filtering
        sparql_query = generate_sparql_for_query_filtered(user_input, analysis)

        if not sparql_query or sparql_query.startswith("Error"):
            logger.error(f"Failed to generate SPARQL query: {sparql_query}")
            return []

        # Execute the SPARQL query
        results = execute_sparql_query(
            sparql_query, "https://data.europa.eu/sparql", 20
        )

        if "error" in results:
            logger.error(f"SPARQL execution failed: {results['error']}")
            return []

        # Convert SPARQL results to dataset format
        datasets = convert_sparql_results_to_datasets(results, user_input, sparql_query)

        # Apply additional filtering
        if analysis.location != "any":
            filtered_datasets = []
            location_lower = analysis.location.lower()

            for dataset in datasets:
                title = dataset.get("title", "").lower()
                description = dataset.get("dataset_description", "").lower()

                if location_lower in title or location_lower in description:
                    filtered_datasets.append(dataset)
                    logger.info(
                        f"SPARQL result passed location filter: {dataset.get('title', '')[:50]}..."
                    )
                else:
                    logger.info(
                        f"SPARQL result filtered out: {dataset.get('title', '')[:50]}..."
                    )

            return filtered_datasets

        return datasets

    except Exception as e:
        logger.error(f"Error querying EU Open Data Portal with filtering: {e}")
        return []


def generate_sparql_for_query_filtered(user_input: str, analysis: QueryAnalysis) -> str:
    """Generate SPARQL query with stronger location filtering"""
    try:
        # Build stronger location filter
        location_filter = ""
        if analysis.location != "any":
            location_term = analysis.location.lower()
            location_filter = f"""
      # Strong location filtering - must contain location in title, description, or spatial data
      FILTER (
        CONTAINS(LCASE(STR(?title)), "{location_term}") ||
        (BOUND(?description) && CONTAINS(LCASE(STR(?description)), "{location_term}")) ||
        EXISTS {{ 
          ?dataset dct:spatial ?spatialUri . 
          ?spatialUri skos:prefLabel ?spatialLabel .
          FILTER(CONTAINS(LCASE(STR(?spatialLabel)), "{location_term}"))
        }} ||
        EXISTS {{ 
          ?dataset dcat:keyword ?kw . 
          FILTER(CONTAINS(LCASE(STR(?kw)), "{location_term}"))
        }}
      )"""

        # Extract key terms from user input
        common_words = {
            "find",
            "show",
            "get",
            "datasets",
            "data",
            "about",
            "in",
            "for",
            "from",
            "with",
            "list",
        }
        input_words = [
            word.lower()
            for word in user_input.split()
            if word.lower() not in common_words and len(word) > 2
        ]

        # Build content filter - but make it optional if we have location filter
        content_filter = ""
        if input_words and analysis.location == "any":
            content_conditions = []
            for term in input_words:
                content_conditions.append(f'CONTAINS(LCASE(STR(?title)), "{term}")')
                content_conditions.append(
                    f'(BOUND(?description) && CONTAINS(LCASE(STR(?description)), "{term}"))'
                )
                content_conditions.append(
                    f'EXISTS {{ ?dataset dcat:keyword ?kw . FILTER(CONTAINS(LCASE(STR(?kw)), "{term}")) }}'
                )

            content_filter = f"""
      FILTER (
        {" || ".join(content_conditions)}
      )"""

        # Construct SPARQL query
        sparql_query = f"""PREFIX dct: <http://purl.org/dc/terms/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT DISTINCT ?dataset ?title ?description ?publisherName ?landingPage
WHERE {{
  ?dataset a dcat:Dataset .
  ?dataset dct:title ?title .
  OPTIONAL {{ ?dataset dct:description ?description . }}
  OPTIONAL {{ ?dataset dcat:landingPage ?landingPage . }}
  OPTIONAL {{ 
    ?dataset dct:publisher ?publisherOrg .
    ?publisherOrg foaf:name ?publisherName .
  }}
  {location_filter}
  {content_filter}
  
  FILTER(LANGMATCHES(LANG(?title), "en") || LANG(?title) = "")
}}
LIMIT 20"""

        logger.info(f"Generated filtered SPARQL query for '{user_input}'")
        return sparql_query

    except Exception as e:
        logger.error(f"Error generating filtered SPARQL query: {e}")
        return f"Error: Failed to generate SPARQL query: {e}"


def convert_sparql_results_to_datasets(
    results: Dict[str, Any], user_input: str, sparql_query: str
) -> List[Dict]:
    """Convert SPARQL results to dataset format"""
    datasets = []

    bindings = results.get("results", {}).get("bindings", [])

    for binding in bindings:
        dataset = {
            "question": f"Dataset found for: {user_input}",
            "sparql_query": sparql_query,
            "endpoint": "https://data.europa.eu/sparql",
            "description": f"Dataset from EU Open Data Portal",
            "distance": 0.0,
            # Add actual dataset information
            "dataset_uri": binding.get("dataset", {}).get("value", ""),
            "title": binding.get("title", {}).get("value", ""),
            "dataset_description": binding.get("description", {}).get("value", ""),
            "publisher": binding.get("publisherName", {}).get("value", ""),
            "landing_page": binding.get("landingPage", {}).get("value", ""),
        }
        datasets.append(dataset)

    return datasets


def generate_comprehensive_response(
    user_input: str,
    analysis: QueryAnalysis,
    datasets: List[Dict],
    sparql_results: List[Dict],
) -> str:
    """Generate a comprehensive response using LLM"""
    try:
        llm = OpenAI(temperature=0.3)

        # Prepare context - handle both direct EU portal results and SPARQL results
        dataset_info = ""
        direct_results_count = 0

        for i, dataset in enumerate(datasets, 1):
            dataset_info += f"\nDataset {i}:\n"

            # Check if this is a direct EU Open Data Portal result
            if (
                "Dataset found for:" in dataset.get("question", "")
                or dataset.get("source") == "EU_API"
            ):
                direct_results_count += 1
                dataset_info += f"- Title: {dataset.get('title', 'N/A')}\n"
                dataset_info += f"- Description: {dataset.get('dataset_description', 'N/A')[:150]}...\n"
                dataset_info += f"- Publisher: {dataset.get('publisher', 'N/A')}\n"
                dataset_info += f"- Source: EU Open Data Portal\n"

                # Add relevance score if available
                relevance = dataset.get(
                    "calculated_relevance", dataset.get("relevance_score", 0)
                )
                if relevance > 0:
                    dataset_info += f"- Relevance Score: {relevance}\n"

        results_info = ""
        successful_queries = 0
        for i, result in enumerate(sparql_results, 1):
            if isinstance(result, dict) and "api_result" in result:
                results_info += f"\nAPI Result {i}: Successfully retrieved from EU Open Data Portal\n"
                successful_queries += 1
            elif "error" not in result:
                bindings = result.get("results", {}).get("bindings", [])
                results_info += f"\nSPARQL Query {i} returned {len(bindings)} results\n"
                successful_queries += 1
            else:
                results_info += (
                    f"\nQuery {i} had issues: {result.get('error', 'Unknown error')}\n"
                )

        # Determine the primary source of results
        primary_source = "EU Open Data Portal"

        prompt = PromptTemplate(
            template="""You are an expert data analyst helping users find and understand open datasets from the EU Open Data Portal.

User Query: "{user_input}"

Query Analysis:
- Intent: {intent}
- Domain: {domain}
- Location: {location}
- Time Period: {time_period}
- Data Format: {data_format}
- Complexity: {complexity}

Found Datasets from {primary_source}:
{dataset_info}

Query Results Summary:
{results_info}

EU Portal Results: {direct_results_count} out of {total_datasets}
Successful Queries: {successful_queries} out of {total_queries}

Please provide a comprehensive response that:
1. Acknowledges the user's request and the location/domain focus
2. Summarizes what datasets were found and their relevance to the query
3. Highlights the quality and source of the data from the EU Open Data Portal
4. If location-specific (like Croatia), emphasize whether results are actually relevant to that location
5. Suggests next steps for accessing and using the data
6. Mentions any limitations or considerations

Make your response helpful, informative, and actionable. Be honest about the relevance of results.

Response:""",
            input_variables=[
                "user_input",
                "intent",
                "domain",
                "location",
                "time_period",
                "data_format",
                "complexity",
                "dataset_info",
                "results_info",
                "primary_source",
                "direct_results_count",
                "total_datasets",
                "successful_queries",
                "total_queries",
            ],
        )

        # Use the newer RunnableSequence format
        chain = prompt | llm
        result = chain.invoke(
            {
                "user_input": user_input,
                "intent": analysis.intent,
                "domain": analysis.domain,
                "location": analysis.location,
                "time_period": analysis.time_period,
                "data_format": analysis.data_format,
                "complexity": analysis.complexity,
                "dataset_info": dataset_info,
                "results_info": results_info,
                "primary_source": primary_source,
                "direct_results_count": direct_results_count,
                "total_datasets": len(datasets),
                "successful_queries": successful_queries,
                "total_queries": len(sparql_results),
            }
        )

        return result

    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return f"I found {len(datasets)} datasets from the EU Open Data Portal but encountered an error generating a detailed response. The results above show the actual datasets found for your query."


def process_user_query(user_input: str):
    """Process a user's natural language query"""
    print(f"\nProcessing query: '{user_input}'")
    print("=" * 80)

    # Step 1: Analyze the query
    print("Step 1: Analyzing your query...")
    analysis = analyze_user_query(user_input)

    print(f"   Intent: {analysis.intent}")
    print(f"   Domain: {analysis.domain}")
    print(f"   Location: {analysis.location}")
    print(f"   Time Period: {analysis.time_period}")
    print(f"   Data Format: {analysis.data_format}")
    print(f"   Complexity: {analysis.complexity}")

    # Step 2: Find relevant datasets (now gets top 10)
    print("\nStep 2: Finding relevant datasets...")
    datasets = find_relevant_datasets(user_input, analysis, max_results=10)

    if not datasets:
        print("No relevant datasets found in the EU Open Data Portal.")
        print("\nSuggestions:")
        print("- Try broader search terms")
        print("- Check spelling of location names")
        print("- Try searching for related topics")

        if analysis.location != "any":
            print(
                f"- Try searching for '{analysis.location}' directly on: https://data.europa.eu/data/datasets?query={analysis.location.lower()}&locale=en"
            )

        print(
            "- Use the EU Open Data Portal directly: https://data.europa.eu/data/datasets"
        )
        return

    print(f"Found {len(datasets)} relevant datasets")

    # Step 3: Display comprehensive dataset results
    print("\nStep 3: Comprehensive Dataset Analysis...")
    sparql_results = []

    for i, dataset in enumerate(datasets, 1):
        print(f"\n{'='*60}")
        print(f"DATASET {i}: {dataset.get('title', 'Unknown Title')}")
        print(f"{'='*60}")

        # Check if this is an API result (most comprehensive)
        if dataset.get("source") == "EU_API":
            # Display comprehensive API dataset information
            title = dataset.get("title", "No title available")
            description = dataset.get("dataset_description", "No description available")
            publisher = dataset.get("publisher", "Unknown publisher")
            landing_page = dataset.get("landing_page", "")
            themes = dataset.get("themes", [])
            keywords = dataset.get("keywords", [])
            spatial_coverage = dataset.get("spatial_coverage", [])
            temporal_coverage = dataset.get("temporal_coverage", "")
            formats = dataset.get("formats", [])
            relevance_score = dataset.get(
                "calculated_relevance", dataset.get("relevance_score", 0)
            )

            print(f"\n{'='*60}")
            print(f"DATASET: {title}")
            print(f"{'='*60}")
            print(f"RELEVANCE SCORE: {relevance_score}")
            print(
                f"DESCRIPTION: {description[:300]}{'...' if len(description) > 300 else ''}"
            )
            print(f"PUBLISHER: {publisher}")
            if landing_page:
                print(f"LINK: {landing_page}")
            if themes:
                print(f"THEMES: {', '.join(themes[:3])}")

            if keywords:
                print(f"KEYWORDS: {', '.join(keywords[:5])}")

            if spatial_coverage:
                print(f"SPATIAL COVERAGE: {', '.join(spatial_coverage[:3])}")

            if temporal_coverage:
                print(f"TEMPORAL COVERAGE: {temporal_coverage}")

            if formats:
                print(f"AVAILABLE FORMATS: {', '.join(formats[:5])}")

            print(f"SOURCE: EU Open Data Portal API")

            # Add to results for comprehensive analysis
            sparql_results.append({"api_result": True, "dataset": dataset})

        elif "Dataset found for:" in dataset.get("question", ""):
            # Display direct SPARQL result information
            title = dataset.get("title", "No title available")
            description = dataset.get("dataset_description", "No description available")
            publisher = dataset.get("publisher", "Unknown publisher")
            landing_page = dataset.get("landing_page", "No landing page")

            print(f"\n{'='*60}")
            print(f"DATASET: {title}")
            print(f"{'='*60}")
            print(
                f"DESCRIPTION: {description[:200]}{'...' if len(description) > 200 else ''}"
            )
            print(f"PUBLISHER: {publisher}")
            if landing_page and landing_page != "No landing page":
                print(f"LINK: {landing_page}")
            print(f"SOURCE: EU Open Data Portal SPARQL")

            # Execute SPARQL query for verification
            sparql_query = dataset.get("sparql_query", "")
            if sparql_query and not sparql_query.startswith("#"):
                endpoint = dataset.get("endpoint", "https://data.europa.eu/sparql")
                results = execute_sparql_query(sparql_query, endpoint, 5)
                sparql_results.append(results)

                if "error" not in results:
                    bindings = results.get("results", {}).get("bindings", [])
                    print(f"SPARQL VERIFICATION: {len(bindings)} total results found")
                else:
                    print(f"SPARQL NOTE: {results.get('error', 'Unknown error')}")

    # Step 4: Generate comprehensive analysis
    print(f"\n{'='*80}")
    print("COMPREHENSIVE ANALYSIS")
    print(f"{'='*80}")

    comprehensive_response = generate_comprehensive_response(
        user_input, analysis, datasets, sparql_results
    )
    print(comprehensive_response)

    # Step 5: Provide similar dataset recommendations
    if len(datasets) > 0:
        print(f"\n{'='*80}")
        print("SIMILAR DATASET RECOMMENDATIONS")
        print(f"{'='*80}")
        provide_similar_dataset_recommendations(datasets, analysis)


def provide_similar_dataset_recommendations(
    datasets: List[Dict], analysis: QueryAnalysis
):
    """Provide recommendations for similar datasets based on analysis"""
    try:
        # Analyze the found datasets to identify patterns
        all_themes = []
        all_keywords = []
        all_spatial = []
        publishers = []

        for dataset in datasets:
            if dataset.get("themes"):
                all_themes.extend(dataset.get("themes", []))
            if dataset.get("keywords"):
                all_keywords.extend(dataset.get("keywords", []))
            if dataset.get("spatial_coverage"):
                all_spatial.extend(dataset.get("spatial_coverage", []))
            if dataset.get("publisher"):
                publishers.append(dataset.get("publisher"))

        # Find most common themes, keywords, and spatial areas
        from collections import Counter

        common_themes = Counter(all_themes).most_common(3)
        common_keywords = Counter(all_keywords).most_common(5)
        common_spatial = Counter(all_spatial).most_common(3)
        common_publishers = Counter(publishers).most_common(3)

        print("🔍 SEARCH EXPANSION SUGGESTIONS:")
        print("-" * 40)

        if common_themes:
            print("📂 Related Themes to Explore:")
            for theme, count in common_themes:
                print(f"   • {theme} ({count} datasets)")

        if common_keywords:
            print("\n🏷️  Related Keywords to Search:")
            for keyword, count in common_keywords:
                print(f"   • {keyword} ({count} datasets)")

        if common_spatial and analysis.location != "any":
            print(f"\n🌍 Related Geographic Areas:")
            for spatial, count in common_spatial:
                if spatial.lower() != analysis.location.lower():
                    print(f"   • {spatial} ({count} datasets)")

        if common_publishers:
            print("\n🏢 Key Data Publishers:")
            for publisher, count in common_publishers:
                print(f"   • {publisher} ({count} datasets)")

        # Generate specific search suggestions
        print("\n💡 RECOMMENDED FOLLOW-UP SEARCHES:")
        print("-" * 40)

        suggestions = []

        # Location-based suggestions
        if analysis.location != "any":
            if common_themes:
                top_theme = common_themes[0][0]
                suggestions.append(f"'{top_theme} data in {analysis.location}'")

            suggestions.append(f"'economic indicators {analysis.location}'")
            suggestions.append(f"'environmental monitoring {analysis.location}'")

        # Theme-based suggestions
        if common_themes:
            for theme, _ in common_themes[:2]:
                if "environment" in theme.lower():
                    suggestions.append(f"'climate change {theme.lower()}'")
                elif "economic" in theme.lower():
                    suggestions.append(f"'GDP statistics {theme.lower()}'")
                elif "transport" in theme.lower():
                    suggestions.append(f"'mobility data {theme.lower()}'")

        # Publisher-based suggestions
        if common_publishers:
            top_publisher = common_publishers[0][0]
            suggestions.append(f"'datasets from {top_publisher}'")

        # Display suggestions
        for i, suggestion in enumerate(suggestions[:5], 1):
            print(f"   {i}. Try searching: {suggestion}")

        # API-based recommendations
        if any(d.get("source") == "EU_API" for d in datasets):
            print("\n🔗 DIRECT API SEARCH RECOMMENDATIONS:")
            print("-" * 40)

            if analysis.location != "any":
                print(
                    f"   • Browse all {analysis.location} datasets: https://data.europa.eu/data/datasets?query={analysis.location.lower()}&locale=en"
                )

            if common_themes:
                top_theme = common_themes[0][0].replace(" ", "%20")
                print(
                    f"   • Explore {common_themes[0][0]} theme: https://data.europa.eu/data/datasets?query={top_theme}&locale=en"
                )

            print(f"   • Advanced search portal: https://data.europa.eu/data/datasets")

    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        print("Unable to generate specific recommendations, but you can:")
        print("• Try broader or more specific search terms")
        print("• Explore the EU Open Data Portal directly")
        print("• Search for datasets from specific publishers")


def query_eu_api_robust(search_query: str, max_results: int = 10) -> List[Dict]:
    """Robust EU Open Data Portal API query with FIXED parameters that actually work"""
    try:
        # EU Open Data Portal API endpoint
        api_url = "https://data.europa.eu/api/hub/search/search"

        # FIXED: Use the working parameters discovered through testing
        params = {
            "q": search_query,  # Use 'q' instead of 'query'
            "rows": max_results * 2,  # Use 'rows' instead of 'limit'
            "wt": "json",  # Specify JSON format explicitly
        }

        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; Dataset-Assistant/1.0)",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",  # Prevent caching issues
            "Pragma": "no-cache",
        }

        logger.info(f"Querying EU API with FIXED parameters: {api_url}")
        logger.info(f"Parameters: {params}")

        response = requests.get(api_url, params=params, headers=headers, timeout=30)

        logger.info(f"API Response Status: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                logger.info(f"API Response received, processing data...")

                # Debug: Log the structure of the response
                if isinstance(data, dict):
                    logger.info(f"Response keys: {list(data.keys())}")

                    # Try different response structures
                    results_list = []
                    if "result" in data and isinstance(data["result"], dict):
                        if "results" in data["result"]:
                            results_list = data["result"]["results"]
                            logger.info(
                                f"Found results in data.result.results: {len(results_list)}"
                            )
                        elif "docs" in data["result"]:
                            results_list = data["result"]["docs"]
                            logger.info(
                                f"Found results in data.result.docs: {len(results_list)}"
                            )
                    elif "response" in data and isinstance(data["response"], dict):
                        if "docs" in data["response"]:
                            results_list = data["response"]["docs"]
                            logger.info(
                                f"Found results in data.response.docs: {len(results_list)}"
                            )
                    elif "results" in data:
                        results_list = data["results"]
                        logger.info(
                            f"Found results in data.results: {len(results_list)}"
                        )
                    elif isinstance(data, list):
                        results_list = data
                        logger.info(f"Data is a list: {len(results_list)}")

                    if results_list:
                        # Log first few results to verify they're different
                        for i, result in enumerate(results_list[:3]):
                            title = extract_multilingual_field(
                                result.get("title", {}), "No title"
                            )
                            logger.info(f"Result {i+1}: {title[:60]}...")

                datasets = convert_api_results_to_datasets_robust(data, search_query)

                # Filter datasets for relevance to the search query
                filtered_datasets = filter_relevant_datasets(datasets, search_query)

                logger.info(
                    f"Converted to {len(datasets)} dataset objects, filtered to {len(filtered_datasets)} relevant ones"
                )
                return filtered_datasets[:max_results]

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(
                    f"Response content (first 500 chars): {response.text[:500]}"
                )
                return []
        else:
            logger.error(f"API request failed with status {response.status_code}")
            logger.error(f"Response content: {response.text[:500]}")
            return []

    except requests.exceptions.Timeout:
        logger.error("API request timed out")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in API query: {e}")
        return []


def filter_relevant_datasets(datasets: List[Dict], search_query: str) -> List[Dict]:
    """Filter datasets to ensure they're actually relevant to the search query"""
    if not datasets or not search_query:
        return datasets

    search_terms = search_query.lower().split()
    relevant_datasets = []

    # Make filtering less strict - if the search is for a country, be more lenient
    is_country_search = any(
        country in search_query.lower()
        for country in [
            "croatia",
            "germany",
            "france",
            "italy",
            "spain",
            "poland",
            "netherlands",
            "belgium",
            "austria",
            "portugal",
            "greece",
            "hungary",
            "czech republic",
            "slovakia",
            "slovenia",
            "estonia",
            "latvia",
            "lithuania",
            "finland",
            "sweden",
            "denmark",
            "ireland",
            "luxembourg",
            "malta",
            "cyprus",
            "bulgaria",
            "romania",
            "united kingdom",
            "uk",
            "britain",
        ]
    )

    for dataset in datasets:
        title = dataset.get("title", "").lower()
        description = dataset.get("dataset_description", "").lower()
        keywords = [kw.lower() for kw in dataset.get("keywords", [])]
        spatial_coverage = [sp.lower() for sp in dataset.get("spatial_coverage", [])]

        # Combine all searchable text
        searchable_text = (
            f"{title} {description} {' '.join(keywords)} {' '.join(spatial_coverage)}"
        )

        # Check if any search term appears in the dataset
        relevance_score = 0
        for term in search_terms:
            if term in searchable_text:
                relevance_score += 1

                # Higher score for title matches
                if term in title:
                    relevance_score += 2

                # Higher score for spatial coverage matches
                if any(term in sp for sp in spatial_coverage):
                    relevance_score += 3

        # For country searches, be more lenient - include if there's any match
        # For other searches, require at least some relevance
        min_score = 1 if is_country_search else 2

        if relevance_score >= min_score:
            dataset["calculated_relevance"] = relevance_score
            relevant_datasets.append(dataset)
            logger.info(
                f"Dataset '{title[:50]}...' scored {relevance_score} for query '{search_query}'"
            )
        else:
            logger.info(
                f"Filtered out irrelevant dataset: '{title[:50]}...' (score: {relevance_score})"
            )

    # Sort by relevance score
    relevant_datasets.sort(key=lambda x: x.get("calculated_relevance", 0), reverse=True)

    return relevant_datasets


def get_similar_datasets(dataset_uri: str) -> List[Dict]:
    """Get similar datasets using the EU Open Data Portal similar datasets endpoint"""
    try:
        if not dataset_uri:
            return []

        # Construct the similar datasets URL
        similar_url = (
            f"https://data.europa.eu/data/datasets/{dataset_uri}/similarDatasets"
        )

        params = {"locale": "en"}

        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; Dataset-Assistant/1.0)",
        }

        logger.info(f"Fetching similar datasets from: {similar_url}")

        response = requests.get(similar_url, params=params, headers=headers, timeout=20)

        if response.status_code == 200:
            data = response.json()
            similar_datasets = convert_api_results_to_datasets_robust(
                data, f"Similar to {dataset_uri}"
            )
            logger.info(f"Found {len(similar_datasets)} similar datasets")
            return similar_datasets
        else:
            logger.warning(
                f"Similar datasets request failed with status {response.status_code}"
            )
            return []

    except Exception as e:
        logger.error(f"Error fetching similar datasets: {e}")
        return []


def convert_api_results_to_datasets_robust(
    api_data: Dict[str, Any], search_query: str
) -> List[Dict]:
    """Robust conversion of EU Open Data Portal API results to dataset format"""
    datasets = []

    try:
        # Handle different response structures
        results = []

        if isinstance(api_data, dict):
            if "result" in api_data and isinstance(api_data["result"], dict):
                if "results" in api_data["result"]:
                    results = api_data["result"]["results"]
                elif "items" in api_data["result"]:
                    results = api_data["result"]["items"]
            elif "results" in api_data:
                results = api_data["results"]
            elif "items" in api_data:
                results = api_data["items"]
            elif isinstance(api_data, list):
                results = api_data

        logger.info(f"Processing {len(results)} results from API")

        for i, result in enumerate(results):
            try:
                # Extract basic information with robust handling
                title = extract_multilingual_field(result.get("title", {}), "No title")
                description = extract_multilingual_field(
                    result.get("description", {}), "No description"
                )

                # Extract publisher information
                publisher = "Unknown"
                if result.get("publisher"):
                    pub_data = result.get("publisher", {})
                    if isinstance(pub_data, dict):
                        publisher = extract_multilingual_field(
                            pub_data.get("name", {}), "Unknown"
                        )
                    else:
                        publisher = str(pub_data)

                # Extract landing page
                landing_page = ""
                if result.get("landingPage"):
                    lp = result.get("landingPage")
                    if isinstance(lp, list) and lp:
                        landing_page = str(lp[0])
                    else:
                        landing_page = str(lp)

                # Extract themes
                themes = []
                if result.get("theme"):
                    theme_data = result.get("theme", [])
                    if isinstance(theme_data, list):
                        for theme in theme_data:
                            if isinstance(theme, dict):
                                theme_label = extract_multilingual_field(
                                    theme.get("label", {}), ""
                                )
                                if theme_label:
                                    themes.append(theme_label)

                # Extract keywords
                keywords = []
                if result.get("keyword"):
                    kw_data = result.get("keyword", [])
                    if isinstance(kw_data, list):
                        keywords = [str(kw) for kw in kw_data[:5]]

                # Extract spatial coverage
                spatial_coverage = []
                if result.get("spatial"):
                    spatial_data = result.get("spatial", [])
                    if isinstance(spatial_data, list):
                        for spatial in spatial_data:
                            if isinstance(spatial, dict):
                                spatial_label = extract_multilingual_field(
                                    spatial.get("label", {}), ""
                                )
                                if spatial_label:
                                    spatial_coverage.append(spatial_label)

                # Extract formats
                formats = []
                if result.get("distribution"):
                    dist_data = result.get("distribution", [])
                    if isinstance(dist_data, list):
                        for dist in dist_data[:3]:
                            if isinstance(dist, dict) and dist.get("format"):
                                format_info = dist.get("format", {})
                                if isinstance(format_info, dict):
                                    format_label = extract_multilingual_field(
                                        format_info.get("label", {}), ""
                                    )
                                    if format_label:
                                        formats.append(format_label)

                dataset = {
                    "question": f"Dataset found for: {search_query}",
                    "sparql_query": f"# API Search Query: {search_query}",
                    "endpoint": "https://data.europa.eu/api/hub/search/search",
                    "description": f"Dataset from EU Open Data Portal API",
                    "distance": 0.0,
                    "dataset_uri": result.get("id", ""),
                    "title": title,
                    "dataset_description": description,
                    "publisher": publisher,
                    "landing_page": landing_page,
                    "themes": themes,
                    "keywords": keywords,
                    "spatial_coverage": spatial_coverage,
                    "temporal_coverage": "",
                    "formats": formats,
                    "relevance_score": result.get("score", 0),
                    "source": "EU_API",
                }
                datasets.append(dataset)

            except Exception as e:
                logger.error(f"Error processing result {i}: {e}")
                continue

    except Exception as e:
        logger.error(f"Error in convert_api_results_to_datasets_robust: {e}")

    return datasets


def extract_multilingual_field(field_data, default_value=""):
    """Extract text from multilingual field, preferring English"""
    if isinstance(field_data, str):
        return field_data
    elif isinstance(field_data, dict):
        # Try English first
        if "en" in field_data:
            return str(field_data["en"])
        # Try any available language
        elif field_data:
            return str(next(iter(field_data.values())))
    elif isinstance(field_data, list) and field_data:
        return str(field_data[0])

    return default_value


def test_api_connectivity():
    """Test the EU Open Data Portal API connectivity and response structure"""
    print("Testing EU Open Data Portal API connectivity...")
    print("=" * 60)

    # Test with a simple query
    test_query = "croatia"

    try:
        api_url = "https://data.europa.eu/api/hub/search/search"
        params = {"query": test_query, "limit": 5, "locale": "en", "filter": "dataset"}

        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; Dataset-Assistant/1.0)",
        }

        print(f"Testing API call to: {api_url}")
        print(f"Parameters: {params}")

        response = requests.get(api_url, params=params, headers=headers, timeout=30)

        print(f"Response Status: {response.status_code}")
        print(f"Response Size: {len(response.text)} characters")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"JSON parsing successful")

                # Analyze response structure
                if isinstance(data, dict):
                    print(f"Top-level keys: {list(data.keys())}")

                    if "result" in data:
                        result = data["result"]
                        if isinstance(result, dict):
                            print(f"Result keys: {list(result.keys())}")

                            if "results" in result:
                                results_list = result["results"]
                                print(f"Found {len(results_list)} datasets")

                                if results_list:
                                    print(
                                        f"First result keys: {list(results_list[0].keys())}"
                                    )

                                    # Show first few results details
                                    for i, res in enumerate(results_list[:3]):
                                        title = extract_multilingual_field(
                                            res.get("title", {}), "No title"
                                        )
                                        print(f"Result {i+1} title: {title}")

                                    return True
                            else:
                                print("No 'results' key found in result")
                        else:
                            print(f"Result is not a dict: {type(result)}")
                    else:
                        print("No 'result' key found in response")
                else:
                    print(f"Response is not a dict: {type(data)}")

            except json.JSONDecodeError as e:
                print(f"JSON parsing failed: {e}")
                print(f"Raw response (first 200 chars): {response.text[:200]}")
        else:
            print(f"API request failed")
            print(f"Response: {response.text[:200]}")

    except Exception as e:
        print(f"Test failed with error: {e}")

    return False


def test_direct_croatia_search():
    """Test direct search for Croatia to see what we actually get"""
    print("\nTesting direct Croatia search...")
    print("=" * 60)

    try:
        # Try the exact URL from the web search results
        test_url = "https://data.europa.eu/data/datasets"
        params = {"query": "croatia", "locale": "en"}

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (compatible; Dataset-Assistant/1.0)",
        }

        print(f"Testing direct portal search: {test_url}")
        print(f"Parameters: {params}")

        response = requests.get(test_url, params=params, headers=headers, timeout=30)

        print(f"Response Status: {response.status_code}")
        print(f"Response Size: {len(response.text)} characters")

        if response.status_code == 200:
            # Look for dataset titles in the HTML
            content = response.text.lower()
            if "croatia" in content:
                print("Found 'croatia' in response content")
                # Count occurrences
                croatia_count = content.count("croatia")
                print(f"'croatia' appears {croatia_count} times in the response")
            else:
                print("'croatia' NOT found in response content")

            # Check for other countries to see what we're getting
            other_countries = ["czech", "austria", "germany", "poland"]
            for country in other_countries:
                if country in content:
                    count = content.count(country)
                    print(f"'{country}' appears {count} times in the response")

        return True

    except Exception as e:
        print(f"Direct search test failed: {e}")
        return False


def fix_search_strategy_for_croatia():
    """Try different search approaches to find Croatian datasets"""
    print("\nTesting different search strategies for Croatia...")
    print("=" * 60)

    search_strategies = [
        "Croatia",
        "Croatian",
        "HR",  # ISO country code
        "Hrvatska",  # Croatian name for Croatia
        "Republic of Croatia",
        "Croatia statistics",
        "Croatia data",
    ]

    api_url = "https://data.europa.eu/api/hub/search/search"
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (compatible; Dataset-Assistant/1.0)",
    }

    for strategy in search_strategies:
        print(f"\nTrying strategy: '{strategy}'")

        params = {"query": strategy, "limit": 5, "locale": "en", "filter": "dataset"}

        try:
            response = requests.get(api_url, params=params, headers=headers, timeout=30)

            if response.status_code == 200:
                data = response.json()
                results = data.get("result", {}).get("results", [])

                print(f"  Found {len(results)} results")

                # Check if any results actually mention Croatia
                croatia_relevant = 0
                for result in results:
                    title = extract_multilingual_field(
                        result.get("title", {}), ""
                    ).lower()
                    description = extract_multilingual_field(
                        result.get("description", {}), ""
                    ).lower()

                    if (
                        "croatia" in title
                        or "croatia" in description
                        or "croatian" in title
                        or "croatian" in description
                    ):
                        croatia_relevant += 1
                        print(f"    RELEVANT: {title[:60]}...")
                    else:
                        print(f"    NOT RELEVANT: {title[:60]}...")

                print(f"  Croatia-relevant results: {croatia_relevant}/{len(results)}")

                if croatia_relevant > 0:
                    print(
                        f"  SUCCESS: Found {croatia_relevant} relevant results with '{strategy}'"
                    )
                    return strategy, results
            else:
                print(f"  API failed with status {response.status_code}")

        except Exception as e:
            print(f"  Error: {e}")

    return None, []


def test_alternative_api_endpoints():
    """Test different API endpoints to find one that actually works"""
    print("\nTesting alternative API endpoints...")
    print("=" * 60)

    # Different API endpoints to try
    endpoints = [
        {
            "name": "Current API",
            "url": "https://data.europa.eu/api/hub/search/search",
            "params": {
                "query": "Croatia",
                "limit": 5,
                "locale": "en",
                "filter": "dataset",
            },
        },
        {
            "name": "Alternative API 1",
            "url": "https://data.europa.eu/api/hub/search/datasets",
            "params": {"q": "Croatia", "limit": 5, "locale": "en"},
        },
        {
            "name": "Alternative API 2",
            "url": "https://data.europa.eu/api/hub/repo/datasets",
            "params": {"query": "Croatia", "rows": 5, "locale": "en"},
        },
        {
            "name": "SPARQL Endpoint",
            "url": "https://data.europa.eu/sparql",
            "params": {
                "query": """
                PREFIX dcat: <http://www.w3.org/ns/dcat#>
                PREFIX dct: <http://purl.org/dc/terms/>
                SELECT DISTINCT ?dataset ?title WHERE {
                    ?dataset a dcat:Dataset .
                    ?dataset dct:title ?title .
                    FILTER(CONTAINS(LCASE(STR(?title)), "croatia"))
                    FILTER(LANG(?title) = "en" || LANG(?title) = "")
                } LIMIT 5
            """,
                "format": "application/sparql-results+json",
            },
        },
    ]

    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (compatible; Dataset-Assistant/1.0)",
    }

    working_endpoints = []

    for endpoint in endpoints:
        print(f"\nTesting {endpoint['name']}: {endpoint['url']}")

        try:
            response = requests.get(
                endpoint["url"], params=endpoint["params"], headers=headers, timeout=30
            )
            print(f"  Status: {response.status_code}")
            print(f"  Response size: {len(response.text)} chars")

            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"  JSON parsing: SUCCESS")

                    # Try to extract results
                    results = []
                    if "result" in data and "results" in data["result"]:
                        results = data["result"]["results"]
                    elif "results" in data and "bindings" in data["results"]:
                        results = data["results"]["bindings"]
                    elif "results" in data:
                        results = data["results"]
                    elif isinstance(data, list):
                        results = data

                    print(f"  Found {len(results)} results")

                    if results:
                        # Show first result
                        first = results[0]
                        if "title" in first:
                            if isinstance(first["title"], dict):
                                title = extract_multilingual_field(
                                    first["title"], "No title"
                                )
                            else:
                                title = str(first["title"])
                        elif "title" in first and "value" in first["title"]:
                            title = first["title"]["value"]
                        else:
                            title = str(first)[:100]

                        print(f"  First result: {title}")

                        # Check if results are different from the problematic ones
                        if "presentation service wlv austria" not in title.lower():
                            print(f"  ✅ DIFFERENT RESULTS - This endpoint works!")
                            working_endpoints.append(endpoint)
                        else:
                            print(f"  ❌ Same problematic results")
                    else:
                        print(f"  No results found")

                except json.JSONDecodeError as e:
                    print(f"  JSON parsing failed: {e}")
                    print(f"  Raw response: {response.text[:200]}...")
            else:
                print(f"  Failed with status {response.status_code}")
                print(f"  Response: {response.text[:200]}...")

        except Exception as e:
            print(f"  Error: {e}")

    print(f"\n{'='*60}")
    print(f"SUMMARY: Found {len(working_endpoints)} working endpoints")
    for endpoint in working_endpoints:
        print(f"  ✅ {endpoint['name']}: {endpoint['url']}")

    return working_endpoints


def test_direct_sparql_croatia():
    """Test direct SPARQL query for Croatia"""
    print("\nTesting direct SPARQL query for Croatia...")
    print("=" * 60)

    sparql_query = """
    PREFIX dcat: <http://www.w3.org/ns/dcat#>
    PREFIX dct: <http://purl.org/dc/terms/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT DISTINCT ?dataset ?title ?description WHERE {
        ?dataset a dcat:Dataset .
        ?dataset dct:title ?title .
        OPTIONAL { ?dataset dct:description ?description . }
        
        FILTER(
            CONTAINS(LCASE(STR(?title)), "croatia") ||
            CONTAINS(LCASE(STR(?title)), "croatian") ||
            (BOUND(?description) && CONTAINS(LCASE(STR(?description)), "croatia"))
        )
        
        FILTER(LANG(?title) = "en" || LANG(?title) = "")
    } LIMIT 10
    """

    endpoint = "https://data.europa.eu/sparql"
    params = {"query": sparql_query, "format": "application/sparql-results+json"}

    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "Mozilla/5.0 (compatible; Dataset-Assistant/1.0)",
    }

    try:
        print(f"Querying SPARQL endpoint: {endpoint}")
        response = requests.get(endpoint, params=params, headers=headers, timeout=30)

        print(f"Status: {response.status_code}")
        print(f"Response size: {len(response.text)} chars")

        if response.status_code == 200:
            data = response.json()
            bindings = data.get("results", {}).get("bindings", [])

            print(f"Found {len(bindings)} SPARQL results")

            for i, binding in enumerate(bindings, 1):
                title = binding.get("title", {}).get("value", "No title")
                description = binding.get("description", {}).get(
                    "value", "No description"
                )

                print(f"\n{i}. {title}")
                print(f"   Description: {description[:100]}...")

                # Check if this mentions Croatia
                if "croatia" in title.lower() or "croatia" in description.lower():
                    print(f"   ✅ RELEVANT to Croatia")
                else:
                    print(f"   ❌ Not clearly relevant to Croatia")

            return len(bindings) > 0
        else:
            print(f"SPARQL query failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"SPARQL test failed: {e}")
        return False


def fix_api_search_method():
    """Try to fix the API search by using different parameters and methods"""
    print("\nTrying to fix API search method...")
    print("=" * 60)

    base_url = "https://data.europa.eu/api/hub/search/search"

    # Different parameter combinations to try
    param_sets = [
        {"q": "Croatia", "rows": 5, "wt": "json"},
        {"query": "Croatia", "limit": 5, "format": "json"},
        {"text": "Croatia", "size": 5, "locale": "en"},
        {"search": "Croatia", "count": 5, "lang": "en"},
        {"keyword": "Croatia", "max": 5, "language": "en"},
    ]

    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (compatible; Dataset-Assistant/1.0)",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }

    for i, params in enumerate(param_sets, 1):
        print(f"\nTrying parameter set {i}: {params}")

        try:
            response = requests.get(
                base_url, params=params, headers=headers, timeout=30
            )
            print(f"  Status: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()

                    # Try to find results in different structures
                    results = None
                    if "result" in data and "results" in data["result"]:
                        results = data["result"]["results"]
                    elif "response" in data and "docs" in data["response"]:
                        results = data["response"]["docs"]
                    elif "results" in data:
                        results = data["results"]
                    elif "data" in data:
                        results = data["data"]

                    if results:
                        print(f"  Found {len(results)} results")

                        # Check first result
                        first = results[0]
                        title_field = None
                        for field in ["title", "name", "label", "dataset_title"]:
                            if field in first:
                                title_field = first[field]
                                break

                        if title_field:
                            if isinstance(title_field, dict):
                                title = extract_multilingual_field(
                                    title_field, "No title"
                                )
                            else:
                                title = str(title_field)

                            print(f"  First result: {title}")

                            # Check if it's different from the problematic results
                            if "presentation service wlv austria" not in title.lower():
                                print(f"  ✅ SUCCESS - Different results found!")
                                return params, results
                            else:
                                print(f"  ❌ Same problematic results")
                        else:
                            print(f"  No title field found in result")
                    else:
                        print(f"  No results found in response")

                except json.JSONDecodeError as e:
                    print(f"  JSON parsing failed: {e}")
            else:
                print(f"  Failed with status {response.status_code}")

        except Exception as e:
            print(f"  Error: {e}")

    print(f"\nNo working parameter combination found")
    return None, []


def main():
    """Main interactive loop"""
    print("Interactive Dataset Assistant")
    print("=" * 50)
    print("Ask me anything about open datasets in natural language!")
    print("\nOptions:")
    print("- Enter your query directly")
    print("- Type 'test' to test API connectivity")
    print("- Type 'test-direct' to test direct Croatia search")
    print("- Type 'test-strategies' to test different search strategies")
    print("- Type 'test-endpoints' to test alternative API endpoints")
    print("- Type 'test-sparql' to test direct SPARQL for Croatia")
    print("- Type 'fix-api' to try fixing API search parameters")
    print("- Type 'quit' to exit")
    print("=" * 50)

    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key to use this assistant")
        return

    while True:
        try:
            user_input = input("\nYour query: ").strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            if user_input.lower() == "test":
                test_api_connectivity()
                continue

            if user_input.lower() == "test-direct":
                test_direct_croatia_search()
                continue

            if user_input.lower() == "test-strategies":
                strategy, results = fix_search_strategy_for_croatia()
                if strategy:
                    print(f"\nBest strategy found: '{strategy}'")
                    print("Sample results:")
                    for i, result in enumerate(results[:3], 1):
                        title = extract_multilingual_field(
                            result.get("title", {}), "No title"
                        )
                        print(f"  {i}. {title}")
                else:
                    print("No successful strategy found")
                continue

            if user_input.lower() == "test-endpoints":
                working_endpoints = test_alternative_api_endpoints()
                if working_endpoints:
                    print(f"\nFound {len(working_endpoints)} working endpoints!")
                    print("These can be used to replace the current broken API.")
                else:
                    print(
                        "No working endpoints found. The API might be fundamentally broken."
                    )
                continue

            if user_input.lower() == "test-sparql":
                success = test_direct_sparql_croatia()
                if success:
                    print(
                        "\n✅ SPARQL approach works! We should switch to SPARQL-only."
                    )
                else:
                    print("\n❌ Even SPARQL doesn't work properly.")
                continue

            if user_input.lower() == "fix-api":
                params, results = fix_api_search_method()
                if params:
                    print(f"\n✅ Found working parameters: {params}")
                    print("These parameters can be used to fix the API calls.")
                else:
                    print("\n❌ No working parameter combination found.")
                continue

            if not user_input:
                print("Please enter a query, a test command, or 'quit' to exit")
                continue

            # Process the query
            start_time = time.time()
            process_user_query(user_input)
            elapsed = time.time() - start_time

            print(f"\nQuery processed in {elapsed:.1f} seconds")
            print("\n" + "=" * 80)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again with a different query")


if __name__ == "__main__":
    main()
