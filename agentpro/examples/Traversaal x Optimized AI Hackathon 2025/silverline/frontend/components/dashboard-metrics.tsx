"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { getSummaryStats, type SummaryMetrics } from "@/lib/api"
import { useDateRange } from "@/components/date-range-picker"
import { format } from "date-fns"

// Fallback data for when API calls fail
const FALLBACK_METRICS: SummaryMetrics = {
  totalCalls: { count: 1248 },
  medical: { count: 624 },
  environmental: { count: 432 },
  others: { count: 192 }
}

export function DashboardMetrics() {
  const [metrics, setMetrics] = useState<SummaryMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { dateRange } = useDateRange()

  useEffect(() => {
    async function fetchMetrics() {
      try {
        setLoading(true)
        setError(null)

        // Do not pass date parameters
        const data = await getSummaryStats()
        setMetrics(data)
      } catch (error) {
        console.error("Failed to fetch metrics:", error)
        
        // Set an error message
        setError("Unable to fetch metrics from the server.")
        
        // Don't set metrics, let the UI show error state
        setMetrics(null)
      } finally {
        setLoading(false)
      }
    }

    fetchMetrics()
  }, [])

  if (loading) {
    return (
      <div className="grid gap-4 md:grid-cols-4 lg:grid-cols-4">
        {Array(4)
          .fill(0)
          .map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium bg-muted h-5 w-24 rounded"></CardTitle>
                <div className="h-4 w-4 rounded-full bg-muted"></div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold bg-muted h-8 w-16 rounded"></div>
              </CardContent>
            </Card>
          ))}
      </div>
    )
  }

  // If there was an error and no data, show error state
  if (error && !metrics) {
    return (
      <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-800 rounded-md">
        <h3 className="font-semibold mb-1">Error Loading Data</h3>
        <p>{error}</p>
        <p className="mt-2 text-sm">Please ensure the backend API is running and accessible.</p>
      </div>
    )
  }

  // Always display metrics, either from API or fallback data
  const displayMetrics = metrics || FALLBACK_METRICS

  return (
    <>
      {error && (
        <div className="mb-4 p-2 bg-amber-50 border border-amber-200 text-amber-800 rounded-md text-sm">
          {error}
        </div>
      )}
      
      <div className="grid gap-4 md:grid-cols-4 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Calls</CardTitle>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              className="h-4 w-4 text-muted-foreground"
            >
              <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
            </svg>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{displayMetrics.totalCalls.count.toLocaleString()}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Medical Emergencies</CardTitle>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              className="h-4 w-4 text-muted-foreground"
            >
              <path d="M16 2v5h5" />
              <path d="M21 6v14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h11l6 3Z" />
              <path d="M8.5 10a.5.5 0 1 0 0-1 .5.5 0 0 0 0 1Z" />
              <path d="M15.5 10a.5.5 0 1 0 0-1 .5.5 0 0 0 0 1Z" />
              <path d="M12 13a2 2 0 0 0 1.857-1.257" />
            </svg>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{displayMetrics.medical.count.toLocaleString()}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Environmental</CardTitle>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              className="h-4 w-4 text-muted-foreground"
            >
              <path d="M12 2v20" />
              <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
            </svg>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{displayMetrics.environmental.count.toLocaleString()}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Others</CardTitle>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              className="h-4 w-4 text-muted-foreground"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="16" />
              <line x1="8" y1="12" x2="16" y2="12" />
            </svg>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{displayMetrics.others.count.toLocaleString()}</div>
          </CardContent>
        </Card>
      </div>
    </>
  )
}
