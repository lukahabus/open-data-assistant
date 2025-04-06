"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useToast } from "@/components/ui/use-toast"
import { ArrowPathIcon, CheckCircleIcon } from "@heroicons/react/24/outline"

interface AwsConfigProps {
  onConfigured: (config: {
    region: string
    accessKeyId: string
    secretAccessKey: string
    modelId: string
  }) => void
}

export default function AwsConfig({ onConfigured }: AwsConfigProps) {
  const { toast } = useToast()
  const [region, setRegion] = useState("us-east-1")
  const [accessKeyId, setAccessKeyId] = useState("")
  const [secretAccessKey, setSecretAccessKey] = useState("")
  const [modelId, setModelId] = useState("anthropic.claude-v2")
  const [isTesting, setIsTesting] = useState(false)

  const availableRegions = [
    { value: "us-east-1", label: "US East (N. Virginia)" },
    { value: "us-west-2", label: "US West (Oregon)" },
    { value: "eu-central-1", label: "EU (Frankfurt)" },
    { value: "ap-northeast-1", label: "Asia Pacific (Tokyo)" },
  ]

  const availableModels = [
    { value: "anthropic.claude-v2", label: "Anthropic Claude V2" },
    { value: "anthropic.claude-instant-v1", label: "Anthropic Claude Instant" },
    { value: "amazon.titan-text-express-v1", label: "Amazon Titan Text" },
    { value: "ai21.j2-ultra-v1", label: "AI21 Jurassic-2 Ultra" },
    { value: "cohere.command-text-v14", label: "Cohere Command" },
  ]

  const handleTestConnection = async () => {
    if (!accessKeyId || !secretAccessKey) {
      toast({
        variant: "destructive",
        title: "Missing credentials",
        description: "Please enter your AWS access key ID and secret access key",
      })
      return
    }

    setIsTesting(true)

    try {
      // Call the server-side API to test the connection
      const response = await fetch("/api/bedrock/test", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          region,
          accessKeyId,
          secretAccessKey,
        }),
      })

      const data = await response.json()

      if (response.ok && data.success) {
        toast({
          title: "Connection successful",
          description: "Successfully connected to Amazon Bedrock",
        })

        onConfigured({
          region,
          accessKeyId,
          secretAccessKey,
          modelId,
        })
      } else {
        toast({
          variant: "destructive",
          title: "Connection test failed",
          description: data.error || "Failed to connect to Amazon Bedrock",
        })
      }
    } catch (error) {
      console.error("Error testing Bedrock connection:", error)
      toast({
        variant: "destructive",
        title: "Connection failed",
        description: error instanceof Error ? error.message : "Failed to connect to Amazon Bedrock",
      })
    } finally {
      setIsTesting(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Amazon Bedrock Configuration</CardTitle>
        <CardDescription>Configure your AWS credentials to use Amazon Bedrock</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="region">AWS Region</Label>
          <Select value={region} onValueChange={setRegion}>
            <SelectTrigger id="region">
              <SelectValue placeholder="Select a region" />
            </SelectTrigger>
            <SelectContent>
              {availableRegions.map((region) => (
                <SelectItem key={region.value} value={region.value}>
                  {region.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="access-key">AWS Access Key ID</Label>
          <Input
            id="access-key"
            value={accessKeyId}
            onChange={(e) => setAccessKeyId(e.target.value)}
            placeholder="AKIAIOSFODNN7EXAMPLE"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="secret-key">AWS Secret Access Key</Label>
          <Input
            id="secret-key"
            type="password"
            value={secretAccessKey}
            onChange={(e) => setSecretAccessKey(e.target.value)}
            placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="model-id">Bedrock Model</Label>
          <Select value={modelId} onValueChange={setModelId}>
            <SelectTrigger id="model-id">
              <SelectValue placeholder="Select a model" />
            </SelectTrigger>
            <SelectContent>
              {availableModels.map((model) => (
                <SelectItem key={model.value} value={model.value}>
                  {model.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </CardContent>
      <CardFooter>
        <Button
          onClick={handleTestConnection}
          disabled={isTesting || !accessKeyId || !secretAccessKey}
          className="w-full"
        >
          {isTesting ? (
            <>
              <ArrowPathIcon className="h-4 w-4 mr-2 animate-spin" />
              Testing Connection...
            </>
          ) : (
            <>
              <CheckCircleIcon className="h-4 w-4 mr-2" />
              Test Connection
            </>
          )}
        </Button>
      </CardFooter>
    </Card>
  )
}

