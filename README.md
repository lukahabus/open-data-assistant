# Open Data Assistant

A tool for working with open data, including DCAT metadata processing, data visualization, and natural language querying of datasets.

## Features

- DCAT (Data Catalog Vocabulary) metadata processing and semantic search
- Natural language question answering about datasets
- SQL-like querying and comparison with LLM-based approaches
- Data visualization and analysis tools

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/open-data-assistant.git
cd open-data-assistant
```

2. Create and activate a virtual environment:
```bash
python -m venv env
# On Windows
env\Scripts\activate
# On macOS/Linux
source env/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your OpenAI API key in a `.env` file:
```bash
OPENAI_API_KEY=your_api_key_here
```

## Usage

### DCAT Assistant

Run the DCAT assistant to interactively query a DCAT catalog:

```bash
python main.py dcat
```

Specify a custom catalog file:

```bash
python main.py dcat --catalog path/to/catalog.json
```

Run with a specific query:

```bash
python main.py dcat --query "What datasets are available about streets?"
```

## Project Structure

- `main.py`: Main entry point for the application
- `dcat/`: DCAT module for working with Data Catalog Vocabulary
  - `dcat_metadata.py`: Data models for DCAT entities
  - `dcat_embedding.py`: Vector embedding and semantic search
  - `dcat_assistant.py`: LLM-powered assistant for DCAT
  - `dcat_sql_comparison.py`: Compare SQL querying with LLM approaches
  - `sample_dcat_data.py`: Generate sample DCAT data
  - `dcat_main.py`: Command-line interface for DCAT module

## License

[MIT License](LICENSE)
