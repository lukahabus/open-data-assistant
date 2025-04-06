import { type NextRequest, NextResponse } from "next/server"
import { BedrockRuntimeClient, InvokeModelCommand } from "@aws-sdk/client-bedrock-runtime"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const {
      region,
      accessKeyId,
      secretAccessKey,
      modelId,
      prompt,
      temperature = 0.7,
      maxTokens = 1000,
      topP = 0.9,
      stopSequences = [],
    } = body

    if (!region || !accessKeyId || !secretAccessKey || !modelId || !prompt) {
      return NextResponse.json({ error: "Missing required parameters" }, { status: 400 })
    }

    // Create Bedrock client
    const client = new BedrockRuntimeClient({
      region,
      credentials: {
        accessKeyId,
        secretAccessKey,
      },
    })

    // Format the request body based on the model provider
    let requestBody: any

    if (modelId.startsWith("anthropic.claude")) {
      // Anthropic Claude models
      requestBody = {
        prompt: `\n\nHuman: ${prompt}\n\nAssistant:`,
        max_tokens_to_sample: maxTokens,
        temperature,
        top_p: topP,
        stop_sequences: stopSequences.length ? stopSequences : ["\n\nHuman:"],
      }
    } else if (modelId.startsWith("amazon.titan")) {
      // Amazon Titan models
      requestBody = {
        inputText: prompt,
        textGenerationConfig: {
          maxTokenCount: maxTokens,
          temperature,
          topP,
          stopSequences,
        },
      }
    } else if (modelId.startsWith("ai21")) {
      // AI21 models
      requestBody = {
        prompt,
        maxTokens,
        temperature,
        topP,
        stopSequences,
      }
    } else if (modelId.startsWith("cohere")) {
      // Cohere models
      requestBody = {
        prompt,
        max_tokens: maxTokens,
        temperature,
        p: topP,
        stop_sequences: stopSequences,
      }
    } else {
      return NextResponse.json({ error: `Unsupported model ID: ${modelId}` }, { status: 400 })
    }

    // Create the command
    const command = new InvokeModelCommand({
      modelId,
      contentType: "application/json",
      accept: "application/json",
      body: JSON.stringify(requestBody),
    })

    // Invoke the model
    console.log(`Invoking Bedrock model: ${modelId}`)
    const response = await client.send(command)

    // Parse the response
    const responseBody = new TextDecoder().decode(response.body)
    const parsedResponse = JSON.parse(responseBody)

    // Extract the generated text based on the model provider
    let generatedText = ""

    if (modelId.startsWith("anthropic.claude")) {
      generatedText = parsedResponse.completion || ""
    } else if (modelId.startsWith("amazon.titan")) {
      generatedText = parsedResponse.results?.[0]?.outputText || ""
    } else if (modelId.startsWith("ai21")) {
      generatedText = parsedResponse.completions?.[0]?.data?.text || ""
    } else if (modelId.startsWith("cohere")) {
      generatedText = parsedResponse.generations?.[0]?.text || ""
    }

    return NextResponse.json({ text: generatedText.trim() })
  } catch (error) {
    console.error("Error generating text with Bedrock:", error)
    return NextResponse.json({ error: error instanceof Error ? error.message : String(error) }, { status: 500 })
  }
}

