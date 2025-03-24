# DCAT Metadata Analysis System

This system provides tools for analyzing DCAT (Data Catalog Vocabulary) metadata using Large Language Models (LLMs). It enables semantic search, natural language querying, and comparison between LLM-based and SQL-like approaches to DCAT metadata analysis.

## Overview

The DCAT Metadata Analysis System extends the OpenData Assistant project with capabilities for:

1. Representing DCAT metadata in a structured format
2. Embedding DCAT metadata for semantic search
3. Providing a conversational interface for querying DCAT metadata
4. Comparing LLM-based and SQL-like approaches to metadata analysis

## Components

- **dcat_metadata.py**: Core classes for DCAT metadata representation
- **dcat_embedding.py**: Tools for embedding DCAT metadata using LangChain and FAISS
- **dcat_assistant.py**: LLM-based assistant for interacting with DCAT metadata
- **sample_dcat_data.py**: Script to generate sample DCAT metadata
- **dcat_main.py**: Main script to run the DCAT Assistant
- **dcat_sql_comparison.py**: Tools for comparing LLM and SQL-like approaches

## Installation

1. Set up a Python virtual environment (recommended):
   ```
   python -m venv dcat_env
   dcat_env\Scripts\activate  # Windows
   source dcat_env/bin/activate  # Linux/Mac
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your-api-key
   ```

## Usage

### Generating Sample DCAT Data

Generate sample DCAT data based on the original project datasets:

```
python sample_dcat_data.py
```

This will create a file called `sample_dcat_catalog.json` with DCAT metadata.

### Running the DCAT Assistant

Start the interactive DCAT Assistant:

```
python dcat_main.py
```

This will:
1. Create or load the sample DCAT catalog
2. Embed the catalog (if not already embedded)
3. Present options for interactive or demonstration mode

### Comparing LLM and SQL Approaches

Run the comparison between LLM-based and SQL-like approaches:

```
python dcat_sql_comparison.py
```

This will generate a report file called `dcat_comparison_report.md` that compares the two approaches across several example queries.

## Key Concepts

### DCAT Vocabulary

DCAT is a W3C standard for describing data catalogs. The key classes in DCAT include:

- **Catalog**: A collection of metadata describing datasets, data services, etc.
- **Dataset**: A collection of data, published or curated by a single agent
- **Distribution**: A specific representation of a dataset
- **DataService**: A collection of operations that provides access to datasets
- **DatasetSeries**: A collection of datasets sharing common characteristics
- **CatalogRecord**: A record in a data catalog describing a single dataset or data service

### Embedding DCAT Metadata

This system uses LangChain and FAISS to embed DCAT metadata, enabling:

- Semantic search based on natural language queries
- Finding related datasets based on content similarity
- Question answering using the embedded metadata

### LLM vs. SQL Comparison

The system provides a comparison between:

- **LLM-based approach**: Using embedded metadata and natural language processing
- **SQL-like approach**: Using structured queries on tabular metadata

Each approach has its advantages and limitations, which are analyzed in the comparison report.

## Extending the System

To extend the system with more datasets or functionality:

1. Add new DCAT metadata to the sample catalog or create a new catalog
2. Customize the prompts in the assistant to handle specific types of queries
3. Add new types of analysis or visualization based on the embedded metadata

## License

This project is licensed under the MIT License - see the LICENSE file for details. 