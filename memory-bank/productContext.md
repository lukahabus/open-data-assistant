# Product Context: Open Data Assistant

## Problem Solved

Finding relevant datasets on large open data portals like the EU Open Data Portal can be challenging. Users may not know SPARQL or the specific structure (ontologies, predicates) used by the portal. Standard keyword searches can be insufficient for complex queries involving multiple criteria or the need to combine information conceptually from different datasets.

This assistant aims to bridge the gap between a user's natural language question about data needs and the technical process of finding relevant datasets via SPARQL.

## How it Should Work (User Perspective)

1.  The user asks a question in natural language (e.g., "Find datasets about air quality and traffic in Paris since 2020").
2.  The assistant processes the request.
3.  The assistant provides a response summarizing the most relevant datasets found, potentially explaining how they relate to the query and if/how they might be combined. The response should include pointers (like titles or URIs) to the datasets.

## User Experience Goals

-   **Accessibility:** Allow users without SPARQL knowledge to query the data portal effectively.
-   **Relevance:** Provide results highly relevant to the user's stated information need.
-   **Clarity:** Present findings in an understandable natural language format.
-   **Transparency (Conceptual):** While hiding SPARQL complexity, the explanation should give the user confidence in the results (e.g., by mentioning the datasets considered). 