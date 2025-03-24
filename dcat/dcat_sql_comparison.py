"""
DCAT SQL Comparison - Compares LLM-based DCAT metadata analysis with SQL-like querying.

This module provides functions for comparing LLM-based DCAT metadata analysis
with SQL-like querying, highlighting the differences, advantages, and limitations
of each approach.
"""

import os
import sys
import json
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple, Union
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

# Dodaj parent direktorij u sys.path za ispravno učitavanje modula
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Nakon dodavanja parent direktorija možemo uvesti module iz dcat paketa
from dcat.dcat_metadata import Catalog, Dataset, load_catalog_from_json
from dcat.dcat_assistant import DCATAssistant
from dcat.dcat_embedding import DCATEmbedder

# Load environment variables
load_dotenv()


class DCATSQLComparison:
    """Class for comparing LLM-based DCAT metadata analysis with SQL-like querying."""

    def __init__(self, catalog_path: str, model_name: str = "gpt-3.5-turbo"):
        """Initialize the DCATSQLComparison.

        Args:
            catalog_path: Path to the DCAT catalog JSON file.
            model_name: The name of the model to use for LLM analysis. Defaults to "gpt-3.5-turbo".
        """
        self.catalog = load_catalog_from_json(catalog_path)
        self.llm = ChatOpenAI(model_name=model_name, temperature=0)
        self.dcat_embedder = None
        self.dcat_assistant = None

        # Convert catalog to DataFrame for SQL-like querying
        self.datasets_df = self._prepare_datasets_dataframe()

    def _prepare_datasets_dataframe(self) -> pd.DataFrame:
        """Convert the catalog's datasets to a pandas DataFrame for SQL-like querying.

        Returns:
            A pandas DataFrame containing the datasets.
        """
        data = []
        for dataset in self.catalog.datasets:
            # Extract relevant fields
            row = {
                "id": dataset.id,
                "title": dataset.title,
                "description": dataset.description,
                "keywords": ", ".join(dataset.keywords),
                "themes": ", ".join(dataset.themes),
                "issued": dataset.issued,
                "modified": dataset.modified,
                "publisher": (
                    dataset.publisher.get("name") if dataset.publisher else None
                ),
                "distribution_count": len(dataset.distributions),
                "distribution_formats": ", ".join(
                    [d.format for d in dataset.distributions if d.format]
                ),
            }
            data.append(row)

        return pd.DataFrame(data)

    def initialize_llm_assistant(self):
        """Initialize the LLM-based assistant."""
        if not self.dcat_embedder:
            self.dcat_embedder = DCATEmbedder()
            vector_store_dir = "vector_store"

            # Check if vector store exists
            if os.path.exists(vector_store_dir):
                self.dcat_embedder.load_vector_store(vector_store_dir)
            else:
                # Embed the catalog
                self.dcat_embedder.embed_catalog(self.catalog)
                os.makedirs(vector_store_dir, exist_ok=True)
                self.dcat_embedder.save_vector_store(
                    self.dcat_embedder.vector_store, vector_store_dir
                )

        if not self.dcat_assistant:
            self.dcat_assistant = DCATAssistant(self.dcat_embedder)

    def sql_query(self, query: str) -> pd.DataFrame:
        """Execute a SQL-like query on the datasets DataFrame.

        Args:
            query: The SQL query to execute.

        Returns:
            A pandas DataFrame containing the query results.
        """
        # Create a prompt for the LLM to convert natural language to pandas query
        system_template = """
        You are a helpful assistant that converts natural language queries into pandas DataFrame queries.
        The DataFrame is called 'df' and has the following columns:
        - id: The ID of the dataset
        - title: The title of the dataset
        - description: The description of the dataset
        - keywords: A comma-separated string of keywords
        - themes: A comma-separated string of themes
        - issued: The date the dataset was issued
        - modified: The date the dataset was last modified
        - publisher: The name of the publisher
        - distribution_count: The number of distributions
        - distribution_formats: A comma-separated string of distribution formats
        
        Return ONLY the pandas code to perform the query, without any explanation or comments.
        The code should start with 'df' and should be a valid pandas DataFrame operation.
        """

        system_message = SystemMessagePromptTemplate.from_template(system_template)
        human_message = HumanMessagePromptTemplate.from_template("{query}")
        chat_prompt = ChatPromptTemplate.from_messages([system_message, human_message])

        # Get the pandas query from the LLM
        formatted_prompt = chat_prompt.format_prompt(query=query).to_messages()
        response = self.llm.invoke(formatted_prompt)
        pandas_query = response.content

        # For safety, add df = self.datasets_df at the beginning and use eval
        pandas_query = pandas_query.strip()

        try:
            # Make a local copy of the dataframe
            df = self.datasets_df.copy()

            # Execute the pandas query
            result = eval(pandas_query)

            return result
        except Exception as e:
            print(f"Error executing pandas query: {e}")
            print(f"Query: {pandas_query}")
            return pd.DataFrame()

    def llm_query(self, query: str) -> str:
        """Execute a natural language query using the LLM-based assistant.

        Args:
            query: The natural language query to execute.

        Returns:
            The response from the assistant.
        """
        self.initialize_llm_assistant()
        result = self.dcat_assistant.process_query(query)
        return result["answer"]

    def compare_approaches(self, query: str) -> Dict[str, Any]:
        """Compare SQL-like querying with LLM-based querying for a given query.

        Args:
            query: The query to compare.

        Returns:
            A dictionary containing the results of both approaches.
        """
        # Execute SQL-like query
        sql_start_time = pd.Timestamp.now()
        sql_result = self.sql_query(query)
        sql_end_time = pd.Timestamp.now()
        sql_time = (sql_end_time - sql_start_time).total_seconds()

        # Execute LLM query
        llm_start_time = pd.Timestamp.now()
        llm_result = self.llm_query(query)
        llm_end_time = pd.Timestamp.now()
        llm_time = (llm_end_time - llm_start_time).total_seconds()

        # Return comparison
        return {
            "query": query,
            "sql_result": sql_result,
            "llm_result": llm_result,
            "sql_time": sql_time,
            "llm_time": llm_time,
        }

    def generate_comparison_report(self, queries: List[str]) -> str:
        """Generate a comparison report for a list of queries.

        Args:
            queries: The list of queries to compare.

        Returns:
            A string containing the comparison report.
        """
        results = []
        for query in queries:
            results.append(self.compare_approaches(query))

        # Create the report
        report = "# SQL vs. LLM DCAT Metadata Analysis Comparison\n\n"

        for result in results:
            report += f"## Query: {result['query']}\n\n"

            report += "### SQL-like Approach\n"
            report += f"Time: {result['sql_time']:.2f} seconds\n\n"
            report += "Result:\n"
            if isinstance(result["sql_result"], pd.DataFrame):
                report += f"```\n{result['sql_result'].to_string()}\n```\n\n"
            else:
                report += f"```\n{result['sql_result']}\n```\n\n"

            report += "### LLM-based Approach\n"
            report += f"Time: {result['llm_time']:.2f} seconds\n\n"
            report += "Result:\n"
            report += f"```\n{result['llm_result']}\n```\n\n"

            report += "---\n\n"

        # Add overall summary and comparison
        report += "## Overall Comparison\n\n"

        # Calculate averages
        avg_sql_time = sum([r["sql_time"] for r in results]) / len(results)
        avg_llm_time = sum([r["llm_time"] for r in results]) / len(results)

        report += f"Average SQL-like query time: {avg_sql_time:.2f} seconds\n"
        report += f"Average LLM-based query time: {avg_llm_time:.2f} seconds\n\n"

        # Add qualitative analysis
        report += "### Advantages and Limitations\n\n"

        report += "#### SQL-like Approach\n\n"
        report += "Advantages:\n"
        report += "- Faster execution time\n"
        report += "- Precise and structured results\n"
        report += "- Well-suited for queries with specific criteria\n\n"

        report += "Limitations:\n"
        report += "- Limited to explicit metadata fields\n"
        report += "- Cannot understand semantic meaning beyond keywords\n"
        report += "- Struggles with ambiguous or nuanced queries\n\n"

        report += "#### LLM-based Approach\n\n"
        report += "Advantages:\n"
        report += "- Can understand semantic meaning and context\n"
        report += "- Handles natural language and ambiguous queries well\n"
        report += "- Can infer relationships and connections between datasets\n"
        report += "- Provides explanatory and conversational responses\n\n"

        report += "Limitations:\n"
        report += "- Slower execution time\n"
        report += "- May introduce inaccuracies or hallucinations\n"
        report += "- Less precise for structured data retrieval\n\n"

        return report


def main():
    """Main function to run the comparison."""
    # Check if the catalog file exists
    current_dir = os.path.dirname(os.path.abspath(__file__))
    catalog_path = os.path.join(current_dir, "sample_dcat_catalog.json")
    if not os.path.exists(catalog_path):
        print(
            f"Sample DCAT catalog not found at {catalog_path}. Please run dcat/sample_dcat_data.py first."
        )
        return

    # Create the comparison object
    comparison = DCATSQLComparison(catalog_path)

    # Define some example queries
    example_queries = [
        "Find datasets about education",
        "Which datasets were modified after January 2023?",
        "Show me datasets related to streets in Zagreb",
        "What datasets have geospatial information?",
        "Find datasets with PDF distributions",
    ]

    # Generate the comparison report
    report = comparison.generate_comparison_report(example_queries)

    # Save the report to a file in the dcat folder
    report_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "dcat_comparison_report.md"
    )
    with open(report_path, "w") as f:
        f.write(report)

    print(f"Comparison report generated and saved to {report_path}")


if __name__ == "__main__":
    main()
