# System Patterns: Open Data Assistant

## Core Pattern: Manual Chain-of-Thought (CoT) Orchestration

The current system (`sparql.py`) employs a manually implemented Chain-of-Thought process to handle natural language queries for the EU Open Data Portal. This pattern uses direct calls to an LLM (OpenAI `gpt-4o`) for different stages of analysis and decision-making.

### Workflow Steps (`answer_complex_query` function):

1.  **SPARQL Generation:**
    *   Input: Natural Language Query, Correction Context (optional).
    *   Process: Calls `generate_sparql_query`, which uses the LLM to generate a SPARQL query targeting dataset metadata.
    *   Output: SPARQL query string or None.
2.  **SPARQL Execution:**
    *   Input: Generated SPARQL query string.
    *   Process: Calls `execute_sparql_query` to run the query against the EU Open Data Portal endpoint via HTTP request.
    *   Output: JSON results dictionary or None (on error).
3.  **Self-Correction (Query Generation/Execution):**
    *   Trigger: `execute_sparql_query` returns None (execution error) or empty results.
    *   Process:
        *   Calls `analyse_with_llm` (type `self_correction_context`) providing the failed query and error type.
        *   LLM analyzes the failure and suggests context for the *next* generation attempt (e.g., "check prefixes", "broaden terms").
        *   The orchestrator loops back to Step 1 (SPARQL Generation) with the new context.
    *   Constraint: Limited number of retries (`max_retries`).
4.  **Metadata Analysis & Candidate Selection:**
    *   Input: Successful SPARQL results (JSON).
    *   Process: Calls `analyse_with_llm` (type `metadata`) to have the LLM analyze the relevance, coverage, and linking potential of the datasets found in the results. The LLM selects candidate datasets and suggests the next step.
    *   Output: JSON object containing analysis summary, candidate list, and next step suggestion.
5.  **Self-Correction (Candidate Selection):**
    *   Trigger: Metadata analysis finds no suitable candidates.
    *   Process: Loops back to Step 1 (SPARQL Generation) with context instructing the generator to refine the search based on the LLM's reasoning for rejection.
    *   Constraint: Limited retries.
6.  **Linking Hypothesis (Optional):**
    *   Input: Metadata analysis result (if multiple candidates selected and linking suggested).
    *   Process: Calls `analyse_with_llm` (type `linking_hypothesis`) for the LLM to propose how candidates might be linked based on metadata and assess feasibility.
    *   Output: JSON object with linking dimensions, logic, feasibility.
7.  **Self-Correction (Linking Feasibility):**
    *   Trigger: Linking analysis suggests low feasibility or recommends refining the search.
    *   Process: Loops back to Step 1 (SPARQL Generation) with context instructing the generator to search specifically for better linkable datasets.
    *   Constraint: Limited retries.
8.  **Final Synthesis:**
    *   Input: Metadata analysis, linking hypothesis (if generated).
    *   Process: Calls `analyse_with_llm` (type `final_synthesis`) for the LLM to construct the final natural language answer, summarizing findings, explaining the plan/result, and noting limitations.
    *   Output: JSON object containing the synthesized answer.

### Key Characteristics:

-   **Explicit Orchestration:** The control flow, retries, and calls to LLM analysis are explicitly coded in the `answer_complex_query` function.
-   **Specialized LLM Calls:** Uses distinct prompts and calls to the `analyse_with_llm` function for different analysis tasks (metadata, linking, self-correction, synthesis), requesting structured JSON output.
-   **State Management:** Relies on variables within the orchestrator function to pass context between steps (e.g., `context_for_generation`, `metadata_analysis`).

## Planned Pattern: Langchain Agent

-   The intention is to refactor the manual CoT orchestration into a Langchain Agent.
-   This would involve defining tools (`generate_sparql_tool`, `execute_sparql_tool`) and crafting a system prompt for the agent that encapsulates the desired workflow, analysis steps, and self-correction logic.
-   The agent framework would handle the CoT reasoning, tool invocation, and state management internally.
-   *(Status: Refactoring attempt made but not successfully applied via AI assistant tooling).* 