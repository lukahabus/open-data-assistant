import os
import sys
import json
from dotenv import load_dotenv

# --- Environment Setup ---
# Load environment variables (expects OPENAI_API_KEY in .env file)
load_dotenv()

# Add parent directory to sys.path to allow importing from 'dcat'
current_dir = os.path.dirname(os.path.abspath(__file__))
# Assuming this script is in the root, the 'dcat' directory is a subdirectory
# If run_sparql_example.py is elsewhere, adjust path logic accordingly
# For now, assume 'dcat' is directly accessible or the parent logic works if needed.
# Simplified: We assume the script is run from the workspace root where 'dcat' exists.
# Ensure the 'dcat' package is importable
# If 'dcat' is not in the root, adjust sys.path:
# parent_dir = os.path.dirname(current_dir) # Use this if script is inside another folder
# if parent_dir not in sys.path:
#     sys.path.insert(0, parent_dir)

try:
    from dcat.dcat_assistant import DCATAssistant

    # DCATEmbedder is needed for DCATAssistant's __init__ signature
    from dcat.dcat_embedding import DCATEmbedder
except ImportError as e:
    print(f"Error importing DCAT modules: {e}")
    print(
        "Please ensure the script is run from the project root directory containing the 'dcat' folder,"
    )
    print("and that all dependencies are installed.")
    sys.exit(1)

# --- Dummy Embedder for Demonstration ---
# In a real scenario, you would initialize DCATEmbedder like this:
# dcat_embedder = DCATEmbedder(openai_api_key=os.getenv("OPENAI_API_KEY"))
# dcat_embedder.embed_catalog(catalog_data) # where catalog_data is your loaded DCAT data


class DummyEmbedder:
    """A placeholder class mimicking DCATEmbedder for instantiation purposes."""

    vector_store = None

    # Add methods expected by DCATAssistant if they were called before SPARQL
    def get_dataset_by_id(self, dataset_id):
        return None

    def find_related_datasets(self, dataset_id, k=3):
        return []

    def semantic_search(self, query, k=5):
        return []

    # Add any other methods DCATAssistant might potentially call internally if needed


# --- Instantiate the Assistant ---
# IMPORTANT: Replace DummyEmbedder with your actual, initialized dcat_embedder instance
#            when integrating into your full application.
try:
    # Check if API key is available for ChatOpenAI initialization within DCATAssistant
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError(
            "OPENAI_API_KEY not found in environment variables. Please set it in a .env file."
        )

    assistant = DCATAssistant(dcat_embedder=DummyEmbedder())
except ValueError as ve:
    print(f"Initialization Error: {ve}")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred during DCATAssistant initialization: {e}")
    sys.exit(1)

# --- SPARQL Query Execution ---

# 1. Define the SPARQL Endpoint URL
# Example: Wikidata's public SPARQL endpoint
sparql_endpoint_url = "https://query.wikidata.org/sparql"

# 2. Define the SPARQL Query
# Example: Find streets in Zagreb (Q1435) named after people (Q5)
# (Modified from the original painter-specific query)
sparql_query = """
SELECT ?streetLabel ?personLabel WHERE {
  ?street wdt:P131 wd:Q1435.  # ?street is located in (P131) Zagreb (Q1435)
  ?street wdt:P138 ?person.  # ?street is named after (P138) ?person
  ?person wdt:P31 wd:Q5.     # ?person is an instance of (P31) human (Q5)

  # Fetch labels in Croatian or English
  SERVICE wikibase:label { bd:serviceParam wikibase:language "hr,en". }
}
LIMIT 15 # Limit results for brevity
"""

# 3. Execute the query using the assistant's method
print("=" * 40)
print("Example 1: Finding streets in Zagreb named after people")
print("=" * 40)
print(f"Executing SPARQL query against: {sparql_endpoint_url}")
results = assistant.execute_sparql_query(sparql_endpoint_url, sparql_query)

# 4. Print the results
if isinstance(results, str):
    # Handle error message
    print(f"\nSPARQL Query Failed:\n{results}")
else:
    # Process successful results (dictionary format)
    print("\nSPARQL Query Results (JSON):")
    # Pretty print the JSON results
    print(
        json.dumps(results, indent=2, ensure_ascii=False)
    )  # ensure_ascii=False for non-Latin characters

    # Example of extracting specific data:
    print("\nList of Streets and People:")
    bindings = results.get("results", {}).get("bindings", [])
    if not bindings:
        print("No results found.")
    else:
        for item in bindings:
            street_name = item.get("streetLabel", {}).get("value", "N/A")
            person_name = item.get("personLabel", {}).get(
                "value", "N/A"
            )  # Changed from painterLabel
            print(f"- Street: {street_name}, Named After: {person_name}")

# --- Example 2: Capitals of countries bordering Croatia ---
print("\n" + "=" * 40)
print("Example 2: Finding capitals of countries bordering Croatia")
print("=" * 40)

sparql_query_borders = """
SELECT ?countryLabel ?capitalLabel WHERE {
  wd:Q224 wdt:P47 ?country. # Croatia shares border with ?country
  ?country wdt:P31 wd:Q6256. # ?country is a sovereign state
  ?country wdt:P36 ?capital. # ?country has capital ?capital

  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
ORDER BY ?countryLabel
"""

print(f"Executing SPARQL query against: {sparql_endpoint_url}")
results_borders = assistant.execute_sparql_query(
    sparql_endpoint_url, sparql_query_borders
)

if isinstance(results_borders, str):
    print(f"\nSPARQL Query Failed:\n{results_borders}")
else:
    print("\nSPARQL Query Results (JSON):")
    print(json.dumps(results_borders, indent=2, ensure_ascii=False))
    print("\nList of Countries and Capitals:")
    bindings = results_borders.get("results", {}).get("bindings", [])
    if not bindings:
        print("No results found.")
    else:
        for item in bindings:
            country_name = item.get("countryLabel", {}).get("value", "N/A")
            capital_name = item.get("capitalLabel", {}).get("value", "N/A")
            print(f"- Country: {country_name}, Capital: {capital_name}")


# --- Example 3: Museums in Zagreb ---
print("\n" + "=" * 40)
print("Example 3: Finding museums in Zagreb")
print("=" * 40)

sparql_query_museums = """
SELECT ?museumLabel WHERE {
  ?museum wdt:P131 wd:Q1435;   # ?museum is located in (P131) Zagreb (Q1435)
          wdt:P31 wd:Q33506;   # ?museum is an instance of (P31) museum (Q33506)
          rdfs:label ?label.  # Get the label directly

  FILTER(LANG(?label) IN ("hr", "en")) # Filter for Croatian or English labels

  # Prefer Croatian label, fallback to English
  OPTIONAL { ?museum rdfs:label ?hrLabel FILTER (LANG(?hrLabel) = "hr") }
  OPTIONAL { ?museum rdfs:label ?enLabel FILTER (LANG(?enLabel) = "en") }
  BIND(COALESCE(?hrLabel, ?enLabel) AS ?museumLabel)

  FILTER(BOUND(?museumLabel) && STR(?museumLabel) != "")
}
ORDER BY ?museumLabel
LIMIT 20 # Limit results
"""

print(f"Executing SPARQL query against: {sparql_endpoint_url}")
results_museums = assistant.execute_sparql_query(
    sparql_endpoint_url, sparql_query_museums
)

if isinstance(results_museums, str):
    print(f"\nSPARQL Query Failed:\n{results_museums}")
else:
    print("\nSPARQL Query Results (JSON):")
    print(json.dumps(results_museums, indent=2, ensure_ascii=False))
    print("\nList of Museums in Zagreb:")
    bindings = results_museums.get("results", {}).get("bindings", [])
    if not bindings:
        print("No results found.")
    else:
        for item in bindings:
            museum_name = item.get("museumLabel", {}).get("value", "N/A")
            print(f"- {museum_name}")


# --- Example 4: Mountains in Croatia ---
print("\n" + "=" * 40)
print("Example 4: Finding mountains in Croatia")
print("=" * 40)

sparql_query_mountains = """
SELECT ?mountainLabel WHERE {
  ?mountain wdt:P31 wd:Q8502;    # ?mountain is an instance of mountain
            wdt:P17 wd:Q224;    # and is located in Croatia
            rdfs:label ?label.  # Get the label directly

  FILTER(LANG(?label) IN ("hr", "en")) # Filter for Croatian or English labels

  # Prefer Croatian label, fallback to English
  OPTIONAL { ?mountain rdfs:label ?hrLabel FILTER (LANG(?hrLabel) = "hr") }
  OPTIONAL { ?mountain rdfs:label ?enLabel FILTER (LANG(?enLabel) = "en") }
  BIND(COALESCE(?hrLabel, ?enLabel) AS ?mountainLabel)

  FILTER(BOUND(?mountainLabel) && STR(?mountainLabel) != "")
}
ORDER BY ?mountainLabel
LIMIT 20
"""

print(f"Executing SPARQL query against: {sparql_endpoint_url}")
results_mountains = assistant.execute_sparql_query(
    sparql_endpoint_url, sparql_query_mountains
)

if isinstance(results_mountains, str):
    print(f"\nSPARQL Query Failed:\n{results_mountains}")
else:
    print("\nSPARQL Query Results (JSON):")
    print(json.dumps(results_mountains, indent=2, ensure_ascii=False))
    print("\nList of Mountains in Croatia:")
    bindings = results_mountains.get("results", {}).get("bindings", [])
    if not bindings:
        print("No results found.")
    else:
        for item in bindings:
            mountain_name = item.get("mountainLabel", {}).get("value", "N/A")
            print(f"- {mountain_name}")


# --- Example 5: Universities in Croatia ---
print("\n" + "=" * 40)
print("Example 5: Finding universities in Croatia")
print("=" * 40)

sparql_query_universities = """
SELECT ?universityLabel WHERE {
  ?university wdt:P31 wd:Q3918;   # ?university is an instance of university
              wdt:P17 wd:Q224;   # and is located in Croatia
              rdfs:label ?label. # Get the label directly

  FILTER(LANG(?label) IN ("hr", "en")) # Filter for Croatian or English labels

  # Prefer Croatian label, fallback to English
  OPTIONAL { ?university rdfs:label ?hrLabel FILTER (LANG(?hrLabel) = "hr") }
  OPTIONAL { ?university rdfs:label ?enLabel FILTER (LANG(?enLabel) = "en") }
  BIND(COALESCE(?hrLabel, ?enLabel) AS ?universityLabel)

  FILTER(BOUND(?universityLabel) && STR(?universityLabel) != "")
}
ORDER BY ?universityLabel
LIMIT 20
"""

print(f"Executing SPARQL query against: {sparql_endpoint_url}")
results_universities = assistant.execute_sparql_query(
    sparql_endpoint_url, sparql_query_universities
)

if isinstance(results_universities, str):
    print(f"\nSPARQL Query Failed:\n{results_universities}")
else:
    print("\nSPARQL Query Results (JSON):")
    print(json.dumps(results_universities, indent=2, ensure_ascii=False))
    print("\nList of Universities in Croatia:")
    bindings = results_universities.get("results", {}).get("bindings", [])
    if not bindings:
        print("No results found.")
    else:
        for item in bindings:
            university_name = item.get("universityLabel", {}).get("value", "N/A")
            print(f"- {university_name}")


# --- Example 6: Rivers in Croatia ---
print("\n" + "=" * 40)
print("Example 6: Finding rivers in Croatia")
print("=" * 40)

sparql_query_rivers = """
SELECT ?riverLabel WHERE {
  ?river wdt:P31 wd:Q4022;    # ?river is an instance of river
         wdt:P17 wd:Q224;    # and is located in Croatia
         rdfs:label ?label.  # Get the label directly

  FILTER(LANG(?label) IN ("hr", "en")) # Filter for Croatian or English labels

  # Prefer Croatian label, fallback to English
  OPTIONAL { ?river rdfs:label ?hrLabel FILTER (LANG(?hrLabel) = "hr") }
  OPTIONAL { ?river rdfs:label ?enLabel FILTER (LANG(?enLabel) = "en") }
  BIND(COALESCE(?hrLabel, ?enLabel) AS ?riverLabel)

  # Ensure we only get results with a non-empty chosen label
  FILTER(BOUND(?riverLabel) && STR(?riverLabel) != "")
}
ORDER BY ?riverLabel
LIMIT 20
"""

print(f"Executing SPARQL query against: {sparql_endpoint_url}")
results_rivers = assistant.execute_sparql_query(
    sparql_endpoint_url, sparql_query_rivers
)

if isinstance(results_rivers, str):
    print(f"\nSPARQL Query Failed:\n{results_rivers}")
else:
    print("\nSPARQL Query Results (JSON):")
    print(json.dumps(results_rivers, indent=2, ensure_ascii=False))
    print("\nList of Rivers in Croatia:")
    bindings = results_rivers.get("results", {}).get("bindings", [])
    if not bindings:
        print("No results found.")
    else:
        for item in bindings:
            river_name = item.get("riverLabel", {}).get("value", "N/A")
            print(f"- {river_name}")


# --- Example 7: Theaters in Zagreb ---
print("\n" + "=" * 40)
print("Example 7: Finding theaters in Zagreb")
print("=" * 40)

sparql_query_theaters = """
SELECT ?theaterLabel WHERE {
  ?theater wdt:P31 wd:Q24354;    # ?theater is an instance of theater
           wdt:P131 wd:Q1435;   # and is located in Zagreb
           rdfs:label ?label.   # Get the label directly

  FILTER(LANG(?label) IN ("hr", "en")) # Filter for Croatian or English labels

  # Prefer Croatian label, fallback to English
  OPTIONAL { ?theater rdfs:label ?hrLabel FILTER (LANG(?hrLabel) = "hr") }
  OPTIONAL { ?theater rdfs:label ?enLabel FILTER (LANG(?enLabel) = "en") }
  BIND(COALESCE(?hrLabel, ?enLabel) AS ?theaterLabel)

  FILTER(BOUND(?theaterLabel) && STR(?theaterLabel) != "")
}
ORDER BY ?theaterLabel
LIMIT 20
"""

print(f"Executing SPARQL query against: {sparql_endpoint_url}")
results_theaters = assistant.execute_sparql_query(
    sparql_endpoint_url, sparql_query_theaters
)

if isinstance(results_theaters, str):
    print(f"\nSPARQL Query Failed:\n{results_theaters}")
else:
    print("\nSPARQL Query Results (JSON):")
    print(json.dumps(results_theaters, indent=2, ensure_ascii=False))
    print("\nList of Theaters in Zagreb:")
    bindings = results_theaters.get("results", {}).get("bindings", [])
    if not bindings:
        print("No results found.")
    else:
        for item in bindings:
            theater_name = item.get("theaterLabel", {}).get("value", "N/A")
            print(f"- {theater_name}")

"""
# --- Example 8: Attempting a complex/subjective query with the LLM ---
# NOTE: This type of query is problematic due to subjectivity, privacy concerns,
# data limitations, and ethical considerations, as explained previously.
# It is highly likely the assistant will refuse or be unable to answer accurately.
# The DummyEmbedder also limits the assistant's capabilities.
print("\n" + "="*40)
print("Example 8: Asking the assistant (LLM) a complex/subjective query")
print("="*40)

natural_language_query = (
    "Give me a list of controversial business owners living near high ranking judges."
)

print(f"Sending query to assistant: '{natural_language_query}'")

# Assuming DCATAssistant has a method like 'process_query' to handle natural language.
# The actual method name might differ based on the class implementation.
try:
    # Replace 'process_query' with the actual method name if it's different
    llm_response = assistant.process_query(natural_language_query)
    print("\nAssistant's Response:")
    print(llm_response)
except AttributeError:
    print(
        "\nError: The assumed method 'process_query' does not exist on DCATAssistant."
    )
    print(
        "Please check the DCATAssistant class definition for the correct method to interact with the LLM."
    )
except Exception as e:
    print(f"\nAn unexpected error occurred while querying the assistant: {e}")
"""

print("\nScript finished.")
