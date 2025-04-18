import React, { useState } from 'react';
import { File, ExternalLink, ChevronDown, ChevronUp, Tag } from 'lucide-react';
import { Dataset } from '../../types/dataset';

interface DatasetCardProps {
  dataset: Dataset;
}

const DatasetCard: React.FC<DatasetCardProps> = ({ dataset }) => {
  const [expanded, setExpanded] = useState(false);

  const toggleExpand = () => {
    setExpanded(!expanded);
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow duration-300">
      <div className="p-5">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center">
              <File className={`h-5 w-5 mr-2 text-${dataset.formatColor}-500`} />
              <span className="text-xs font-medium px-2.5 py-0.5 rounded bg-gray-100 text-gray-800">
                {dataset.format}
              </span>
            </div>
            <h3 className="mt-2 text-lg font-semibold text-gray-900 line-clamp-2">
              {dataset.title}
            </h3>
          </div>
        </div>
        
        <p className="mt-2 text-gray-600 text-sm line-clamp-3">
          {dataset.description}
        </p>

        <div className="mt-4 flex flex-wrap gap-2">
          {dataset.categories.slice(0, 3).map((category, index) => (
            <span 
              key={index} 
              className="inline-flex items-center text-xs px-2 py-1 rounded-full bg-blue-50 text-blue-700"
            >
              <Tag className="h-3 w-3 mr-1" />
              {category}
            </span>
          ))}
          {dataset.categories.length > 3 && (
            <span className="text-xs text-gray-500">+{dataset.categories.length - 3} more</span>
          )}
        </div>

        <div className="mt-4 text-xs text-gray-500">
          <div>Publisher: <span className="font-medium">{dataset.publisher}</span></div>
          <div>Updated: <span className="font-medium">{dataset.updated}</span></div>
        </div>

        <div className="mt-4 flex items-center justify-between">
          <a 
            href={dataset.url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-800"
          >
            View Source <ExternalLink className="ml-1 h-3 w-3" />
          </a>
          <button
            onClick={toggleExpand}
            className="inline-flex items-center text-sm font-medium text-gray-500 hover:text-gray-700"
          >
            {expanded ? (
              <>Hide Details <ChevronUp className="ml-1 h-4 w-4" /></>
            ) : (
              <>Show Details <ChevronDown className="ml-1 h-4 w-4" /></>
            )}
          </button>
        </div>

        {/* Expanded content */}
        {expanded && (
          <div className="mt-4 border-t border-gray-200 pt-4">
            <h4 className="text-sm font-medium text-gray-900">DCAT Metadata</h4>
            <div className="mt-2 space-y-2 text-sm text-gray-600">
              <div><span className="font-medium">Identifier:</span> {dataset.identifier}</div>
              <div><span className="font-medium">License:</span> {dataset.license}</div>
              <div><span className="font-medium">Spatial Coverage:</span> {dataset.spatial}</div>
              <div><span className="font-medium">Temporal Coverage:</span> {dataset.temporal}</div>
              <div><span className="font-medium">Created:</span> {dataset.created}</div>
              <div><span className="font-medium">Access Rights:</span> {dataset.accessRights}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DatasetCard;