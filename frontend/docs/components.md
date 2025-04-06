# Frontend Components Documentation

This document provides detailed information about the components used in the DCAT Metadata Explorer frontend application.

## Page Components

### Search Component (`/src/pages/Search.tsx`)

The Search component provides a comprehensive interface for searching and filtering datasets.

#### Features

- Natural language search input
- Advanced filtering options
  - Theme-based filtering
  - Format-based filtering
  - Publisher-based filtering
- Sorting capabilities
  - Relevance (default)
  - Date
  - Title
- Responsive grid layout
- URL-based state management
- Pagination support

#### Props

None (standalone page component)

#### State Management

```typescript
const [searchQuery, setSearchQuery] = useState(string);
const [page, setPage] = useState(number);
const [sortBy, setSortBy] = useState(string);
const [filters, setFilters] = useState({
  theme: string,
  format: string,
  publisher: string,
});
```

#### Key Functions

- `handleSearch(event: React.FormEvent)`: Handles form submission
- `handleFilterChange(field: string, value: string)`: Updates filter state
- `useQueryParams()`: Custom hook for URL parameter management

#### Usage Example

The Search component is typically rendered through the router:

```typescript
<Route path="/search" element={<Search />} />
```

### Dataset Component (`/src/pages/Dataset.tsx`)

Displays detailed information about a specific dataset.

#### Features

- Comprehensive metadata display
- Quality analysis insights
- Related datasets suggestions
- Distribution information
- Temporal and spatial coverage visualization

#### Props

```typescript
interface DatasetProps {
  datasetId: string;
}
```

### Clusters Component (`/src/pages/Clusters.tsx`)

Visualizes dataset clusters and relationships.

#### Features

- Interactive cluster visualization
- Theme-based grouping
- Similarity metrics display
- Drill-down capabilities

## Core Components

### Layout Component (`/src/components/Layout.tsx`)

The main application layout wrapper.

#### Features

- Responsive navigation drawer
- App bar with search integration
- Theme switching capability
- Breadcrumb navigation

#### Props

```typescript
interface LayoutProps {
  children: React.ReactNode;
}
```

### SearchBar Component (`/src/components/SearchBar.tsx`)

Reusable search input component.

#### Features

- Autocomplete suggestions
- Search history
- Clear input button
- Loading state indication

#### Props

```typescript
interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  initialValue?: string;
  autoFocus?: boolean;
}
```

### DatasetCard Component (`/src/components/DatasetCard.tsx`)

Card component for displaying dataset summaries.

#### Features

- Title and description display
- Metadata highlights
- Action buttons
- Relevance score indication

#### Props

```typescript
interface DatasetCardProps {
  dataset: Dataset;
  relevanceScore?: number;
  onClick?: (datasetId: string) => void;
}
```

### MetadataInsights Component (`/src/components/MetadataInsights.tsx`)

Displays analysis insights for datasets.

#### Features

- Quality metrics visualization
- Improvement suggestions
- Relationship indicators
- Confidence scores

#### Props

```typescript
interface MetadataInsightsProps {
  insights: MetadataInsight[];
  onInsightClick?: (insight: MetadataInsight) => void;
}
```

## Utility Components

### FilterGroup Component (`/src/components/FilterGroup.tsx`)

Reusable filter group component.

#### Props

```typescript
interface FilterGroupProps {
  filters: Filter[];
  onChange: (filters: Filter[]) => void;
  title?: string;
}
```

### Pagination Component (`/src/components/Pagination.tsx`)

Custom pagination component with additional features.

#### Props

```typescript
interface PaginationProps {
  totalPages: number;
  currentPage: number;
  onPageChange: (page: number) => void;
  pageSize?: number;
}
```

## Best Practices

1. **Component Organization**
   - Keep components focused and single-responsibility
   - Use TypeScript interfaces for props
   - Implement proper error boundaries
   - Document component APIs

2. **State Management**
   - Use React Query for server state
   - Implement local state with useState/useReducer
   - Consider context for shared state
   - Document state updates

3. **Performance**
   - Implement useMemo and useCallback where appropriate
   - Use React.memo for expensive renders
   - Lazy load components when possible
   - Monitor and optimize re-renders

4. **Accessibility**
   - Use semantic HTML elements
   - Implement ARIA attributes
   - Ensure keyboard navigation
   - Test with screen readers

5. **Testing**
   - Write unit tests for components
   - Test user interactions
   - Verify accessibility
   - Test error states 