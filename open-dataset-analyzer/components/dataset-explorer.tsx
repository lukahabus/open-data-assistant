"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog"
import {
  ArrowDownTrayIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  InformationCircleIcon,
  TableCellsIcon,
} from "@heroicons/react/24/outline"
import type { Dataset, Resource, Tag, Extra } from "@/lib/ckan-api"
import { importDataset } from "@/app/actions/import-dataset"
import { useToast } from "@/components/ui/use-toast"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"

// Helper function to generate a date string between start and end
const randomDate = (start: Date, end: Date): string => {
  const date = new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
  return date.toISOString(); // Keep ISO format for internal consistency
}

// Helper to create mock resources
const createMockResource = (id: string, datasetId: string, format: string, index: number): Resource => ({
  id: `r-${datasetId}-${index}`,
  name: `${format.toUpperCase()} Resource ${index + 1}`,
  description: `This is the resource number ${index + 1} for dataset ${datasetId}.`,
  format: format,
  url: `https://example.com/data/${datasetId}/resource_${index + 1}.${format.toLowerCase()}`,
  created: randomDate(new Date(2022, 0, 1), new Date(2023, 0, 1)),
  last_modified: randomDate(new Date(2023, 0, 1), new Date(2024, 0, 1)),
  size: Math.floor(Math.random() * 5000000) + 100000, // Random size between 100KB and 5MB
});

// Mock organization names
const mockOrgs = [
  { name: "health-dept", title: "Ministry of Health" },
  { name: "transport-corp", title: "National Transport Corp." },
  { name: "env-agency", title: "Environmental Protection Agency" },
  { name: "stats-office", title: "Central Statistics Office" },
  { name: "city-planning", title: "City Planning Department" },
  { name: "agri-data", title: "Agriculture Data Hub" },
  { name: "finance-board", title: "National Finance Board" },
  { name: "education-stats", title: "Education Statistics Unit" },
];

// Mock tags
const mockTags = ["health", "covid", "transport", "schedule", "environment", "air quality", "pollution", "economy", "statistics", "census", "urban", "planning", "agriculture", "crops", "finance", "budget", "education", "schools"];

// Function to get random subset of tags
const getRandomTags = (count: number = 3): Tag[] => {
  const shuffled = [...mockTags].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, count).map((tag, i) => ({ id: `t-${tag}-${i}`, name: tag, display_name: tag.charAt(0).toUpperCase() + tag.slice(1) }));
}

// Function to create mock extras
const getRandomExtras = (): Extra[] => {
    const extras: Extra[] = [
        { key: 'Update Frequency', value: ['Annual', 'Quarterly', 'Monthly', 'Daily'][Math.floor(Math.random()*4)] },
        { key: 'Spatial Coverage', value: ['National', 'Regional', 'City'][Math.floor(Math.random()*3)] },
    ];
    if (Math.random() > 0.5) {
        extras.push({ key: 'Temporal Coverage', value: `2020-${2022 + Math.floor(Math.random()*3)}` })
    }
    return extras;
}

// Function to generate the mock datasets (will be called inside useEffect)
const generateInitialMockDatasets = (): Dataset[] => {
  return Array.from({ length: 10 }, (_, i) => {
    const datasetId = `ds-${i + 1}`;
    const org = mockOrgs[i % mockOrgs.length];
    const tag = mockTags[i % mockTags.length];
    const title = `${tag.charAt(0).toUpperCase() + tag.slice(1)} Data from ${org.title}`;
    const createdDate = randomDate(new Date(2022, 0, 1), new Date(2023, 6, 1));
    const modifiedDate = randomDate(new Date(createdDate), new Date());
    const numResources = Math.floor(Math.random() * 3) + 1;
    const formats = ['CSV', 'JSON', 'XML', 'XLSX', 'GeoJSON'];

    return {
      id: datasetId,
      name: title.toLowerCase().replace(/ /g, '-').replace(/[^a-z0-9-]/g, ''),
      title: title,
      notes: `This is a detailed description for Mock Dataset ${String.fromCharCode(65 + i)}. It contains valuable information about ${mockTags[i % mockTags.length]}. The data covers the period mentioned in the extras and is updated regularly.`,
      metadata_created: createdDate,
      metadata_modified: modifiedDate,
      organization: org,
      resources: Array.from({ length: numResources }, (__, rIndex) =>
        createMockResource(datasetId, datasetId, formats[Math.floor(Math.random() * formats.length)], rIndex)
      ),
      tags: getRandomTags(Math.floor(Math.random() * 3) + 2),
      extras: getRandomExtras(),
    };
  });
}

export default function DatasetExplorer() {
  const { toast } = useToast()
  const [datasetUrl, setDatasetUrl] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [importError, setImportError] = useState<string | null>(null)
  const [importSuccess, setImportSuccess] = useState<string | null>(null)
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null)

  // Generate mock data on client mount
  useEffect(() => {
    // Only generate if datasets haven't been loaded (e.g., from API later)
    if (datasets.length === 0) { 
        const mockData = generateInitialMockDatasets();
        setDatasets(mockData);
    }
  }, []); // Empty dependency array ensures this runs only once on mount

  const handleFetchDataset = async (event: React.FormEvent) => {
    event.preventDefault()

    if (!datasetUrl) {
      setImportError("Please enter a dataset URL")
      return
    }

    setIsLoading(true)
    setImportError(null)
    setImportSuccess(null)

    try {
      const formData = new FormData()
      formData.append("datasetUrl", datasetUrl)

      const result = await importDataset(formData)

      if (result.success && result.dataset) {
        // Add the new dataset to the list
        setDatasets([result.dataset, ...datasets])
        setImportSuccess(`Successfully imported "${result.dataset.title}"`)
        setDatasetUrl("")

        toast({
          title: "Dataset imported",
          description: `Successfully imported "${result.dataset.title}"`,
        })
      } else {
        setImportError(result.error || "Failed to import dataset")

        toast({
          variant: "destructive",
          title: "Import failed",
          description: result.error || "Failed to import dataset",
        })
      }
    } catch (error) {
      console.error("Error importing dataset:", error)
      setImportError("An unexpected error occurred")

      toast({
        variant: "destructive",
        title: "Import failed",
        description: "An unexpected error occurred",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const formatDate = (dateString: string | undefined): string => {
    if (!dateString) return "N/A";
    try {
       const date = new Date(dateString)
       return date.toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit', year: 'numeric' });
    } catch (e) {
        return dateString;
    }
  }

  const handleViewClick = (dataset: Dataset) => {
    setSelectedDataset(dataset);
  }

  return (
    <Card className="col-span-1">
      <CardHeader>
        <CardTitle>Dataset Explorer</CardTitle>
        <CardDescription>Browse and import open datasets for analysis</CardDescription>
      </CardHeader>
      <CardContent>
        <Dialog open={!!selectedDataset} onOpenChange={(isOpen) => { if (!isOpen) setSelectedDataset(null); }}>
          <Tabs defaultValue="browse">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="browse">Browse</TabsTrigger>
              <TabsTrigger value="import">Import</TabsTrigger>
            </TabsList>
            <TabsContent value="browse" className="space-y-4">
              <div className="space-y-4 mt-4">
                {datasets.map((dataset) => (
                  <div key={dataset.id} className="flex flex-col space-y-1 rounded-md border p-3">
                    <div className="font-medium">{dataset.title}</div>
                    <div className="text-sm text-muted-foreground">
                      Publisher: {dataset.organization?.title || "Unknown"}
                    </div>
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>Format: {dataset.resources?.[0]?.format || "Unknown"}</span>
                      <span>Updated: {formatDate(dataset.metadata_modified)}</span>
                    </div>
                    <div className="flex items-center justify-end space-x-2 pt-2">
                      <DialogTrigger asChild>
                        <Button variant="outline" size="sm" onClick={() => handleViewClick(dataset)}>
                          View
                        </Button>
                      </DialogTrigger>
                      <Button size="sm">Analyze</Button>
                    </div>
                  </div>
                ))}
              </div>
            </TabsContent>
            <TabsContent value="import" className="space-y-4">
              <div className="space-y-4 mt-4">
                <Alert className="bg-blue-50 border-blue-200">
                  <InformationCircleIcon className="h-4 w-4 text-blue-600" />
                  <AlertTitle className="text-blue-800">Demo Mode</AlertTitle>
                  <AlertDescription className="text-blue-700">
                    For testing, you can use "sample" or "test" in the URL to import a sample dataset.
                  </AlertDescription>
                </Alert>

                <form onSubmit={handleFetchDataset} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="dataset-url">CKAN Dataset URL</Label>
                    <div className="flex space-x-2">
                      <Input
                        id="dataset-url"
                        placeholder="https://data.gov/dataset/123 or sample-dataset"
                        value={datasetUrl}
                        onChange={(e) => setDatasetUrl(e.target.value)}
                      />
                      <Button type="submit" disabled={isLoading}>
                        {isLoading ? (
                          <ArrowPathIcon className="h-4 w-4 animate-spin" />
                        ) : (
                          <ArrowDownTrayIcon className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </div>

                  {importError && (
                    <Alert variant="destructive">
                      <ExclamationCircleIcon className="h-4 w-4" />
                      <AlertTitle>Error</AlertTitle>
                      <AlertDescription>{importError}</AlertDescription>
                    </Alert>
                  )}

                  {importSuccess && (
                    <Alert variant="default" className="bg-green-50 border-green-200">
                      <CheckCircleIcon className="h-4 w-4 text-green-600" />
                      <AlertTitle className="text-green-800">Success</AlertTitle>
                      <AlertDescription className="text-green-700">{importSuccess}</AlertDescription>
                    </Alert>
                  )}

                  <div className="text-sm text-muted-foreground">
                    <p className="mb-2">Enter the URL of a CKAN dataset to import its metadata for analysis.</p>
                    <p className="font-medium">Supported URL formats:</p>
                    <ul className="list-disc pl-5 space-y-1">
                      <li>https://data.gov/dataset/dataset-id</li>
                      <li>https://data.gov/api/3/action/package_show?id=dataset-id</li>
                      <li>For testing: "sample-dataset" or any URL with "test" in it</li>
                    </ul>
                  </div>
                </form>
              </div>
            </TabsContent>
          </Tabs>

          <DialogContent className="sm:max-w-lg">
            {selectedDataset && (
              <>
                <DialogHeader>
                  <DialogTitle>{selectedDataset.title || "Dataset Details"}</DialogTitle>
                  <DialogDescription>
                    Metadata for dataset: {selectedDataset.name || selectedDataset.id}
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-3 py-4 px-1 text-sm max-h-[60vh] overflow-y-auto pr-6"> 
                   <div className="grid grid-cols-[100px_1fr] items-start gap-y-1 gap-x-2">
                     <Label className="text-right text-muted-foreground pt-0.5">Publisher:</Label>
                     <span>{selectedDataset.organization?.title || "N/A"}</span>

                     <Label className="text-right text-muted-foreground pt-0.5">Created:</Label>
                     <span>{formatDate(selectedDataset.metadata_created)}</span>

                     <Label className="text-right text-muted-foreground pt-0.5">Modified:</Label>
                     <span>{formatDate(selectedDataset.metadata_modified)}</span>
                   </div>

                   {selectedDataset.notes && (
                     <div className="pt-2">
                       <h4 className="font-medium mb-1">Description</h4>
                       <p className="text-muted-foreground bg-muted/30 p-2 rounded border text-xs whitespace-pre-wrap">
                         {selectedDataset.notes}
                       </p>
                     </div>
                   )}

                   {selectedDataset.tags && selectedDataset.tags.length > 0 && (
                     <div className="pt-2">
                       <h4 className="font-medium mb-1">Tags</h4>
                       <div className="flex flex-wrap gap-1">
                         {selectedDataset.tags.map(tag => (
                           <Badge key={tag.id || tag.name} variant="secondary">
                             {tag.display_name || tag.name}
                           </Badge>
                         ))}
                       </div>
                     </div>
                   )}

                   {selectedDataset.extras && selectedDataset.extras.length > 0 && (
                     <div className="pt-2">
                       <h4 className="font-medium mb-1">Additional Info</h4>
                       <dl className="text-xs border rounded p-2 space-y-1 bg-muted/30">
                         {selectedDataset.extras.map(extra => (
                           <div key={extra.key} className="grid grid-cols-[120px_1fr]">
                             <dt className="font-medium text-muted-foreground truncate" title={extra.key}>{extra.key}:</dt>
                             <dd>{extra.value}</dd>
                           </div>
                         ))}
                       </dl>
                     </div>
                   )}

                   {selectedDataset.resources && selectedDataset.resources.length > 0 && (
                      <div className="pt-2">
                        <h4 className="font-medium mb-1 flex items-center"><TableCellsIcon className="w-4 h-4 mr-2"/> Resources ({selectedDataset.resources.length})</h4>
                        <div className="space-y-2 border rounded-md p-2 bg-muted/50 text-xs">
                          {selectedDataset.resources.map(res => (
                            <div key={res.id} className="p-1.5 border-b last:border-b-0">
                              <div className="font-medium mb-0.5">{res.name || res.id}</div>
                              <div className="text-muted-foreground space-x-2 mb-0.5">
                                 <span>Format: {res.format || 'N/A'}</span>
                                 <span>|</span>
                                  <span>Size: {res.size ? `${(res.size / (1024*1024)).toFixed(2)} MB` : 'N/A'}</span>
                                 <span>|</span>
                                 <span>Created: {formatDate(res.created)}</span>
                              </div>
                              {res.description && <p className="text-muted-foreground/80 text-[11px] italic mb-0.5">{res.description}</p>}
                               {res.url && res.url !== '#' && (
                                <a href={res.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline break-all text-[11px]">
                                  {res.url}
                                </a>
                               )}
                            </div>
                          ))}
                        </div>
                      </div>
                   )}
                </div>
                <DialogFooter>
                  <DialogClose asChild>
                    <Button variant="outline">Close</Button>
                  </DialogClose>
                </DialogFooter>
              </>
            )}
          </DialogContent>
        </Dialog>
      </CardContent>
      <CardFooter className="border-t px-6 py-4">
        <Button variant="outline" className="w-full">
          Load More Datasets
        </Button>
      </CardFooter>
    </Card>
  )
}

