import React from 'react';
import { BookOpen, FileCheck, Database, Users } from 'lucide-react';

const About = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">About the Project</h1>
        <p className="mt-2 text-gray-600">
          A system for metadata analysis of open datasets using LLM technology
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-2">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Project Overview</h2>
            <div className="prose max-w-none">
              <p>
                The growing availability of open data does not necessarily imply its greater usability. 
                Although standardized metadata formats (e.g., DCAT) make it easier to find and interpret 
                published individual datasets, additional value lies in connecting them and finding new 
                insights and hidden knowledge.
              </p>
              <p>
                The rapid rise of artificial intelligence tools based on large language models represents 
                a promising direction for developing tools that would provide ordinary users with new insights 
                into and use of open data.
              </p>
              <p>
                This project explores the capabilities of large language models and techniques for automated 
                searching of connections between datasets. It proposes a tool for retrieving and analyzing 
                metadata of open datasets, as well as providing support to users in connecting datasets based 
                on metadata analysis.
              </p>
              <p>
                The prototype system is implemented for the CKAN portal using tools based on large language 
                models, with an evaluation of the system's usability.
              </p>
            </div>

            <h2 className="text-xl font-semibold text-gray-900 mt-8 mb-4">Key Technologies</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="border border-gray-200 rounded-lg p-4">
                <h3 className="flex items-center text-lg font-medium text-gray-900 mb-2">
                  <Database className="h-5 w-5 mr-2 text-blue-500" />
                  DCAT (Data Catalog Vocabulary)
                </h3>
                <p className="text-gray-600 text-sm">
                  A W3C recommendation designed to facilitate interoperability between data catalogs 
                  published on the Web. DCAT enables better discovery of datasets and data services.
                </p>
              </div>
              <div className="border border-gray-200 rounded-lg p-4">
                <h3 className="flex items-center text-lg font-medium text-gray-900 mb-2">
                  <FileCheck className="h-5 w-5 mr-2 text-purple-500" />
                  SPARQL
                </h3>
                <p className="text-gray-600 text-sm">
                  A semantic query language for databases, able to retrieve and manipulate data stored 
                  in Resource Description Framework (RDF) format. It allows complex queries across diverse data sources.
                </p>
              </div>
              <div className="border border-gray-200 rounded-lg p-4">
                <h3 className="flex items-center text-lg font-medium text-gray-900 mb-2">
                  <BookOpen className="h-5 w-5 mr-2 text-teal-500" />
                  Large Language Models
                </h3>
                <p className="text-gray-600 text-sm">
                  Advanced AI systems trained on vast amounts of text data that can understand, generate, 
                  and analyze natural language. They enable semantic understanding of dataset descriptions.
                </p>
              </div>
              <div className="border border-gray-200 rounded-lg p-4">
                <h3 className="flex items-center text-lg font-medium text-gray-900 mb-2">
                  <Users className="h-5 w-5 mr-2 text-orange-500" />
                  CKAN
                </h3>
                <p className="text-gray-600 text-sm">
                  An open-source data management system that makes data accessible by providing tools to 
                  streamline publishing, sharing, finding, and using data. Used by many open data portals worldwide.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div>
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Research Objectives</h2>
            <ul className="space-y-4">
              <li className="flex">
                <span className="flex-shrink-0 flex items-center justify-center h-6 w-6 rounded-full bg-blue-100 text-blue-800 text-sm font-medium">1</span>
                <span className="ml-3 text-gray-600">Study the capabilities of large language models for metadata analysis</span>
              </li>
              <li className="flex">
                <span className="flex-shrink-0 flex items-center justify-center h-6 w-6 rounded-full bg-blue-100 text-blue-800 text-sm font-medium">2</span>
                <span className="ml-3 text-gray-600">Explore DCAT norm for describing open data sets</span>
              </li>
              <li className="flex">
                <span className="flex-shrink-0 flex items-center justify-center h-6 w-6 rounded-full bg-blue-100 text-blue-800 text-sm font-medium">3</span>
                <span className="ml-3 text-gray-600">Investigate possibilities for automated connection discovery between datasets</span>
              </li>
              <li className="flex">
                <span className="flex-shrink-0 flex items-center justify-center h-6 w-6 rounded-full bg-blue-100 text-blue-800 text-sm font-medium">4</span>
                <span className="ml-3 text-gray-600">Develop a prototype system for the CKAN portal</span>
              </li>
              <li className="flex">
                <span className="flex-shrink-0 flex items-center justify-center h-6 w-6 rounded-full bg-blue-100 text-blue-800 text-sm font-medium">5</span>
                <span className="ml-3 text-gray-600">Compare SPARQL and LLM approaches for metadata analysis</span>
              </li>
            </ul>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6 mt-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Resources</h2>
            <ul className="space-y-3">
              <li>
                <a 
                  href="https://www.w3.org/TR/vocab-dcat-2/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 hover:underline flex items-center"
                >
                  <BookOpen className="h-4 w-4 mr-2" />
                  DCAT Specification
                </a>
              </li>
              <li>
                <a 
                  href="https://www.w3.org/TR/rdf-sparql-query/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 hover:underline flex items-center"
                >
                  <BookOpen className="h-4 w-4 mr-2" />
                  SPARQL Query Language
                </a>
              </li>
              <li>
                <a 
                  href="https://ckan.org/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 hover:underline flex items-center"
                >
                  <BookOpen className="h-4 w-4 mr-2" />
                  CKAN Open Data Platform
                </a>
              </li>
              <li>
                <a 
                  href="https://github.com/ckan/ckanext-dcat" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 hover:underline flex items-center"
                >
                  <BookOpen className="h-4 w-4 mr-2" />
                  CKAN DCAT Extension
                </a>
              </li>
              <li>
                <a 
                  href="https://data.europa.eu/en" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 hover:underline flex items-center"
                >
                  <BookOpen className="h-4 w-4 mr-2" />
                  European Data Portal
                </a>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default About;