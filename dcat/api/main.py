from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from pathlib import Path
import os
from dotenv import load_dotenv
import logging

from ..harvester import DCATHarvester
from ..sparql_processor import SparqlQueryProcessor

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="DCAT Metadata Explorer API",
    description="API for exploring and analyzing DCAT metadata",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
cache_dir = os.getenv("CACHE_DIR", "cache")
harvester = DCATHarvester(cache_dir=cache_dir)
query_processor = SparqlQueryProcessor()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Source(BaseModel):
    """Data source configuration."""

    id: str = Field(..., description="Unique identifier for the source")
    type: str = Field(..., description="Source type (sparql, rdf, ckan)")
    url: str = Field(..., description="Source URL")
    api_key: Optional[str] = Field(None, description="Optional API key")
    format: Optional[str] = Field(None, description="Format for RDF sources")


class QueryRequest(BaseModel):
    """Natural language query request."""

    query: str = Field(..., description="Natural language query")
    sources: Optional[List[str]] = Field(None, description="Source IDs to query")


class Dataset(BaseModel):
    """DCAT dataset metadata."""

    id: str = Field(..., alias="@id")
    type: str = Field("dcat:Dataset", alias="@type")
    title: Optional[str] = Field(None, alias="dct:title")
    description: Optional[str] = Field(None, alias="dct:description")
    modified: Optional[str] = Field(None, alias="dct:modified")
    publisher: Optional[Dict[str, Any]] = Field(None, alias="dct:publisher")
    distributions: Optional[List[Dict[str, Any]]] = Field(
        None, alias="dcat:distribution"
    )


@app.post("/sources/{source_id}/harvest")
async def harvest_source(source: Source) -> List[Dataset]:
    """Harvest datasets from a source."""
    try:
        if source.type == "sparql":
            # Use default query if none provided
            query = """
                PREFIX dcat: <http://www.w3.org/ns/dcat#>
                PREFIX dct: <http://purl.org/dc/terms/>
                SELECT ?dataset ?title ?description ?modified ?publisher
                WHERE {
                    ?dataset a dcat:Dataset ;
                            dct:title ?title ;
                            dct:description ?description ;
                            dct:modified ?modified ;
                            dct:publisher ?publisher .
                }
                LIMIT 100
            """
            datasets = harvester.harvest_sparql(source.url, query)
        elif source.type == "rdf":
            datasets = harvester.harvest_rdf(source.url, source.format)
        elif source.type == "ckan":
            datasets = harvester.harvest_ckan(source.url, source.api_key)
        else:
            raise HTTPException(
                status_code=400, detail=f"Unsupported source type: {source.type}"
            )

        # Cache results
        harvester.save_cache(datasets, source.id)
        return datasets
    except Exception as e:
        logger.error(f"Error harvesting from {source.url}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
async def query_datasets(request: QueryRequest) -> List[Dataset]:
    """Query datasets using natural language."""
    try:
        # Load cached datasets from specified or all sources
        all_datasets = []
        cache_dir = Path(cache_dir)
        source_pattern = (
            "*" if not request.sources else "{" + ",".join(request.sources) + "}"
        )

        for cache_file in cache_dir.glob(f"{source_pattern}_*.json"):
            datasets = harvester.load_cache(cache_file.stem.split("_")[0])
            all_datasets.extend(datasets)

        if not all_datasets:
            return []

        # Generate and execute SPARQL query
        sparql_query = query_processor.process_query(request.query)
        results = query_processor.execute_query(sparql_query, all_datasets)

        return results
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/datasets")
async def list_datasets(
    offset: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)
) -> List[Dataset]:
    """List cached datasets with pagination."""
    try:
        all_datasets = []
        cache_dir = Path(cache_dir)

        for cache_file in cache_dir.glob("*_*.json"):
            datasets = harvester.load_cache(cache_file.stem.split("_")[0])
            all_datasets.extend(datasets)

        return all_datasets[offset : offset + limit]
    except Exception as e:
        logger.error(f"Error listing datasets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: str) -> Dataset:
    """Get a specific dataset by ID."""
    try:
        cache_dir = Path(cache_dir)

        # Search all cache files for the dataset
        for cache_file in cache_dir.glob("*_*.json"):
            datasets = harvester.load_cache(cache_file.stem.split("_")[0])
            for dataset in datasets:
                if dataset.get("@id") == dataset_id:
                    return dataset

        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")
    except Exception as e:
        logger.error(f"Error getting dataset {dataset_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
