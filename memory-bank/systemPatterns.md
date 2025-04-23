# System Patterns: Open Data Assistant

## Core Pattern: Langchain Agent with Tools

The current system (`sparql.py`) employs a Langchain Agent (`AgentExecutor`) built using `create_openai_tools_agent`. This agent orchestrates the process of handling natural language queries for the EU Open Data Portal using specialized tools.

### Workflow Steps (Agent Internal Logic - Guided by Prompt):

1.  **Parse Input:** The agent receives the natural language query.
2.  **Tool Selection (Generate):** The agent determines the need to generate a SPARQL query and selects the `generate_sparql_tool`.
    *   Input: Natural Language Query, Correction Context (from previous failed attempts, if any).
    *   Process: Calls the `generate_sparql_tool`, which uses the configured LLM (OpenAI `gpt-4o` with a 5s timeout) to generate SPARQL. Includes detailed logging of the attempt.
    *   Output: SPARQL query string or error message.
3.  **Tool Selection (Execute):** The agent receives the SPARQL query (or decides to execute a potentially problematic one based on warnings) and selects the `execute_sparql_tool`.
    *   Input: Generated SPARQL query string.
    *   Process: Calls `execute_sparql_tool`, which runs the query against the EU Open Data Portal endpoint via HTTP request (with a 5s timeout). Includes detailed logging of the execution attempt and outcome.
    *   Output: JSON results dictionary or error message string (e.g., timeout, HTTP error, JSON error).
4.  **Result/Error Analysis (Agent Internal Logic):**
    *   Trigger: Receives output from `execute_sparql_tool`.
    *   Process: Based on the system prompt, the agent analyzes the result:
        *   **Execution Error:** Identifies the error message. Considers retrying generation (Step 2) with context about the error. Limits retries.
        *   **No Results:** Identifies empty `bindings`. Considers retrying generation (Step 2) with context suggesting broader terms. Limits retries.
        *   **Successful Results:** Analyzes metadata within the JSON bindings (relevance, coverage, constraints). Hypothesizes linking if appropriate.
    *   Constraint: Relies on the agent's LLM reasoning guided by the prompt.
5.  **Final Synthesis (Agent Internal Logic):**
    *   Input: Analysis of successful results (or conclusion from failed attempts).
    *   Process: The agent formulates the final natural language answer based on its analysis, summarizing findings, explaining relevance, mentioning linking (if applicable), and acknowledging limitations (including potential impact of timeouts).
    *   Output: Final answer string provided in the `AgentExecutor` response.

### Key Characteristics:

-   **Agent-Driven Orchestration:** The Langchain `AgentExecutor` manages the Chain-of-Thought reasoning, tool selection, execution, and state based on the LLM's interpretation of the prompt and tool outputs. `verbose=False` is set on the executor to prevent duplicate console output, as custom logging is implemented.
-   **Tool-Based Functionality:** Core tasks (SPARQL generation, execution) are encapsulated in distinct `@tool`-decorated functions.
-   **Structured Logging:** The script implements detailed logging using Python's `logging` module. Every run creates a timestamped log file in the `logs/` directory, capturing inputs, tool calls, generated SPARQL, execution results/errors, and final agent outputs. Standard output logging is also maintained.
-   **API Timeouts:** Aggressive 5-second timeouts are configured for both the LLM calls (`ChatOpenAI`) and the SPARQL endpoint requests (`requests.get`). This may impact reliability for complex operations.
-   **Self-Correction:** Relies on the agent's prompt-guided reasoning to retry steps with added context upon encountering errors or empty results.

## Previous Pattern: Manual Chain-of-Thought (Deprecated)

-   The system previously used a manually coded function (`answer_complex_query`) to orchestrate LLM calls and logic flow. This has been replaced by the Langchain Agent pattern.