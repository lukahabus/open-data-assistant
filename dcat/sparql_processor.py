import re
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, RDFS, DCTERMS


@dataclass
class QueryContext:
    """Context for SPARQL query generation."""

    keywords: List[str] = None
    time_range: Dict[str, str] = None
    formats: List[str] = None
    themes: List[str] = None
    languages: List[str] = None
    limit: int = 10


class SparqlQueryProcessor:
    """Process and execute SPARQL queries for EU datasets."""

    # EU Data Portal SPARQL endpoint
    EU_SPARQL_ENDPOINT = "https://data.europa.eu/sparql"

    # Common EU dataset prefixes
    DEFAULT_PREFIXES = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX schema: <http://schema.org/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX euvoc: <http://publications.europa.eu/ontology/euvoc#>
        PREFIX org: <http://www.w3.org/ns/org#>
    """

    def __init__(self):
        """Initialize the SPARQL processor."""
        self.graph = Graph()

    def extract_time_constraints(self, query: str) -> Dict[str, str]:
        """Extract temporal constraints from the query."""
        constraints = {}

        for pattern, constraint_type in self.time_patterns.items():
            matches = re.findall(pattern, query.lower())
            if matches:
                if constraint_type == "relative":
                    amount, unit = matches[0]
                    date = self._calculate_relative_date(int(amount), unit)
                    constraints["after"] = date
                elif constraint_type == "latest":
                    # Default to last 6 months for "latest"
                    date = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
                    constraints["after"] = date
                else:
                    date = matches[0]
                    constraints[constraint_type] = date

        return constraints

    def _calculate_relative_date(self, amount: int, unit: str) -> str:
        """Calculate relative date based on amount and unit."""
        now = datetime.now()
        if unit == "day":
            delta = timedelta(days=amount)
        elif unit == "week":
            delta = timedelta(weeks=amount)
        elif unit == "month":
            delta = timedelta(days=amount * 30)  # Approximate
        else:  # year
            delta = timedelta(days=amount * 365)  # Approximate

        past_date = now - delta
        return past_date.strftime("%Y-%m-%d")

    def process_query(self, natural_query: str) -> str:
        """Convert natural language query to SPARQL query."""
        context = self._build_query_context(natural_query)
        return self._generate_sparql(context)

    def _build_query_context(self, query: str) -> QueryContext:
        """Build query context from natural language query."""
        context = QueryContext()

        # Extract time constraints
        context.time_range = self.extract_time_constraints(query)

        # Extract formats
        formats = []
        for pattern, _ in self.format_patterns.items():
            matches = re.findall(pattern, query.lower())
            formats.extend(matches)
        context.formats = formats if formats else None

        # Extract themes
        themes = []
        for pattern, _ in self.theme_patterns.items():
            matches = re.findall(pattern, query.lower())
            themes.extend(matches)
        context.themes = themes if themes else None

        # Extract keywords (remaining significant words)
        stop_words = {
            "show",
            "me",
            "find",
            "get",
            "in",
            "the",
            "with",
            "and",
            "or",
            "dataset",
            "datasets",
        }
        words = query.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        context.keywords = keywords if keywords else None

        return context

    def _generate_sparql(self, context: QueryContext) -> str:
        """Generate SPARQL query from context."""
        query = f"""{self.DEFAULT_PREFIXES}
        SELECT DISTINCT ?dataset ?title ?description ?publisher ?modified ?theme
        WHERE {{
            ?dataset a dcat:Dataset ;
                    dct:title ?title ;
                    dct:description ?description .
            
            OPTIONAL {{ ?dataset dct:publisher/foaf:name ?publisher }}
            OPTIONAL {{ ?dataset dct:modified ?modified }}
            OPTIONAL {{ ?dataset dcat:theme/skos:prefLabel ?theme }}

            # Process natural query keywords
            {self._get_filter_conditions(context)}
        }}
        ORDER BY DESC(?modified)
        LIMIT {context.limit}
        """
        return query

    def _get_filter_conditions(self, context: QueryContext) -> str:
        """Generate SPARQL filter conditions from natural query.

        Args:
            context: Query context

        Returns:
            SPARQL filter conditions
        """
        conditions = []

        # Language filters - default to English if not specified
        conditions.append('FILTER(LANG(?title) = "en" || LANG(?title) = "")')
        conditions.append(
            'FILTER(LANG(?description) = "en" || LANG(?description) = "")'
        )

        # Theme/category filtering
        if context.themes:
            for theme in context.themes:
                conditions.append(
                    f'FILTER(CONTAINS(LCASE(STR(?theme)), "{theme.lower()}"))'
                )

        # Time-based filtering
        if context.time_range:
            for constraint_type, date in context.time_range.items():
                if constraint_type == "after":
                    conditions.append(f'FILTER(?modified >= "{date}"^^xsd:date)')
                elif constraint_type == "before":
                    conditions.append(f'FILTER(?modified <= "{date}"^^xsd:date)')

        # Format/distribution filtering
        if context.formats:
            format_conditions = []
            for fmt in context.formats:
                format_conditions.append(
                    f'CONTAINS(LCASE(STR(?format)), "{fmt.lower()}")'
                )
            if format_conditions:
                conditions.append("FILTER(" + " || ".join(format_conditions) + ")")

        # Keyword-based filtering
        if context.keywords:
            keyword_filters = []
            for keyword in context.keywords:
                keyword_filters.append(
                    f"""
                    (CONTAINS(LCASE(STR(?title)), "{keyword}") ||
                     CONTAINS(LCASE(STR(?description)), "{keyword}"))
                """
                )
            conditions.append("FILTER(" + " || ".join(keyword_filters) + ")")

        return "\n        ".join(conditions)

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract search keywords from natural query.

        Args:
            query: Natural language query

        Returns:
            List of keywords
        """
        # Remove common words and extract key terms
        stop_words = {
            "show",
            "me",
            "find",
            "about",
            "with",
            "the",
            "in",
            "on",
            "at",
            "from",
            "to",
        }
        words = query.lower().split()
        return [word for word in words if word not in stop_words and len(word) > 2]

    def execute_query(
        self, query: str, datasets: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Execute SPARQL query against EU datasets.

        Args:
            query: SPARQL query string
            datasets: List of datasets to query (for local testing)

        Returns:
            Query results
        """
        # For local testing with provided datasets
        if datasets:
            # Load datasets into graph
            for dataset in datasets:
                self._add_dataset_to_graph(dataset)

            # Execute query locally
            results = self.graph.query(query)
            return self._process_results(results)

        # For actual EU Data Portal querying
        # This would use SPARQLWrapper to query the EU SPARQL endpoint
        return []

    def _add_dataset_to_graph(self, dataset: Dict[str, Any]):
        """Add a dataset to the RDF graph.

        Args:
            dataset: Dataset metadata dictionary
        """
        dataset_uri = URIRef(dataset["@id"])
        self.graph.add(
            (dataset_uri, RDF.type, URIRef("http://www.w3.org/ns/dcat#Dataset"))
        )

        # Add basic metadata
        if "dct:title" in dataset:
            self.graph.add((dataset_uri, DCTERMS.title, dataset["dct:title"]))
        if "dct:description" in dataset:
            self.graph.add(
                (dataset_uri, DCTERMS.description, dataset["dct:description"])
            )
        if "dct:modified" in dataset:
            self.graph.add((dataset_uri, DCTERMS.modified, dataset["dct:modified"]))

        # Add publisher info
        if "dct:publisher" in dataset:
            publisher = dataset["dct:publisher"]
            if isinstance(publisher, dict) and "foaf:name" in publisher:
                self.graph.add((dataset_uri, DCTERMS.publisher, publisher["foaf:name"]))

    def _process_results(self, results) -> List[Dict[str, Any]]:
        """Process SPARQL query results.

        Args:
            results: Query results

        Returns:
            List of result dictionaries
        """
        processed = []
        for row in results:
            item = {}
            for var, value in row.items():
                item[str(var)] = str(value)
            processed.append(item)
        return processed
