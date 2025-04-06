"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"

interface DcatViewerProps {
  metadata: any
}

export default function DcatViewer({ metadata }: DcatViewerProps) {
  const [activeTab, setActiveTab] = useState("visual")

  // Sample DCAT metadata for demonstration
  const dcatMetadata = metadata || {
    "@context": "https://www.w3.org/ns/dcat.jsonld",
    "@type": "Dataset",
    title: "COVID-19 Cases by Region",
    description: "Daily COVID-19 case counts by region, including confirmed cases, recoveries, and fatalities.",
    issued: "2023-01-15T00:00:00Z",
    modified: "2023-05-15T00:00:00Z",
    publisher: {
      "@type": "Organization",
      name: "Health Ministry",
    },
    contactPoint: {
      "@type": "vcard:Contact",
      fn: "Data Services",
      hasEmail: "mailto:data@health.gov",
    },
    keyword: ["health", "covid-19", "statistics", "regions", "daily-updates"],
    license: "http://creativecommons.org/licenses/by/4.0/",
    distribution: [
      {
        "@type": "Distribution",
        title: "CSV Download",
        description: "CSV file containing daily COVID-19 cases by region",
        format: "CSV",
        mediaType: "text/csv",
        downloadURL: "https://example.com/datasets/covid19-cases.csv",
      },
    ],
    temporal: {
      startDate: "2020-01-01",
      endDate: "2023-05-15",
    },
    spatial: {
      "@type": "dct:Location",
      geometry: {
        "@type": "gsp:Geometry",
        asWKT: "POLYGON((-10.58 70.09,34.59 70.09,34.59 34.56,-10.58 34.56,-10.58 70.09))",
      },
    },
  }

  const renderJsonView = () => {
    return <pre className="bg-muted p-4 rounded-md overflow-auto text-xs">{JSON.stringify(dcatMetadata, null, 2)}</pre>
  }

  const renderVisualView = () => {
    return (
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-medium">{dcatMetadata.title}</h3>
          <p className="text-sm text-muted-foreground">{dcatMetadata.description}</p>
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <div className="font-medium">Publisher</div>
            <div>{dcatMetadata.publisher?.name}</div>
          </div>
          <div>
            <div className="font-medium">License</div>
            <div>{dcatMetadata.license?.split("/").pop() || dcatMetadata.license}</div>
          </div>
          <div>
            <div className="font-medium">Issued</div>
            <div>{new Date(dcatMetadata.issued).toLocaleDateString()}</div>
          </div>
          <div>
            <div className="font-medium">Modified</div>
            <div>{new Date(dcatMetadata.modified).toLocaleDateString()}</div>
          </div>
        </div>

        <div>
          <div className="font-medium mb-2">Keywords</div>
          <div className="flex flex-wrap gap-2">
            {dcatMetadata.keyword?.map((keyword: string) => (
              <Badge key={keyword} variant="secondary">
                {keyword}
              </Badge>
            ))}
          </div>
        </div>

        <div>
          <div className="font-medium mb-2">Distributions</div>
          <div className="space-y-2">
            {dcatMetadata.distribution?.map((dist: any, index: number) => (
              <div key={index} className="border rounded-md p-2">
                <div className="font-medium">{dist.title}</div>
                <div className="text-sm">{dist.description}</div>
                <div className="text-sm mt-1">
                  <span className="font-medium">Format:</span> {dist.format}
                </div>
              </div>
            ))}
          </div>
        </div>

        {dcatMetadata.temporal && (
          <div>
            <div className="font-medium mb-1">Temporal Coverage</div>
            <div className="text-sm">
              {dcatMetadata.temporal.startDate} to {dcatMetadata.temporal.endDate}
            </div>
          </div>
        )}
      </div>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>DCAT Metadata Viewer</CardTitle>
        <CardDescription>View and explore DCAT-compliant metadata</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="visual" onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="visual">Visual</TabsTrigger>
            <TabsTrigger value="json">JSON-LD</TabsTrigger>
          </TabsList>
          <TabsContent value="visual" className="space-y-4 mt-4">
            {renderVisualView()}
          </TabsContent>
          <TabsContent value="json" className="mt-4">
            {renderJsonView()}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

