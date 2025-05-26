# Open Data Assistant

A master's thesis project focused on enhancing open data accessibility through intelligent metadata analysis and natural language interactions. The project combines DCAT (Data Catalog Vocabulary) metadata processing with modern LLM approaches to improve dataset discovery and understanding.

## Research Goals

- Develop intelligent methods for processing and analyzing DCAT metadata
- Implement semantic search capabilities for improved dataset discovery
- Create natural language interfaces for dataset exploration
- Compare traditional SQL-based approaches with LLM-powered solutions
- Evaluate the effectiveness of AI assistance in open data exploration

## Features

- DCAT metadata processing and semantic analysis
- LLM-powered natural language querying of datasets
- Intelligent dataset suggestion system
- Metadata quality assessment and enhancement
- Modern web interface for dataset exploration
- Comparative analysis of traditional and AI-based approaches

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

### Backend Server

Start the FastAPI backend server:

```bash
python -m uvicorn src.dcat.api.main:app --reload --port 8000
```

The API documentation will be available at http://localhost:8000/docs

### Frontend Application

Start the React development server:

```bash
cd frontend
npm install
npm start
```

The web interface will be available at http://localhost:3000

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

- `src/dcat/`: Core DCAT processing module
  - `api/`: FastAPI backend implementation
  - `assistant/`: LLM-powered dataset assistant
  - `embedding/`: Vector embedding and semantic search
  - `metadata/`: DCAT metadata models and processing
  - `analysis/`: Dataset analysis and quality assessment
- `frontend/`: React-based web interface
- `tests/`: Test suite for all components
- `docs/`: Project documentation and research findings
- `data/`: Sample datasets and DCAT metadata

## Research Context

This project is part of a master's thesis at the Faculty of Electrical Engineering and Computing, University of Zagreb. The research explores the application of modern AI techniques to improve the accessibility and usability of open data catalogs.

## License

[MIT License](LICENSE)


python simple_rag_test.py

python interactive_dataset_assistant.py