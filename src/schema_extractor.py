import requests
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import re
import os
from urllib.parse import urlparse

try:
    from .rag_system import RAGSystem, SchemaInfo
except ImportError:
    from rag_system import RAGSystem, SchemaInfo


@dataclass
class ClassInfo:
    """Information about a class in the schema"""

    uri: str
    name: str
    label: str = ""
    comment: str = ""
    instance_count: int = 0
    properties: List[str] = None

    def __post_init__(self):
        if self.properties is None:
            self.properties = []


@dataclass
class PropertyInfo:
    """Information about a property in the schema"""

    uri: str
    name: str
    label: str = ""
    comment: str = ""
    domain_classes: List[str] = None
    range_classes: List[str] = None
    usage_count: int = 0

    def __post_init__(self):
        if self.domain_classes is None:
            self.domain_classes = []
        if self.range_classes is None:
            self.range_classes = []


class SchemaExtractor:
    """
    Extracts schema information from SPARQL endpoints following the research paper approach.
    Automatically retrieves VoID descriptions, class information, and property relationships.
    """

    def __init__(self, endpoint_url: str, cache_dir: str = ".cache"):
        self.endpoint_url = endpoint_url
        self.logger = logging.getLogger(__name__)
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "schema_cache.json")
        self.cache_expiry = timedelta(hours=24)  # Cache expires after 24 hours

        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def _load_cache(self) -> Optional[Dict[str, Any]]:
        """Load cached schema information if available and not expired"""
        if not os.path.exists(self.cache_file):
            return None

        try:
            with open(self.cache_file, "r") as f:
                cache_data = json.load(f)

            # Check if cache is expired
            cached_time = datetime.fromisoformat(
                cache_data.get("timestamp", "2000-01-01T00:00:00")
            )
            if datetime.now() - cached_time > self.cache_expiry:
                return None

            return cache_data.get("schema_info")
        except Exception as e:
            self.logger.warning(f"Failed to load cache: {e}")
            return None

    def _save_cache(self, schema_info: Dict[str, Any]):
        """Save schema information to cache"""
        try:
            cache_data = {
                "timestamp": datetime.now().isoformat(),
                "schema_info": schema_info,
            }
            with open(self.cache_file, "w") as f:
                json.dump(cache_data, f)
        except Exception as e:
            self.logger.warning(f"Failed to save cache: {e}")

    def execute_sparql_query(self, query: str, timeout: int = 30) -> Optional[Dict]:
        """Execute a SPARQL query and return results"""
        try:
            headers = {"Accept": "application/sparql-results+json"}
            params = {"query": query}

            response = requests.get(
                self.endpoint_url, headers=headers, params=params, timeout=timeout
            )

            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning(
                    f"SPARQL query failed with status {response.status_code}"
                )
                return None

        except Exception as e:
            self.logger.error(f"Error executing SPARQL query: {e}")
            return None

    def get_void_description(self) -> Dict[str, Any]:
        """Extract VoID (Vocabulary of Interlinked Datasets) description"""

        void_query = """
        PREFIX void: <http://rdfs.org/ns/void#>
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?dataset ?title ?description ?subjects ?triples ?classes ?properties
        WHERE {
          ?dataset a void:Dataset .
          OPTIONAL { ?dataset dct:title ?title . }
          OPTIONAL { ?dataset dct:description ?description . }
          OPTIONAL { ?dataset void:distinctSubjects ?subjects . }
          OPTIONAL { ?dataset void:triples ?triples . }
          OPTIONAL { ?dataset void:classes ?classes . }
          OPTIONAL { ?dataset void:properties ?properties . }
        }
        """

        results = self.execute_sparql_query(void_query)

        void_info = {}
        if results and results.get("results", {}).get("bindings"):
            for binding in results["results"]["bindings"]:
                dataset = binding.get("dataset", {}).get("value", "")
                void_info[dataset] = {
                    "title": binding.get("title", {}).get("value", ""),
                    "description": binding.get("description", {}).get("value", ""),
                    "subjects": (
                        int(binding.get("subjects", {}).get("value", 0))
                        if binding.get("subjects")
                        else 0
                    ),
                    "triples": (
                        int(binding.get("triples", {}).get("value", 0))
                        if binding.get("triples")
                        else 0
                    ),
                    "classes": (
                        int(binding.get("classes", {}).get("value", 0))
                        if binding.get("classes")
                        else 0
                    ),
                    "properties": (
                        int(binding.get("properties", {}).get("value", 0))
                        if binding.get("properties")
                        else 0
                    ),
                }

        self.logger.info(f"Extracted VoID information for {len(void_info)} datasets")
        return void_info

    def get_class_information(self, limit: int = 50) -> List[ClassInfo]:
        """Extract information about classes in the knowledge graph"""

        # Query for classes with instance counts and labels
        class_query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/2001/XMLSchema#>
        
        SELECT DISTINCT ?class ?label ?comment (COUNT(?instance) AS ?instanceCount)
        WHERE {{
          ?class a rdfs:Class .
          OPTIONAL {{ ?class rdfs:label ?label . }}
          OPTIONAL {{ ?class rdfs:comment ?comment . }}
          OPTIONAL {{ ?instance a ?class . }}
        }}
        GROUP BY ?class ?label ?comment
        ORDER BY DESC(?instanceCount)
        LIMIT {limit}
        """

        results = self.execute_sparql_query(class_query)
        classes = []

        if results and results.get("results", {}).get("bindings"):
            for binding in results["results"]["bindings"]:
                class_uri = binding.get("class", {}).get("value", "")
                if class_uri:
                    # Extract class name from URI
                    class_name = self._extract_name_from_uri(class_uri)

                    class_info = ClassInfo(
                        uri=class_uri,
                        name=class_name,
                        label=binding.get("label", {}).get("value", ""),
                        comment=binding.get("comment", {}).get("value", ""),
                        instance_count=int(
                            binding.get("instanceCount", {}).get("value", 0)
                        ),
                    )
                    classes.append(class_info)

        self.logger.info(f"Extracted information for {len(classes)} classes")
        return classes

    def get_property_information(self, limit: int = 100) -> List[PropertyInfo]:
        """Extract information about properties in the knowledge graph"""

        property_query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT DISTINCT ?property ?label ?comment ?domain ?range (COUNT(?usage) AS ?usageCount)
        WHERE {{
          ?property a rdf:Property .
          OPTIONAL {{ ?property rdfs:label ?label . }}
          OPTIONAL {{ ?property rdfs:comment ?comment . }}
          OPTIONAL {{ ?property rdfs:domain ?domain . }}
          OPTIONAL {{ ?property rdfs:range ?range . }}
          OPTIONAL {{ ?s ?property ?o . ?s a ?usage . }}
        }}
        GROUP BY ?property ?label ?comment ?domain ?range
        ORDER BY DESC(?usageCount)
        LIMIT {limit}
        """

        results = self.execute_sparql_query(property_query)
        properties = []

        if results and results.get("results", {}).get("bindings"):
            for binding in results["results"]["bindings"]:
                prop_uri = binding.get("property", {}).get("value", "")
                if prop_uri:
                    prop_name = self._extract_name_from_uri(prop_uri)

                    property_info = PropertyInfo(
                        uri=prop_uri,
                        name=prop_name,
                        label=binding.get("label", {}).get("value", ""),
                        comment=binding.get("comment", {}).get("value", ""),
                        usage_count=int(binding.get("usageCount", {}).get("value", 0)),
                    )

                    # Add domain and range if available
                    if binding.get("domain"):
                        property_info.domain_classes.append(binding["domain"]["value"])
                    if binding.get("range"):
                        property_info.range_classes.append(binding["range"]["value"])

                    properties.append(property_info)

        self.logger.info(f"Extracted information for {len(properties)} properties")
        return properties

    def get_dcat_specific_schema(self) -> Dict[str, Any]:
        """Extract DCAT-specific schema information for EU Open Data Portal"""

        # Try to load from cache first
        cached_info = self._load_cache()
        if cached_info:
            self.logger.info("Using cached DCAT schema information")
            return cached_info

        dcat_query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        
        SELECT DISTINCT ?datasetCount ?distributionCount ?catalogCount ?publisherCount ?themeCount
        WHERE {
          {
            SELECT (COUNT(DISTINCT ?dataset) AS ?datasetCount) WHERE {
              ?dataset a dcat:Dataset .
            }
          }
          {
            SELECT (COUNT(DISTINCT ?distribution) AS ?distributionCount) WHERE {
              ?distribution a dcat:Distribution .
            }
          }
          {
            SELECT (COUNT(DISTINCT ?catalog) AS ?catalogCount) WHERE {
              ?catalog a dcat:Catalog .
            }
          }
          {
            SELECT (COUNT(DISTINCT ?publisher) AS ?publisherCount) WHERE {
              ?dataset dct:publisher ?publisher .
            }
          }
          {
            SELECT (COUNT(DISTINCT ?theme) AS ?themeCount) WHERE {
              ?dataset dcat:theme ?theme .
            }
          }
        }
        """

        results = self.execute_sparql_query(dcat_query)

        dcat_info = {
            "datasets": 0,
            "distributions": 0,
            "catalogs": 0,
            "publishers": 0,
            "themes": 0,
        }

        if results and results.get("results", {}).get("bindings"):
            binding = results["results"]["bindings"][0]
            dcat_info = {
                "datasets": int(binding.get("datasetCount", {}).get("value", 0)),
                "distributions": int(
                    binding.get("distributionCount", {}).get("value", 0)
                ),
                "catalogs": int(binding.get("catalogCount", {}).get("value", 0)),
                "publishers": int(binding.get("publisherCount", {}).get("value", 0)),
                "themes": int(binding.get("themeCount", {}).get("value", 0)),
            }

        self.logger.info(f"Extracted DCAT schema: {dcat_info}")

        # Save to cache
        self._save_cache(dcat_info)

        return dcat_info

    def get_common_patterns(self) -> Dict[str, Any]:
        """Extract common query patterns and frequently used predicates"""

        patterns_query = """
        SELECT ?predicate (COUNT(?predicate) AS ?count)
        WHERE {
          ?s ?predicate ?o .
        }
        GROUP BY ?predicate
        ORDER BY DESC(?count)
        LIMIT 50
        """

        results = self.execute_sparql_query(patterns_query)
        patterns = []

        if results and results.get("results", {}).get("bindings"):
            for binding in results["results"]["bindings"]:
                predicate = binding.get("predicate", {}).get("value", "")
                count = int(binding.get("count", {}).get("value", 0))
                patterns.append(
                    {
                        "predicate": predicate,
                        "usage_count": count,
                        "name": self._extract_name_from_uri(predicate),
                    }
                )

        self.logger.info(f"Extracted {len(patterns)} common patterns")
        return {"patterns": patterns}

    def _extract_name_from_uri(self, uri: str) -> str:
        """Extract the local name from a URI"""
        if "#" in uri:
            return uri.split("#")[-1]
        elif "/" in uri:
            return uri.split("/")[-1]
        else:
            return uri

    def extract_complete_schema(self) -> SchemaInfo:
        """Extract complete schema information from the endpoint"""

        self.logger.info(f"Starting schema extraction for {self.endpoint_url}")

        # Extract all components
        void_description = self.get_void_description()
        classes = self.get_class_information()
        properties = self.get_property_information()
        dcat_schema = self.get_dcat_specific_schema()
        patterns = self.get_common_patterns()

        # Convert to the format expected by RAGSystem
        classes_dict = []
        for cls in classes:
            classes_dict.append(
                {
                    "uri": cls.uri,
                    "name": cls.name,
                    "label": cls.label,
                    "comment": cls.comment,
                    "instance_count": cls.instance_count,
                }
            )

        properties_dict = []
        for prop in properties:
            properties_dict.append(
                {
                    "uri": prop.uri,
                    "name": prop.name,
                    "label": prop.label,
                    "comment": prop.comment,
                    "domain_classes": prop.domain_classes,
                    "range_classes": prop.range_classes,
                    "usage_count": prop.usage_count,
                }
            )

        # Combine all information
        complete_void = {
            "void_datasets": void_description,
            "dcat_schema": dcat_schema,
            "common_patterns": patterns,
            "extracted_at": datetime.now().isoformat(),
        }

        schema_info = SchemaInfo(
            endpoint=self.endpoint_url,
            classes=classes_dict,
            properties=properties_dict,
            void_description=complete_void,
        )

        self.logger.info("Schema extraction completed successfully")
        return schema_info


def auto_populate_rag_with_schema():
    """Automatically populate RAG system with schema information from EU Open Data Portal"""

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Initialize systems
    rag_system = RAGSystem()
    extractor = SchemaExtractor("https://data.europa.eu/sparql")

    try:
        # Extract schema
        logger.info("Extracting schema from EU Open Data Portal...")
        schema_info = extractor.extract_complete_schema()

        # Add to RAG system
        logger.info("Adding schema information to RAG system...")
        schema_id = rag_system.add_schema_info(schema_info)

        logger.info(f"Successfully populated RAG system with schema ID: {schema_id}")

        # Print summary
        print("📊 Schema Extraction Summary:")
        print(f"✅ Classes extracted: {len(schema_info.classes)}")
        print(f"✅ Properties extracted: {len(schema_info.properties)}")
        print(
            f"✅ VoID datasets: {len(schema_info.void_description.get('void_datasets', {}))}"
        )

        dcat_info = schema_info.void_description.get("dcat_schema", {})
        if dcat_info:
            print(f"📈 DCAT Statistics:")
            print(f"   - Datasets: {dcat_info.get('datasets', 0):,}")
            print(f"   - Distributions: {dcat_info.get('distributions', 0):,}")
            print(f"   - Publishers: {dcat_info.get('publishers', 0):,}")
            print(f"   - Themes: {dcat_info.get('themes', 0):,}")

        return schema_info

    except Exception as e:
        logger.error(f"Failed to populate RAG with schema: {e}")
        raise


if __name__ == "__main__":
    # Extract and populate schema automatically
    schema_info = auto_populate_rag_with_schema()

    # Test schema extraction
    print("\n🔍 Top 10 Classes by Instance Count:")
    top_classes = sorted(
        schema_info.classes, key=lambda x: x.get("instance_count", 0), reverse=True
    )[:10]
    for i, cls in enumerate(top_classes, 1):
        print(f"{i:2d}. {cls['name']} ({cls.get('instance_count', 0):,} instances)")

    print("\n🔗 Top 10 Properties by Usage:")
    top_properties = sorted(
        schema_info.properties, key=lambda x: x.get("usage_count", 0), reverse=True
    )[:10]
    for i, prop in enumerate(top_properties, 1):
        print(f"{i:2d}. {prop['name']} ({prop.get('usage_count', 0):,} uses)")
