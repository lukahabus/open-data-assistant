# sparql.py
import openai
import json
import re
import requests
import os
import logging
import datetime
import sys
import traceback
from typing import List, Dict, Any, Optional, TypedDict
import coloredlogs  # Added for colored console logging

# Langchain imports
from langchain_openai import ChatOpenAI

# from langchain.agents import AgentExecutor, create_openai_tools_agent # Removed old agent imports
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder # Removed old agent imports
from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage

# LangGraph imports
from langgraph.graph import StateGraph, END


# --- Logging Setup ---
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = os.path.join(log_directory, f"sparql_run_{timestamp}.log")

# Configure file logging
file_handler = logging.FileHandler(log_filename)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Get the root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Set root logger level
logger.addHandler(file_handler)

# Configure colored console logging
coloredlogs.install(
    level="INFO", logger=logger, fmt="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("--- Starting SPARQL Agent Script (LangGraph Version) ---")

# --- Setup ---
# Ensure OpenAI API key is available
# It will default to checking the OPENAI_API_KEY environment variable
llm = ChatOpenAI(model="gpt-4o", temperature=0.1, request_timeout=60)
logging.info(f"Initialized LLM: model=gpt-4o, temperature=0.1, timeout=60s")

# EU Open Data Portal SPARQL Endpoint
SPARQL_ENDPOINT = "https://data.europa.eu/sparql"
logging.info(f"SPARQL Endpoint: {SPARQL_ENDPOINT}")

# Constants for retries
MAX_GENERATION_RETRIES = 2
MAX_EXECUTION_RETRIES = 1  # Max times to retry executing the *same* query on timeout


# --- Langchain Tools (remain mostly the same, used by graph nodes) ---


@tool
def generate_sparql_tool(natural_language_query: str, context: str = "") -> str:
    """
    Generates a SPARQL query for the EU Open Data Portal based on a natural language query.
    Use this tool first to get a query.
    Provide context only if a previous generation attempt failed and you have specific instructions for correction (e.g., 'Previous query failed execution. Check prefixes.').
    """
    logging.info(
        f"Attempting to generate SPARQL for NLQ: '{natural_language_query}' (Context: '{context}')"
    )
    # Prompt for the LLM to generate a SPARQL query
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
        logging.info("Invoking LLM for SPARQL generation...")
        response = llm.invoke(
            [
                HumanMessage(
                    content=f"Generate a SPARQL query based on these instructions:\n{sparql_prompt}"
                )
            ]
        )
        generated_query = response.content.strip()
        logging.info("LLM call successful.")

        # Clean up potential markdown code fences
        cleaned_query = re.sub(
            r"^```sparql\s*", "", generated_query, flags=re.IGNORECASE
        )
        cleaned_query = re.sub(r"\s*```$", "", cleaned_query)

        # Basic syntax check
        if not cleaned_query.strip().upper().startswith(
            "PREFIX"
        ) and not cleaned_query.strip().upper().startswith("SELECT"):
            warning = f"Warning: Generated query might be invalid (doesn't start with PREFIX or SELECT)."
            logging.warning(f"{warning} Query: {cleaned_query}")
            # Return the potentially invalid query along with a warning note for the agent
            # We will handle this structure in the graph node now
            # return f"{warning}\n\nSPARQL Query:\n{cleaned_query}"
            # Return the query as is, let the graph logic decide
            return cleaned_query

        logging.info(
            f"--- Generated SPARQL ---\n{cleaned_query}\n------------------------"
        )
        return cleaned_query

    except Exception as e:
        logging.error(
            f"Error generating SPARQL for query: '{natural_language_query}'. Error: {e}",
            exc_info=True,
        )
        # Return error message for the graph to handle
        return f"Error: Failed to generate SPARQL query. LLM call failed: {e}"


@tool
def execute_sparql_tool(sparql_query: str) -> Dict[str, Any] | str:
    """
    Executes a given SPARQL query against the EU Open Data Portal endpoint ({SPARQL_ENDPOINT}).
    Use this tool *after* generating a query with generate_sparql_tool.
    Input is the raw SPARQL query string.
    Returns the JSON results if successful, or an error message string if execution fails or the response is not valid JSON.
    """
    logging.info(f"\n--- Executing SPARQL ---\n{sparql_query}\n-----------------------")
    headers = {"Accept": "application/sparql-results+json"}
    params = {"query": sparql_query}
    try:
        response = requests.get(
            SPARQL_ENDPOINT, headers=headers, params=params, timeout=30
        )
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        results = response.json()
        result_count = len(results.get("results", {}).get("bindings", []))
        logging.info(f"--- SPARQL Execution Success: Got {result_count} results ---")
        return results
    except requests.exceptions.Timeout:
        error_msg = (
            f"Error: SPARQL query execution failed. Request timed out after 30 seconds."
        )
        logging.error(f"--- {error_msg} --- Query:\n{sparql_query}")
        return error_msg  # Specific error type for retry logic
    except requests.exceptions.RequestException as e:
        error_msg = f"Error: SPARQL query execution failed. Request Error: {e}"
        logging.error(f"--- {error_msg} --- Query:\n{sparql_query}", exc_info=True)
        return error_msg
    except json.JSONDecodeError as e:
        error_msg = f"Error: SPARQL query execution failed. Response was not valid JSON. Error: {e}. Response Text (first 500 chars): {response.text[:500]}"
        logging.error(f"--- {error_msg} --- Query:\n{sparql_query}", exc_info=True)
        return error_msg
    except Exception as e:  # Catch any other unexpected errors
        error_msg = f"Error: An unexpected error occurred during SPARQL execution: {e}"
        logging.error(f"--- {error_msg} --- Query:\n{sparql_query}", exc_info=True)
        return error_msg


# --- LangGraph State Definition ---


class GraphState(TypedDict):
    natural_language_query: str
    current_sparql_query: Optional[str]
    execution_result: Optional[Dict[str, Any] | str]
    retry_context: str  # Context for the *next* generation attempt
    generation_retries: int
    execution_retries: int  # Retries for the *current* query
    max_generation_retries: int
    max_execution_retries: int
    final_answer: Optional[str]


# --- LangGraph Node Functions ---


def generate_sparql_node(state: GraphState) -> Dict[str, Any]:
    """Generates a SPARQL query using the tool."""
    logging.info(
        f"--- Node: generate_sparql_node (Attempt {state['generation_retries'] + 1}) ---"
    )
    nl_query = state["natural_language_query"]
    context = state.get("retry_context", "")

    # Call the tool
    generated_query = generate_sparql_tool.invoke(
        {"natural_language_query": nl_query, "context": context}
    )

    return {
        "current_sparql_query": generated_query,
        "generation_retries": state.get("generation_retries", 0) + 1,
        "execution_retries": 0,  # Reset execution retries for new query
        "retry_context": "",  # Clear context after using it
        "execution_result": None,  # Clear previous execution result
    }


def execute_sparql_node(state: GraphState) -> Dict[str, Any]:
    """Executes the current SPARQL query using the tool."""
    logging.info(
        f"--- Node: execute_sparql_node (Execution Attempt {state['execution_retries'] + 1}) ---"
    )
    sparql_query = state["current_sparql_query"]

    if (
        not sparql_query
        or sparql_query.startswith("Error:")
        or not isinstance(sparql_query, str)
    ):
        # Should not happen if generate node ran correctly, but handle defensively
        logging.error("Execute node called with invalid/missing SPARQL query.")
        return {
            "execution_result": "Error: Invalid SPARQL query provided to execution node."
        }

    # Call the tool
    result = execute_sparql_tool.invoke({"sparql_query": sparql_query})

    return {
        "execution_result": result,
        "execution_retries": state.get("execution_retries", 0) + 1,
    }


def synthesize_answer_node(state: GraphState) -> Dict[str, Any]:
    """Synthesizes the final answer based on successful SPARQL results."""
    logging.info("--- Node: synthesize_answer_node ---")
    nl_query = state["natural_language_query"]
    sparql_results = state["execution_result"]

    if not isinstance(sparql_results, dict):
        logging.error("Synthesize node called without valid dictionary results.")
        return {
            "final_answer": "Error: Internal error - Synthesis called without valid results."
        }

    # Extract bindings
    bindings = sparql_results.get("results", {}).get("bindings", [])
    results_summary = json.dumps(bindings, indent=2)  # Simple summary for now
    result_count = len(bindings)

    # Use LLM to synthesize a natural language answer
    synthesis_prompt = f"""
    Given the original user query: "{nl_query}"

    And the following SPARQL query results (found {result_count} items):
    ```json
    {results_summary}
    ```

    Synthesize a concise, user-friendly answer based *only* on the provided results.
    - Summarize the key findings or datasets found.
    - If no results were found (bindings array is empty), state that clearly.
    - Mention the number of results found if applicable.
    - If the results contain dataset URIs, titles, or landing pages, mention them briefly as examples.
    - Do NOT invent information not present in the results.
    - Acknowledge potential limitations if appropriate (e.g., based on LIMIT clause if known, or complexity).
    - Format the answer clearly for the user.
    """
    try:
        logging.info("Invoking LLM for answer synthesis...")
        response = llm.invoke([HumanMessage(content=synthesis_prompt)])
        final_answer = response.content.strip()
        logging.info("LLM synthesis successful.")
    except Exception as e:
        logging.error(f"Error during LLM synthesis: {e}", exc_info=True)
        final_answer = f"Successfully retrieved {result_count} results, but failed to synthesize a final answer. Raw results summary:\n{results_summary}"

    return {"final_answer": final_answer}


def report_failure_node(state: GraphState) -> Dict[str, Any]:
    """Reports failure if retries are exhausted or an unrecoverable error occurs."""
    logging.info("--- Node: report_failure_node ---")
    nl_query = state["natural_language_query"]
    gen_retries = state["generation_retries"]
    max_gen_retries = state["max_generation_retries"]
    exec_result = state["execution_result"]
    sparql_query = state["current_sparql_query"]

    reason = "Unknown failure reason."
    if gen_retries >= max_gen_retries:
        reason = f"Maximum generation retries ({max_gen_retries}) reached."
    if isinstance(sparql_query, str) and sparql_query.startswith("Error:"):
        reason = f"Failed during SPARQL generation: {sparql_query}"
    elif isinstance(exec_result, str) and exec_result.startswith("Error:"):
        reason = f"Failed during SPARQL execution: {exec_result}"
    elif isinstance(exec_result, dict) and not exec_result.get("results", {}).get(
        "bindings", []
    ):
        reason = "Query executed successfully but found no matching datasets after retrying generation."

    final_answer = f"Sorry, I could not successfully answer the query: '{nl_query}'.\nReason: {reason}"
    logging.warning(f"Reporting failure for query '{nl_query}'. Reason: {reason}")

    return {"final_answer": final_answer}


# --- LangGraph Conditional Logic ---


def should_retry_or_proceed(state: GraphState) -> str:
    """Determines the next step after execution based on results and retries."""
    logging.info("--- Condition: should_retry_or_proceed ---")
    sparql_query = state["current_sparql_query"]
    exec_result = state["execution_result"]
    gen_retries = state["generation_retries"]
    exec_retries = state["execution_retries"]
    max_gen = state["max_generation_retries"]
    max_exec = state["max_execution_retries"]

    # Check if generation failed outright
    if isinstance(sparql_query, str) and sparql_query.startswith("Error:"):
        logging.warning("Generation failed. Reporting failure.")
        return "report_failure"  # Generation error is usually fatal

    # Check execution results
    if isinstance(exec_result, str):
        # Execution failed with an error message
        error_msg = exec_result
        logging.warning(f"Execution failed: {error_msg}")
        if "timed out" in error_msg.lower() and exec_retries <= max_exec:
            logging.info(
                f"Execution timed out. Retrying execution (Attempt {exec_retries}/{max_exec})."
            )
            return "retry_execution"  # Retry same query on timeout if attempts remain
        else:
            # Non-timeout error or max execution retries reached for this query
            if gen_retries < max_gen:
                logging.info(
                    "Execution failed (non-timeout or max retries). Retrying generation with context."
                )
                # Set context for the *next* generation attempt
                state["retry_context"] = (
                    f"Previous query ('{sparql_query[:100]}...') failed execution. Error: {error_msg}. Try generating a different query (e.g., simplify, check syntax/prefixes)."
                )
                return "retry_generation"
            else:
                logging.warning(
                    "Execution failed, max generation retries reached. Reporting failure."
                )
                return "report_failure"
    elif isinstance(exec_result, dict):
        # Execution successful, returned JSON
        bindings = exec_result.get("results", {}).get("bindings", [])
        if not bindings:
            # Successful execution, but no results
            logging.info("Execution successful, but no results found.")
            if gen_retries < max_gen:
                logging.info("Retrying generation with context for broader search.")
                # Set context for the *next* generation attempt
                state["retry_context"] = (
                    f"Previous query ('{sparql_query[:100]}...') returned no results. Try generating a query with broader terms or fewer filters."
                )
                return "retry_generation"
            else:
                logging.warning(
                    "No results found, max generation retries reached. Reporting failure."
                )
                return "report_failure"
        else:
            # Successful execution with results
            logging.info("Execution successful with results. Proceeding to synthesis.")
            return "synthesize_answer"
    else:
        # Should not happen
        logging.error("Invalid execution result type in state. Reporting failure.")
        return "report_failure"


# --- Build LangGraph ---

workflow = StateGraph(GraphState)

# Add nodes
workflow.add_node("generate", generate_sparql_node)
workflow.add_node("execute", execute_sparql_node)
workflow.add_node("synthesize", synthesize_answer_node)
workflow.add_node("report_failure", report_failure_node)

# Set entry point
workflow.set_entry_point("generate")

# Add edges
workflow.add_edge("generate", "execute")
workflow.add_conditional_edges(
    "execute",
    should_retry_or_proceed,
    {
        "retry_execution": "execute",  # Loop back to execute for timeout retry
        "retry_generation": "generate",  # Loop back to generate for other failures/no results
        "synthesize_answer": "synthesize",
        "report_failure": "report_failure",
    },
)
workflow.add_edge("synthesize", END)
workflow.add_edge("report_failure", END)

# Compile the graph
app = workflow.compile()
logging.info("LangGraph app compiled.")


# --- Main Function to Run Agent --- (Now uses LangGraph app)


def ask_data_portal_agent(user_query: str) -> Dict[str, Any]:
    """
    Uses the LangGraph app to answer a question about the EU Open Data Portal.
    """
    logging.info(f"--- Running Agent for Query: '{user_query}' ---")
    initial_state = GraphState(
        natural_language_query=user_query,
        current_sparql_query=None,
        execution_result=None,
        retry_context="",
        generation_retries=0,
        execution_retries=0,
        max_generation_retries=MAX_GENERATION_RETRIES,
        max_execution_retries=MAX_EXECUTION_RETRIES,
        final_answer=None,
    )
    try:
        logging.info("Invoking LangGraph app...")
        # Stream events for detailed logging (optional but helpful)
        # for event in app.stream(initial_state):
        #     logging.debug(f"Graph Event: {event}")

        # Run the graph to completion
        final_state = app.invoke(initial_state)

        final_answer = final_state.get(
            "final_answer", "Graph did not produce a final answer."
        )
        logging.info(
            f"--- Agent Final Answer ---\n{final_answer}\n--------------------------"
        )
        # Return a structured dictionary
        return {"status": "success", "query": user_query, "answer": final_answer}

    except Exception as e:
        logging.error(
            f"Error running LangGraph Agent for query: '{user_query}'. Error: {e}",
            exc_info=True,  # Log exception info to file
        )
        # Print traceback to console (stderr)
        traceback.print_exc()
        return {
            "status": "error",
            "query": user_query,
            "message": f"Agent execution failed: {e}",
        }


# --- Example Natural Language Queries --- (Remain the same)

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
    "Identify datasets on agricultural subsidies distributed per region (NUTS 2 level) within the EU over the last 5 years, cross-referenced with datasets on regional GDP growth.",
    "Find data linking fish stock assessments (e.g., biomass, fishing mortality) in the North Sea with ocean temperature anomalies reported by Copernicus Marine Service for the period 2015-2023.",
    "Show me datasets about migration flows into Germany, Italy, and Greece, specifically looking for data disaggregated by country of origin and year, alongside datasets about social integration policies or outcomes in those host countries since 2018.",
    "Invalid SPARQL generation test query",  # Add a test case likely to fail generation
    "Query likely to timeout often",  # Add a test case for timeout handling
]


# --- Run Examples using the Langchain Agent --- (Now uses LangGraph)

if __name__ == "__main__":
    logging.info("\n--- Running Agent Examples ---")

    # Combine examples for testing
    all_examples = example_nl_queries_single + example_nl_queries_multi

    # Limit examples for quicker testing if needed
    # all_examples = all_examples[:3]

    for i, nl_query in enumerate(all_examples):
        logging.info(f"\n========== Example {i+1} ==========")
        agent_result = ask_data_portal_agent(nl_query)
        logging.info(f"\nResult Dictionary for Example {i+1}:")
        # Pretty print the JSON result dictionary to log
        logging.info(json.dumps(agent_result, indent=2))
        logging.info("===================================")

    logging.info("--- Finished SPARQL Agent Script ---")


# Removed old agent setup code (prompt, agent, executor)
# Removed old orchestrator function
