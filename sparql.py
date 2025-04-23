import openai
import json
import re
import requests
import os  # Added for environment variables
from typing import List, Dict, Any, Optional  # Added for type hinting

# Langchain imports
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage  # Added for chat history

# Load environment variables (optional, assumes OPENAI_API_KEY is set)
# from dotenv import load_dotenv
# load_dotenv()

# --- Setup ---
# Ensure OpenAI API key is available
# It will default to checking the OPENAI_API_KEY environment variable
llm = ChatOpenAI(model="gpt-4o", temperature=0.1)

# EU Open Data Portal SPARQL Endpoint
SPARQL_ENDPOINT = "https://data.europa.eu/sparql"

# --- Langchain Tools ---


@tool
def generate_sparql_tool(natural_language_query: str, context: str = "") -> str:
    """
    Generates a SPARQL query for the EU Open Data Portal based on a natural language query.
    Use this tool first to get a query.
    Provide context only if a previous generation attempt failed and you have specific instructions for correction (e.g., 'Previous query failed execution. Check prefixes.').
    """
    # Prompt for the LLM to generate a SPARQL query
    # This prompt is kept similar to the original for consistency
    sparql_prompt = f"""
    Given the natural language query: "{natural_language_query}"
    {context} # Add context if provided (e.g., for refinement)

    Generate a SPARQL query for the EU Open Data Portal ({SPARQL_ENDPOINT}) to find **datasets relevant to the themes** mentioned in the query.
    - The primary goal is to identify datasets. Focus on searching dataset metadata (title, description, keywords) for relevance.
    - Use standard prefixes like `dct:` (<http://purl.org/dc/terms/>) and `dcat:` (<http://www.w3.org/ns/dcat#>).
    - If you use XML Schema datatypes (like `xsd:date`), include `PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>`.
    - If you use Friend of a Friend terms (like `foaf:name` for publisher names), include `PREFIX foaf: <http://xmlns.com/foaf/0.1/>`.
    - Target datasets (`?dataset a dcat:Dataset`).
    - Extract relevant *dataset* information (e.g., `dct:title`, `dct:description`, `dct:publisher`, `dcat:landingPage`, dataset URI). Always include the dataset URI.
    - Filter datasets based on keywords, themes, dates, publishers, formats etc. mentioned in the query by searching `dcat:keyword`, `dct:title`, `dct:description`.
    - Use `dct:issued` for publication date filtering.
    - Use `dct:publisher` and potentially `foaf:name` for publisher filtering.
    - Use `dcat:distribution` to link to distributions only if filtering by `dct:format` or `dcat:mediaType` is explicitly requested.
    - Use FILTER with `CONTAINS` or `REGEX` for flexible text matching on title, description, or keywords. Apply `STR()` and `LCASE()` for case-insensitive matching on potentially non-string variables: `FILTER(CONTAINS(LCASE(STR(?var)), "term"))`.
    - Avoid complex joins or analysis *within* the SPARQL query itself unless the query explicitly asks for specific data points likely found together. The main aim is dataset discovery.
    - Add a LIMIT clause (e.g., LIMIT 10) to keep results manageable.

    Return *only* the raw SPARQL query string, without any explanations or formatting like ```sparql ... ```.
    """
    try:
        # Using the configured Langchain LLM
        response = llm.invoke(
            [
                HumanMessage(
                    content=f"Generate a SPARQL query based on these instructions:\n{sparql_prompt}"
                )
            ]
        )
        generated_query = response.content.strip()

        # Clean up potential markdown code fences
        generated_query = re.sub(
            r"^```sparql\s*", "", generated_query, flags=re.IGNORECASE
        )
        generated_query = re.sub(r"\s*```$", "", generated_query)

        # Basic syntax check
        if not generated_query.strip().upper().startswith(
            "PREFIX"
        ) and not generated_query.strip().upper().startswith("SELECT"):
            warning = f"Warning: Generated query might be invalid (doesn't start with PREFIX or SELECT): {generated_query}"
            print(warning)
            # Return the potentially invalid query along with a warning note for the agent
            return f"{warning}\n\nSPARQL Query:\n{generated_query}"

        print(f"--- Generated SPARQL ---\n{generated_query}\n------------------------")
        return generated_query

    except Exception as e:
        print(
            f"\n--- Error generating SPARQL for query: '{natural_language_query}' ---"
        )
        print(f"Error: {e}")
        # Return error message for the agent to handle
        return f"Error: Failed to generate SPARQL query. LLM call failed: {e}"


@tool
def execute_sparql_tool(sparql_query: str) -> Dict[str, Any] | str:
    """
    Executes a given SPARQL query against the EU Open Data Portal endpoint ({SPARQL_ENDPOINT}).
    Use this tool *after* generating a query with generate_sparql_tool.
    Input is the raw SPARQL query string.
    Returns the JSON results if successful, or an error message string if execution fails or the response is not valid JSON.
    The agent should analyze the results (or error) to decide the next step.
    """
    print(f"\n--- Executing SPARQL ---\n{sparql_query}\n-----------------------")
    headers = {"Accept": "application/sparql-results+json"}
    params = {"query": sparql_query}
    try:
        response = requests.get(
            SPARQL_ENDPOINT, headers=headers, params=params, timeout=60
        )
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        results = response.json()
        print(
            f"--- SPARQL Execution Success: Got {len(results.get('results', {}).get('bindings', []))} results ---"
        )
        # Limit the size of the result passed back to the agent prompt if necessary
        # results_str = json.dumps(results)
        # if len(results_str) > 4000:
        #     print("Truncating large SPARQL results for agent context.")
        #     # Basic truncation, could be smarter
        #     truncated_results = results.get('results', {}).get('bindings', [])[:10]
        #     return {"results": {"bindings": truncated_results}, "metadata": {"truncated": True, "original_count": len(results.get('results', {}).get('bindings', []))}}
        return results
    except requests.exceptions.RequestException as e:
        error_msg = f"Error: SPARQL query execution failed. Request Error: {e}"
        print(f"--- {error_msg} ---")
        print(f"Query:\n{sparql_query}")
        return error_msg  # Return error string for the agent
    except json.JSONDecodeError as e:
        error_msg = f"Error: SPARQL query execution failed. Response was not valid JSON. Error: {e}. Response Text (first 500 chars): {response.text[:500]}"
        print(f"--- {error_msg} ---")
        print(f"Query:\n{sparql_query}")
        return error_msg  # Return error string for the agent
    except Exception as e:  # Catch any other unexpected errors
        error_msg = f"Error: An unexpected error occurred during SPARQL execution: {e}"
        print(f"--- {error_msg} ---")
        print(f"Query:\n{sparql_query}")
        return error_msg  # Return error string for the agent


# --- Langchain Agent Setup ---

# Define the tools the agent can use
tools = [generate_sparql_tool, execute_sparql_tool]

# Define the Agent Prompt
# Note: This prompt guides the agent's internal reasoning process (Chain of Thought)
# It instructs the agent on how to use the tools and interpret their results.
agent_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            f"""You are an AI assistant designed to answer questions by querying the EU Open Data Portal ({SPARQL_ENDPOINT}) using SPARQL.

Your goal is to find relevant datasets and synthesize an answer based on their metadata. You have two tools:
1.  `generate_sparql_tool`: Generates a SPARQL query from a natural language question. Takes `natural_language_query` (string) and optional `context` (string) for corrections. Returns the SPARQL query string or an error message.
2.  `execute_sparql_tool`: Executes a SPARQL query. Takes `sparql_query` (string). Returns JSON results or an error message string.

Follow these steps:
1.  **Generate SPARQL:** Use `generate_sparql_tool` with the user's query (`input`).
    *   If generation fails, report the error.
    *   If generation returns a warning about invalid syntax, decide whether to try executing it anyway or report the issue. Usually, try executing it.
2.  **Execute SPARQL:** Use `execute_sparql_tool` with the generated query.
3.  **Analyze Results/Errors:**
    *   **Execution Error:** If `execute_sparql_tool` returns an error string (starting with "Error:"), the query likely failed. Analyze the error. Consider using `generate_sparql_tool` again, providing the original query AND context explaining the error (e.g., "Previous query failed execution. Error: [error message]. Recheck syntax and prefixes."). Limit retries to 1-2 attempts. If errors persist, report the failure.
    *   **No Results:** If the execution was successful (returned JSON) but `results.bindings` is empty, the query found nothing. Consider using `generate_sparql_tool` again with context suggesting broader terms or relaxed filters (e.g., "Previous query returned no results. Try broader search terms."). Limit retries. If still no results, report that no relevant datasets were found.
    *   **Successful Results:** If you get JSON results with bindings:
        a.  **Analyze Metadata:** Examine the `results.bindings`. Identify the most relevant datasets based on title, description, keywords etc. Check if they cover the query's constraints (time, location). Note potential linking dimensions (common geo/time references, IDs).
        b.  **Hypothesize Linking (if needed):** If multiple datasets seem necessary and the metadata suggests potential linking dimensions (e.g., common NUTS codes, years), briefly describe how they could be linked. Assess feasibility based *only* on metadata.
        c.  **Synthesize Answer:** Based on the analysis, formulate a final answer.
            *   Summarize the key datasets found.
            *   If linking was hypothesized, mention the proposed logic and feasibility.
            *   Explain how these datasets address the user's query.
            *   Acknowledge limitations (e.g., "Requires data download for full analysis", "Assumes consistent units based on metadata").
            *   Present the answer clearly to the user. Do NOT just return raw JSON results. Provide a natural language summary. Include dataset URIs or titles for reference.

**Important:** Think step-by-step. Explain your reasoning before taking action (calling a tool or providing the final answer). If you retry a query, explain why.
""",
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(
            variable_name="agent_scratchpad"
        ),  # Tracks agent's internal steps
    ]
)

# Create the Agent
agent = create_openai_tools_agent(llm, tools, agent_prompt)

# Create the Agent Executor
# verbose=True helps in debugging by showing the agent's thoughts
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


# --- Main Function to Run Agent ---


def ask_data_portal_agent(user_query: str) -> Dict[str, Any]:
    """
    Uses the Langchain agent to answer a question about the EU Open Data Portal.
    """
    print(f"\n--- Running Agent for Query: '{user_query}' ---")
    # Initialize chat history (can be managed across calls if needed)
    chat_history = []
    try:
        # Invoke the agent executor
        # The agent will internally use the tools and follow the prompt logic
        response = agent_executor.invoke(
            {"input": user_query, "chat_history": chat_history}
        )
        # The final answer is expected in the 'output' key
        final_answer = response.get("output", "Agent did not provide a final output.")
        print(f"\n--- Agent Final Answer ---")
        print(final_answer)
        print("--------------------------")
        # Return a structured dictionary
        return {"status": "success", "query": user_query, "answer": final_answer}

    except Exception as e:
        print(f"\n--- Error running Langchain Agent ---")
        print(f"Query: {user_query}")
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()  # Print stack trace for detailed debugging
        return {
            "status": "error",
            "query": user_query,
            "message": f"Agent execution failed: {e}",
        }


# --- Example Natural Language Queries ---

# Single dataset examples
example_nl_queries_single = [
    "Find datasets about climate change tagged with 'environment'. Retrieve their titles and descriptions.",
    "List datasets published by the European Environment Agency, showing their title and landing page.",
]

# Complex/Multi-dataset examples
example_nl_queries_multi = [
    "Find datasets related to COVID-19 impacts, traffic levels, and air quality measurements, particularly focusing on European cities since 2020.",
    "Search for datasets containing information on the locations or spatial distribution of educational institutions (schools) and gambling facilities (casinos, betting shops). Include datasets related to urban planning.",
    "Correlate NO2 levels and road traffic in Paris, Berlin, Madrid for 2022 (monthly avg).",
    "List publications since 2021 from EU renewable energy research projects.",
]

# --- Run Examples using the Langchain Agent ---

if __name__ == "__main__":
    print("\n--- Running Agent Examples ---")

    all_examples = example_nl_queries_single + example_nl_queries_multi

    for i, nl_query in enumerate(all_examples):
        print(f"\n========== Example {i+1} ==========")
        agent_result = ask_data_portal_agent(nl_query)
        print(f"\nResult Dictionary for Example {i+1}:")
        # Pretty print the JSON result dictionary
        print(json.dumps(agent_result, indent=2))
        print("===================================")


# --- Code below this line is removed (Old orchestrator, analysis function) ---
