import React from 'react';
import { Link } from 'react-router-dom';
import { Database, LineChart, BarChart4, Search } from 'lucide-react';

const HomePage = () => {
  return (
    <div className="flex flex-col space-y-16 py-8 px-4 sm:px-6 lg:px-8">
      {/* Hero Section */}
      <section className="max-w-7xl mx-auto text-center pt-8 pb-12">
        <h1 className="text-4xl tracking-tight font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
          <span className="block">Open Dataset</span>
          <span className="block text-blue-600">Metadata Analyzer</span>
        </h1>
        <p className="mt-6 max-w-2xl mx-auto text-xl text-gray-500">
          Discover connections and insights from open datasets using advanced LLM technology
        </p>
        <div className="mt-8 flex justify-center gap-x-4">
          <Link
            to="/explorer"
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 transition-colors duration-150"
          >
            Explore Datasets
          </Link>
          <Link
            to="/analyzer"
            className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 transition-colors duration-150"
          >
            Try LLM Analyzer
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section className="max-w-7xl mx-auto">
        <h2 className="text-3xl font-extrabold text-gray-900 text-center mb-12">
          Key Features
        </h2>
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
          <div className="relative bg-white p-6 rounded-lg shadow-md transform hover:-translate-y-1 transition-transform duration-300">
            <div className="absolute -top-4 left-6 bg-blue-100 rounded-full p-3">
              <Database className="h-6 w-6 text-blue-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mt-4">Dataset Explorer</h3>
            <p className="mt-2 text-gray-600">
              Browse and search open datasets with rich DCAT metadata visualization
            </p>
          </div>
          
          <div className="relative bg-white p-6 rounded-lg shadow-md transform hover:-translate-y-1 transition-transform duration-300">
            <div className="absolute -top-4 left-6 bg-teal-100 rounded-full p-3">
              <LineChart className="h-6 w-6 text-teal-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mt-4">LLM Analysis</h3>
            <p className="mt-2 text-gray-600">
              Discover hidden connections between datasets using AI-powered analysis
            </p>
          </div>
          
          <div className="relative bg-white p-6 rounded-lg shadow-md transform hover:-translate-y-1 transition-transform duration-300">
            <div className="absolute -top-4 left-6 bg-purple-100 rounded-full p-3">
              <BarChart4 className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mt-4">Query Comparison</h3>
            <p className="mt-2 text-gray-600">
              Compare SPARQL and LLM approaches for querying linked open data
            </p>
          </div>
          
          <div className="relative bg-white p-6 rounded-lg shadow-md transform hover:-translate-y-1 transition-transform duration-300">
            <div className="absolute -top-4 left-6 bg-orange-100 rounded-full p-3">
              <Search className="h-6 w-6 text-orange-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mt-4">Natural Language</h3>
            <p className="mt-2 text-gray-600">
              Query datasets using natural language instead of complex query languages
            </p>
          </div>
        </div>
      </section>

      {/* Use Case Section */}
      <section className="max-w-7xl mx-auto bg-white rounded-lg shadow-md overflow-hidden">
        <div className="md:flex">
          <div className="md:shrink-0 bg-gradient-to-r from-blue-500 to-teal-500 md:w-48 flex items-center justify-center p-8">
            <Search className="h-24 w-24 text-white" />
          </div>
          <div className="p-8">
            <div className="uppercase tracking-wide text-sm text-blue-600 font-semibold">Example Use Case</div>
            <h3 className="mt-1 text-2xl font-semibold text-gray-900">
              Finding Zagreb Streets Named After Famous Painters
            </h3>
            <p className="mt-4 text-gray-600">
              Our system makes it easy to connect datasets like "Streets in Zagreb" with "Famous Croatian Artists" 
              to answer complex queries like "show me all streets in Zagreb named after famous painters" without 
              writing complex SPARQL or SQL queries.
            </p>
            <div className="mt-6">
              <Link
                to="/comparison"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 transition-colors duration-150"
              >
                Try This Example
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;