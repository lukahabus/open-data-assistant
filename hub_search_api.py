import openai
import json
import re
import requests
import os
import logging
import datetime
import sys
import traceback
from typing import List, Dict, Any, Optional

# Langchain imports (optional, could use direct openai client)
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage


# ANSI color codes for terminal output
class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"  # Reset color
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


# --- Logging Setup ---
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = os.path.join(log_directory, f"hub_search_api_run_{timestamp}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_filename), logging.StreamHandler()],
    force=True,
)

logging.info("--- Starting Hub-Search API Agent Script ---")

# --- Setup ---
# Ensure API key is available
# NOTE: Using OpenAI API Key again!
try:
    # Use the gpt-4.1 model
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set.")

    llm = ChatOpenAI(
        model="gpt-4.1",  # Set model to gpt-4.1
        temperature=0.1,
        request_timeout=60,
        api_key=openai_api_key,  # Use the OpenAI key
        # base_url removed to use default OpenAI endpoint
    )
    logging.info(f"Initialized LLM: model=gpt-4.1, temperature=0.1, timeout=60s")
except Exception as e:
    logging.error(f"Failed to initialize LLM. Ensure OPENAI_API_KEY is set. Error: {e}")
    sys.exit(1)


# Hub-Search API Endpoint
HUB_SEARCH_ENDPOINT = (
    "https://data.europa.eu/api/hub/search/search"  # Using /search path
)
logging.info(f"Hub-Search API Endpoint: {HUB_SEARCH_ENDPOINT}")

# --- Tools ---


@tool
def generate_hub_search_params_tool(
    natural_language_query: str, context: str = ""
) -> str:
    """
    Generates JSON request body string for Hub-Search API from NLQ.
    Input: natural_language_query (str), context (str, optional for corrections).
    Output: JSON string for POST /search endpoint or error message.
    """
    logging.info(
        f"Attempting to generate Hub-Search params for NLQ: '{natural_language_query}' (Context: '{context}')"
    )

    # Prompt for the LLM to generate JSON parameters based on openapi.yaml Query schema
    # Focus on mapping NLQ to 'q', 'filters', 'facets', 'limit', 'sort', 'minDate', 'maxDate' etc.
    prompt = f"""
    Given the natural language query: "{natural_language_query}"
    {context} # Add context if provided

    Generate a JSON object representing the request body for a POST request to the
    EU Open Data Hub-Search API endpoint ({HUB_SEARCH_ENDPOINT}).
    The JSON object MUST conform to the structure expected by the API's Query schema.

    Your primary goal is **dataset discovery for exploration**: identify a range of potentially relevant datasets (use a limit around 10-20).

    Key Query Schema fields to consider mapping from the natural language query:
    - `q` (string): The main search query string. Map keywords, topics etc. here.
    - `filters` (array of strings): Filter by document type (e.g., ["dataset", "catalogue"]). Often just ["dataset"].
    - `facets` (object): Map specific criteria like publisher, format, theme, country. Keys are facet names (e.g., "publisher_name", "country", "keywords", "categories"), values are arrays of strings (e.g., {{"publisher_name": ["European Environment Agency"], "keywords": ["climate"]}}). You may need to infer standard facet names. Use `keywords` for general tags/keywords. Use `categories` for DCAT themes (e.g. `http://publications.europa.eu/resource/authority/data-theme/ENVI`).
    - `limit` (integer): Set to around 10 or 20 for exploration.
    - `page` (integer): Usually 0 for the first page.
    - `sort` (array of strings): e.g., ["title+asc", "modified+desc"]. Default sort is usually fine unless specified.
    - `minDate`, `maxDate` (string, format: date-time): For date range filtering (e.g., "2020-01-01T00:00:00Z"). Map terms like "since 2020", "last 5 years". These should be nested under a `searchParams` object.
    - `boundingBox` (object with minLon, maxLon, maxLat, minLat): Nested under `searchParams`.
    - `minScoring`, `maxScoring` (integer): Can be nested under `searchParams.scoring` object OR top-level.
    - `countryData` (boolean): If explicitly asking for country-specific or non-country data.
    - `dataServices` (boolean): If asking specifically for datasets with access services.
    - `autocomplete` (boolean): Might be useful for quick title searches.

    Return *only* the raw JSON object string, without any explanations or formatting like ```json ... ```.
    Ensure the output is a single, valid JSON object string.
    """
    try:
        logging.info("Invoking LLM for Hub-Search JSON generation...")
        response = llm.invoke([HumanMessage(content=prompt)])
        generated_json_str = response.content.strip()
        logging.info("LLM call successful.")

        # Clean up potential markdown code fences
        cleaned_json_str = re.sub(
            r"^```json\s*", "", generated_json_str, flags=re.IGNORECASE
        )
        cleaned_json_str = re.sub(r"\s*```$", "", cleaned_json_str)

        # Basic validation: Check if it looks like JSON
        try:
            json.loads(cleaned_json_str)
            logging.info(
                f"--- Generated Hub-Search Params (JSON String) ---\n{cleaned_json_str}\n------------------------"
            )
            return cleaned_json_str
        except json.JSONDecodeError as json_err:
            error_msg = f"Error: LLM generated invalid JSON: {json_err}. Output: {cleaned_json_str}"
            logging.error(error_msg)
            return error_msg

    except Exception as e:
        logging.error(
            f"Error generating Hub-Search params for query: '{natural_language_query}'. Error: {e}",
            exc_info=True,
        )
        return f"Error: Failed to generate Hub-Search params. LLM call failed: {e}"


@tool
def execute_hub_search_tool(
    request_body_input: Dict[str, Any] | str,
) -> Dict[str, Any] | str:
    """
    Executes Hub-Search API POST /search request.
    Input: request_body_input (JSON string or dict).
    Output: Summary dictionary {'success': bool, 'count': int, 'message': str} or error message string.
    """
    logging.info(f"\n--- Executing Hub-Search POST Request ---")

    request_body: Dict[str, Any]
    if isinstance(request_body_input, str):
        logging.info(f"Received JSON string. Parsing...")
        logging.info(
            f"Request Body String:\n{request_body_input}\n-----------------------"
        )
        try:
            request_body = json.loads(request_body_input)
        except json.JSONDecodeError as json_err:
            error_msg = (
                f"Error: Invalid JSON string provided for request body: {json_err}"
            )
            logging.error(error_msg)
            return error_msg
    elif isinstance(request_body_input, dict):
        logging.info(f"Received dictionary. Using directly.")
        request_body = request_body_input
        logging.info(
            f"Request Body Dict:\n{json.dumps(request_body, indent=2)}\n-----------------------"
        )  # Log the dict nicely
    else:
        error_msg = f"Error: Invalid input type for request body. Expected dict or str, got {type(request_body_input)}"
        logging.error(error_msg)
        return error_msg

    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    try:
        # Now use the guaranteed dictionary `request_body`
        response = requests.post(
            HUB_SEARCH_ENDPOINT, headers=headers, json=request_body, timeout=30
        )
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        results = response.json()

        # Check API-level success indicator if present (based on OpenAPI responses)
        if not results.get(
            "success", True
        ):  # Assume success if 'success' field is missing, check API specific error structure
            error_msg = f"Error: Hub-Search API indicated failure. Response: {results.get('message', json.dumps(results))}"
            logging.error(f"--- {error_msg} ---")
            return error_msg  # Return the API's error message

        result_count = len(results.get("result", {}).get("results", []))
        logging.info(f"--- Hub-Search API Call Success: Got {result_count} results ---")
        # Return a summary to the agent, not the full result object
        return {
            "success": True,
            "count": result_count,
            "message": f"Successfully found {result_count} results.",
            "_full_results": results,  # Store full results temporarily for extraction later
        }

    except requests.exceptions.Timeout:
        error_msg = f"Error: Hub-Search API request timed out after 30 seconds."
        logging.error(f"--- {error_msg} ---")
        return error_msg  # Keep error short
    except requests.exceptions.RequestException as e:
        # Try to get more info from the response if available, but keep it brief
        response_text = ""
        status_code = "N/A"
        if e.response is not None:
            status_code = e.response.status_code
            try:
                # Try parsing JSON error first
                err_json = e.response.json()
                response_text = f" API Message: {err_json.get('message', e.response.text[:200])}"  # Limit length
            except json.JSONDecodeError:
                response_text = f" Response Text (truncated): {e.response.text[:200]}"  # Limit length

        error_msg = f"Error: Hub-Search API request failed. Status Code: {status_code}. Error: {e}.{response_text}"
        logging.error(
            f"--- {error_msg} --- Details: {e}"
        )  # Log full details separately
        return error_msg  # Return concise error to agent
    except json.JSONDecodeError as e:
        # This might happen if the successful response is not JSON (unlikely based on Accept header)
        # Also capture error if parsing input string fails inside the try block
        error_msg = f"Error: Failed to decode JSON. Error: {e}."
        # Avoid logging potentially large response text here
        logging.error(f"--- {error_msg} --- Traceback: {traceback.format_exc()}")
        return error_msg  # Return concise error
    except Exception as e:  # Catch any other unexpected errors
        error_msg = f"Error: An unexpected error occurred during Hub-Search API execution: {e.__class__.__name__}"
        logging.error(f"--- {error_msg} --- Full Error: {e}", exc_info=True)
        return error_msg  # Return concise error


# --- Langchain Agent Setup ---

tools = [generate_hub_search_params_tool, execute_hub_search_tool]

# Define the Agent Prompt
# This prompt guides the agent's reasoning and tool usage.
agent_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            f"""You are an AI assistant querying the EU Open Data Hub-Search API ({HUB_SEARCH_ENDPOINT}).
Your goal is **dataset discovery**.

Tools:
1.  `generate_hub_search_params_tool`: Generates JSON request body for the API from a user query. Use this first.
2.  `execute_hub_search_tool`: Executes the API search. Takes JSON string or dict. Returns a summary dict {{{{ 'success': bool, 'count': int, 'message': str }}}} or error string.

Workflow:
1.  Generate search parameters using `generate_hub_search_params_tool`.
2.  Execute search using `execute_hub_search_tool`.
3.  Analyze result/error:
    *   Generation Error: Report it.
    *   Execution Error: Analyze error. Consider **one retry** if it seems recoverable (e.g., timeout, bad params). Call `generate_hub_search_params_tool` again with context about the error. If retry fails, report final error.
    *   No Results (`success: true, count: 0`): Report that no datasets were found. Consider **one retry** only if the query was very specific and broadening it might help.
    *   Success (`success: true, count: >0`): Report success and the number of datasets found based on the summary message. Stop execution.

Your final output should be a concise message indicating success (and count) or failure.
""",
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# Create the Agent
agent = create_openai_tools_agent(llm, tools, agent_prompt)

# Create the Agent Executor
agent_executor = AgentExecutor(
    agent=agent, tools=tools, verbose=True
)  # verbose=True for debugging
logging.info("Langchain Agent Executor created.")


# --- Main Function to Run Agent Logic ---


def run_agent_query(user_query: str) -> Dict[str, Any]:
    """
    Invokes the Langchain agent executor for the given user query.
    Returns the agent's final response dictionary.
    """
    logging.info(f"--- Running Agent Executor for Query: '{user_query}' ---")
    chat_history = []  # Keep history simple for now
    full_api_results = None  # Variable to store full results if successful

    try:
        # Need to intercept the successful result from execute_hub_search_tool
        # Langchain agent execution doesn't easily expose intermediate tool *outputs* directly
        # outside the loop if the final agent answer is just a summary.
        # Option 1: Modify agent prompt to output a specific marker on success?
        # Option 2: Customize the AgentExecutor or use LangGraph for better state management.
        # Option 3 (Simpler workaround): Run the successful tool call AGAIN after agent finishes,
        # using the generated params (if the agent output implies success). This is inefficient.

        # Let's stick to the agent determining success/failure for now, and modify the final summarization.
        # The agent's *final* output should be sufficient to decide if we need to summarize.

        response = agent_executor.invoke(
            {"input": user_query, "chat_history": chat_history}
        )

        agent_final_answer = response.get(
            "output", "Agent did not provide a final output."
        )
        logging.info(
            f"--- Agent Final Output ---\n{agent_final_answer}\n--------------------------"
        )

        # Attempt to parse the agent's final answer to see if it indicates success and how many results.
        # This is brittle and relies on the agent following the prompt strictly.
        success_match = re.search(
            r"Successfully found (\d+) results", agent_final_answer, re.IGNORECASE
        )
        if success_match:
            count = int(success_match.group(1))
            if count > 0:
                # Agent reported success. Now, we need the *actual* results.
                # Since we can't easily get the intermediate `execute_hub_search_tool` output
                # from the executor, we might need to re-run the *generation* step
                # or parse the agent trace (complex).
                # --- Workaround: Re-generate params and re-execute --- (Inefficient but simpler for now)
                logging.warning(
                    "Re-running generation and execution to get full results for summary..."
                )
                regen_params_str = generate_hub_search_params_tool.invoke(
                    {"natural_language_query": user_query}
                )
                if isinstance(
                    regen_params_str, str
                ) and not regen_params_str.startswith("Error:"):
                    full_api_results_dict = execute_hub_search_tool.invoke(
                        {"request_body_input": regen_params_str}
                    )
                    # The tool call above returns the *summary* now.
                    # We stored the full result in the `_full_results` key within the summary dict.
                    if (
                        isinstance(full_api_results_dict, dict)
                        and "_full_results" in full_api_results_dict
                    ):
                        full_api_results = full_api_results_dict["_full_results"]
                        logging.info(
                            "Successfully retrieved full results for summarization."
                        )
                    else:
                        logging.error("Failed to retrieve full results via workaround.")
                        # Fall back to just the agent's summary message
                        return {
                            "status": "success",
                            "query": user_query,
                            "answer": agent_final_answer,
                        }
                else:
                    logging.error("Failed to re-generate parameters for summarization.")
                    return {
                        "status": "success",
                        "query": user_query,
                        "answer": agent_final_answer,
                    }

                # Now, synthesize the *user-facing* summary from full_api_results
                if (
                    full_api_results
                    and isinstance(full_api_results, dict)
                    and full_api_results.get("success")
                ):
                    search_results = full_api_results.get("result", {})
                    datasets = search_results.get("results", [])
                    actual_count = search_results.get("count", len(datasets))
                    summary_lines = [
                        f"Found {actual_count} potentially relevant datasets:"
                    ]
                    limit = 10  # Hardcode limit for summary display
                    for i, ds in enumerate(datasets):
                        if i >= limit:
                            break
                        title_obj = ds.get("title", {})
                        title = title_obj.get(
                            "en", next(iter(title_obj.values()), ds.get("id", "N/A"))
                        )
                        desc_obj = ds.get("description", {})
                        description = desc_obj.get(
                            "en",
                            next(iter(desc_obj.values()), "No description available."),
                        )
                        landing_page = ds.get("landing_page", [{}])[0].get(
                            "resource", "N/A"
                        )
                        if landing_page == "N/A" and ds.get("id"):
                            landing_page = f"https://data.europa.eu/data/datasets/{ds['id']}"  # Construct likely URL
                        summary_lines.append(
                            f"\n{i+1}. {bcolors.BOLD}{title}{bcolors.ENDC}"
                        )
                        summary_lines.append(
                            f"   - Description: {description[:200]}..."
                        )  # Truncate description
                        summary_lines.append(
                            f"   - Link: {bcolors.UNDERLINE}{landing_page}{bcolors.ENDC}"
                        )
                    final_summary = "\n".join(summary_lines)
                    logging.info(f"Synthesized Final Summary:\n{final_summary}")
                    return {
                        "status": "success",
                        "query": user_query,
                        "answer": final_summary,
                    }
                else:
                    # If getting full results failed, return agent's message
                    logging.warning(
                        "Summarization step failed, returning agent's final answer."
                    )
                    return {
                        "status": "success",
                        "query": user_query,
                        "answer": agent_final_answer,
                    }
            else:
                # Agent reported success but count was 0
                return {
                    "status": "success",
                    "query": user_query,
                    "answer": agent_final_answer,
                }
        else:
            # Agent did not report success or format was unexpected
            return {
                "status": "success",
                "query": user_query,
                "answer": agent_final_answer,
            }

    except Exception as e:
        logging.error(
            f"Error running Langchain Agent for query: '{user_query}'. Error: {e}",
            exc_info=True,
        )
        traceback.print_exc()
        return {
            "status": "error",
            "query": user_query,
            "message": f"Agent execution failed with unexpected error: {e}",
        }


# --- Example Natural Language Queries (Copied from sparql.py) ---

# Single dataset examples
example_nl_queries_single = [
    "Find datasets about climate change tagged with 'environment'. Retrieve their titles and descriptions.",
    "List datasets published by the European Environment Agency, showing their title and landing page.",
    "Show me datasets related to bicycle traffic in major European cities.",
    "Find datasets about the budget of the European Union.",
]

# Complex/Multi-dataset examples
example_nl_queries_multi = [
    "Find datasets related to COVID-19 impacts, traffic levels, and air quality measurements, particularly focusing on European cities since 2020.",
    "Search for datasets containing information on the locations or spatial distribution of educational institutions (schools) and gambling facilities (casinos, betting shops). Include datasets related to urban planning.",
    # "Correlate NO2 levels and road traffic in Paris, Berlin, Madrid for 2022 (monthly avg).", # This requires analysis beyond dataset discovery
    "List publications since 2021 from EU renewable energy research projects.",
    # "Identify datasets on agricultural subsidies distributed per region (NUTS 2 level) within the EU over the last 5 years, cross-referenced with datasets on regional GDP growth.", # Requires linking/analysis
    # "Find data linking fish stock assessments (e.g., biomass, fishing mortality) in the North Sea with ocean temperature anomalies reported by Copernicus Marine Service for the period 2015-2023.", # Requires linking/analysis
    "Show me datasets about migration flows into Germany, Italy, and Greece, specifically looking for data disaggregated by country of origin and year, alongside datasets about social integration policies or outcomes in those host countries since 2018.",
    "Find datasets on energy consumption per capita compared to GDP per capita for EU member states over the last decade.",
    "List datasets showing public transport usage trends before and after the COVID-19 pandemic in capital cities.",
]

# --- Run Examples using the Hub-Search Agent ---

if __name__ == "__main__":
    logging.info("\n--- Initializing Hub-Search API Agent Interface ---")

    # Combine examples, potentially removing ones requiring complex analysis beyond discovery
    analysis_heavy_queries = [
        "Correlate NO2 levels and road traffic in Paris, Berlin, Madrid for 2022 (monthly avg).",
        "Identify datasets on agricultural subsidies distributed per region (NUTS 2 level) within the EU over the last 5 years, cross-referenced with datasets on regional GDP growth.",
        "Find data linking fish stock assessments (e.g., biomass, fishing mortality) in the North Sea with ocean temperature anomalies reported by Copernicus Marine Service for the period 2015-2023.",
    ]
    all_examples = [
        q
        for q in example_nl_queries_single + example_nl_queries_multi
        if q not in analysis_heavy_queries
    ]

    while True:  # Outer loop to restart after completion
        print("\nAvailable Example Queries (Hub-Search API):")
        for i, nl_query in enumerate(all_examples):
            print(f"{i+1}. {nl_query}")
        print("0. Run ALL examples")

        while True:
            try:
                choice_str = input(
                    f"\nEnter the number of the example to run (1-{len(all_examples)}) or 0 to run all: "
                )
                choice = int(choice_str)
                if 0 <= choice <= len(all_examples):
                    break  # Valid input
                else:
                    print(
                        f"Invalid choice. Please enter a number between 0 and {len(all_examples)}."
                    )
            except ValueError:
                print("Invalid input. Please enter a number.")

        if choice == 0:
            logging.info("\n--- Running ALL Examples ---")
            for i, nl_query in enumerate(all_examples):
                logging.info(f"\n========== Running Example {i+1} ==========")
                # Use the new agent execution function
                agent_result = run_agent_query(nl_query)
                logging.info(f"\nResult Dictionary for Example {i+1}:")
                # Pretty print the JSON result dictionary to log, excluding raw response if too large
                log_result = agent_result.copy()
                # if 'api_response' in log_result: del log_result['api_response'] # Avoid logging large raw responses
                logging.info(json.dumps(log_result, indent=2))
                logging.info("===================================")
                print(f"\n--- Example {i+1} ---")
                print(f"{bcolors.HEADER}Query:{bcolors.ENDC} {nl_query}")
                # Print colored result
                if agent_result.get("status") == "success":
                    # Split the answer into lines for individual coloring if needed
                    # For simplicity, just print the answer block, assuming the agent formats it
                    print(
                        f"{bcolors.OKCYAN}Result:{bcolors.ENDC}\n{agent_result.get('answer', 'No answer found.')}"
                    )
                else:
                    print(
                        f"{bcolors.FAIL}Result: {agent_result.get('message', 'Error occurred.')}{bcolors.ENDC}"
                    )
                print("--------------------")

        else:
            selected_query = all_examples[choice - 1]  # Adjust for 0-based index
            logging.info(f"\n--- Running Selected Example {choice} ---")
            logging.info(f"Query: {selected_query}")
            # Use the new agent execution function
            agent_result = run_agent_query(selected_query)
            logging.info(f"\nResult Dictionary for Example {choice}:")
            # Pretty print the JSON result dictionary to log
            log_result = agent_result.copy()
            # if 'api_response' in log_result: del log_result['api_response']
            logging.info(json.dumps(log_result, indent=2))
            logging.info("===================================")
            print(f"\n--- Example {choice} ---")
            print(f"{bcolors.HEADER}Query:{bcolors.ENDC} {selected_query}")
            # Print colored result
            if agent_result.get("status") == "success":
                print(
                    f"{bcolors.OKCYAN}Result:{bcolors.ENDC}\n{agent_result.get('answer', 'No answer found.')}"
                )
            else:
                print(
                    f"{bcolors.FAIL}Result: {agent_result.get('message', 'Error occurred.')}{bcolors.ENDC}"
                )
            print("--------------------")

        # Ask user if they want to continue
        while True:
            another_query = (
                input("\nDo you want to run another example? (yes/no): ")
                .strip()
                .lower()
            )
            if another_query in ["yes", "y"]:
                break  # Continue outer loop
            elif another_query in ["no", "n"]:
                logging.info("--- Exiting Hub-Search API Agent Interface ---")
                sys.exit()  # Exit the script cleanly
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")

    logging.info("--- Finished Hub-Search API Agent Script ---")
