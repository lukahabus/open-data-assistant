import React from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  CardMedia,
} from '@mui/material';
import {
  Search as SearchIcon,
  Psychology as PsychologyIcon,
  Storage as StorageIcon,
  Hub as HubIcon,
} from '@mui/icons-material';

const About: React.FC = () => {
  const features = [
    {
      title: 'Natural Language Search',
      description:
        'Search for datasets using natural language queries. Our system understands context and intent to provide relevant results.',
      icon: <SearchIcon sx={{ fontSize: 40 }} />,
    },
    {
      title: 'Semantic Analysis',
      description:
        'Advanced semantic analysis of metadata using state-of-the-art language models to extract insights and relationships.',
      icon: <PsychologyIcon sx={{ fontSize: 40 }} />,
    },
    {
      title: 'Metadata Quality',
      description:
        'Automated assessment of metadata quality with suggestions for improvement and completeness analysis.',
      icon: <StorageIcon sx={{ fontSize: 40 }} />,
    },
    {
      title: 'Dataset Relationships',
      description:
        'Discover related datasets through semantic clustering and similarity analysis.',
      icon: <HubIcon sx={{ fontSize: 40 }} />,
    },
  ];

  return (
    <Container maxWidth="lg">
      {/* Hero Section */}
      <Paper
        sx={{
          p: 6,
          mb: 4,
          textAlign: 'center',
          backgroundColor: 'primary.main',
          color: 'primary.contrastText',
        }}
      >
        <Typography variant="h3" gutterBottom>
          DCAT Metadata Analysis System
        </Typography>
        <Typography variant="h6">
          Enhancing open data discovery through intelligent metadata analysis
        </Typography>
      </Paper>

      {/* Features */}
      <Grid container spacing={4} sx={{ mb: 6 }}>
        {features.map((feature, index) => (
          <Grid item xs={12} md={6} key={index}>
            <Card>
              <CardContent>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    mb: 2,
                    color: 'primary.main',
                  }}
                >
                  {feature.icon}
                  <Typography variant="h6" sx={{ ml: 2 }}>
                    {feature.title}
                  </Typography>
                </Box>
                <Typography variant="body1" color="text.secondary">
                  {feature.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* System Overview */}
      <Paper sx={{ p: 4, mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          System Overview
        </Typography>
        <Typography variant="body1" paragraph>
          The DCAT Metadata Analysis System is designed to improve the
          discoverability and usability of open datasets by applying advanced
          natural language processing techniques to metadata analysis. The system
          integrates with CKAN-based data portals and provides intelligent search
          and analysis capabilities.
        </Typography>
        <Typography variant="body1" paragraph>
          Key components of the system include:
        </Typography>
        <ul>
          <li>
            <Typography variant="body1">
              DCAT Adapter: Interfaces with CKAN portals and standardizes metadata
              according to the DCAT vocabulary
            </Typography>
          </li>
          <li>
            <Typography variant="body1">
              Embedding Engine: Generates semantic embeddings for metadata fields
              using state-of-the-art language models
            </Typography>
          </li>
          <li>
            <Typography variant="body1">
              Semantic Analyzer: Processes metadata embeddings to extract insights,
              identify relationships, and assess quality
            </Typography>
          </li>
          <li>
            <Typography variant="body1">
              LLM Assistant: Provides natural language interaction and generates
              human-readable insights
            </Typography>
          </li>
        </ul>
      </Paper>

      {/* Technology Stack */}
      <Paper sx={{ p: 4 }}>
        <Typography variant="h5" gutterBottom>
          Technology Stack
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Frontend
                </Typography>
                <ul>
                  <li>React with TypeScript</li>
                  <li>Material-UI components</li>
                  <li>React Query for data fetching</li>
                  <li>React Router for navigation</li>
                </ul>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Backend
                </Typography>
                <ul>
                  <li>FastAPI framework</li>
                  <li>LangChain for LLM integration</li>
                  <li>Vector databases for embeddings</li>
                  <li>Redis for caching</li>
                </ul>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  AI/ML
                </Typography>
                <ul>
                  <li>Transformer-based language models</li>
                  <li>Semantic similarity analysis</li>
                  <li>Clustering algorithms</li>
                  <li>Quality assessment models</li>
                </ul>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};

export default About; 