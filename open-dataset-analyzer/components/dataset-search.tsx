"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ArrowPathIcon } from "@heroicons/react/24/outline"
import { DataGrid } from "@/components/ui/data-grid"
import { useToast } from "@/components/ui/use-toast"

interface Dataset {
  id: string;
  title?: string;
  description?: string;
  modified?: string;
  publisher?: {
    name?: string;
  };
}

export default function DatasetSearch() {
  const [query, setQuery] = useState("")
  const [isSearching, setIsSearching] = useState(false)
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const { toast } = useToast()

  const handleSearch = async () => {
    if (!query) return

    setIsSearching(true)

    try {
      const response = await fetch("/api/datasets/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query })
      })

      if (!response.ok) {
        throw new Error("Search failed")
      }

      const results = await response.json()
      setDatasets(results)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to search datasets. Please try again.",
        variant: "destructive"
      })
    } finally {
      setIsSearching(false)
    }
  }

  const columns = [
    {
      field: "title",
      headerName: "Title",
      flex: 2,
      renderCell: (params: any) => (
        <div className="font-medium">{params.value}</div>
      )
    },
    {
      field: "publisher",
      headerName: "Publisher",
      flex: 1,
      valueGetter: (params: any) => params.row.publisher?.name || "N/A"
    },
    {
      field: "modified",
      headerName: "Modified",
      flex: 1,
      valueGetter: (params: any) => {
        if (!params.value) return "N/A"
        return new Date(params.value).toLocaleDateString()
      }
    }
  ]

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Dataset Search</CardTitle>
        <CardDescription>Search for datasets using natural language queries</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-4">
          <div className="flex-1">
            <Label htmlFor="query">Search Query</Label>
            <Input
              id="query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSearch()}
              placeholder="e.g., Find datasets about education published in the last year"
            />
          </div>
          <Button
            onClick={handleSearch}
            disabled={isSearching || !query}
            className="self-end"
          >
            {isSearching ? (
              <>
                <ArrowPathIcon className="h-4 w-4 mr-2 animate-spin" />
                Searching...
              </>
            ) : (
              "Search"
            )}
          </Button>
        </div>

        {datasets.length > 0 && (
          <div className="h-[500px] w-full">
            <DataGrid
              rows={datasets}
              columns={columns}
              getRowId={(row) => row.id}
              pageSize={10}
              rowsPerPageOptions={[10, 25, 50]}
              disableSelectionOnClick
              autoHeight
            />
          </div>
        )}
      </CardContent>
    </Card>
  )
}