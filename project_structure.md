# Project Structure

## Implementation (/src)
```
src/
├── dcat/                      # Core DCAT functionality
│   ├── metadata/             # DCAT metadata models
│   │   ├── base.py          # Base metadata classes
│   │   ├── ckan.py          # CKAN-specific adaptors
│   │   └── validators.py    # Metadata validation
│   ├── embedding/           # Embedding functionality
│   │   ├── engine.py        # Embedding core
│   │   └── similarity.py    # Similarity calculations
│   ├── assistant/           # LLM-based assistant
│   │   ├── chat.py          # Chat interface
│   │   ├── prompts.py       # System prompts
│   │   └── tools.py         # Assistant tools
│   └── api/                 # API interfaces
│       ├── ckan.py          # CKAN API client
│       └── endpoints.py      # REST API endpoints
├── frontend/                 # Web interface
│   ├── components/          # React components
│   ├── pages/              # Page definitions
│   └── public/             # Static assets
└── tests/                   # Test suite
    ├── unit/               # Unit tests
    ├── integration/        # Integration tests
    └── evaluation/         # System evaluation tests

## Documentation (/docs)
docs/
├── thesis/                  # Thesis document
│   ├── chapters/           # Thesis chapters
│   ├── figures/            # Figures and diagrams
│   └── references/         # Bibliography
├── api/                    # API documentation
├── user_guide/            # User documentation
└── developer_guide/       # Developer documentation

## Data (/data)
data/
├── raw/                    # Raw CKAN metadata
├── processed/             # Processed DCAT metadata
└── embeddings/            # Stored embeddings

## Configuration
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables
└── config/                # Configuration files
    ├── app.yaml           # Application config
    └── logging.yaml       # Logging config
```

## Key Components

1. **DCAT Core (src/dcat/)**
   - Enhanced metadata models with CKAN support
   - Embedding and similarity analysis
   - LLM-based assistant integration
   - API interfaces for CKAN integration

2. **Frontend (src/frontend/)**
   - Modern React-based interface
   - Dataset visualization components
   - Interactive query interface
   - Relationship visualization

3. **Documentation (docs/)**
   - Comprehensive thesis document
   - API and implementation documentation
   - User and developer guides

4. **Testing & Evaluation (src/tests/)**
   - Unit and integration tests
   - System evaluation framework
   - Performance metrics

## Implementation Plan

1. Phase 1: Core Infrastructure
   - Enhanced DCAT metadata model
   - CKAN API integration
   - Basic embedding functionality

2. Phase 2: Analysis Features
   - Dataset linking implementation
   - Similarity analysis
   - LLM-based querying

3. Phase 3: User Interface
   - Web interface development
   - Visualization components
   - Interactive features

4. Phase 4: Evaluation
   - Testing framework
   - Performance evaluation
   - User studies

5. Phase 5: Documentation
   - Thesis writing
   - Technical documentation
   - User guides 