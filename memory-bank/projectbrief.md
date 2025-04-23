# Project Brief: Open Data Assistant

## Core Goal

To develop an intelligent assistant capable of understanding natural language questions and translating them into effective SPARQL queries to retrieve relevant dataset information from the EU Open Data Portal.

## Key Objectives

1.  **Natural Language Understanding:** Accurately interpret user queries related to finding datasets on the EU Open Data Portal.
2.  **SPARQL Generation:** Generate syntactically correct and semantically relevant SPARQL queries based on the user's intent.
3.  **Data Retrieval:** Execute SPARQL queries against the EU Open Data Portal endpoint.
4.  **Result Analysis & Synthesis:** Analyze the metadata retrieved via SPARQL to identify the most relevant datasets, potentially hypothesizing how multiple datasets could be combined.
5.  **Self-Correction:** Implement mechanisms to handle failures in SPARQL generation or execution, allowing the system to retry with modifications.
6.  **User Interface:** (Future Goal) Provide a user-friendly interface for interaction.

## Scope

-   Focus on dataset discovery and metadata analysis from the EU Open Data Portal.
-   Initial implementation targets generating and executing SPARQL, analyzing results using LLMs, and providing a synthesized natural language answer about relevant datasets.
-   Does not initially include downloading or performing complex analysis on the *contents* of the datasets themselves, but focuses on identifying *which* datasets are relevant. 