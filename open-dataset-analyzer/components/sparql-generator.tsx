"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ArrowPathIcon, CodeBracketIcon } from "@heroicons/react/24/outline"

export default function SparqlGenerator() {
  const [question, setQuestion] = useState("")
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedQuery, setGeneratedQuery] = useState("")

  const handleGenerate = async () => {
    if (!question) return

    setIsGenerating(true)

    // Simulate API call to generate SPARQL
    setTimeout(() => {
      const query = `
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?dataset ?title ?publisher ?modified
WHERE {
  ?dataset a dcat:Dataset ;
           dct:title ?title ;
           dct:publisher ?publisherURI ;
           dct:modified ?modified .
  
  ?publisherURI dct:title ?publisher .
  
  # Filter for datasets related to the user's question
  FILTER(CONTAINS(LCASE(?title), "covid") || CONTAINS(LCASE(?title), "health"))
  
  # Filter for recent datasets
  FILTER(?modified >= "2022-01-01"^^xsd:date)
}
ORDER BY DESC(?modified)
LIMIT 10
      `.trim()

      setGeneratedQuery(query)
      setIsGenerating(false)
    }, 2000)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>SPARQL Query Generator</CardTitle>
        <CardDescription>Generate SPARQL queries for dataset integration using LLM</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="question">What would you like to know?</Label>
          <Input
            id="question"
            placeholder="e.g., Show me the correlation between COVID-19 cases and air quality"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
        </div>

        {generatedQuery && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="query">Generated SPARQL Query</Label>
              <Button variant="ghost" size="sm" className="h-8 gap-1">
                <CodeBracketIcon className="h-4 w-4" />
                Copy
              </Button>
            </div>
            <Textarea id="query" className="font-mono text-xs h-[200px]" value={generatedQuery} readOnly />
          </div>
        )}
      </CardContent>
      <CardFooter>
        <Button onClick={handleGenerate} disabled={isGenerating || !question} className="w-full">
          {isGenerating ? (
            <>
              <ArrowPathIcon className="h-4 w-4 mr-2 animate-spin" />
              Generating Query...
            </>
          ) : (
            "Generate SPARQL Query"
          )}
        </Button>
      </CardFooter>
    </Card>
  )
}

