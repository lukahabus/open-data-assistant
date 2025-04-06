"use client"

import { useState, useEffect } from "react"
import { useSearchParams } from 'next/navigation'
import DashboardHeader from "@/components/dashboard-header"
import AssistantInteraction from "@/components/bedrock-test"

export default function AssistantPage() {
  const searchParams = useSearchParams()
  const [initialQuery, setInitialQuery] = useState<string | null>(null)

  useEffect(() => {
    const queryFromUrl = searchParams.get('query')
    if (queryFromUrl) {
        setInitialQuery(queryFromUrl)
    }
  }, [searchParams])

  return (
    <div className="flex min-h-screen flex-col">
      <DashboardHeader />
      <main className="flex-1 space-y-4 p-8 pt-6">
        <div className="flex items-center justify-between space-y-2">
          <h2 className="text-3xl font-bold tracking-tight">AI Assistant Interaction</h2>
        </div>

        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="col-span-2">
              <AssistantInteraction initialQuery={initialQuery} />
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

