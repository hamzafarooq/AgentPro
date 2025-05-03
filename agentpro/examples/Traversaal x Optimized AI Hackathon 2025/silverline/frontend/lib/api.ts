// API configuration
const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:8000"
const API_PREFIX = process.env.NEXT_PUBLIC_API_PREFIX || "/ai/api"
const API_TIMEOUT = +process.env.NEXT_PUBLIC_API_TIMEOUT! || 90000 // 90 seconds timeout for all API calls

console.log("BASE_URL", BASE_URL)
console.log("API_PREFIX", API_PREFIX)
console.log("API_TIMEOUT", API_TIMEOUT)

// Flag to use fallback data instead of trying to call the API
const USE_FALLBACK_DATA = false

// Debug flag to log detailed API responses
const DEBUG_API = true

// Type definitions
export interface CallHistory {
  id: string
  timestamp: string
  type?: string
  caller_number?: string
  twilio_number?: string
  call_duration?: number
  is_spam?: string
  reason?: string
}

export interface SummaryMetrics {
  totalCalls: { count: number }
  medical: { count: number }
  environmental: { count: number }
  others: { count: number }
}

export interface CallVolume {
  labels: string[]
  datasets: { label: string; data: number[] }[]
}

export interface TypeBreakdown {
  data: { name: string; value: number; percentage: number }[]
}

// Fallback data for when API calls fail
const FALLBACK_CALLS: CallHistory[] = [
  {
    id: "EC-1234",
    caller_number: "+14155552671",
    twilio_number: "+15105551234",
    type: "Medical",
    timestamp: new Date().toISOString(),
    is_spam: "NOT_SPAM",
    call_duration: 180,
    reason: "Caller reported chest pain and trouble breathing."
  },
  {
    id: "EC-1235",
    caller_number: "+14155552672",
    twilio_number: "+15105551234",
    type: "Environmental",
    timestamp: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
    is_spam: "NOT_SPAM",
    call_duration: 240,
    reason: "Caller witnessed a chemical spill on a nearby highway."
  },
  {
    id: "EC-1236",
    caller_number: "+14155552673",
    twilio_number: "+15105551235",
    type: "Emotional",
    timestamp: new Date(Date.now() - 7200000).toISOString(), // 2 hours ago
    is_spam: "NOT_SPAM",
    call_duration: 120,
    reason: "Caller reported ongoing anxiety and insomnia."
  },
  {
    id: "EC-1237",
    caller_number: "+14155552674",
    twilio_number: "+15105551236",
    type: "Daily Living",
    timestamp: new Date(Date.now() - 10800000).toISOString(), // 3 hours ago
    is_spam: "NOT_SPAM",
    call_duration: 300,
    reason: "Caller needed help with grocery delivery logistics."
  },
  {
    id: "EC-1238",
    caller_number: "+14155552675",
    twilio_number: "+15105551237",
    type: "Other",
    timestamp: new Date(Date.now() - 14400000).toISOString(), // 4 hours ago
    is_spam: "NOT_SPAM",
    call_duration: 90,
    reason: "Caller had questions regarding an upcoming community event."
  },
  {
    id: "EC-1239",
    caller_number: "+14155552676",
    twilio_number: "+15105551238",
    type: "Not Sure",
    timestamp: new Date(Date.now() - 18000000).toISOString(), // 5 hours ago
    is_spam: "NOT_SURE",
    call_duration: 60,
    reason: "Caller was unsure of the purpose for calling."
  },
  {
    id: "EC-1240",
    caller_number: "+14155552677",
    twilio_number: "+15105551239",
    type: "Other",
    timestamp: new Date(Date.now() - 21600000).toISOString(), // 6 hours ago
    is_spam: "SPAM",
    call_duration: 150,
    reason: "Unsolicited sales pitch for discount insurance."
  },
]

const FALLBACK_SUMMARY: SummaryMetrics = {
  totalCalls: { count: 1248 },
  medical: { count: 624 },
  environmental: { count: 432 },
  others: { count: 192 }
}

const FALLBACK_CALL_VOLUME: CallVolume = {
  labels: ["Jan 01", "Jan 02", "Jan 03", "Jan 04", "Jan 05", "Jan 06", "Jan 07"],
  datasets: [
    {
      label: "Calls",
      data: [45, 52, 48, 61, 55, 67, 62],
    },
    {
      label: "Medical",
      data: [25, 30, 28, 35, 32, 40, 36],
    },
    {
      label: "Environmental",
      data: [20, 22, 20, 26, 23, 27, 26],
    },
  ],
}

const FALLBACK_CALL_TYPES: TypeBreakdown = {
  data: [
    { name: "Medical", value: 624, percentage: 50 },
    { name: "Environmental", value: 432, percentage: 34.6 },
    { name: "Fall Detection", value: 124, percentage: 9.9 },
    { name: "Other", value: 68, percentage: 5.5 },
  ],
}

// Helper function to safely parse JSON
async function safeJsonParse(response: Response) {
  const text = await response.text()
  try {
    return JSON.parse(text)
  } catch (e: unknown) {
    console.error("Failed to parse JSON response:", text.substring(0, 100) + "...")
    throw new Error(`Invalid JSON response: ${(e as Error).message}`)
  }
}

// Check if the backend server is available
export async function checkBackendConnection(): Promise<boolean> {
  try {
    const healthCheckUrl = `${BASE_URL}/ai/health`;
    console.log(`Checking backend health at: ${healthCheckUrl}`);
    
    const response = await fetch(healthCheckUrl, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      },
      signal: AbortSignal.timeout(5000) // Short timeout for health check
    });
    
    if (response.ok) {
      console.log('Backend health check passed');
      return true;
    } else {
      console.warn(`Backend health check failed with status: ${response.status}`);
      return false;
    }
  } catch (error) {
    console.error('Backend health check failed:', error);
    return false;
  }
}

// API functions
export async function getCalls(): Promise<CallHistory[]> {
  // Use fallback data directly if flag is set
  if (USE_FALLBACK_DATA) {
    console.log("Using fallback call data")
    return FALLBACK_CALLS
  }

  try {
    const url = `${BASE_URL}${API_PREFIX}/calls`
    console.log(`Fetching calls from: ${url}`)
    
    const startTime = Date.now()
    
    const response = await fetch(url, {
      headers: {
        Accept: "application/json",
      },
      // Add a timeout to prevent hanging
      signal: AbortSignal.timeout(API_TIMEOUT),
    })
    
    const responseTime = Date.now() - startTime
    console.log(`Response received in ${responseTime}ms`)

    // Check if response is JSON
    const contentType = response.headers.get("content-type")
    if (!contentType || !contentType.includes("application/json")) {
      console.error(`API returned non-JSON response: ${contentType}`)
      throw new Error(`API returned non-JSON response: ${contentType}`)
    }

    if (!response.ok) {
      console.error(`API error: ${response.status} ${response.statusText}`)
      throw new Error(`API error: ${response.status} ${response.statusText}`)
    }

    const data = await response.json()
    if (DEBUG_API) {
      console.log("API returned data:", data)
    }
    
    return data
  } catch (error) {
    console.error("Error fetching calls:", error)
    
    // More detailed error logging
    if (error instanceof TypeError && error.message.includes("Failed to fetch")) {
      console.error("Network error: Check if the backend server is running at " + BASE_URL)
      console.error("This usually means the server is down or there's a network/CORS issue")
    }
    
    throw error
  }
}

export async function getSummaryStats(startDate?: string, endDate?: string): Promise<SummaryMetrics> {
  // Use fallback data directly if flag is set
  if (USE_FALLBACK_DATA) {
    console.log("Using fallback summary stats")
    return FALLBACK_SUMMARY
  }

  try {
    // Don't use date parameters
    const url = `${BASE_URL}${API_PREFIX}/statistics/summary`
    console.log(`Fetching summary stats from: ${url}`)

    const startTime = Date.now()
    const response = await fetch(url, {
      headers: {
        Accept: "application/json",
      },
      // Add a timeout to prevent hanging
      signal: AbortSignal.timeout(API_TIMEOUT),
    })
    const responseTime = Date.now() - startTime
    console.log(`Response received in ${responseTime}ms`)

    // Check if response is JSON
    const contentType = response.headers.get("content-type")
    if (!contentType || !contentType.includes("application/json")) {
      console.error(`API returned non-JSON response: ${contentType}`)
      throw new Error(`API returned non-JSON response: ${contentType}`)
    }

    if (!response.ok) {
      console.error(`API error: ${response.status} ${response.statusText}`)
      throw new Error(`API error: ${response.status} ${response.statusText}`)
    }

    const data = await response.json()
    if (DEBUG_API) {
      console.log("API returned data:", data)
    }
    
    return data
  } catch (error) {
    console.error("Error fetching summary statistics:", error)
    throw error
  }
}

export async function getCallVolume(startDate?: string, endDate?: string, interval = "day"): Promise<CallVolume> {
  // Use fallback data directly if flag is set
  if (USE_FALLBACK_DATA) {
    console.log("Using fallback call volume data")
    return FALLBACK_CALL_VOLUME
  }

  try {
    const params = new URLSearchParams()
    // Remove date parameters
    params.append("interval", interval)

    const url = `${BASE_URL}${API_PREFIX}/statistics/call-volume?${params}`
    console.log(`Fetching call volume from: ${url}`)

    const response = await fetch(url, {
      headers: {
        Accept: "application/json",
      },
      // Add a timeout to prevent hanging
      signal: AbortSignal.timeout(API_TIMEOUT),
    })

    // Check if response is JSON
    const contentType = response.headers.get("content-type")
    if (!contentType || !contentType.includes("application/json")) {
      console.error(`API returned non-JSON response: ${contentType}`)
      throw new Error(`API returned non-JSON response: ${contentType}`)
    }

    if (!response.ok) {
      console.error(`API error: ${response.status} ${response.statusText}`)
      throw new Error(`API error: ${response.status} ${response.statusText}`)
    }

    return await response.json()
  } catch (error) {
    console.error("Error fetching call volume:", error)
    throw error
  }
}

export async function getCallTypes(startDate?: string, endDate?: string): Promise<TypeBreakdown> {
  // Use fallback data directly if flag is set
  if (USE_FALLBACK_DATA) {
    console.log("Using fallback call types data")
    return FALLBACK_CALL_TYPES
  }

  try {
    // Don't use date parameters
    const url = `${BASE_URL}${API_PREFIX}/statistics/types`
    console.log(`Fetching call types from: ${url}`)

    const response = await fetch(url, {
      headers: {
        Accept: "application/json",
      },
      // Add a timeout to prevent hanging
      signal: AbortSignal.timeout(API_TIMEOUT),
    })

    // Check if response is JSON
    const contentType = response.headers.get("content-type")
    if (!contentType || !contentType.includes("application/json")) {
      console.error(`API returned non-JSON response: ${contentType}`)
      throw new Error(`API returned non-JSON response: ${contentType}`)
    }

    if (!response.ok) {
      console.error(`API error: ${response.status} ${response.statusText}`)
      throw new Error(`API error: ${response.status} ${response.statusText}`)
    }

    return await response.json()
  } catch (error) {
    console.error("Error fetching call types:", error)
    throw error
  }
}

export async function getSpamStatusData() {
  // Use fallback data directly if flag is set
  if (USE_FALLBACK_DATA) {
    console.log("Using fallback spam status data")
    // You could create a fallback object here if needed
    return {
      data: [
        { status: "NOT_SPAM", count: 85, percentage: 70.8 },
        { status: "NOT_SURE", count: 22, percentage: 18.3 },
        { status: "SPAM", count: 13, percentage: 10.9 }
      ]
    }
  }

  try {
    const url = `${BASE_URL}${API_PREFIX}/statistics/spam-status`
    console.log(`Fetching spam status data from: ${url}`)
    
    const response = await fetch(url, {
      headers: {
        Accept: "application/json",
      },
      // Add a timeout to prevent hanging
      signal: AbortSignal.timeout(API_TIMEOUT),
    })
    
    // Check if response is JSON
    const contentType = response.headers.get("content-type")
    if (!contentType || !contentType.includes("application/json")) {
      console.error(`API returned non-JSON response: ${contentType}`)
      throw new Error(`API returned non-JSON response: ${contentType}`)
    }
    
    if (!response.ok) {
      console.error(`API error: ${response.status} ${response.statusText}`)
      throw new Error(`API error: ${response.status} ${response.statusText}`)
    }
    
    const data = await response.json()
    if (DEBUG_API) {
      console.log("API returned spam status data:", data)
    }
    
    return data
  } catch (error) {
    console.error('Failed to fetch spam status data:', error)
    throw error
  }
}
