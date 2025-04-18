import { DatasetSearch } from "@/components/dataset-search"

export const metadata = {
  title: "Dataset Search - DCAT Metadata Explorer",
  description: "Search and explore datasets using natural language queries"
}

export default function DatasetsPage() {
  return (
    <div className="container py-6 space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Dataset Search</h1>
        <p className="text-muted-foreground">
          Search datasets using natural language queries, powered by DCAT metadata analysis
        </p>
      </div>
      
      <DatasetSearch />
    </div>
  )
}