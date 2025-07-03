# LaTeX Diagrams for Thesis

This directory contains LaTeX source files for creating meaningful diagrams for the thesis.

## Available Diagrams

1. **system_architecture.tex** - Overall system architecture showing components and data flow
2. **rag_pipeline.tex** - Detailed RAG pipeline showing the step-by-step process
3. **multimodal_search.tex** - Multimodal search approach with different strategies
4. **schema_extraction.tex** - Schema extraction process from SPARQL endpoints
5. **validation_error_handling.tex** - Validation and error handling workflow

## Compilation

### Automatic Compilation

Run the Python script to compile all diagrams:

```bash
python compile_diagrams.py
```

### Manual Compilation

If you prefer to compile manually:

1. **Compile LaTeX to PDF:**
   ```bash
   pdflatex -interaction=nonstopmode diagram_name.tex
   ```

2. **Convert PDF to PNG (using ImageMagick):**
   ```bash
   magick -density 300 diagram_name.pdf -quality 100 diagram_name.png
   ```

### Requirements

- **LaTeX distribution** (TeX Live, MiKTeX, etc.)
- **ImageMagick** for PDF to PNG conversion
- **Python 3** (for automatic compilation script)

## Diagram Descriptions

### System Architecture
Shows the main components of the system including:
- User interface
- RAG system
- LLM (GPT-4)
- Vector database (ChromaDB)
- SPARQL processor
- EU Open Data Portal

### RAG Pipeline
Illustrates the 6-step RAG process:
1. User query
2. Embedding generation
3. Vector search
4. Prompt construction
5. SPARQL generation
6. Validation and execution

### Multimodal Search
Shows the three parallel search strategies:
1. RAG SPARQL search
2. REST API search
3. Similar datasets search
With intelligent synthesis of results

### Schema Extraction
Demonstrates the schema extraction process:
- VoID descriptor extraction
- DCAT analysis
- Classes and properties analysis
- Schema integration

### Validation and Error Handling
Shows the three-stage validation process:
1. Syntax validation
2. Semantic validation
3. Test execution
With error recovery and fallback strategies

## Usage in Thesis

These diagrams are referenced in the thesis chapters:

- **Introduction & Background**: RAG pipeline, multimodal search
- **System Design & Implementation**: All diagrams

The diagrams provide visual support for the technical concepts described in the text. 