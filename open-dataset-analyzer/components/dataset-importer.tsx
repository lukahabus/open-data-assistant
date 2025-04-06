"use client"

import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { useToast } from "@/components/ui/use-toast"
import { ArrowPathIcon } from "@heroicons/react/24/outline"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogClose,
} from "@/components/ui/dialog"

interface DatasetImporterProps {
  triggerButton: React.ReactNode;
}

export default function DatasetImporter({ triggerButton }: DatasetImporterProps) {
  const [ckanUrl, setCkanUrl] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isOpen, setIsOpen] = useState(false);
  const { toast } = useToast()

  const handleImport = async () => {
    if (!ckanUrl) {
      toast({
        variant: "destructive",
        title: "Missing URL",
        description: "Please enter a CKAN portal URL.",
      })
      return
    }

    if (!ckanUrl.startsWith("http://") && !ckanUrl.startsWith("https://")) {
       toast({
        variant: "destructive",
        title: "Invalid URL",
        description: "Please enter a valid URL starting with http:// or https://.",
      })
      return
    }


    setIsLoading(true)

    try {
      const response = await fetch("http://localhost:8000/import/ckan", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ ckan_url: ckanUrl }),
      })

      const data = await response.json()

      if (response.ok) {
        toast({
          title: "Import Started",
          description: data.message || "Import process initiated successfully.",
        })
        setIsOpen(false);
        setCkanUrl("");
      } else {
        toast({
          variant: "destructive",
          title: "Import Failed",
          description: data.detail || "Failed to start import process.",
        })
      }
    } catch (error) {
      console.error("Error importing from CKAN:", error)
      toast({
        variant: "destructive",
        title: "Request Failed",
        description: "Could not connect to the backend API to start the import.",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>{triggerButton}</DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Import from CKAN Portal</DialogTitle>
          <DialogDescription>
            Enter the base URL of the CKAN portal (e.g., https://data.gov).
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="ckan-url" className="text-right">
              CKAN URL
            </Label>
            <Input
              id="ckan-url"
              value={ckanUrl}
              onChange={(e) => setCkanUrl(e.target.value)}
              placeholder="https://your-ckan-instance.com"
              className="col-span-3"
              disabled={isLoading}
            />
          </div>
        </div>
        <DialogFooter>
           <DialogClose asChild>
              <Button variant="outline" disabled={isLoading}>Cancel</Button>
           </DialogClose>
          <Button onClick={handleImport} disabled={isLoading || !ckanUrl}>
            {isLoading ? (
              <>
                <ArrowPathIcon className="h-4 w-4 mr-2 animate-spin" />
                Importing...
              </>
            ) : (
              "Start Import"
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
} 