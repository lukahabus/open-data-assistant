import { QueryClient, DefaultOptions } from "react-query";
import { ApiError } from "./api";

// Default stale time for queries (5 minutes)
const DEFAULT_STALE_TIME = 5 * 60 * 1000;

// Default cache time for queries (30 minutes)
const DEFAULT_CACHE_TIME = 30 * 60 * 1000;

// Default options for queries
const defaultQueryOptions: DefaultOptions["queries"] = {
  staleTime: DEFAULT_STALE_TIME,
  cacheTime: DEFAULT_CACHE_TIME,
  refetchOnWindowFocus: false,
  refetchOnReconnect: true,
  retry: (failureCount, error) => {
    const apiError = error as ApiError;
    // Don't retry on 4xx errors
    if (apiError.status >= 400 && apiError.status < 500) {
      return false;
    }
    // Retry up to 3 times on other errors
    return failureCount < 3;
  },
  retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
};

// Default options for mutations
const defaultMutationOptions: DefaultOptions["mutations"] = {
  retry: false,
};

// Create Query Client
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: defaultQueryOptions,
    mutations: defaultMutationOptions,
  },
});

// Query Keys
export const QueryKeys = {
  datasets: {
    all: ["datasets"] as const,
    search: (query: string) =>
      [...QueryKeys.datasets.all, "search", query] as const,
    detail: (id: string) => [...QueryKeys.datasets.all, "detail", id] as const,
    similar: (id: string) =>
      [...QueryKeys.datasets.all, "similar", id] as const,
    clusters: (params: { minSize: number; similarity: number }) =>
      [...QueryKeys.datasets.all, "clusters", params] as const,
  },
  metadata: {
    all: ["metadata"] as const,
    quality: (id: string) =>
      [...QueryKeys.metadata.all, "quality", id] as const,
    relationships: (id: string) =>
      [...QueryKeys.metadata.all, "relationships", id] as const,
    coverage: (id: string) =>
      [...QueryKeys.metadata.all, "coverage", id] as const,
  },
  system: {
    status: ["system", "status"] as const,
    stats: ["system", "stats"] as const,
  },
};

// Query Options Types
export interface QueryConfig {
  staleTime?: number;
  cacheTime?: number;
  retry?: boolean | number;
  refetchOnWindowFocus?: boolean;
}

// Utility function to merge query options
export const getQueryOptions = (config?: QueryConfig) => ({
  ...defaultQueryOptions,
  ...config,
});

// Error Boundary fallback component props
export interface QueryErrorBoundaryProps {
  error: Error;
  resetErrorBoundary: () => void;
}

export default queryClient;
