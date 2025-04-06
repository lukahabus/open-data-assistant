"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ArrowPathIcon, DocumentTextIcon, TagIcon, CalendarIcon, UserIcon } from "@heroicons/react/24/outline"

export default function MetadataAnalyzer() {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [selectedDataset, setSelectedDataset] = useState({
    title: "COVID-19 Cases by Region",
    description: "Daily COVID-19 case counts by region, including confirmed cases, recoveries, and fatalities.",
    publisher: "Health Ministry",
    created: "2023-01-15",
    updated: "2023-05-15",
    format: "CSV",
    license: "CC BY 4.0",
    tags: ["health", "covid-19", "statistics", "regions", "daily-updates"],
  })

  const [analysis, setAnalysis] = useState({
    quality: 85,
    completeness: 92,
    accuracy: 78,
    consistency: 88,
    suggestions: [
      "Add temporal coverage metadata",
      "Include geographic coordinates for regions",
      "Add data dictionary for column descriptions",
    ],
  })

  const handleAnalyze = () => {
    setIsAnalyzing(true)
    // Simulate analysis with LLM
    setTimeout(() => {
      setAnalysis({
        quality: Math.floor(Math.random() * 20) + 75,
        completeness: Math.floor(Math.random() * 20) + 75,
        accuracy: Math.floor(Math.random() * 20) + 75,
        consistency: Math.floor(Math.random() * 20) + 75,
        suggestions: [
          "Add temporal coverage metadata",
          "Include geographic coordinates for regions",
          "Add data dictionary for column descriptions",
          "Specify update frequency in metadata",
        ],
      })
      setIsAnalyzing(false)
    }, 2000)
  }

  return (
    <Card className="col-span-1">
      <CardHeader>
        <CardTitle>Metadata Analyzer</CardTitle>
        <CardDescription>Analyze dataset metadata using LLM techniques</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="metadata">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="metadata">Metadata</TabsTrigger>
            <TabsTrigger value="analysis">Analysis</TabsTrigger>
          </TabsList>
          <TabsContent value="metadata" className="space-y-4">
            <div className="space-y-4 mt-4">
              <div className="space-y-2">
                <h3 className="text-lg font-medium flex items-center">
                  <DocumentTextIcon className="h-5 w-5 mr-2" />
                  {selectedDataset.title}
                </h3>
                <p className="text-sm text-muted-foreground">{selectedDataset.description}</p>
              </div>

              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="flex items-center space-x-2">
                  <UserIcon className="h-4 w-4 text-muted-foreground" />
                  <span>{selectedDataset.publisher}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CalendarIcon className="h-4 w-4 text-muted-foreground" />
                  <span>Updated: {selectedDataset.updated}</span>
                </div>
              </div>

              <div className="pt-2">
                <div className="text-sm font-medium mb-2">Tags:</div>
                <div className="flex flex-wrap gap-2">
                  {selectedDataset.tags.map((tag) => (
                    <Badge key={tag} variant="secondary" className="flex items-center">
                      <TagIcon className="h-3 w-3 mr-1" />
                      {tag}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          </TabsContent>
          <TabsContent value="analysis" className="space-y-4">
            <div className="space-y-4 mt-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <div className="text-sm font-medium">Quality Score</div>
                  <div className="flex items-center">
                    <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                      <div className="h-full bg-primary" style={{ width: `${analysis.quality}%` }} />
                    </div>
                    <span className="ml-2 text-sm font-medium">{analysis.quality}%</span>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="text-sm font-medium">Completeness</div>
                  <div className="flex items-center">
                    <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                      <div className="h-full bg-green-500" style={{ width: `${analysis.completeness}%` }} />
                    </div>
                    <span className="ml-2 text-sm font-medium">{analysis.completeness}%</span>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="text-sm font-medium">Accuracy</div>
                  <div className="flex items-center">
                    <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                      <div className="h-full bg-blue-500" style={{ width: `${analysis.accuracy}%` }} />
                    </div>
                    <span className="ml-2 text-sm font-medium">{analysis.accuracy}%</span>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="text-sm font-medium">Consistency</div>
                  <div className="flex items-center">
                    <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                      <div className="h-full bg-purple-500" style={{ width: `${analysis.consistency}%` }} />
                    </div>
                    <span className="ml-2 text-sm font-medium">{analysis.consistency}%</span>
                  </div>
                </div>
              </div>

              <div className="space-y-2 pt-2">
                <div className="text-sm font-medium">Improvement Suggestions:</div>
                <ul className="text-sm space-y-1">
                  {analysis.suggestions.map((suggestion, index) => (
                    <li key={index} className="flex items-start">
                      <span className="mr-2">•</span>
                      <span>{suggestion}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
      <CardFooter className="border-t px-6 py-4">
        <Button onClick={handleAnalyze} disabled={isAnalyzing} className="w-full">
          {isAnalyzing ? (
            <>
              <ArrowPathIcon className="h-4 w-4 mr-2 animate-spin" />
              Analyzing with LLM...
            </>
          ) : (
            "Analyze Metadata with LLM"
          )}
        </Button>
      </CardFooter>
    </Card>
  )
}

