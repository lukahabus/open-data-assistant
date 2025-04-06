import { type NextRequest, NextResponse } from "next/server"
import { BedrockRuntimeClient } from "@aws-sdk/client-bedrock-runtime"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { region, accessKeyId, secretAccessKey } = body

    if (!region || !accessKeyId || !secretAccessKey) {
      return NextResponse.json({ error: "Missing required parameters" }, { status: 400 })
    }

    // Create Bedrock client to test connection
    const client = new BedrockRuntimeClient({
      region,
      credentials: {
        accessKeyId,
        secretAccessKey,
      },
    })

    // Just initialize the client to test credentials
    // This will throw an error if credentials are invalid
    await client.config.credentials()

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error("Error testing Bedrock connection:", error)
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : String(error),
      },
      { status: 500 },
    )
  }
}

