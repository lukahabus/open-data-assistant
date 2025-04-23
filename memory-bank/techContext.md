# Tech Context: Open Data Assistant

## Core Technologies

-   **Language:** Python 3
-   **LLM Interaction:** `langchain_openai` (`ChatOpenAI` with `gpt-4o`, 5s timeout)
-   **Agent Framework:** `langchain` (`AgentExecutor`, `create_openai_tools_agent`)
-   **HTTP Requests:** `requests` library (for executing SPARQL queries, 5s timeout)
-   **SPARQL Endpoint:** EU Open Data Portal (`https://data.europa.eu/sparql`)
-   **Logging:** Python standard `logging` module.

## Key Libraries & Dependencies

Refer to `requirements.txt` for a full list. Key active libraries include:

-   `openai`: Underlying library for LLM interaction (via Langchain).
-   `langchain`, `langchain-openai`: Core agent framework and OpenAI integration.
-   `requests`: For sending SPARQL queries to the endpoint.
-   `json`: For handling SPARQL results.
-   `re`: For basic text manipulation (cleaning LLM output).
-   `logging`, `datetime`: For structured, timestamped logging to files.
-   `os`: For basic OS interactions (creating log directory).

## Planned/Intended Technologies

-   **Langchain Framework:** (`langchain`, `langchain-openai`, `langchain-community`) Intended for refactoring the core logic to use Agents or Chains for more robust Chain-of-Thought execution, tool management, and potentially improved prompt engineering and self-correction. The refactoring attempt was made but not successfully applied via the AI assistant tool.

## Development Environment

-   Assumed standard Python environment.
-   API keys (e.g., `OPENAI_API_KEY`) should be managed securely (e.g., via environment variables).
-   Creates a `logs/` directory in the workspace root to store runtime logs.

## Technical Constraints

-   Reliant on the EU Open Data Portal SPARQL endpoint availability and performance.
-   Dependent on OpenAI API availability and performance.
-   **Aggressive Timeouts:** The configured 5-second timeouts for both OpenAI API calls and SPARQL endpoint requests may lead to failures for complex queries, slow network conditions, or during high load on the external services.
-   SPARQL query complexity and execution time limits imposed by the endpoint (independent of the client-side timeout).
-   LLM context window limitations when analyzing large SPARQL results (though currently results are not truncated before returning from the tool).
-   LLM prompt effectiveness for SPARQL generation and agent reasoning. 