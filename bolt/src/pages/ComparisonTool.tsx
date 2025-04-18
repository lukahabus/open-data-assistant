import React, { useState } from 'react';
import { Code, Database, Sparkles, RefreshCw } from 'lucide-react';

const ComparisonTool = () => {
  const [query, setQuery] = useState('show me all streets in Zagreb named after famous painters');
  const [isExecuting, setIsExecuting] = useState(false);
  const [showResults, setShowResults] = useState(false);

  const examples = [
    'show me all streets in Zagreb named after famous painters',
    'find datasets about air quality in European capitals',
    'which transportation datasets overlap with tourism datasets',
    'compare spending on education across EU countries for 2020-2022'
  ];

  const handleExecute = () => {
    if (!query.trim()) return;
    
    setIsExecuting(true);
    
    // Simulate query execution
    setTimeout(() => {
      setIsExecuting(false);
      setShowResults(true);
    }, 2000);
  };

  const handleExampleClick = (example: string) => {
    setQuery(example);
    setShowResults(false);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Query Comparison Tool</h1>
        <p className="mt-2 text-gray-600">
          Compare SPARQL and LLM approaches for querying linked open data
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-sm overflow-hidden mb-8">
        <div className="p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Natural Language Query</h2>
          
          <div className="mb-4">
            <textarea
              rows={3}
              name="query"
              id="query"
              className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
              placeholder="Enter your query in natural language..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          
          <div className="flex flex-wrap gap-2 mb-4">
            <span className="text-sm text-gray-500">Examples:</span>
            {examples.map((example, index) => (
              <button
                key={index}
                onClick={() => handleExampleClick(example)}
                className="inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                {example}
              </button>
            ))}
          </div>
          
          <button
            onClick={handleExecute}
            disabled={isExecuting || !query.trim()}
            className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
              isExecuting || !query.trim() ? 'bg-blue-400' : 'bg-blue-600 hover:bg-blue-700'
            } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
          >
            {isExecuting ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </>
            ) : (
              <>
                <RefreshCw className="h-4 w-4 mr-2" />
                Execute Query
              </>
            )}
          </button>
        </div>
      </div>

      {showResults && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* SPARQL Approach */}
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <div className="bg-purple-50 p-4 border-b border-purple-100 flex items-center">
              <Code className="h-5 w-5 text-purple-600 mr-2" />
              <h2 className="text-lg font-semibold text-purple-900">SPARQL Approach</h2>
            </div>
            <div className="p-6">
              <div className="mb-4">
                <h3 className="text-sm font-medium text-gray-900 mb-2">Generated SPARQL Query</h3>
                <div className="bg-gray-50 p-4 rounded-md overflow-x-auto">
                  <pre className="text-sm text-gray-800 whitespace-pre-wrap">
{`PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?streetName ?painterName
WHERE {
  ?street a dcat:Dataset ;
          dct:title ?streetName ;
          dct:spatial "Zagreb" ;
          dct:type "Street" .
  
  ?painter a dcat:Dataset ;
           dct:title ?painterName ;
           dct:subject "Painter" .
  
  ?street dct:subject ?subject .
  ?painter dct:subject ?subject .
}`}
                  </pre>
                </div>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-gray-900 mb-2">Query Results</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Street Name
                        </th>
                        <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Painter Name
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      <tr>
                        <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">Bukovačka Ulica</td>
                        <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">Vlaho Bukovac</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">Ulica Miroslava Kraljevića</td>
                        <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">Miroslav Kraljević</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">Ulica Emanuela Vidovića</td>
                        <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">Emanuel Vidović</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">Ulica Slave Raškaj</td>
                        <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">Slava Raškaj</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              
              <div className="mt-4">
                <h3 className="text-sm font-medium text-gray-900 mb-2">SPARQL Characteristics</h3>
                <ul className="list-disc pl-5 text-sm text-gray-600 space-y-1">
                  <li>Precise, structured query language for RDF data</li>
                  <li>Requires knowledge of dataset schema and ontology</li>
                  <li>Supports complex joins and filters</li>
                  <li>Limited by exact matching of terms</li>
                  <li>Results are deterministic and reproducible</li>
                </ul>
              </div>
            </div>
          </div>
          
          {/* LLM Approach */}
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <div className="bg-blue-50 p-4 border-b border-blue-100 flex items-center">
              <Sparkles className="h-5 w-5 text-blue-600 mr-2" />
              <h2 className="text-lg font-semibold text-blue-900">LLM Approach</h2>
            </div>
            <div className="p-6">
              <div className="mb-4">
                <h3 className="text-sm font-medium text-gray-900 mb-2">LLM Processing</h3>
                <div className="bg-gray-50 p-4 rounded-md overflow-x-auto">
                  <pre className="text-sm text-gray-800 whitespace-pre-wrap">
{`1. Analyzing natural language query
2. Identifying key entities: "streets", "Zagreb", "painters"
3. Searching for datasets containing relevant metadata
4. Finding datasets: "Zagreb Streets", "Croatian Artists"
5. Analyzing DCAT metadata relationships
6. Creating semantic connections between datasets
7. Extracting and formatting matching results`}
                  </pre>
                </div>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-gray-900 mb-2">Query Results</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Street Name
                        </th>
                        <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Painter Name
                        </th>
                        <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Confidence
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      <tr>
                        <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">Bukovačka Ulica</td>
                        <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">Vlaho Bukovac</td>
                        <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">0.95</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">Ulica Miroslava Kraljevića</td>
                        <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">Miroslav Kraljević</td>
                        <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">0.92</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">Ulica Emanuela Vidovića</td>
                        <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">Emanuel Vidović</td>
                        <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">0.89</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">Ulica Slave Raškaj</td>
                        <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">Slava Raškaj</td>
                        <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">0.88</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">Medulićeva Ulica</td>
                        <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">Andrija Medulić</td>
                        <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">0.77</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              
              <div className="mt-4">
                <h3 className="text-sm font-medium text-gray-900 mb-2">LLM Characteristics</h3>
                <ul className="list-disc pl-5 text-sm text-gray-600 space-y-1">
                  <li>Natural language understanding without schema knowledge</li>
                  <li>Semantic understanding of concepts beyond exact matches</li>
                  <li>Can make connections across heterogeneous datasets</li>
                  <li>Results include confidence scores for uncertainty</li>
                  <li>May find additional relevant results through inference</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {showResults && (
        <div className="mt-8 bg-white rounded-lg shadow-sm overflow-hidden">
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Approach Comparison</h2>
            
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Feature
                    </th>
                    <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      SPARQL
                    </th>
                    <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      LLM
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  <tr>
                    <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-gray-900">Query complexity</td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-700">High (requires expertise)</td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-700">Low (natural language)</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-gray-900">Schema knowledge</td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-700">Required</td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-700">Not required</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-gray-900">Result precision</td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-700">High (exact matching)</td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-700">Variable (semantic matching)</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-gray-900">Result coverage</td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-700">Limited to explicit relationships</td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-700">Can discover implicit connections</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-gray-900">Performance</td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-700">Fast for indexed data</td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-700">Computationally intensive</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-gray-900">Handling ambiguity</td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-700">Poor (requires precise queries)</td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-700">Good (handles context and meaning)</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-gray-900">Standardization</td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-700">W3C standard</td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-700">Implementation-dependent</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ComparisonTool;