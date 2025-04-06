"use client"

import { useState } from "react"
import Link from "next/link"
import { useRouter } from 'next/navigation'
import { MagnifyingGlassIcon, Bars3Icon, XMarkIcon } from "@heroicons/react/24/outline"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import DatasetImporter from "./dataset-importer"

export default function DashboardHeader() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const router = useRouter()

  const handleSearchSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      router.push(`/assistant?query=${encodeURIComponent(searchQuery.trim())}`)
      setSearchQuery("")
      setIsMenuOpen(false)
    }
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center gap-2">
          <Link href="/" className="flex items-center space-x-2">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-6 w-6"
            >
              <path d="M20 14.66V20a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h5.34" />
              <polygon points="18 2 22 6 12 16 8 16 8 12 18 2" />
            </svg>
            <span className="hidden font-bold sm:inline-block">Open Dataset Analyzer</span>
          </Link>
        </div>

        <div className="hidden md:flex md:flex-1 md:items-center md:justify-end md:space-x-4">
          <form onSubmit={handleSearchSubmit} className="relative w-full max-w-sm">
            <MagnifyingGlassIcon className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Ask the assistant..."
              className="w-full bg-background pl-8 md:w-[300px] lg:w-[400px]"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </form>
          <nav className="flex items-center space-x-2">
            <Button variant="ghost" asChild>
              <Link href="/">Datasets</Link>
            </Button>
            <Button variant="ghost" asChild>
              <Link href="/assistant">Assistant</Link>
            </Button>
            <Button variant="ghost">Analytics</Button>
            <DatasetImporter
              triggerButton={<Button>Import Dataset</Button>}
            />
          </nav>
        </div>

        <button
          className="flex items-center justify-center rounded-md p-2 md:hidden"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
        >
          {isMenuOpen ? <XMarkIcon className="h-6 w-6" /> : <Bars3Icon className="h-6 w-6" />}
          <span className="sr-only">Toggle menu</span>
        </button>
      </div>

      {isMenuOpen && (
        <div className="container pb-4 md:hidden">
          <form onSubmit={handleSearchSubmit} className="relative mb-4 w-full">
            <MagnifyingGlassIcon className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Ask the assistant..."
              className="w-full bg-background pl-8"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </form>
          <nav className="flex flex-col space-y-2">
            <Button variant="ghost" className="justify-start" asChild>
              <Link href="/">Datasets</Link>
            </Button>
            <Button variant="ghost" className="justify-start" asChild>
              <Link href="/assistant">Assistant</Link>
            </Button>
            <Button variant="ghost" className="justify-start">
              Analytics
            </Button>
            <DatasetImporter
              triggerButton={<Button className="justify-start">Import Dataset</Button>}
            />
          </nav>
        </div>
      )}
    </header>
  )
}

