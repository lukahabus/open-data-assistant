/**
 * API types for the DCAT Metadata Explorer
 */

export interface DatasetSuggestion {
  id: string;
  dataset_id: string;
  title: string;
  description: string;
  publisher: string;
  themes: string[];
  temporal_coverage: {
    start_date: string;
    end_date: string;
  };
  relevance_score: number;
  explanation?: string;
}

export interface MetadataInsight {
  insight_type: string;
  description: string;
  confidence: number;
  affected_datasets?: string[];
}

export interface AssistantResponse {
  answer: string;
  suggestions: DatasetSuggestion[];
  insights: MetadataInsight[];
  next_steps?: string[];
}

export interface ApiErrorResponse {
  message: string;
  details?: Record<string, any>;
}

export interface ApiError {
  status: number;
  message: string;
  details?: Record<string, any>;
}

export interface QueryRequest {
  query: string;
  context?: Record<string, string>;
  filters?: Record<string, string>;
}

export interface DatasetAnalysisRequest {
  dataset_id: string;
  include_similar?: boolean;
  max_similar?: number;
}

export interface DatasetCluster {
  id: string;
  datasets: Dataset[];
  theme?: string;
  size: number;
}

export interface Dataset {
  id: string;
  title: string;
  description: string;
  keywords: string[];
  themes: string[];
  publisher: {
    name: string;
    url?: string;
  };
  spatial_coverage?: string;
  temporal_coverage?: {
    start_date: string;
    end_date: string;
  };
  modified: string;
  license?: string;
  distributions: Distribution[];
}

export interface Distribution {
  id: string;
  format: string;
  description?: string;
  byte_size?: number;
  download_url: string;
}
