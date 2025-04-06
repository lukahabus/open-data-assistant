import React, { useState } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import { useQuery } from 'react-query';
import { getDatasetClusters } from '../api/datasets';
import { DatasetCluster } from '../types/api';

const Clusters: React.FC = () => {
  const [minSize, setMinSize] = useState<number>(3);
  const [similarity, setSimilarity] = useState<number>(0.7);
  const [sortBy, setSortBy] = useState<string>('size');

  // Fetch clusters
  const {
    data: clusters,
    isLoading,
    error,
  } = useQuery<DatasetCluster[]>(
    ['clusters', minSize, similarity],
    () => getDatasetClusters(minSize, similarity),
    {
      keepPreviousData: true,
    }
  );

  // Sort clusters based on selected criteria
  const sortedClusters = React.useMemo(() => {
    if (!clusters) return [];
    return [...clusters].sort((a, b) => {
      switch (sortBy) {
        case 'size':
          return b.size - a.size;
        case 'theme':
          return (a.theme || '').localeCompare(b.theme || '');
        default:
          return 0;
      }
    });
  }, [clusters, sortBy]);

  const handleSimilarityChange = (
    event: Event,
    newValue: number | number[]
  ) => {
    setSimilarity(newValue as number);
  };

  const handleMinSizeChange = (event: Event, newValue: number | number[]) => {
    setMinSize(newValue as number);
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container>
        <Alert severity="error">Error loading dataset clusters.</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      {/* Controls */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          Dataset Clusters
        </Typography>
        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Typography gutterBottom>Minimum Similarity</Typography>
            <Slider
              value={similarity}
              onChange={handleSimilarityChange}
              min={0.5}
              max={1}
              step={0.05}
              marks
              valueLabelDisplay="auto"
              valueLabelFormat={(value) => `${(value * 100).toFixed(0)}%`}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography gutterBottom>Minimum Cluster Size</Typography>
            <Slider
              value={minSize}
              onChange={handleMinSizeChange}
              min={2}
              max={10}
              step={1}
              marks
              valueLabelDisplay="auto"
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Sort By</InputLabel>
              <Select
                value={sortBy}
                label="Sort By"
                onChange={(e) => setSortBy(e.target.value)}
              >
                <MenuItem value="size">Cluster Size</MenuItem>
                <MenuItem value="theme">Theme</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      {/* Clusters Grid */}
      <Grid container spacing={3}>
        {sortedClusters.map((cluster, index) => (
          <Grid item xs={12} key={index}>
            <Card>
              <CardContent>
                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    mb: 2,
                  }}
                >
                  <Typography variant="h6">
                    Cluster {index + 1}
                    {cluster.theme && ` - ${cluster.theme}`}
                  </Typography>
                  <Chip
                    label={`${cluster.size} datasets`}
                    color="primary"
                    size="small"
                  />
                </Box>

                <Grid container spacing={2}>
                  {cluster.datasets.map((dataset) => (
                    <Grid item xs={12} md={6} key={dataset.id}>
                      <Paper
                        sx={{
                          p: 2,
                          height: '100%',
                          display: 'flex',
                          flexDirection: 'column',
                        }}
                      >
                        <Typography variant="subtitle2" gutterBottom>
                          {dataset.title}
                        </Typography>
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{
                            mb: 2,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            display: '-webkit-box',
                            WebkitLineClamp: 3,
                            WebkitBoxOrient: 'vertical',
                          }}
                        >
                          {dataset.description}
                        </Typography>
                        <Box sx={{ mt: 1 }}>
                          {dataset.themes.map((theme) => (
                            <Chip
                              key={theme}
                              label={theme}
                              size="small"
                              sx={{ mr: 0.5, mb: 0.5 }}
                            />
                          ))}
                        </Box>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* No Results */}
      {sortedClusters.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="body1" color="text.secondary">
            No clusters found with the current settings.
            Try adjusting the minimum size or similarity threshold.
          </Typography>
        </Box>
      )}
    </Container>
  );
};

export default Clusters; 