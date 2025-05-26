import json
import logging
import os
import requests
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

# Langchain imports
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage

# Import our RAG system
try:
    from .rag_system import RAGSystem, QueryExample
except ImportError:
    from rag_system import RAGSystem, QueryExample
from dotenv import load_dotenv

load_dotenv()

# Setup logging
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = os.path.join(log_directory, f"unified_assistant_{timestamp}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_filename), logging.StreamHandler()],
    force=True,
)


class UnifiedDataAssistant:
    """
    Unified Data Assistant that combines RAG-enhanced SPARQL generation,
    EU Open Data Portal API calls, and similar dataset discovery
    """

    def __init__(self, llm_model: str = "gpt-4o"):
        self.llm = ChatOpenAI(model=llm_model, temperature=0.1, request_timeout=60)
        self.rag_system = RAGSystem()

        # EU Open Data Portal endpoints
        self.sparql_endpoint = "https://data.europa.eu/sparql"
        self.api_endpoint = "https://data.europa.eu/api/hub/search/search"
        self.similar_datasets_api = (
            "https://data.europa.eu/data/datasets/{dataset_id}/similarDatasets"
        )

        self.logger = logging.getLogger(__name__)
        self.logger.info("Unified Data Assistant initialized")

        # Initialize RAG system with examples
        self.rag_system.populate_with_examples()

    def execute_sparql_query(self, sparql_query: str) -> Dict[str, Any]:
        """Execute SPARQL query against EU Open Data Portal"""
        try:
            headers = {"Accept": "application/sparql-results+json"}
            params = {"query": sparql_query}

            response = requests.get(
                self.sparql_endpoint, headers=headers, params=params, timeout=30
            )
            response.raise_for_status()

            results = response.json()
            result_count = len(results.get("results", {}).get("bindings", []))

            self.logger.info(
                f"SPARQL query executed successfully: {result_count} results"
            )
            return {
                "success": True,
                "results": results,
                "count": result_count,
                "source": "sparql",
            }

        except Exception as e:
            self.logger.error(f"SPARQL execution failed: {e}")
            return {"success": False, "error": str(e), "source": "sparql"}

    def execute_api_search(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute search using EU Open Data Portal API"""
        try:
            headers = {"Content-Type": "application/json", "Accept": "application/json"}

            response = requests.post(
                self.api_endpoint, headers=headers, json=search_params, timeout=30
            )
            response.raise_for_status()

            results = response.json()

            if not results.get("success", True):
                return {
                    "success": False,
                    "error": results.get("message", "API indicated failure"),
                    "source": "api",
                }

            result_count = len(results.get("result", {}).get("results", []))

            self.logger.info(
                f"API search executed successfully: {result_count} results"
            )
            return {
                "success": True,
                "results": results,
                "count": result_count,
                "source": "api",
            }

        except Exception as e:
            self.logger.error(f"API search failed: {e}")
            return {"success": False, "error": str(e), "source": "api"}

    def get_similar_datasets(self, dataset_id: str) -> Dict[str, Any]:
        """Get similar datasets for a given dataset ID"""
        try:
            url = self.similar_datasets_api.format(dataset_id=dataset_id)
            params = {"locale": "en"}

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            results = response.json()

            self.logger.info(f"Retrieved similar datasets for {dataset_id}")
            return {
                "success": True,
                "results": results,
                "count": len(results.get("similarDatasets", [])),
                "source": "similar_api",
            }

        except Exception as e:
            self.logger.error(f"Similar datasets API failed: {e}")
            return {"success": False, "error": str(e), "source": "similar_api"}


# Langchain Tools for the Agent


@tool
def generate_rag_sparql_tool(natural_language_query: str, context: str = "") -> str:
    """
    Generate SPARQL query using RAG (Retrieval-Augmented Generation).
    Uses similar examples and schema information to create better queries.
    """
    assistant = UnifiedDataAssistant()

    try:
        # Use RAG system to generate enhanced SPARQL
        sparql_query = assistant.rag_system.generate_sparql_with_rag(
            natural_language_query, context
        )

        # Validate the generated query
        is_valid, validation_message = assistant.rag_system.validate_sparql_query(
            sparql_query
        )

        if not is_valid:
            return f"Generated query failed validation: {validation_message}\n\nQuery:\n{sparql_query}"

        return sparql_query

    except Exception as e:
        return f"Error: Failed to generate RAG-enhanced SPARQL query. {e}"


@tool
def execute_sparql_tool(sparql_query: str) -> Dict[str, Any]:
    """Execute SPARQL query against EU Open Data Portal endpoint"""
    assistant = UnifiedDataAssistant()
    return assistant.execute_sparql_query(sparql_query)


@tool
def generate_api_params_tool(natural_language_query: str, context: str = "") -> str:
    """Generate JSON parameters for EU Open Data Portal API search"""

    # Use LLM to generate API parameters
    llm = ChatOpenAI(model="gpt-4o", temperature=0.1)

    prompt = f"""
    Generate JSON request body for EU Open Data Portal API search.
    Natural language query: "{natural_language_query}"
    {f"Context: {context}" if context else ""}
    
    Map the query to these API parameters:
    - q: main search terms
    - filters: ["dataset"] for datasets only
    - facets: object with keys like "keywords", "categories", "publisher_name", "country"
    - limit: 10-20 for exploration
    - page: 0
    - sort: ["modified+desc"] for recent first
    - minDate/maxDate: for date ranges (ISO format)
    
    Return only valid JSON without explanations.
    """

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        json_str = response.content.strip()

        # Clean up markdown formatting
        json_str = re.sub(r"^```json\s*", "", json_str, flags=re.IGNORECASE)
        json_str = re.sub(r"\s*```$", "", json_str)

        # Validate JSON
        json.loads(json_str)
        return json_str

    except Exception as e:
        return f"Error: Failed to generate API parameters. {e}"


@tool
def execute_api_search_tool(search_params_json: str) -> Dict[str, Any]:
    """Execute search using EU Open Data Portal API"""
    assistant = UnifiedDataAssistant()

    try:
        # Parse JSON parameters
        if isinstance(search_params_json, str):
            search_params = json.loads(search_params_json)
        else:
            search_params = search_params_json

        return assistant.execute_api_search(search_params)

    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Invalid JSON parameters: {e}",
            "source": "api",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"API execution failed: {e}",
            "source": "api",
        }


@tool
def find_similar_datasets_tool(dataset_uri: str) -> Dict[str, Any]:
    """Find datasets similar to a given dataset using the similar datasets API"""
    assistant = UnifiedDataAssistant()

    try:
        # Extract dataset ID from URI
        if "datasets/" in dataset_uri:
            dataset_id = dataset_uri.split("datasets/")[-1]
        else:
            dataset_id = dataset_uri

        return assistant.get_similar_datasets(dataset_id)

    except Exception as e:
        return {
            "success": False,
            "error": f"Similar datasets search failed: {e}",
            "source": "similar_api",
        }


@tool
def analyze_and_combine_results_tool(
    sparql_results: Dict[str, Any], api_results: Dict[str, Any], user_query: str
) -> str:
    """Analyze and combine results from SPARQL and API searches"""

    llm = ChatOpenAI(model="gpt-4o", temperature=0.1)

    # Truncate results to prevent token limit issues
    def truncate_results(results: Dict[str, Any], max_items: int = 5) -> Dict[str, Any]:
        if results.get("success") and isinstance(results.get("results"), dict):
            if (
                "results" in results["results"]
                and "bindings" in results["results"]["results"]
            ):
                # API results format
                original_results = results["results"]["results"]["bindings"]
                results["results"]["results"]["bindings"] = original_results[:max_items]
            elif "bindings" in results["results"]:
                # SPARQL results format
                original_bindings = results["results"]["bindings"]
                results["results"]["bindings"] = original_bindings[:max_items]
        return results

    # Truncate both result sets to manageable size
    truncated_sparql = truncate_results(sparql_results, max_items=3)
    truncated_api = truncate_results(api_results, max_items=3)

    prompt = f"""
    Analyze and combine the following search results for the query: "{user_query}"
    
    SPARQL Results Summary:
    - Success: {truncated_sparql.get('success', False)}
    - Count: {truncated_sparql.get('count', 0)}
    - Source: SPARQL endpoint
    - Sample Results: {str(truncated_sparql).replace(truncated_sparql.get('results', {}), '[TRUNCATED]') if truncated_sparql.get('success') else 'No results'}
    
    API Results Summary:
    - Success: {truncated_api.get('success', False)}
    - Count: {truncated_api.get('count', 0)}
    - Source: REST API
    - Sample Results: {str(truncated_api).replace(truncated_api.get('results', {}), '[TRUNCATED]') if truncated_api.get('success') else 'No results'}
    
    Provide a comprehensive analysis that:
    1. Compares the effectiveness of both approaches
    2. Identifies unique datasets found by each method
    3. Recommends the best datasets for the user's query
    4. Suggests potential data linking opportunities
    5. Provides actionable insights for the user
    
    Keep the response concise (under 200 words) and actionable.
    """

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content

    except Exception as e:
        return f"Error analyzing results: {e}"


# Agent Setup
tools = [
    generate_rag_sparql_tool,
    execute_sparql_tool,
    generate_api_params_tool,
    execute_api_search_tool,
    find_similar_datasets_tool,
    analyze_and_combine_results_tool,
]

agent_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an intelligent data discovery assistant for the EU Open Data Portal.
    
Your goal is to find the most relevant datasets using multiple complementary approaches:

1. **RAG-Enhanced SPARQL**: Use semantic similarity to retrieve similar examples and generate better SPARQL queries
2. **API Search**: Use the REST API for flexible text-based search
3. **Similar Datasets**: Find related datasets using the similarity API
4. **Multi-Modal Analysis**: Combine results from different approaches for comprehensive discovery

## Workflow:
1. Start with RAG-enhanced SPARQL generation using `generate_rag_sparql_tool`
2. Execute the SPARQL query with `execute_sparql_tool`
3. Generate API search parameters with `generate_api_params_tool`  
4. Execute API search with `execute_api_search_tool`
5. If specific datasets are found, use `find_similar_datasets_tool` to expand the search
6. Combine and analyze all results with `analyze_and_combine_results_tool`

## Error Handling:
- If SPARQL fails, focus on API search
- If API search fails, rely on SPARQL results
- Always try at least 2 different approaches
- Provide context for retry attempts

## Output:
Provide a comprehensive summary that includes:
- Total datasets found across all methods
- Key dataset recommendations with titles and descriptions
- Data linking opportunities
- Methodology comparison
- Actionable next steps for the user

Focus on dataset discovery and exploration rather than complex data analysis.""",
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)


def create_unified_agent():
    """Create the unified data discovery agent"""
    llm = ChatOpenAI(model="gpt-4o", temperature=0.1, request_timeout=60)
    agent = create_openai_tools_agent(llm, tools, agent_prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)


def ask_unified_assistant(user_query: str) -> Dict[str, Any]:
    """Main function to query the unified data assistant"""
    logging.info(f"Processing query with unified assistant: {user_query}")

    agent_executor = create_unified_agent()
    chat_history = []

    try:
        response = agent_executor.invoke(
            {"input": user_query, "chat_history": chat_history}
        )

        final_answer = response.get("output", "No response generated.")

        logging.info("Unified assistant completed successfully")
        return {
            "status": "success",
            "query": user_query,
            "answer": final_answer,
            "approach": "unified_rag_sparql_api",
        }

    except Exception as e:
        logging.error(f"Unified assistant failed: {e}")
        return {
            "status": "error",
            "query": user_query,
            "message": f"Unified assistant execution failed: {e}",
            "approach": "unified_rag_sparql_api",
        }


# Example usage and testing
if __name__ == "__main__":

    # Test queries that demonstrate different capabilities
    test_queries = [
        "Find datasets about climate change and renewable energy from European agencies",
        "Show me air quality data for major European cities since 2020",
        "List COVID-19 datasets with health and economic impact data",
        "Find energy consumption datasets that can be linked with economic indicators",
        "Search for transportation and mobility datasets in CSV format",
    ]

    print("🚀 Unified Data Assistant - Combining RAG, SPARQL, and API")
    print("=" * 60)

    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Test Query {i}: {query}")
        print("-" * 50)

        result = ask_unified_assistant(query)

        if result["status"] == "success":
            print("✅ Success!")
            print(f"Answer: {result['answer'][:500]}...")
        else:
            print("❌ Error!")
            print(f"Error: {result['message']}")

        print("\n" + "=" * 60)
