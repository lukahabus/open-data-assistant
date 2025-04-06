// API Configuration
export const API_BASE_URL =
  process.env.REACT_APP_API_URL || "http://localhost:8000";

// API Endpoints
export const ENDPOINTS = {
  // Dataset endpoints
  QUERY: "/query",
  SUGGEST: "/suggest",
  ANALYZE: "/analyze",
  CLUSTERS: "/clusters",
  SIMILAR: (datasetId: string) => `/similar/${datasetId}`,
  DATASET: (datasetId: string) => `/dataset/${datasetId}`,

  // Metadata analysis endpoints
  QUALITY: "/quality",
  RELATIONSHIPS: "/relationships",
  COVERAGE: "/coverage",

  // System endpoints
  STATUS: "/",
  STATS: "/stats",
} as const;

// API Response Types
export interface ApiError {
  status: number;
  message: string;
  details?: Record<string, unknown>;
}

// API Configuration Types
export interface ApiConfig {
  baseURL: string;
  timeout: number;
  headers: Record<string, string>;
}

// Default API Configuration
export const DEFAULT_CONFIG: ApiConfig = {
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    "Content-Type": "application/json",
  },
};

// Utility function to build full URL
export const buildUrl = (endpoint: string): string => {
  return `${API_BASE_URL}${endpoint}`;
};

// Utility function to handle API errors
export const handleApiError = (error: unknown): ApiError => {
  if (error instanceof Error) {
    return {
      status: 500,
      message: error.message,
    };
  }
  return {
    status: 500,
    message: "An unknown error occurred",
  };
};
