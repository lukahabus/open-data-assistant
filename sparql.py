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
from dotenv import load_dotenv

# Langchain imports
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage

# --- Logging Setup ---
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = os.path.join(log_directory, f"sparql_run_{timestamp}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_filename), logging.StreamHandler()],
    force=True,
)

logging.info("--- Starting SPARQL Agent Script ---")

# --- Setup ---
# Load environment variables from .env file
load_dotenv()

# Ensure OpenAI API key is available
# It will default to checking the OPENAI_API_KEY environment variable
llm = ChatOpenAI(model="gpt-4o", temperature=0.1, request_timeout=60)
logging.info(f"Initialized LLM: model=gpt-4o, temperature=0.1, timeout=60s")

# EU Open Data Portal SPARQL Endpoint
SPARQL_ENDPOINT = "https://data.europa.eu/sparql"
logging.info(f"SPARQL Endpoint: {SPARQL_ENDPOINT}")

# --- Langchain Tools ---


@tool
def generate_sparql_tool(natural_language_query: str, context: str = "") -> str:
    """
    Generates a SPARQL query for the EU Open Data Portal based on a natural language query.
    Use this tool first to get a query.
    Provide context only if a previous generation attempt failed and you have specific instructions for correction (e.g., 'Previous query failed with: [error message]. Check prefixes and resource types.').
    """
    logging.info(
        f"Attempting to generate SPARQL for NLQ: '{natural_language_query}' (Context: '{context}')"
    )
    # Prompt for the LLM to generate a SPARQL query
    sparql_prompt = f"""
    Given the natural language query: "{natural_language_query}"
    {f"Additional context for refinement based on previous attempt: {context}" if context else ""}

    Generate a SPARQL query for the EU Open Data Portal ({SPARQL_ENDPOINT}) to find **multiple datasets relevant to the themes** mentioned in the query.
    - The primary goal is **dataset discovery for exploration**: identify a range of potentially relevant datasets (up to 10-20).
    - Focus on searching dataset metadata (title, description, keywords) for relevance.
    - Use standard prefixes. Commonly used ones include:
        - `dct: <http://purl.org/dc/terms/>` (for titles, descriptions, dates, publishers, formats, spatial, etc.)
        - `dcat: <http://www.w3.org/ns/dcat#>` (for dataset/distribution types, keywords, themes, landing pages, start/end dates for temporal coverage)
        - `xsd: <http://www.w3.org/2001/XMLSchema#>` (for data types like dates)
        - `foaf: <http://xmlns.com/foaf/0.1/>` (for names, homepages, e.g., publisher names)
        - `skos: <http://www.w3.org/2004/02/skos/core#>` (for labels of controlled vocabulary terms, e.g., themes, file types, status)
        - `adms: <http://www.w3.org/ns/adms#>` (for status of distributions, e.g. adms:status)
        - `rdfs: <http://www.w3.org/2000/01/rdf-schema#>` (for labels, comments)
    - Target datasets (`?dataset a dcat:Dataset`).
    - Extract relevant *dataset* information (e.g., dataset URI, `dct:title`, `dct:description`, `dct:publisher` -> `foaf:name`, `dcat:landingPage`, `dct:issued`, `dct:modified`). Always include the dataset URI.
    - **Language Preference:** Prioritize datasets with English metadata (e.g., `dct:title`, `dct:description`, `skos:prefLabel`). Use `FILTER(LANGMATCHES(LANG(?title), "en") || LANG(?title) = "")` for titles. Apply similar logic for descriptions and labels. If English is not available, results in other languages are acceptable.
    - Filter datasets based on keywords, themes, dates, publishers, formats etc. mentioned in the query by searching `dcat:keyword`, `dct:title`, `dct:description`.
        - For themes, use `dcat:theme` and link to specific theme URIs (e.g., from `<http://publications.europa.eu/resource/authority/data-theme>`). You might need to find the theme URI by its label (e.g., `?themeURI skos:prefLabel "Environment"@en`).
        - For dates, use `dct:issued` (publication), `dct:modified` (update), or `dct:temporal` with `dcat:startDate`/`dcat:endDate` for the period covered by the data.
        - For publishers, use `dct:publisher` and then `foaf:name` for the publisher's name.
        - For file formats, link `?dataset dcat:distribution ?distribution . ?distribution dct:format <URI_of_file_type_from_controlled_vocabulary>` or `?distribution dcat:mediaType "iana/mimetype"`. Example file type URI for CSV: `<http://publications.europa.eu/resource/authority/file-type/CSV>`. Use `skos:prefLabel` to get the format name.
    - Use FILTER with `CONTAINS` or `REGEX` for flexible text matching on title, description, or keywords. Apply `STR()` and `LCASE()` for case-insensitive matching on potentially non-string variables: `FILTER(CONTAINS(LCASE(STR(?var)), "term"))`.
    - **Avoid complex joins or analysis *within* the SPARQL query itself.** However, simple links to distributions (for format filtering) or publishers are acceptable.
    - Add a LIMIT clause (e.g., LIMIT 20) to retrieve a good number of results for exploration.

    Here are some examples to guide your generation:

    --- Example 1 ---
    Natural Language Query: "Find datasets about air quality in Germany."
    SPARQL Query:
    PREFIX dct: <http://purl.org/dc/terms/>
    PREFIX dcat: <http://www.w3.org/ns/dcat#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT DISTINCT ?dataset ?title ?description
    WHERE {{
      ?dataset a dcat:Dataset .
      ?dataset dct:title ?title .
      OPTIONAL {{ ?dataset dct:description ?description . }}
      # Filter by keywords or text in title/description
      FILTER (
        CONTAINS(LCASE(STR(?title)), "air quality") ||
        (BOUND(?description) && CONTAINS(LCASE(STR(?description)), "air quality")) ||
        EXISTS {{ ?dataset dcat:keyword ?kw . FILTER(CONTAINS(LCASE(STR(?kw)), "air quality")) }}
      )
      # Filter by location if mentioned (Germany example)
      FILTER (
        CONTAINS(LCASE(STR(?title)), "germany") ||
        (BOUND(?description) && CONTAINS(LCASE(STR(?description)), "germany")) ||
        EXISTS {{ ?dataset dct:spatial ?spatialUri . OPTIONAL {{?spatialUri skos:prefLabel ?spatialLabelEN . FILTER(LANGMATCHES(LANG(?spatialLabelEN), "en"))}} OPTIONAL {{?spatialUri rdfs:label ?spatialLabel .}} FILTER(CONTAINS(LCASE(STR(?spatialLabelEN)), "germany") || CONTAINS(LCASE(STR(?spatialLabel)), "germany")) }} ||
        EXISTS {{ ?dataset dcat:keyword ?kw_loc . FILTER(CONTAINS(LCASE(STR(?kw_loc)), "germany")) }}
      )
      # Language preference for title
      FILTER(LANGMATCHES(LANG(?title), "en") || LANG(?title) = "")
      # Optional language preference for description
      OPTIONAL {{ FILTER(LANGMATCHES(LANG(?description), "en") || LANG(?description) = "") }}
    }}
    LIMIT 15
    --- End Example 1 ---

    --- Example 2 ---
    Natural Language Query: "List datasets published by Eurostat concerning unemployment rates, issued after 2020."
    SPARQL Query:
    PREFIX dct: <http://purl.org/dc/terms/>
    PREFIX dcat: <http://www.w3.org/ns/dcat#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT DISTINCT ?dataset ?title ?publisherName ?issuedDate
    WHERE {{
      ?dataset a dcat:Dataset .
      ?dataset dct:title ?title .
      ?dataset dct:publisher ?publisherOrg .
      ?publisherOrg foaf:name ?publisherName .
      OPTIONAL {{ ?dataset dct:issued ?issuedDate . }}
      OPTIONAL {{ ?dataset dct:description ?description . }}

      # Filter by publisher name
      FILTER(CONTAINS(LCASE(STR(?publisherName)), "eurostat"))

      # Filter by keywords in title/description
      FILTER (
        CONTAINS(LCASE(STR(?title)), "unemployment") ||
        (BOUND(?description) && CONTAINS(LCASE(STR(?description)), "unemployment")) ||
        EXISTS {{ ?dataset dcat:keyword ?kw . FILTER(CONTAINS(LCASE(STR(?kw)), "unemployment")) }}
      )
      # Filter by issue date
      FILTER(!BOUND(?issuedDate) || ?issuedDate > "2020-01-01"^^xsd:date)

      # Language preference for title
      FILTER(LANGMATCHES(LANG(?title), "en") || LANG(?title) = "")
    }}
    LIMIT 10
    --- End Example 2 ---

    --- Example 3 ---
    Natural Language Query: "Find datasets in the 'Environment' theme, available in CSV format, and include their modification date."
    SPARQL Query:
    PREFIX dct: <http://purl.org/dc/terms/>
    PREFIX dcat: <http://www.w3.org/ns/dcat#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT DISTINCT ?dataset ?title ?modifiedDate ?formatLabel
    WHERE {{
      ?dataset a dcat:Dataset .
      ?dataset dct:title ?title .
      OPTIONAL {{ ?dataset dct:modified ?modifiedDate . }}

      # Filter by theme: Attempt to match "Environment" theme label
      ?dataset dcat:theme ?themeURI .
      ?themeURI skos:prefLabel ?themeLabel .
      FILTER(LANGMATCHES(LANG(?themeLabel), "en") && CONTAINS(LCASE(STR(?themeLabel)), "environment"))

      # Filter by distribution format: Specifically CSV
      ?dataset dcat:distribution ?distribution .
      ?distribution dct:format <http://publications.europa.eu/resource/authority/file-type/CSV> .
      # Optionally get the label of the format if needed for display
      <http://publications.europa.eu/resource/authority/file-type/CSV> skos:prefLabel ?formatLabel .
      FILTER(LANGMATCHES(LANG(?formatLabel), "en") || LANG(?formatLabel) = "")

      # Language preference for title
      FILTER(LANGMATCHES(LANG(?title), "en") || LANG(?title) = "")
    }}
    LIMIT 15
    --- End Example 3 ---

    Return *only* the raw SPARQL query string, without any explanations or formatting like ```sparql ... ```.
    """
    try:
        # Using the configured Langchain LLM
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
            return f"{warning}\n\nSPARQL Query:\n{cleaned_query}"

        logging.info(
            f"--- Generated SPARQL ---\n{cleaned_query}\n------------------------"
        )
        return cleaned_query

    except Exception as e:
        logging.error(
            f"Error generating SPARQL for query: '{natural_language_query}'. Error: {e}",
            exc_info=True,
        )
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
        # Limit the size of the result passed back to the agent prompt if necessary
        # results_str = json.dumps(results)
        # if len(results_str) > 4000:
        #     logging.warning("Truncating large SPARQL results for agent context.")
        #     # Basic truncation, could be smarter
        #     truncated_results = results.get('results', {}).get('bindings', [])[:10]
        #     return {"results": {"bindings": truncated_results}, "metadata": {"truncated": True, "original_count": len(results.get('results', {}).get('bindings', []))}}
        return results
    except requests.exceptions.Timeout:
        error_msg = (
            f"Error: SPARQL query execution failed. Request timed out after 30 seconds."
        )
        logging.error(f"--- {error_msg} --- Query:\n{sparql_query}")
        return error_msg
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

Your primary goal is **dataset discovery for exploration**. You should find a range of potentially relevant datasets (up to 10-20) based on the user's query and synthesize an answer summarizing these findings.

You have two tools:
1.  `generate_sparql_tool`: Generates a SPARQL query from a natural language question. Takes `natural_language_query` (string) and optional `context` (string) for corrections. Returns the SPARQL query string or an error message. **This tool is configured to generate queries aiming for multiple (up to 20) results.**
2.  `execute_sparql_tool`: Executes a SPARQL query. Takes `sparql_query` (string). Returns JSON results or an error message string.

Follow these steps:
1.  **Generate SPARQL:** Use `generate_sparql_tool` with the user's query (`input`).
    *   If generation fails, report the error.
    *   If generation returns a warning about invalid syntax, decide whether to try executing it anyway or report the issue. Usually, try executing it.
2.  **Execute SPARQL:** Use `execute_sparql_tool` with the generated query.
3.  **Analyze Results/Errors:**
    *   **Execution Error:** If `execute_sparql_tool` returns an error string (starting with "Error:"), the query likely failed. Analyze the error (e.g., timeout, request error, syntax error). Consider using `generate_sparql_tool` again, providing the original query AND context explaining the error (e.g., "Previous query failed execution. Error: [error message]. Recheck syntax and prefixes."). Limit retries to 1-2 attempts. If errors persist, report the failure.
    *   **No Results:** If the execution was successful (returned JSON) but `results.bindings` is empty, the query found nothing. Consider using `generate_sparql_tool` again with context suggesting broader terms or relaxed filters (e.g., "Previous query returned no results. Try broader search terms."). Limit retries. If still no results, report that no relevant datasets were found.
    *   **Successful Results:** If you get JSON results with bindings:
        a.  **Analyze Metadata:** Examine the `results.bindings` (potentially up to 20 datasets). Identify datasets relevant to the query based on title, description, keywords etc. Check if they cover the query's constraints (time, location).
        b.  **Hypothesize Linking (if needed):** If multiple datasets seem necessary and the metadata suggests potential linking dimensions (e.g., common NUTS codes, years), briefly describe how they could be linked. Assess feasibility based *only* on metadata.
        c.  **Synthesize Answer:** Based on the analysis, formulate a final answer.
            *   **Summarize the range of key datasets found.** Highlight the breadth of relevant findings for exploration.
            *   If linking was hypothesized, mention the proposed logic and feasibility.
            *   Explain how these datasets address the user's query.
            *   Acknowledge limitations (e.g., "Requires data download for full analysis", "Assumes consistent units based on metadata", "Short API timeout might limit results for complex queries", "Results limited to the first 20 found").
            *   Present the answer clearly to the user. Do NOT just return raw JSON results. Provide a natural language summary. Include dataset URIs or titles for reference.

**Important:** Think step-by-step. Explain your reasoning before taking action (calling a tool or providing the final answer). If you retry a query, explain why. Pay attention to potential timeouts.
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
logging.info("Langchain Agent Executor created.")


# --- Main Function to Run Agent ---


def ask_data_portal_agent(user_query: str) -> Dict[str, Any]:
    """
    Uses the Langchain agent to answer a question about the EU Open Data Portal.
    """
    logging.info(f"--- Running Agent for Query: '{user_query}' ---")
    # Initialize chat history (can be managed across calls if needed)
    chat_history = []
    try:
        # Invoke the agent executor
        # The agent will internally use the tools and follow the prompt logic
        logging.info("Invoking agent executor...")
        response = agent_executor.invoke(
            {"input": user_query, "chat_history": chat_history}
        )
        # The final answer is expected in the 'output' key
        final_answer = response.get("output", "Agent did not provide a final output.")
        logging.info(
            f"--- Agent Final Answer ---\n{final_answer}\n--------------------------"
        )
        # Return a structured dictionary
        return {"status": "success", "query": user_query, "answer": final_answer}

    except Exception as e:
        logging.error(
            f"Error running Langchain Agent for query: '{user_query}'. Error: {e}",
            exc_info=True,
        )
        # Print traceback to console (stderr)
        traceback.print_exc()
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
    "Show me datasets related to bicycle traffic in major European cities.",
    "Find datasets about the budget of the European Union.",
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
    "Find datasets on energy consumption per capita compared to GDP per capita for EU member states over the last decade.",
    "List datasets showing public transport usage trends before and after the COVID-19 pandemic in capital cities.",
    "Find datasets about environmental protection, published after 2022, and available in CSV or XML format.",
    "List datasets related to fishery statistics, including their last modification date, prioritizing English titles.",
    "Show me datasets from the 'Justice, legal system and public safety' data theme, specifically those mentioning 'crime statistics' in their title or description.",
    "Find datasets about energy consumption that have been modified since January 2023 and list their publisher.",
]

# --- Run Examples using the Langchain Agent ---

if __name__ == "__main__":
    logging.info("\n--- Initializing SPARQL Agent Interface ---")

    all_examples = example_nl_queries_single + example_nl_queries_multi

    while True:  # Outer loop to restart after completion
        print("\nAvailable Example Queries:")
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
                agent_result = ask_data_portal_agent(nl_query)
                logging.info(f"\nResult Dictionary for Example {i+1}:")
                # Pretty print the JSON result dictionary to log
                logging.info(json.dumps(agent_result, indent=2))
                logging.info("===================================")
        else:
            selected_query = all_examples[choice - 1]  # Adjust for 0-based index
            logging.info(f"\n--- Running Selected Example {choice} ---")
            logging.info(f"Query: {selected_query}")
            agent_result = ask_data_portal_agent(selected_query)
            logging.info(f"\nResult Dictionary for Example {choice}:")
            # Pretty print the JSON result dictionary to log
            logging.info(json.dumps(agent_result, indent=2))
            logging.info("===================================")

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
                logging.info("--- Exiting SPARQL Agent Interface ---")
                sys.exit()  # Exit the script cleanly
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")

    logging.info("--- Finished SPARQL Agent Script ---")


# --- Code below this line is removed (Old orchestrator, analysis function) ---
