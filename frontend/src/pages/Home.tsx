import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Container,
  Grid,
  Paper,
  TextField,
  Typography,
  Card,
  CardContent,
  CardActionArea,
} from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';
import { useQuery } from 'react-query';
import { getFeaturedDatasets } from '../api/datasets';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = React.useState('');

  const { data: featuredDatasets } = useQuery('featuredDatasets', getFeaturedDatasets);

  const handleSearch = (event: React.FormEvent) => {
    event.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <Container maxWidth="lg">
      {/* Hero Section */}
      <Paper
        sx={{
          p: { xs: 4, md: 6 },
          mt: 4,
          mb: 6,
          textAlign: 'center',
          backgroundColor: 'primary.main',
          color: 'primary.contrastText',
        }}
      >
        <Typography variant="h3" component="h1" gutterBottom>
          DCAT Metadata Explorer
        </Typography>
        <Typography variant="h5" gutterBottom>
          Discover and analyze open datasets using natural language
        </Typography>

        {/* Search Form */}
        <Box
          component="form"
          onSubmit={handleSearch}
          sx={{
            mt: 4,
            display: 'flex',
            flexDirection: { xs: 'column', sm: 'row' },
            gap: 2,
            maxWidth: 600,
            mx: 'auto',
          }}
        >
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Search datasets..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            sx={{ backgroundColor: 'background.paper', borderRadius: 1 }}
          />
          <Button
            type="submit"
            variant="contained"
            size="large"
            startIcon={<SearchIcon />}
            sx={{ backgroundColor: 'secondary.main', px: 4 }}
          >
            Search
          </Button>
        </Box>
      </Paper>

      {/* Featured Datasets */}
      <Typography variant="h4" gutterBottom>
        Featured Datasets
      </Typography>
      <Grid container spacing={3} sx={{ mb: 6 }}>
        {featuredDatasets?.map((dataset) => (
          <Grid item xs={12} md={4} key={dataset.id}>
            <Card>
              <CardActionArea onClick={() => navigate(`/dataset/${dataset.id}`)}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {dataset.title}
                  </Typography>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      display: '-webkit-box',
                      WebkitLineClamp: 3,
                      WebkitBoxOrient: 'vertical',
                    }}
                  >
                    {dataset.description}
                  </Typography>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Quick Links */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Browse Clusters
            </Typography>
            <Typography variant="body2" paragraph>
              Explore semantically related datasets grouped by theme and content.
            </Typography>
            <Button
              variant="outlined"
              onClick={() => navigate('/clusters')}
            >
              View Clusters
            </Button>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Advanced Search
            </Typography>
            <Typography variant="body2" paragraph>
              Use natural language queries and filters to find specific datasets.
            </Typography>
            <Button
              variant="outlined"
              onClick={() => navigate('/search')}
            >
              Advanced Search
            </Button>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              About the System
            </Typography>
            <Typography variant="body2" paragraph>
              Learn about the metadata analysis capabilities and features.
            </Typography>
            <Button
              variant="outlined"
              onClick={() => navigate('/about')}
            >
              Learn More
            </Button>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Home; 