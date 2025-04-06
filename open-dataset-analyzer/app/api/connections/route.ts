import { type NextRequest, NextResponse } from "next/server"
import { defaultLlmService } from "@/lib/llm-service"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { datasets } = body

    if (!datasets || !Array.isArray(datasets) || datasets.length < 2) {
      return NextResponse.json({ error: "At least two datasets are required" }, { status: 400 })
    }

    const connections = await defaultLlmService.discoverConnections(datasets)

    return NextResponse.json({ connections })
  } catch (error) {
    console.error("Error discovering connections:", error)
    return NextResponse.json({ error: "Failed to discover connections" }, { status: 500 })
  }
}

