"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { ArrowPathIcon } from "@heroicons/react/24/outline"
import { useToast } from "@/components/ui/use-toast"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"

// Define props interface
interface AssistantInteractionProps {
  initialQuery?: string | null;
}

// Define the structure based on backend's AssistantResponse
interface AssistantResponseData {
  answer: string;
  suggestions: { dataset_id: string; relevance_score: number; explanation: string }[];
  insights: { insight_type: string; description: string; confidence: number; affected_datasets: string[] }[];
  next_steps: string[];
}

// Accept props
export default function AssistantInteraction({ initialQuery }: AssistantInteractionProps) {
  const { toast } = useToast()
  const [prompt, setPrompt] = useState(
    initialQuery || "Give me some insights about open government data portals.",
  )
  const [response, setResponse] = useState<AssistantResponseData | null>(null)
  const [rawResponse, setRawResponse] = useState("")
  const [isGenerating, setIsGenerating] = useState(false)

  // Effect to set prompt from prop when it changes
  useEffect(() => {
    if (initialQuery) {
      setPrompt(initialQuery);
      setResponse(null);
      setRawResponse("");
    }
  }, [initialQuery]);

  const handleGenerate = async () => {
    if (!prompt) {
      toast({
        variant: "destructive",
        title: "Empty prompt",
        description: "Please enter a prompt",
      })
      return
    }

    setIsGenerating(true)
    setResponse(null)
    setRawResponse("")

    try {
      const apiResponse = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: prompt,
        }),
      })

      const data = await apiResponse.json()
      setRawResponse(JSON.stringify(data, null, 2))

      if (apiResponse.ok) {
        setResponse(data as AssistantResponseData)
      } else {
        toast({
          variant: "destructive",
          title: "API Error",
          description: data.detail || "Failed to get response from backend",
        })
      }
    } catch (error) {
      console.error("Error calling backend API:", error)
      toast({
        variant: "destructive",
        title: "Request failed",
        description: error instanceof Error ? error.message : "Failed to connect to the backend API",
      })
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>AI Assistant</CardTitle>
        <CardDescription>Interact with the backend AI assistant</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="prompt">Your Query</Label>
          <Textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Enter your query here..."
            className="min-h-[100px]"
            disabled={isGenerating}
          />
        </div>

        {response && (
          <div className="space-y-4 pt-4">
            <div>
              <Label>Answer</Label>
              <div className="p-4 rounded-md border bg-muted/50 whitespace-pre-wrap">
                {response.answer || "No answer provided."}
              </div>
            </div>

            {(response.suggestions?.length > 0 || response.insights?.length > 0 || response.next_steps?.length > 0) && (
               <Accordion type="single" collapsible className="w-full">
                 {response.suggestions?.length > 0 && (
                   <AccordionItem value="suggestions">
                     <AccordionTrigger>Suggestions ({response.suggestions.length})</AccordionTrigger>
                     <AccordionContent>
                       <ul className="space-y-2 list-disc pl-5 text-sm">
                         {response.suggestions.map((s, i) => (
                           <li key={`sugg-${i}`}>
                             <strong>{s.dataset_id}</strong> (Score: {s.relevance_score.toFixed(2)}): {s.explanation}
                           </li>
                         ))}
                       </ul>
                     </AccordionContent>
                   </AccordionItem>
                 )}

                 {response.insights?.length > 0 && (
                    <AccordionItem value="insights">
                     <AccordionTrigger>Insights ({response.insights.length})</AccordionTrigger>
                     <AccordionContent>
                       <ul className="space-y-2 list-disc pl-5 text-sm">
                         {response.insights.map((ins, i) => (
                           <li key={`ins-${i}`}>
                              <strong>[{ins.insight_type}]</strong> {ins.description} (Confidence: {ins.confidence.toFixed(2)})
                              {ins.affected_datasets?.length > 0 && ` - Affects: ${ins.affected_datasets.join(', ')}`}
                           </li>
                         ))}
                       </ul>
                     </AccordionContent>
                   </AccordionItem>
                 )}

                  {response.next_steps?.length > 0 && (
                     <AccordionItem value="next-steps">
                     <AccordionTrigger>Next Steps</AccordionTrigger>
                     <AccordionContent>
                       <ul className="space-y-1 list-disc pl-5 text-sm">
                         {response.next_steps.map((step, i) => (
                           <li key={`step-${i}`}>{step}</li>
                         ))}
                       </ul>
                     </AccordionContent>
                   </AccordionItem>
                  )}
               </Accordion>
            )}
          </div>
        )}

         {/* Optionally display raw response for debugging */} 
         {/* {rawResponse && (
           <div className="space-y-2 pt-4">
             <Label>Raw Response (Debug)</Label>
             <pre className="p-4 rounded-md border bg-muted/90 text-xs overflow-x-auto">
               {rawResponse}
              </pre>
           </div>
         )} */}
      </CardContent>
      <CardFooter>
        <Button onClick={handleGenerate} disabled={isGenerating || !prompt} className="w-full">
          {isGenerating ? (
            <>
              <ArrowPathIcon className="h-4 w-4 mr-2 animate-spin" />
              Processing...
            </>
          ) : (
            "Send Query"
          )}
        </Button>
      </CardFooter>
    </Card>
  )
}

