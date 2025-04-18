import openai
import json
import re
import requests

# Set up the OpenAI client
client = openai.OpenAI()

# --- SPARQL Query Generation Function ---


def generate_sparql_query(nl_query):
    """Generates a SPARQL query using OpenAI based on a natural language query."""
    # Prompt for the LLM to generate a SPARQL query
    sparql_prompt = f"""
    Given the natural language query: "{nl_query}"

    Generate a SPARQL query for the EU Open Data Portal (https://data.europa.eu/data/sparql) to find relevant datasets.
    - Use standard prefixes like `dct:` (<http://purl.org/dc/terms/>) and `dcat:` (<http://www.w3.org/ns/dcat#>).
    - If you use XML Schema datatypes (like `xsd:date`), include `PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>`.
    - If you use Friend of a Friend terms (like `foaf:name` for publisher names), include `PREFIX foaf: <http://xmlns.com/foaf/0.1/>`.
    - Look for datasets (`?dataset a dcat:Dataset`).
    - Extract relevant information requested in the query (e.g., title, description, date, URL).
    - Filter based on keywords, dates, publishers, formats etc. mentioned in the query.
    - Use `dcat:keyword` for tags/keywords.
    - Use `dct:issued` for publication date.
    - Use `dct:publisher` for the publisher. To filter by publisher *name*, link the publisher variable (e.g., `?publisher`) to its `foaf:name`.
    - Use `dcat:distribution` to link to distributions and check `dct:format` or `dcat:mediaType`.
    - Use FILTER with CONTAINS, REGEX, or comparison operators (e.g., >= for dates, requiring `xsd:date`).
    - **Important:** When using functions like `CONTAINS` or `REGEX` for case-insensitive filtering on potentially non-string variables (like keywords or formats), always cast the variable to a string first using `STR()` and then apply `LCASE()`. For example: `FILTER(CONTAINS(LCASE(STR(?keyword)), "searchterm"))`.
    - Add a LIMIT clause (e.g., LIMIT 10) to keep the results manageable.

    Return *only* the raw SPARQL query string, without any explanations or formatting like ```sparql ... ```.

    SPARQL Query:
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that generates SPARQL queries based on a natural language question for the EU Open Data Portal.",
                },
                {"role": "user", "content": sparql_prompt},
            ],
            max_tokens=400,
            temperature=0.2,
        )
        generated_query = response.choices[0].message.content.strip()

        # Clean up potential markdown code fences
        generated_query = re.sub(
            r"^```sparql\s*", "", generated_query, flags=re.IGNORECASE
        )
        generated_query = re.sub(r"\s*```$", "", generated_query)
        return generated_query

    except Exception as e:
        print(f"\n--- Error generating SPARQL for query: '{nl_query}' ---")
        print(f"Error: {e}")
        return "# Error generating query. Fallback not implemented in this example generator."  # Simple error message


# --- Example Natural Language Queries ---

example_nl_queries = [
    "Find datasets about climate change tagged with 'environment'. Retrieve their titles and descriptions.",
    "Show me datasets about transport published since the beginning of 2023. Include their title and publication date.",
    "List datasets published by the European Environment Agency, showing their title and landing page.",
    "I need datasets about 'health' that are available in CSV format. Give me their titles and download URLs if available.",
]

# --- Generate and Print Examples ---

print("--- Generating SPARQL Query Examples ---")

for i, nl_query in enumerate(example_nl_queries):
    print(f"\nExample {i+1}:\n")
    print(f"Natural Language Query:")
    print(f"{nl_query}")
    print("Generated SPARQL Query:")
    sparql_query = generate_sparql_query(nl_query)
    print(sparql_query)
    print("----------------------------------------")


# --- SPARQL Endpoint Call (REMOVED) ---
# The following code block that executed the query has been removed.
