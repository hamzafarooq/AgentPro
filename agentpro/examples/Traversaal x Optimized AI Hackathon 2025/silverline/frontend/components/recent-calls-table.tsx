"use client"

import { useState, useEffect } from "react"
import { getCalls, type CallHistory } from "@/lib/api"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { useDateRange } from "@/components/date-range-picker"
import { format } from "date-fns"
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert"
import { AlertCircle, RefreshCw } from "lucide-react"
import { ScrollArea } from "@/components/ui/scroll-area"

// Fallback data to show when the API times out or returns an error
const FALLBACK_CALLS: CallHistory[] = [
  {
    id: "fallback-1",
    timestamp: new Date().toISOString(),
    type: "Medical",
    caller_number: "+1415XXXXXXX",
    twilio_number: "+1510XXXXXXX",
    call_duration: 180,
    is_spam: "NOT_SPAM",
    reason: "Caller reported chest pain. Information from fallback data due to API timeout."
  },
  {
    id: "fallback-2",
    timestamp: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
    type: "Environmental",
    caller_number: "+1415XXXXXXX",
    twilio_number: "+1510XXXXXXX",
    call_duration: 240,
    is_spam: "NOT_SPAM",
    reason: "Caller reported a gas leak. Information from fallback data due to API timeout."
  },
  {
    id: "fallback-3",
    timestamp: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
    type: "Emotional",
    caller_number: "+1415XXXXXXX",
    twilio_number: "+1510XXXXXXX",
    call_duration: 120,
    is_spam: "NOT_SPAM",
    reason: "Caller reported anxiety. Information from fallback data due to API timeout."
  },
  {
    id: "fallback-4",
    timestamp: new Date(Date.now() - 259200000).toISOString(), // 3 days ago
    type: "Daily Living",
    caller_number: "+1415XXXXXXX",
    twilio_number: "+1510XXXXXXX",
    call_duration: 300,
    is_spam: "NOT_SPAM",
    reason: "Caller needed assistance with groceries. Information from fallback data due to API timeout."
  },
  {
    id: "fallback-5",
    timestamp: new Date(Date.now() - 345600000).toISOString(), // 4 days ago
    type: "Other",
    caller_number: "+1415XXXXXXX",
    twilio_number: "+1510XXXXXXX",
    call_duration: 90,
    is_spam: "NOT_SPAM",
    reason: "Caller had questions about an event. Information from fallback data due to API timeout."
  }
];

export function RecentCallsTable() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [calls, setCalls] = useState<CallHistory[]>([])
  const [usingFallback, setUsingFallback] = useState(false)
  const { dateRange } = useDateRange()

  const fetchCalls = async () => {
    try {
      setLoading(true)
      setError(null)
      setUsingFallback(false)

      const data = await getCalls()
      
      // Sort calls by timestamp, newest first
      const sortedCalls = [...data].sort((a, b) => 
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      )
      
      setCalls(sortedCalls)
    } catch (err: any) {
      console.error("Error fetching calls:", err)
      
      // Check specifically for Gateway Timeout (504) errors
      if (err.message && err.message.includes("504")) {
        console.warn("API timed out, using fallback data")
        setError("The API request timed out. Showing sample data instead.")
        // Sort fallback data as well
        setCalls([...FALLBACK_CALLS].sort((a, b) => 
          new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        ))
        setUsingFallback(true)
      } else {
        setError("Failed to load call data from the API. Please ensure the backend server is running.")
        // Sort fallback data as well
        setCalls([...FALLBACK_CALLS].sort((a, b) => 
          new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        ))
        setUsingFallback(true)
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCalls()
  }, [])

  // Generate spam status badge
  const getSpamBadge = (status: string | undefined) => {
    if (!status) return "bg-gray-600 text-white hover:bg-gray-700";
    
    const statusMap: Record<string, string> = {
      "SPAM": "bg-red-600 text-white hover:bg-red-700",
      "NOT_SPAM": "bg-green-600 text-white hover:bg-green-700",
      "NOT_SURE": "bg-amber-600 text-white hover:bg-amber-700",
    }

    return statusMap[status] || "bg-gray-600 text-white hover:bg-gray-700"
  }

  // Generate type badge
  const getTypeBadge = (type: string | undefined) => {
    if (!type) return "bg-gray-600 text-white hover:bg-gray-700";
    
    const typeMap: Record<string, string> = {
      "Medical": "bg-red-600 text-white hover:bg-red-700",
      "Environmental": "bg-emerald-600 text-white hover:bg-emerald-700",
      "Emotional": "bg-blue-600 text-white hover:bg-blue-700",
      "Daily Living": "bg-purple-600 text-white hover:bg-purple-700",
      "Other": "bg-gray-600 text-white hover:bg-gray-700",
      "Not Sure": "bg-amber-600 text-white hover:bg-amber-700",
    }

    return typeMap[type] || "bg-gray-600 text-white hover:bg-gray-700"
  }

  // Format duration in seconds to minutes and seconds
  const formatDuration = (seconds: number | undefined) => {
    if (!seconds) return "N/A";
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  }

  return (
    <>
      {error && (
        <Alert variant={usingFallback ? "default" : "destructive"} className="mb-4">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>{usingFallback ? "Using Sample Data" : "Error"}</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      
      {loading ? (
        <div className="space-y-2">
          {Array(5)
            .fill(0)
            .map((_, i) => (
              <div key={i} className="flex items-center space-x-4">
                <div className="h-12 w-full animate-pulse rounded-md bg-muted"></div>
              </div>
            ))}
        </div>
      ) : calls.length > 0 ? (
        <div className="relative overflow-x-auto border rounded-md">
          <div className="min-w-[800px]">
            <Table>
              <TableHeader className="sticky top-0 z-10 bg-background shadow-sm">
                <TableRow>
                  <TableHead className="bg-background">Caller Number</TableHead>
                  <TableHead className="bg-background">Twilio Number</TableHead>
                  <TableHead className="bg-background">Type</TableHead>
                  <TableHead className="bg-background">Duration</TableHead>
                  <TableHead className="bg-background">Time</TableHead>
                  <TableHead className="bg-background">Spam Status</TableHead>
                  <TableHead className="bg-background w-[300px]">Reason</TableHead>
                </TableRow>
              </TableHeader>
            </Table>
          </div>
          
          <ScrollArea className="h-[450px]">
            <div className="min-w-[800px]">
              <Table>
                <TableBody>
                  {calls.map((call) => (
                    <TableRow key={call.id}>
                      <TableCell>{call.caller_number || "N/A"}</TableCell>
                      <TableCell>{call.twilio_number || "N/A"}</TableCell>
                      <TableCell>
                        <Badge className={getTypeBadge(call.type)}>
                          {call.type || "Unknown"}
                        </Badge>
                      </TableCell>
                      <TableCell>{formatDuration(call.call_duration)}</TableCell>
                      <TableCell>{format(new Date(call.timestamp), "MMM dd, h:mm a")}</TableCell>
                      <TableCell>
                        <Badge className={getSpamBadge(call.is_spam)}>
                          {call.is_spam || "Unknown"}
                        </Badge>
                      </TableCell>
                      <TableCell className="w-[300px] max-w-[300px]">
                        <div className="line-clamp-2 hover:line-clamp-none">{call.reason || "N/A"}</div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </ScrollArea>
        </div>
      ) : (
        <div className="flex h-[200px] items-center justify-center rounded-md border border-dashed">
          <div className="text-center">
            <p className="text-sm text-muted-foreground">No calls found</p>
          </div>
        </div>
      )}
    </>
  )
}

function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp)
  const now = new Date()
  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)

  // Check if it's today
  if (date.toDateString() === now.toDateString()) {
    return `Today, ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`
  }

  // Check if it's yesterday
  if (date.toDateString() === yesterday.toDateString()) {
    return `Yesterday, ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`
  }

  // Check if it's within the last week
  const daysDiff = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24))
  if (daysDiff < 7) {
    return `${daysDiff} days ago, ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`
  }

  // Otherwise, return the full date
  return date.toLocaleDateString() + ", " + date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
}
