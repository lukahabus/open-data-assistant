# Tech Context: Open Data Assistant

## Core Technologies

-   **Language:** Python 3
-   **LLM Interaction:** `openai` library (currently using direct API calls via `client.chat.completions.create` with `gpt-4o`)
-   **HTTP Requests:** `requests` library (for executing SPARQL queries)
-   **SPARQL Endpoint:** EU Open Data Portal (`https://data.europa.eu/sparql`)

## Key Libraries & Dependencies

Refer to `requirements.txt` for a full list. Key active libraries include:

-   `openai`: For all LLM interactions (SPARQL generation, analysis).
-   `requests`: For sending SPARQL queries to the endpoint.
-   `json`: For handling SPARQL results and LLM JSON responses.
-   `re`: For basic text manipulation (cleaning LLM output).

## Planned/Intended Technologies

-   **Langchain Framework:** (`langchain`, `langchain-openai`, `langchain-community`) Intended for refactoring the core logic to use Agents or Chains for more robust Chain-of-Thought execution, tool management, and potentially improved prompt engineering and self-correction. The refactoring attempt was made but not successfully applied via the AI assistant tool.

## Development Environment

-   Assumed standard Python environment.
-   API keys (e.g., `OPENAI_API_KEY`) should be managed securely (e.g., via environment variables, potentially using `python-dotenv`).

## Technical Constraints

-   Reliant on the EU Open Data Portal SPARQL endpoint availability and performance.
-   Dependent on OpenAI API availability and performance.
-   SPARQL query complexity and execution time limits imposed by the endpoint.
-   LLM context window limitations when analyzing large SPARQL results.
-   LLM prompt effectiveness for SPARQL generation and analysis. 