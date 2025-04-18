import React from 'react';
import { Layers } from 'lucide-react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';
import HomePage from './pages/HomePage';
import DatasetExplorer from './pages/DatasetExplorer';
import LlmAnalyzer from './pages/LlmAnalyzer';
import ComparisonTool from './pages/ComparisonTool';
import About from './pages/About';

function App() {
  return (
    <Router>
      <div className="flex flex-col min-h-screen bg-gray-50">
        <Navbar />
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/explorer" element={<DatasetExplorer />} />
            <Route path="/analyzer" element={<LlmAnalyzer />} />
            <Route path="/comparison" element={<ComparisonTool />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;