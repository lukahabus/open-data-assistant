import { type NextRequest, NextResponse } from "next/server"
import { defaultLlmService } from "@/lib/llm-service"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { metadata } = body

    if (!metadata) {
      return NextResponse.json({ error: "Metadata is required" }, { status: 400 })
    }

    const analysis = await defaultLlmService.analyzeMetadata(metadata)

    return NextResponse.json({ analysis })
  } catch (error) {
    console.error("Error analyzing metadata:", error)
    return NextResponse.json({ error: "Failed to analyze metadata" }, { status: 500 })
  }
}

