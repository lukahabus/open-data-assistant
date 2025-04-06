import React from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Link,
  CircularProgress,
  Alert,
  Card,
  CardContent,
} from '@mui/material';
import {
  CalendarToday,
  LocationOn,
  Person,
  Category,
  Description,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { getDataset, analyzeDataset, getSimilarDatasets } from '../api/datasets';
import { Dataset as DatasetType, MetadataInsight, DatasetSuggestion } from '../types/api';

const Dataset: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  // Fetch dataset details
  const {
    data: dataset,
    isLoading,
    error,
  } = useQuery<DatasetType>(['dataset', id], () => getDataset(id!), {
    enabled: !!id,
  });

  // Fetch dataset analysis
  const { data: insights } = useQuery<MetadataInsight[]>(
    ['dataset-analysis', id],
    () => analyzeDataset(id!, { includeSimilar: true, maxSimilar: 5 }),
    {
      enabled: !!id,
    }
  );

  // Fetch similar datasets
  const { data: similarDatasets } = useQuery<DatasetSuggestion[]>(
    ['similar-datasets', id],
    () => getSimilarDatasets(id!, { maxResults: 5, minSimilarity: 0.7 }),
    {
      enabled: !!id,
    }
  );

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
        <Alert severity="error">Error loading dataset details.</Alert>
      </Container>
    );
  }

  if (!dataset) {
    return (
      <Container>
        <Alert severity="warning">Dataset not found.</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      {/* Dataset Header */}
      <Paper sx={{ p: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          {dataset?.title || 'Loading...'}
        </Typography>
        <Box sx={{ mb: 2 }}>
          {dataset.themes.map((theme) => (
            <Chip
              key={theme}
              label={theme}
              color="primary"
              size="small"
              sx={{ mr: 1 }}
            />
          ))}
          {dataset.keywords.map((keyword) => (
            <Chip
              key={keyword}
              label={keyword}
              variant="outlined"
              size="small"
              sx={{ mr: 1 }}
            />
          ))}
        </Box>
        <Typography variant="body1" paragraph>
          {dataset?.description || 'No description available.'}
        </Typography>

        {/* Dataset Metadata */}
        <Grid container spacing={3} sx={{ mt: 2 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Person sx={{ mr: 1 }} />
              <Typography variant="body2">
                Publisher: {dataset?.publisher?.name || 'Unknown'}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <CalendarToday sx={{ mr: 1 }} />
              <Typography variant="body2">
                Updated: {dataset?.modified ? new Date(dataset.modified).toLocaleDateString() : 'Unknown'}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <LocationOn sx={{ mr: 1 }} />
              <Typography variant="body2">
                Coverage: {dataset?.spatial_coverage || 'Not specified'}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Category sx={{ mr: 1 }} />
              <Typography variant="body2">
                License: {dataset?.license || 'Not specified'}
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      <Grid container spacing={4}>
        {/* Main Content */}
        <Grid item xs={12} md={8}>
          {/* Distributions */}
          <Paper sx={{ p: 3, mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              Available Distributions
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Format</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Size</TableCell>
                    <TableCell>Action</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {dataset?.distributions.map((dist) => (
                    <TableRow key={dist.id}>
                      <TableCell>{dist.format}</TableCell>
                      <TableCell>{dist.description || 'No description'}</TableCell>
                      <TableCell>{dist.byte_size ? `${Math.round(dist.byte_size / 1024)} KB` : 'Unknown'}</TableCell>
                      <TableCell>
                        <Link href={dist.download_url} target="_blank">
                          Download
                        </Link>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>

          {/* Temporal Coverage */}
          {dataset.temporal_coverage && (
            <Paper sx={{ p: 3, mb: 4 }}>
              <Typography variant="h6" gutterBottom>
                Temporal Coverage
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">Start Date</Typography>
                  <Typography>
                    {new Date(
                      dataset.temporal_coverage.start_date
                    ).toLocaleDateString()}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">End Date</Typography>
                  <Typography>
                    {new Date(
                      dataset.temporal_coverage.end_date
                    ).toLocaleDateString()}
                  </Typography>
                </Grid>
              </Grid>
            </Paper>
          )}
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} md={4}>
          {/* Metadata Insights */}
          {insights && insights.length > 0 && (
            <Paper sx={{ p: 3, mb: 4 }}>
              <Typography variant="h6" gutterBottom>
                Metadata Insights
              </Typography>
              {insights.map((insight, index) => (
                <Box key={index} sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="primary" gutterBottom>
                    {insight.insight_type}
                  </Typography>
                  <Typography variant="body2">{insight.description}</Typography>
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                      Confidence: {Math.round(insight.confidence * 100)}%
                    </Typography>
                  </Box>
                </Box>
              ))}
            </Paper>
          )}

          {/* Similar Datasets */}
          {similarDatasets && similarDatasets.length > 0 && (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Similar Datasets
              </Typography>
              {similarDatasets.map((similar) => (
                <Card key={similar.dataset_id} sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="subtitle2" gutterBottom>
                      {similar.dataset_id}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {similar.explanation}
                    </Typography>
                    <Box sx={{ mt: 1 }}>
                      <Chip
                        label={`Similarity: ${(
                          similar.relevance_score * 100
                        ).toFixed(0)}%`}
                        size="small"
                        color="primary"
                      />
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </Paper>
          )}
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dataset; 