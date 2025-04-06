import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  TextField,
  Button,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Pagination,
} from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';
import { useQuery } from 'react-query';
import { queryDatasets } from '../api/datasets';
import { AssistantResponse, DatasetSuggestion } from '../types/api';

// Helper function to get query params
const useQueryParams = () => {
  return new URLSearchParams(useLocation().search);
};

const Search: React.FC = () => {
  const navigate = useNavigate();
  const queryParams = useQueryParams();
  const [searchQuery, setSearchQuery] = useState(queryParams.get('q') || '');
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState('relevance');
  const [filters, setFilters] = useState({
    theme: '',
    format: '',
    publisher: '',
  });

  // Update URL when search params change
  useEffect(() => {
    const params = new URLSearchParams();
    if (searchQuery) params.set('q', searchQuery);
    if (page > 1) params.set('page', page.toString());
    if (sortBy !== 'relevance') params.set('sort', sortBy);
    if (filters.theme) params.set('theme', filters.theme);
    if (filters.format) params.set('format', filters.format);
    if (filters.publisher) params.set('publisher', filters.publisher);

    navigate({ search: params.toString() });
  }, [searchQuery, page, sortBy, filters, navigate]);

  // Fetch search results
  const {
    data: searchResults,
    isLoading,
    error,
  } = useQuery<AssistantResponse>(
    ['search', searchQuery, page, sortBy, filters],
    () =>
      queryDatasets(searchQuery, {
        page,
        sort: sortBy,
        filters,
      }),
    {
      enabled: !!searchQuery,
      keepPreviousData: true,
    }
  );

  const handleSearch = (event: React.FormEvent) => {
    event.preventDefault();
    setPage(1);
  };

  const handleFilterChange = (
    field: keyof typeof filters,
    value: string
  ) => {
    setFilters((prev) => ({ ...prev, [field]: value }));
    setPage(1);
  };

  return (
    <Container maxWidth="lg">
      {/* Search Form */}
      <Box
        component="form"
        onSubmit={handleSearch}
        sx={{ mb: 4, mt: 2 }}
      >
        <Grid container spacing={2}>
          <Grid item xs={12} md={8}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Search datasets..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <Button
              fullWidth
              type="submit"
              variant="contained"
              size="large"
              startIcon={<SearchIcon />}
              disabled={!searchQuery.trim()}
            >
              Search
            </Button>
          </Grid>
        </Grid>
      </Box>

      {/* Filters and Sort */}
      <Box sx={{ mb: 4 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>Theme</InputLabel>
              <Select
                value={filters.theme}
                label="Theme"
                onChange={(e) => handleFilterChange('theme', e.target.value)}
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="environment">Environment</MenuItem>
                <MenuItem value="health">Health</MenuItem>
                <MenuItem value="economy">Economy</MenuItem>
                {/* Add more themes */}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>Format</InputLabel>
              <Select
                value={filters.format}
                label="Format"
                onChange={(e) => handleFilterChange('format', e.target.value)}
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="csv">CSV</MenuItem>
                <MenuItem value="json">JSON</MenuItem>
                <MenuItem value="xml">XML</MenuItem>
                {/* Add more formats */}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>Publisher</InputLabel>
              <Select
                value={filters.publisher}
                label="Publisher"
                onChange={(e) => handleFilterChange('publisher', e.target.value)}
              >
                <MenuItem value="">All</MenuItem>
                {/* Add publishers dynamically */}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>Sort By</InputLabel>
              <Select
                value={sortBy}
                label="Sort By"
                onChange={(e) => setSortBy(e.target.value)}
              >
                <MenuItem value="relevance">Relevance</MenuItem>
                <MenuItem value="date">Date</MenuItem>
                <MenuItem value="title">Title</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Box>

      {/* Results */}
      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error">Error loading search results.</Alert>
      ) : searchResults ? (
        <>
          {/* Results Summary */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              Search Results
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {searchResults.answer}
            </Typography>
          </Box>

          {/* Dataset Cards */}
          <Grid container spacing={3}>
            {searchResults.suggestions.map((dataset: DatasetSuggestion) => (
              <Grid item xs={12} key={dataset.dataset_id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {dataset.dataset_id}
                    </Typography>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      paragraph
                    >
                      {dataset.explanation}
                    </Typography>
                    <Box sx={{ mt: 1 }}>
                      <Chip
                        label={`Relevance: ${(
                          dataset.relevance_score * 100
                        ).toFixed(0)}%`}
                        color="primary"
                        size="small"
                        sx={{ mr: 1 }}
                      />
                      {/* Add more dataset metadata chips */}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* Pagination */}
          <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
            <Pagination
              count={10} // Replace with actual page count
              page={page}
              onChange={(_, value) => setPage(value)}
              color="primary"
            />
          </Box>
        </>
      ) : null}
    </Container>
  );
};

export default Search; 