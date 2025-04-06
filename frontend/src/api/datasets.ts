import { httpClient } from "../services/http";
import {
  AssistantResponse,
  DatasetSuggestion,
  MetadataInsight,
  DatasetCluster,
  Dataset,
  QueryRequest,
} from "../types/api";

export const queryDatasets = async (
  query: string,
  options?: {
    page?: number;
    sort?: string;
    filters?: Record<string, string>;
  }
): Promise<AssistantResponse> => {
  try {
    return await httpClient.post<AssistantResponse>("/query", {
      query,
      ...options,
    });
  } catch (error) {
    console.error("Error querying datasets:", error);
    throw error;
  }
};

export const suggestDatasets = async (
  query: string,
  filters?: Record<string, string>
): Promise<DatasetSuggestion[]> => {
  try {
    return await httpClient.post<DatasetSuggestion[]>("/suggest", {
      query,
      filters,
    });
  } catch (error) {
    console.error("Error getting dataset suggestions:", error);
    throw error;
  }
};

export const analyzeDataset = async (
  datasetId: string,
  options?: {
    includeSimilar?: boolean;
    maxSimilar?: number;
  }
): Promise<MetadataInsight[]> => {
  try {
    return await httpClient.post<MetadataInsight[]>("/analyze", {
      dataset_id: datasetId,
      ...options,
    });
  } catch (error) {
    console.error("Error analyzing dataset:", error);
    throw error;
  }
};

export const getDatasetClusters = async (
  minSize: number = 3,
  minSimilarity: number = 0.6
): Promise<DatasetCluster[]> => {
  return await httpClient.get<DatasetCluster[]>("/clusters", {
    params: {
      min_size: minSize,
      min_similarity: minSimilarity,
    },
  });
};

export const getSimilarDatasets = async (
  datasetId: string,
  options?: {
    maxResults?: number;
    minSimilarity?: number;
  }
): Promise<DatasetSuggestion[]> => {
  try {
    return await httpClient.get<DatasetSuggestion[]>(`/similar/${datasetId}`, {
      params: options,
    });
  } catch (error) {
    console.error("Error getting similar datasets:", error);
    throw error;
  }
};

// Mock function for development
export const getFeaturedDatasets = async (): Promise<DatasetSuggestion[]> => {
  // Mock implementation
  return [
    {
      id: "air-quality-2023",
      dataset_id: "air-quality-2023",
      title: "Air Quality Measurements 2023",
      description:
        "Hourly measurements of air quality parameters in major cities",
      publisher: "Environmental Protection Agency",
      themes: ["environment", "health", "urban-planning"],
      temporal_coverage: {
        start_date: "2023-01-01",
        end_date: "2023-12-31",
      },
      relevance_score: 0.95,
      explanation:
        "Featured dataset with comprehensive air quality measurements from major cities",
    },
    {
      id: "covid19-stats",
      dataset_id: "covid19-stats",
      title: "COVID-19 Statistics",
      description: "Daily COVID-19 cases, deaths, and vaccination rates",
      publisher: "Ministry of Health",
      themes: ["health", "statistics"],
      temporal_coverage: {
        start_date: "2020-03-01",
        end_date: "2023-12-31",
      },
      relevance_score: 0.92,
      explanation:
        "High-impact public health dataset with extensive temporal coverage",
    },
    {
      id: "climate-indicators",
      dataset_id: "climate-indicators",
      title: "Climate Change Indicators",
      description:
        "Monthly climate change indicators including temperature and precipitation",
      publisher: "Meteorological Institute",
      themes: ["environment", "climate", "research"],
      temporal_coverage: {
        start_date: "2010-01-01",
        end_date: "2023-12-31",
      },
      relevance_score: 0.88,
      explanation:
        "Long-term climate change monitoring data with research applications",
    },
  ];
};

export const getDataset = async (datasetId: string): Promise<Dataset> => {
  return await httpClient.get<Dataset>(`/dataset/${datasetId}`);
};
