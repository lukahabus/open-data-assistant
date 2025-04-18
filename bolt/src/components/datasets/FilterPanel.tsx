import React from 'react';
import { mockFormats, mockCategories, mockPublishers } from '../../data/mockData';

interface FilterPanelProps {
  activeFilters: {
    format: string[];
    category: string[];
    publisher: string[];
  };
  updateFilters: (filterType: string, values: string[]) => void;
}

const FilterPanel: React.FC<FilterPanelProps> = ({ activeFilters, updateFilters }) => {
  const handleFormatChange = (format: string) => {
    const newFormats = activeFilters.format.includes(format)
      ? activeFilters.format.filter(f => f !== format)
      : [...activeFilters.format, format];
    
    updateFilters('format', newFormats);
  };

  const handleCategoryChange = (category: string) => {
    const newCategories = activeFilters.category.includes(category)
      ? activeFilters.category.filter(c => c !== category)
      : [...activeFilters.category, category];
    
    updateFilters('category', newCategories);
  };

  const handlePublisherChange = (publisher: string) => {
    const newPublishers = activeFilters.publisher.includes(publisher)
      ? activeFilters.publisher.filter(p => p !== publisher)
      : [...activeFilters.publisher, publisher];
    
    updateFilters('publisher', newPublishers);
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div>
        <h3 className="text-sm font-medium text-gray-900 mb-3">Format</h3>
        <div className="space-y-2">
          {mockFormats.map((format) => (
            <div key={format.value} className="flex items-center">
              <input
                id={`format-${format.value}`}
                name={`format-${format.value}`}
                type="checkbox"
                checked={activeFilters.format.includes(format.value)}
                onChange={() => handleFormatChange(format.value)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor={`format-${format.value}`} className="ml-2 text-sm text-gray-700">
                {format.label}
              </label>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-sm font-medium text-gray-900 mb-3">Category</h3>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {mockCategories.map((category) => (
            <div key={category.value} className="flex items-center">
              <input
                id={`category-${category.value}`}
                name={`category-${category.value}`}
                type="checkbox"
                checked={activeFilters.category.includes(category.value)}
                onChange={() => handleCategoryChange(category.value)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor={`category-${category.value}`} className="ml-2 text-sm text-gray-700">
                {category.label}
              </label>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-sm font-medium text-gray-900 mb-3">Publisher</h3>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {mockPublishers.map((publisher) => (
            <div key={publisher.value} className="flex items-center">
              <input
                id={`publisher-${publisher.value}`}
                name={`publisher-${publisher.value}`}
                type="checkbox"
                checked={activeFilters.publisher.includes(publisher.value)}
                onChange={() => handlePublisherChange(publisher.value)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor={`publisher-${publisher.value}`} className="ml-2 text-sm text-gray-700">
                {publisher.label}
              </label>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FilterPanel;