import React from 'react';
import { ExternalLink, Github } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-white border-t border-gray-200 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="md:flex md:items-center md:justify-between">
          <div className="flex justify-center md:justify-start space-x-6">
            <a href="https://github.com" className="text-gray-500 hover:text-gray-900" aria-label="GitHub repository">
              <Github className="h-6 w-6" />
            </a>
            <a href="https://www.w3.org/TR/vocab-dcat-2/" className="text-gray-500 hover:text-gray-900" aria-label="DCAT Documentation">
              <ExternalLink className="h-6 w-6" />
            </a>
          </div>
          <div className="mt-8 md:mt-0">
            <p className="text-center md:text-right text-base text-gray-500">
              &copy; {new Date().getFullYear()} Open Dataset Metadata Analyzer. All rights reserved.
            </p>
          </div>
        </div>
        <div className="mt-4 text-center text-sm text-gray-500">
          <p>A system for metadata analysis of open datasets using LLM technology</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;