import { type NextRequest, NextResponse } from "next/server"
import { defaultCkanApi } from "@/lib/ckan-api"

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const query = searchParams.get("q") || ""
  const rows = Number.parseInt(searchParams.get("rows") || "10", 10)
  const start = Number.parseInt(searchParams.get("start") || "0", 10)

  try {
    const response = await defaultCkanApi.searchDatasets({
      q: query,
      rows,
      start,
    })

    return NextResponse.json(response)
  } catch (error) {
    console.error("Error fetching datasets:", error)
    return NextResponse.json({ error: "Failed to fetch datasets" }, { status: 500 })
  }
}

