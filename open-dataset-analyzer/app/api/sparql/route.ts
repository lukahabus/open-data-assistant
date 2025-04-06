import { type NextRequest, NextResponse } from "next/server"
import { defaultLlmService } from "@/lib/llm-service"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { datasets, question } = body

    if (!datasets || !Array.isArray(datasets)) {
      return NextResponse.json({ error: "Datasets are required" }, { status: 400 })
    }

    if (!question) {
      return NextResponse.json({ error: "Question is required" }, { status: 400 })
    }

    const query = await defaultLlmService.generateSparqlQuery(datasets, question)

    return NextResponse.json({ query })
  } catch (error) {
    console.error("Error generating SPARQL query:", error)
    return NextResponse.json({ error: "Failed to generate SPARQL query" }, { status: 500 })
  }
}

