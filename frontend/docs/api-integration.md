# API Integration Documentation

This document details the API integration between the frontend application and the backend services.

## API Client Configuration

The API client is configured in `src/api/config.ts`:

```typescript
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

## API Endpoints

### Dataset Queries

#### Query Datasets

```typescript
async function queryDatasets(
  query: string,
  options?: {
    page?: number;
    sort?: string;
    filters?: Record<string, string>;
  }
): Promise<AssistantResponse> {
  const response = await apiClient.post('/query', {
    query,
    ...options,
  });
  return response.data;
}
```

**Usage Example:**
```typescript
const results = await queryDatasets('environmental datasets from 2023', {
  page: 1,
  sort: 'relevance',
  filters: {
    theme: 'environment',
  },
});
```

#### Get Dataset Suggestions

```typescript
async function suggestDatasets(
  query: string,
  filters?: Record<string, string>
): Promise<DatasetSuggestion[]> {
  const response = await apiClient.post('/suggest', {
    query,
    filters,
  });
  return response.data;
}
```

### Dataset Analysis

#### Analyze Dataset Metadata

```typescript
async function analyzeDataset(
  datasetId: string,
  options?: {
    includeSimilar?: boolean;
    maxSimilar?: number;
  }
): Promise<MetadataInsight[]> {
  const response = await apiClient.post('/analyze', {
    dataset_id: datasetId,
    ...options,
  });
  return response.data;
}
```

#### Get Dataset Clusters

```typescript
async function getDatasetClusters(
  options?: {
    minSize?: number;
    minSimilarity?: number;
  }
): Promise<DatasetCluster[]> {
  const response = await apiClient.get('/clusters', {
    params: options,
  });
  return response.data;
}
```

## Response Types

### Assistant Response

```typescript
interface AssistantResponse {
  answer: string;
  suggestions: DatasetSuggestion[];
  insights: MetadataInsight[];
  next_steps?: string[];
}
```

### Dataset Suggestion

```typescript
interface DatasetSuggestion {
  dataset_id: string;
  relevance_score: number;
  explanation: string;
}
```

### Metadata Insight

```typescript
interface MetadataInsight {
  type: InsightType;
  description: string;
  confidence: number;
  affected_datasets?: string[];
}
```

### Dataset Cluster

```typescript
interface DatasetCluster {
  id: string;
  datasets: string[];
  theme?: string;
  size: number;
}
```

## Error Handling

### API Error Types

```typescript
interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
}
```

### Error Handling Example

```typescript
try {
  const results = await queryDatasets(searchQuery);
  // Handle success
} catch (error) {
  if (axios.isAxiosError(error)) {
    const apiError = error.response?.data as ApiError;
    // Handle API error
    console.error(`API Error: ${apiError.code} - ${apiError.message}`);
  } else {
    // Handle other errors
    console.error('Unexpected error:', error);
  }
}
```

## React Query Integration

### Query Configuration

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 30 * 60 * 1000, // 30 minutes
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
  },
});
```

### Query Hooks

#### useDatasetQuery

```typescript
export function useDatasetQuery(query: string, options?: QueryOptions) {
  return useQuery(
    ['datasets', query, options],
    () => queryDatasets(query, options),
    {
      enabled: !!query,
      keepPreviousData: true,
    }
  );
}
```

#### useDatasetAnalysis

```typescript
export function useDatasetAnalysis(datasetId: string) {
  return useQuery(
    ['dataset', datasetId, 'analysis'],
    () => analyzeDataset(datasetId),
    {
      enabled: !!datasetId,
    }
  );
}
```

## Best Practices

1. **Error Handling**
   - Implement consistent error handling across all API calls
   - Use type-safe error responses
   - Provide meaningful error messages to users
   - Log errors appropriately

2. **Caching**
   - Configure appropriate cache durations
   - Implement cache invalidation strategies
   - Use optimistic updates where appropriate
   - Monitor cache size

3. **Performance**
   - Implement request debouncing
   - Use pagination for large datasets
   - Optimize payload size
   - Monitor API response times

4. **Security**
   - Implement proper authentication
   - Validate input data
   - Sanitize API responses
   - Use HTTPS for all requests

5. **Testing**
   - Write unit tests for API functions
   - Mock API responses in component tests
   - Test error scenarios
   - Verify type safety 