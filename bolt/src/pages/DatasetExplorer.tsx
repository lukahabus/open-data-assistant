import React, { useState } from 'react';
import { Search, Filter, Download, RefreshCw } from 'lucide-react';
import DatasetCard from '../components/datasets/DatasetCard';
import FilterPanel from '../components/datasets/FilterPanel';
import { mockDatasets } from '../data/mockData';

const DatasetExplorer = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [activeFilters, setActiveFilters] = useState({
    format: [],
    category: [],
    publisher: []
  });

  // Simple filtering functionality
  const filteredDatasets = mockDatasets.filter(dataset => {
    const matchesSearch = dataset.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
                           dataset.description.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesFormat = activeFilters.format.length === 0 || 
                            activeFilters.format.includes(dataset.format);
    
    const matchesCategory = activeFilters.category.length === 0 || 
                              dataset.categories.some(cat => activeFilters.category.includes(cat));
    
    const matchesPublisher = activeFilters.publisher.length === 0 || 
                               activeFilters.publisher.includes(dataset.publisher);
    
    return matchesSearch && matchesFormat && matchesCategory && matchesPublisher;
  });

  const toggleFilters = () => {
    setShowFilters(!showFilters);
  };

  const updateFilters = (filterType, values) => {
    setActiveFilters({
      ...activeFilters,
      [filterType]: values
    });
  };

  const resetFilters = () => {
    setActiveFilters({
      format: [],
      category: [],
      publisher: []
    });
    setSearchQuery('');
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dataset Explorer</h1>
        <p className="mt-2 text-gray-600">
          Browse and search through available open datasets with DCAT metadata
        </p>
      </div>

      {/* Search and filters */}
      <div className="mb-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-grow">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="Search datasets..."
            />
          </div>
          <button 
            onClick={toggleFilters}
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Filter className="h-5 w-5 mr-2" />
            Filters
          </button>
          <button 
            onClick={resetFilters}
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <RefreshCw className="h-5 w-5 mr-2" />
            Reset
          </button>
        </div>
      </div>

      {/* Filter panel */}
      {showFilters && (
        <div className="mb-6 bg-white p-4 rounded-md shadow">
          <FilterPanel 
            activeFilters={activeFilters} 
            updateFilters={updateFilters} 
          />
        </div>
      )}

      {/* Results count */}
      <div className="mb-4 flex justify-between items-center">
        <p className="text-sm text-gray-600">
          Showing {filteredDatasets.length} of {mockDatasets.length} datasets
        </p>
        <button
          className="inline-flex items-center px-3 py-1 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <Download className="h-4 w-4 mr-1" />
          Export Results
        </button>
      </div>

      {/* Results grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredDatasets.map((dataset) => (
          <DatasetCard key={dataset.id} dataset={dataset} />
        ))}
      </div>

      {/* Empty state */}
      {filteredDatasets.length === 0 && (
        <div className="text-center py-12">
          <Search className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-lg font-medium text-gray-900">No datasets found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Try adjusting your search or filter criteria to find what you're looking for.
          </p>
        </div>
      )}
    </div>
  );
};

export default DatasetExplorer;