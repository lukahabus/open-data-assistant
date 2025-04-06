import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';
import Layout from './components/Layout';
import Home from './pages/Home';
import Search from './pages/Search';
import Dataset from './pages/Dataset';
import Clusters from './pages/Clusters';
import About from './pages/About';

const App: React.FC = () => {
  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/search" element={<Search />} />
          <Route path="/dataset/:id" element={<Dataset />} />
          <Route path="/clusters" element={<Clusters />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </Layout>
    </Box>
  );
};

export default App; 