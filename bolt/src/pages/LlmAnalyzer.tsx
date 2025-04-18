import React, { useState } from 'react';
import { Search, Sparkles, BadgeInfo, AlertTriangle } from 'lucide-react';
import { mockDatasets } from '../data/mockData';
import RelationshipGraph from '../components/analyzer/RelationshipGraph';

const LlmAnalyzer = () => {
  const [query, setQuery] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState<any | null>(null);
  const [selectedDatasets, setSelectedDatasets] = useState<string[]>([]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setAnalyzing(true);

    // Simulate LLM analysis
    setTimeout(() => {
      // Mock result based on the query
      const mockResult = {
        relatedDatasets: mockDatasets.slice(0, 3),
        connections: [
          { 
            source: mockDatasets[0].id, 
            target: mockDatasets[1].id, 
            strength: 0.85,
            relationship: "Spatial overlap - both cover Zagreb city area" 
          },
          { 
            source: mockDatasets[0].id, 
            target: mockDatasets[2].id, 
            strength: 0.72,
            relationship: "Subject relationship - streets named after artists" 
          },
          { 
            source: mockDatasets[1].id, 
            target: mockDatasets[2].id, 
            strength: 0.63,
            relationship: "Temporal relationship - data from the same period" 
          }
        ],
        suggestedQuery: `
SELECT ?street ?painter
WHERE {
  ?street a dcat:Dataset ;
          dct:title ?streetName ;
          dct:spatial "Zagreb" .
  
  ?painter a dcat:Dataset ;
           dct:title ?painterName ;
           dct:type "Artist" ;
           dct:subject "Painting" .
  
  ?street dct:relation ?painter .
}
        `
      };

      setResults(mockResult);
      setSelectedDatasets(mockResult.relatedDatasets.map(d => d.id));
      setAnalyzing(false);
    }, 2000);
  };

  const handleDatasetToggle = (datasetId: string) => {
    setSelectedDatasets(prev => 
      prev.includes(datasetId)
        ? prev.filter(id => id !== datasetId)
        : [...prev, datasetId]
    );
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">LLM Dataset Analyzer</h1>
        <p className="mt-2 text-gray-600">
          Discover connections between datasets using natural language and AI-powered analysis
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Natural Language Query</h2>
            <form onSubmit={handleSubmit}>
              <div className="mt-1">
                <textarea
                  rows={4}
                  name="query"
                  id="query"
                  className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  placeholder="e.g., Find streets in Zagreb named after famous painters"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />
              </div>
              <div className="mt-4">
                <button
                  type="submit"
                  disabled={analyzing || !query.trim()}
                  className={`w-full inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
                    analyzing || !query.trim() ? 'bg-blue-400' : 'bg-blue-600 hover:bg-blue-700'
                  } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
                >
                  {analyzing ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-5 w-5 mr-2" />
                      Analyze with LLM
                    </>
                  )}
                </button>
              </div>
            </form>

            {results && (
              <div className="mt-8">
                <h3 className="text-lg font-medium text-gray-900 mb-2">Related Datasets</h3>
                <div className="space-y-3">
                  {results.relatedDatasets.map((dataset) => (
                    <div key={dataset.id} className="flex items-start">
                      <input
                        type="checkbox"
                        checked={selectedDatasets.includes(dataset.id)}
                        onChange={() => handleDatasetToggle(dataset.id)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 mt-1"
                      />
                      <div className="ml-3">
                        <p className="text-sm font-medium text-gray-900">{dataset.title}</p>
                        <p className="text-xs text-gray-500">{dataset.format} • {dataset.publisher}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="mt-8 p-4 bg-blue-50 rounded-md border border-blue-100">
              <div className="flex">
                <div className="flex-shrink-0">
                  <BadgeInfo className="h-5 w-5 text-blue-400" />
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-blue-800">LLM Analysis</h3>
                  <div className="mt-2 text-sm text-blue-700">
                    <p>Our system uses large language models to analyze dataset metadata and discover meaningful connections between different datasets.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="lg:col-span-2">
          {!results && !analyzing && (
            <div className="bg-white rounded-lg shadow-sm p-6 flex flex-col items-center justify-center h-full">
              <Search className="h-16 w-16 text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900">Enter a query to analyze datasets</h3>
              <p className="mt-1 text-sm text-gray-500 text-center max-w-md">
                Use natural language to describe what connections you'd like to find between open datasets
              </p>
            </div>
          )}

          {analyzing && (
            <div className="bg-white rounded-lg shadow-sm p-6 flex flex-col items-center justify-center h-full">
              <div className="flex flex-col items-center">
                <div className="animate-pulse flex space-x-4 items-center mb-8">
                  <div className="h-12 w-12 bg-blue-200 rounded-full"></div>
                  <div className="flex-1 space-y-4">
                    <div className="h-4 bg-blue-200 rounded w-3/4"></div>
                    <div className="h-4 bg-blue-200 rounded"></div>
                    <div className="h-4 bg-blue-200 rounded w-5/6"></div>
                  </div>
                </div>
                <p className="text-gray-600">The LLM is analyzing dataset metadata and finding connections...</p>
              </div>
            </div>
          )}

          {results && !analyzing && (
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Dataset Relationships</h2>
              
              <div className="mb-6 h-96 border border-gray-200 rounded-lg">
                <RelationshipGraph 
                  datasets={results.relatedDatasets.filter(d => selectedDatasets.includes(d.id))} 
                  connections={results.connections.filter(c => 
                    selectedDatasets.includes(c.source) && selectedDatasets.includes(c.target)
                  )} 
                />
              </div>

              <div className="mt-6">
                <h3 className="text-lg font-medium text-gray-900 mb-2">Suggested SPARQL Query</h3>
                <div className="bg-gray-50 p-4 rounded-md">
                  <pre className="text-sm text-gray-800 whitespace-pre-wrap">{results.suggestedQuery}</pre>
                </div>
              </div>

              <div className="mt-6 flex items-start p-4 bg-yellow-50 rounded-md border border-yellow-100">
                <div className="flex-shrink-0">
                  <AlertTriangle className="h-5 w-5 text-yellow-400" />
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-yellow-800">Prototype Limitation</h3>
                  <div className="mt-2 text-sm text-yellow-700">
                    <p>This is a prototype demonstration with simulated results. In a production environment, this would use real LLM analysis of actual DCAT metadata from connected datasets.</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LlmAnalyzer;