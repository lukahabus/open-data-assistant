import type { Metadata } from "next"
import DashboardHeader from "@/components/dashboard-header"
import DatasetExplorer from "@/components/dataset-explorer"
import MetadataAnalyzer from "@/components/metadata-analyzer"
import ConnectionDiscovery from "@/components/connection-discovery"

export const metadata: Metadata = {
  title: "Open Dataset Metadata Analyzer",
  description: "A system for metadata analysis of open datasets using large language models",
}

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      <DashboardHeader />
      <main className="flex-1 space-y-4 p-8 pt-6">
        <div className="flex items-center justify-between space-y-2">
          <h2 className="text-3xl font-bold tracking-tight">Dataset Metadata Analysis Dashboard</h2>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <DatasetExplorer />
          <MetadataAnalyzer />
          <ConnectionDiscovery />
        </div>
      </main>
    </div>
  )
}

