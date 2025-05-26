import chromadb
import json
import logging
import os
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import requests
from sentence_transformers import SentenceTransformer
from dataclasses import dataclass
import hashlib

# Langchain imports
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()


@dataclass
class QueryExample:
    """Represents a question-query pair example"""

    question: str
    sparql_query: str
    endpoint: str
    description: str = ""
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class SchemaInfo:
    """Represents schema information about a dataset/endpoint"""

    endpoint: str
    classes: List[Dict[str, Any]]
    properties: List[Dict[str, Any]]
    void_description: Dict[str, Any]


class RAGSystem:
    """
    Retrieval-Augmented Generation system for SPARQL query generation
    Based on the research paper: LLM-based SPARQL Query Generation from Natural Language over Federated Knowledge Graphs
    """

    def __init__(
        self,
        chroma_persist_directory: str = "./vector_store",
        embedding_model: str = "all-MiniLM-L6-v2",
        llm_model: str = "gpt-4o",
    ):

        self.chroma_persist_directory = chroma_persist_directory
        self.embedding_model_name = embedding_model
        self.llm_model = llm_model

        # Initialize logging
        self.logger = logging.getLogger(__name__)

        # Initialize embedding model
        self.embedding_model = SentenceTransformer(embedding_model)

        # Initialize LLM
        self.llm = ChatOpenAI(model=llm_model, temperature=0.1, request_timeout=60)

        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path=chroma_persist_directory)

        # Create collections for different types of data
        self.query_examples_collection = self._get_or_create_collection(
            "query_examples"
        )
        self.schema_collection = self._get_or_create_collection("schema_info")
        self.endpoint_metadata_collection = self._get_or_create_collection(
            "endpoint_metadata"
        )

        # EU Open Data Portal endpoints
        self.sparql_endpoint = "https://data.europa.eu/sparql"
        self.api_endpoint = "https://data.europa.eu/api/hub/search/search"

        self.logger.info(
            f"RAG System initialized with embedding model: {embedding_model}"
        )

    def _get_or_create_collection(self, name: str):
        """Get or create a ChromaDB collection"""
        try:
            return self.chroma_client.get_collection(name)
        except:
            return self.chroma_client.create_collection(name)

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for given text"""
        return self.embedding_model.encode(text).tolist()

    def _create_document_id(self, content: str) -> str:
        """Create a unique document ID based on content hash"""
        return hashlib.md5(content.encode()).hexdigest()

    def add_query_example(self, example: QueryExample) -> str:
        """Add a query example to the vector store"""
        doc_id = self._create_document_id(f"{example.question}_{example.sparql_query}")

        # Generate embedding for the question
        embedding = self._generate_embedding(example.question)

        # Store in ChromaDB
        self.query_examples_collection.add(
            documents=[example.question],
            embeddings=[embedding],
            metadatas=[
                {
                    "sparql_query": example.sparql_query,
                    "endpoint": example.endpoint,
                    "description": example.description,
                    "tags": json.dumps(example.tags),
                    "added_at": datetime.now().isoformat(),
                }
            ],
            ids=[doc_id],
        )

        self.logger.info(f"Added query example with ID: {doc_id}")
        return doc_id

    def add_schema_info(self, schema: SchemaInfo) -> str:
        """Add schema information to the vector store"""
        # Create a text representation of the schema for embedding
        schema_text = f"Endpoint: {schema.endpoint}\n"
        schema_text += (
            f"Classes: {', '.join([cls.get('name', '') for cls in schema.classes])}\n"
        )
        schema_text += f"Properties: {', '.join([prop.get('name', '') for prop in schema.properties])}"

        doc_id = self._create_document_id(schema_text)
        embedding = self._generate_embedding(schema_text)

        self.schema_collection.add(
            documents=[schema_text],
            embeddings=[embedding],
            metadatas=[
                {
                    "endpoint": schema.endpoint,
                    "classes": json.dumps(schema.classes),
                    "properties": json.dumps(schema.properties),
                    "void_description": json.dumps(schema.void_description),
                    "added_at": datetime.now().isoformat(),
                }
            ],
            ids=[doc_id],
        )

        self.logger.info(f"Added schema info for endpoint: {schema.endpoint}")
        return doc_id

    def retrieve_similar_examples(
        self, query: str, n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve similar query examples using vector similarity search"""
        query_embedding = self._generate_embedding(query)

        results = self.query_examples_collection.query(
            query_embeddings=[query_embedding], n_results=n_results
        )

        similar_examples = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                similar_examples.append(
                    {
                        "question": doc,
                        "sparql_query": metadata.get("sparql_query"),
                        "endpoint": metadata.get("endpoint"),
                        "description": metadata.get("description"),
                        "distance": (
                            results["distances"][0][i]
                            if results.get("distances")
                            else None
                        ),
                    }
                )

        return similar_examples

    def retrieve_relevant_schema(
        self, query: str, n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant schema information"""
        query_embedding = self._generate_embedding(query)

        results = self.schema_collection.query(
            query_embeddings=[query_embedding], n_results=n_results
        )

        schema_info = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                schema_info.append(
                    {
                        "schema_text": doc,
                        "endpoint": metadata.get("endpoint"),
                        "classes": json.loads(metadata.get("classes", "[]")),
                        "properties": json.loads(metadata.get("properties", "[]")),
                        "void_description": json.loads(
                            metadata.get("void_description", "{}")
                        ),
                        "distance": (
                            results["distances"][0][i]
                            if results.get("distances")
                            else None
                        ),
                    }
                )

        return schema_info

    def build_rag_prompt(self, user_query: str, context: str = "") -> str:
        """Build an enhanced prompt using RAG with similar examples and schema info"""

        # Retrieve similar examples and schema
        similar_examples = self.retrieve_similar_examples(user_query, n_results=3)
        schema_info = self.retrieve_relevant_schema(user_query, n_results=2)

        # Build the enhanced prompt
        prompt = f"""
        Given the natural language query: "{user_query}"
        {f"Additional context: {context}" if context else ""}

        You are generating a SPARQL query for the EU Open Data Portal ({self.sparql_endpoint}).
        Use the following similar examples and schema information to guide your generation:

        ## Similar Query Examples:
        """

        for i, example in enumerate(similar_examples):
            prompt += f"""
        Example {i+1}:
        Question: {example['question']}
        SPARQL Query:
        {example['sparql_query']}
        """

        prompt += """
        ## Schema Information:
        """

        for i, schema in enumerate(schema_info):
            prompt += f"""
        Schema {i+1} - Endpoint: {schema['endpoint']}
        Available Classes: {', '.join([cls.get('name', cls.get('uri', '')) for cls in schema['classes'][:10]])}
        Available Properties: {', '.join([prop.get('name', prop.get('uri', '')) for prop in schema['properties'][:15]])}
        """

        prompt += f"""
        
        ## Instructions:
        Generate a SPARQL query following these guidelines:
        
        1. **Target Dataset Discovery**: Focus on finding multiple relevant datasets (10-20 results)
        2. **Use Standard Prefixes**: 
           - dct: <http://purl.org/dc/terms/>
           - dcat: <http://www.w3.org/ns/dcat#>
           - foaf: <http://xmlns.com/foaf/0.1/>
           - skos: <http://www.w3.org/2004/02/skos/core#>
           - rdfs: <http://www.w3.org/2000/01/rdf-schema#>
           - xsd: <http://www.w3.org/2001/XMLSchema#>
        
        3. **Extract Dataset Information**:
           - Dataset URI (?dataset)
           - Title (dct:title)
           - Description (dct:description)
           - Publisher (dct:publisher -> foaf:name)
           - Landing page (dcat:landingPage)
           - Issue/modification dates (dct:issued, dct:modified)
        
        4. **Language Filtering**: Prioritize English metadata using LANGMATCHES
        
        5. **Use Flexible Text Search**: CONTAINS, REGEX with case-insensitive matching
        
        6. **Add LIMIT clause**: Set to around 15-20 results
        
        7. **Learn from Examples**: Follow the patterns shown in similar examples above
        
        Return ONLY the raw SPARQL query without any formatting or explanations.
        """

        return prompt

    def generate_sparql_with_rag(self, user_query: str, context: str = "") -> str:
        """Generate SPARQL query using RAG-enhanced prompting"""

        try:
            # Build RAG-enhanced prompt
            enhanced_prompt = self.build_rag_prompt(user_query, context)

            self.logger.info("Generating SPARQL with RAG enhancement...")

            # Call LLM with enhanced prompt
            response = self.llm.invoke([HumanMessage(content=enhanced_prompt)])
            generated_query = response.content.strip()

            # Clean up potential markdown formatting
            import re

            cleaned_query = re.sub(
                r"^```sparql\s*", "", generated_query, flags=re.IGNORECASE
            )
            cleaned_query = re.sub(r"\s*```$", "", cleaned_query)

            self.logger.info(
                f"Generated SPARQL query with RAG: {len(cleaned_query)} characters"
            )
            return cleaned_query

        except Exception as e:
            self.logger.error(f"Error generating SPARQL with RAG: {e}")
            return f"Error: Failed to generate SPARQL query with RAG. {e}"

    def validate_sparql_query(self, sparql_query: str) -> Tuple[bool, str]:
        """Validate SPARQL query by attempting to execute it with LIMIT 1"""

        try:
            # Create a validation version with LIMIT 1
            validation_query = sparql_query
            if "LIMIT" not in sparql_query.upper():
                validation_query += "\nLIMIT 1"
            elif "LIMIT" in sparql_query.upper():
                # Replace existing LIMIT with LIMIT 1
                import re

                validation_query = re.sub(
                    r"LIMIT\s+\d+", "LIMIT 1", sparql_query, flags=re.IGNORECASE
                )

            # Execute validation query
            headers = {"Accept": "application/sparql-results+json"}
            params = {"query": validation_query}

            response = requests.get(
                self.sparql_endpoint, headers=headers, params=params, timeout=10
            )

            if response.status_code == 200:
                results = response.json()
                return True, "Query syntax is valid"
            else:
                return False, f"HTTP {response.status_code}: {response.text[:200]}"

        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def populate_with_examples(self):
        """Populate the RAG system with predefined examples for EU Open Data Portal"""

        examples = [
            QueryExample(
                question="Find datasets about air quality in Germany",
                sparql_query="""PREFIX dct: <http://purl.org/dc/terms/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT DISTINCT ?dataset ?title ?description
WHERE {
  ?dataset a dcat:Dataset .
  ?dataset dct:title ?title .
  OPTIONAL { ?dataset dct:description ?description . }
  FILTER (
    CONTAINS(LCASE(STR(?title)), "air quality") ||
    (BOUND(?description) && CONTAINS(LCASE(STR(?description)), "air quality")) ||
    EXISTS { ?dataset dcat:keyword ?kw . FILTER(CONTAINS(LCASE(STR(?kw)), "air quality")) }
  )
  FILTER (
    CONTAINS(LCASE(STR(?title)), "germany") ||
    (BOUND(?description) && CONTAINS(LCASE(STR(?description)), "germany")) ||
    EXISTS { ?dataset dct:spatial ?spatialUri . OPTIONAL {?spatialUri skos:prefLabel ?spatialLabelEN . FILTER(LANGMATCHES(LANG(?spatialLabelEN), "en"))} OPTIONAL {?spatialUri rdfs:label ?spatialLabel .} FILTER(CONTAINS(LCASE(STR(?spatialLabelEN)), "germany") || CONTAINS(LCASE(STR(?spatialLabel)), "germany")) } ||
    EXISTS { ?dataset dcat:keyword ?kw_loc . FILTER(CONTAINS(LCASE(STR(?kw_loc)), "germany")) }
  )
  FILTER(LANGMATCHES(LANG(?title), "en") || LANG(?title) = "")
}
LIMIT 15""",
                endpoint=self.sparql_endpoint,
                description="Search for air quality datasets in Germany",
                tags=["air quality", "germany", "environment"],
            ),
            QueryExample(
                question="List datasets published by Eurostat concerning unemployment rates after 2020",
                sparql_query="""PREFIX dct: <http://purl.org/dc/terms/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT DISTINCT ?dataset ?title ?publisherName ?issuedDate
WHERE {
  ?dataset a dcat:Dataset .
  ?dataset dct:title ?title .
  ?dataset dct:publisher ?publisherOrg .
  ?publisherOrg foaf:name ?publisherName .
  OPTIONAL { ?dataset dct:issued ?issuedDate . }
  OPTIONAL { ?dataset dct:description ?description . }

  FILTER(CONTAINS(LCASE(STR(?publisherName)), "eurostat"))
  
  FILTER (
    CONTAINS(LCASE(STR(?title)), "unemployment") ||
    (BOUND(?description) && CONTAINS(LCASE(STR(?description)), "unemployment")) ||
    EXISTS { ?dataset dcat:keyword ?kw . FILTER(CONTAINS(LCASE(STR(?kw)), "unemployment")) }
  )
  
  FILTER(!BOUND(?issuedDate) || ?issuedDate > "2020-01-01"^^xsd:date)
  FILTER(LANGMATCHES(LANG(?title), "en") || LANG(?title) = "")
}
LIMIT 10""",
                endpoint=self.sparql_endpoint,
                description="Find unemployment datasets from Eurostat after 2020",
                tags=["eurostat", "unemployment", "statistics", "2020"],
            ),
            QueryExample(
                question="Find datasets in the Environment theme available in CSV format",
                sparql_query="""PREFIX dct: <http://purl.org/dc/terms/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT DISTINCT ?dataset ?title ?modifiedDate ?formatLabel
WHERE {
  ?dataset a dcat:Dataset .
  ?dataset dct:title ?title .
  OPTIONAL { ?dataset dct:modified ?modifiedDate . }

  ?dataset dcat:theme ?themeURI .
  ?themeURI skos:prefLabel ?themeLabel .
  FILTER(LANGMATCHES(LANG(?themeLabel), "en") && CONTAINS(LCASE(STR(?themeLabel)), "environment"))

  ?dataset dcat:distribution ?distribution .
  ?distribution dct:format <http://publications.europa.eu/resource/authority/file-type/CSV> .
  <http://publications.europa.eu/resource/authority/file-type/CSV> skos:prefLabel ?formatLabel .
  FILTER(LANGMATCHES(LANG(?formatLabel), "en") || LANG(?formatLabel) = "")

  FILTER(LANGMATCHES(LANG(?title), "en") || LANG(?title) = "")
}
LIMIT 15""",
                endpoint=self.sparql_endpoint,
                description="Find environment datasets in CSV format",
                tags=["environment", "CSV", "theme", "format"],
            ),
            QueryExample(
                question="Show datasets about COVID-19 published since 2020",
                sparql_query="""PREFIX dct: <http://purl.org/dc/terms/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT DISTINCT ?dataset ?title ?description ?issuedDate
WHERE {
  ?dataset a dcat:Dataset .
  ?dataset dct:title ?title .
  OPTIONAL { ?dataset dct:description ?description . }
  OPTIONAL { ?dataset dct:issued ?issuedDate . }
  
  FILTER (
    CONTAINS(LCASE(STR(?title)), "covid") ||
    CONTAINS(LCASE(STR(?title)), "coronavirus") ||
    (BOUND(?description) && (CONTAINS(LCASE(STR(?description)), "covid") || CONTAINS(LCASE(STR(?description)), "coronavirus"))) ||
    EXISTS { ?dataset dcat:keyword ?kw . FILTER(CONTAINS(LCASE(STR(?kw)), "covid") || CONTAINS(LCASE(STR(?kw)), "coronavirus")) }
  )
  
  FILTER(!BOUND(?issuedDate) || ?issuedDate >= "2020-01-01"^^xsd:date)
  FILTER(LANGMATCHES(LANG(?title), "en") || LANG(?title) = "")
}
LIMIT 20""",
                endpoint=self.sparql_endpoint,
                description="Find COVID-19 related datasets since 2020",
                tags=["covid-19", "coronavirus", "pandemic", "2020"],
            ),
            QueryExample(
                question="Find datasets about energy consumption with publisher information",
                sparql_query="""PREFIX dct: <http://purl.org/dc/terms/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT DISTINCT ?dataset ?title ?description ?publisherName ?landingPage
WHERE {
  ?dataset a dcat:Dataset .
  ?dataset dct:title ?title .
  OPTIONAL { ?dataset dct:description ?description . }
  OPTIONAL { ?dataset dcat:landingPage ?landingPage . }
  
  ?dataset dct:publisher ?publisherOrg .
  ?publisherOrg foaf:name ?publisherName .
  
  FILTER (
    CONTAINS(LCASE(STR(?title)), "energy consumption") ||
    CONTAINS(LCASE(STR(?title)), "energy") ||
    (BOUND(?description) && CONTAINS(LCASE(STR(?description)), "energy consumption")) ||
    EXISTS { ?dataset dcat:keyword ?kw . FILTER(CONTAINS(LCASE(STR(?kw)), "energy")) }
  )
  
  FILTER(LANGMATCHES(LANG(?title), "en") || LANG(?title) = "")
}
LIMIT 15""",
                endpoint=self.sparql_endpoint,
                description="Find energy consumption datasets with publisher info",
                tags=["energy", "consumption", "publisher"],
            ),
        ]

        # Add all examples to the RAG system
        for example in examples:
            self.add_query_example(example)

        self.logger.info(f"Populated RAG system with {len(examples)} query examples")


if __name__ == "__main__":
    # Initialize and test the RAG system
    rag = RAGSystem()

    # Populate with examples
    rag.populate_with_examples()

    # Test query
    test_query = "Find climate change datasets from European agencies"

    # Test similar example retrieval
    similar = rag.retrieve_similar_examples(test_query)
    print(f"Similar examples for '{test_query}':")
    for ex in similar:
        print(f"- {ex['question']} (distance: {ex.get('distance', 'N/A')})")

    # Test RAG-enhanced query generation
    sparql_query = rag.generate_sparql_with_rag(test_query)
    print(f"\nGenerated SPARQL:\n{sparql_query}")

    # Test validation
    is_valid, message = rag.validate_sparql_query(sparql_query)
    print(f"\nValidation: {'✓' if is_valid else '✗'} {message}")
