"use client"

import { useEffect, useState, useCallback } from "react"
import { 
  Line, 
  LineChart, 
  CartesianGrid, 
  ResponsiveContainer, 
  XAxis, 
  YAxis, 
  Legend, 
  Tooltip, 
  TooltipProps,
  BarChart,
  Bar,
  Cell
} from "recharts"
import { ChartContainer } from "@/components/ui/chart"
import { getCallVolume, getSpamStatusData } from "@/lib/api"
import { useDateRange } from "@/components/date-range-picker"
import { format } from "date-fns"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

// Define chart data types
type ChartDataPoint = {
  date: string;
  call_volume?: number;
  medical?: number;
  environmental?: number;
  emotional?: number;
  daily_living?: number;
  other?: number;
  not_sure?: number;
  [key: string]: any;
}

type SpamStatusItem = {
  status: string;
  count: number;
  percentage: number;
  color?: string;
}

// Create gradient color mapping
const gradientColors = {
  "Not Spam": {
    start: "#00C853",  // Lighter green
    end: "#2E7D32"     // Darker green
  },
  "Not Sure": { 
    start: "#FFD54F",  // Lighter amber
    end: "#FF8F00"     // Darker amber
  },
  "Spam": {
    start: "#FF5252",  // Lighter red
    end: "#C62828"     // Darker red
  }
};

export function EmergencyCallsChart() {
  const [chartData, setChartData] = useState<ChartDataPoint[]>([])
  const [spamData, setSpamData] = useState<SpamStatusItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { dateRange } = useDateRange()

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true)
        setError(null)

        // Get call volume data from API
        const volumeData = await getCallVolume()
        
        // Get spam status data from API
        const spamResponse = await getSpamStatusData()

        // Process spam data
        if (spamResponse && spamResponse.data && spamResponse.data.length > 0) {
          const processedSpamData = spamResponse.data.map((item: SpamStatusItem) => {
            // Format the status label to be more readable
            const readableStatus = item.status === 'NOT_SPAM' 
              ? 'Not Spam' 
              : item.status === 'NOT_SURE' 
                ? 'Not Sure' 
                : 'Spam';

            return {
              ...item,
              status: readableStatus
            };
          });
          setSpamData(processedSpamData);
        } else {
          setError("No spam data available from API");
        }

        // Process call volume data
        if (volumeData && volumeData.labels && volumeData.labels.length > 0 && volumeData.datasets && volumeData.datasets.length > 0) {
          // Transform API data to chart format
          const formattedData = volumeData.labels.map((label: string, index: number) => {
            const dataPoint: ChartDataPoint = { date: label }
            volumeData.datasets.forEach((dataset: any) => {
              // Convert label to snake_case for consistency
              const key = dataset.label.toLowerCase().replace(/\s+/g, '_');
              dataPoint[key] = dataset.data[index]
            })
            return dataPoint
          })
          setChartData(formattedData)
        } else {
          setError("Invalid or empty data received from API");
        }
      } catch (error) {
        console.error("Failed to fetch data:", error)
        setError("Failed to load chart data.")
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  // Format date for X-axis
  const formatXAxis = (tickItem: string): string => {
    try {
      return format(new Date(tickItem), "MMM dd")
    } catch (e) {
      return tickItem
    }
  }

  // Custom tooltip
  const CustomTooltip = ({ 
    active, 
    payload, 
    label 
  }: TooltipProps<number, string>) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-[#1e1e1e] border border-gray-700 rounded p-2 shadow-md">
          <p className="font-medium text-gray-200">{typeof label === 'string' && label.includes('-') ? formatXAxis(label) : label}</p>
          {payload.map((entry, index) => {
            const entryName = entry.name as keyof typeof gradientColors;
            const color = entry.color || (gradientColors[entryName]?.start) || '#AAAAAA';
            return (
              <p key={index} style={{ color }}>
                {entry.name}: {entry.value} {entry.payload.percentage ? `(${entry.payload.percentage.toFixed(1)}%)` : ''}
              </p>
            );
          })}
        </div>
      )
    }
    return null
  }

  // Custom gradient for bars
  const getBarGradient = useCallback((entry: SpamStatusItem) => {
    const status = entry.status as keyof typeof gradientColors;
    return gradientColors[status] || { start: '#AAAAAA', end: '#666666' };
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[200px]">
        <div className="animate-pulse bg-muted h-[150px] w-full rounded"></div>
      </div>
    )
  }

  if (error && (!chartData.length || !spamData.length)) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  return (
    <Tabs defaultValue="spam_status" className="w-full">
      <TabsList className="mb-4">
        <TabsTrigger value="spam_status">Spam Status Count</TabsTrigger>
        <TabsTrigger value="category">By Category</TabsTrigger>
      </TabsList>
      
      <TabsContent value="spam_status" className="mt-0">
        <div className="space-y-4">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart
              data={spamData}
              margin={{ top: 5, right: 20, left: 20, bottom: 5 }}
              style={{ backgroundColor: '#121212' }}
            >
              <defs>
                {spamData.map((entry, index) => {
                  const gradientInfo = getBarGradient(entry);
                  return (
                    <linearGradient 
                      key={`gradient-${index}`} 
                      id={`gradient-${entry.status.replace(/\s+/g, '-').toLowerCase()}`} 
                      x1="0" y1="0" x2="0" y2="1"
                    >
                      <stop offset="5%" stopColor={gradientInfo.start} stopOpacity={0.9}/>
                      <stop offset="95%" stopColor={gradientInfo.end} stopOpacity={0.9}/>
                    </linearGradient>
                  );
                })}
              </defs>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted opacity-30" />
              <XAxis 
                dataKey="status" 
                tickLine={false}
                axisLine={false}
                tickMargin={8}
                className="text-xs text-muted-foreground fill-gray-400"
              />
              <YAxis 
                tickLine={false} 
                axisLine={false} 
                tickMargin={8} 
                className="text-xs text-muted-foreground fill-gray-400"
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Bar 
                dataKey="count" 
                name="Count" 
                radius={[4, 4, 0, 0]}
              >
                {spamData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={`url(#gradient-${entry.status.replace(/\s+/g, '-').toLowerCase()})`} 
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </TabsContent>
      
      <TabsContent value="category" className="mt-0">
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-[#121212] rounded-md p-2">
            <h3 className="text-sm font-medium text-gray-200 mb-2">Medical</h3>
            <ResponsiveContainer width="100%" height={80}>
              <LineChart data={chartData} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
                <Line type="natural" dataKey="medical" stroke="#34A853" strokeWidth={2} dot={false} />
                <XAxis dataKey="date" tickLine={false} axisLine={false} tick={false} />
                <YAxis tickLine={false} axisLine={false} tick={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="bg-[#121212] rounded-md p-2">
            <h3 className="text-sm font-medium text-gray-200 mb-2">Environmental</h3>
            <ResponsiveContainer width="100%" height={80}>
              <LineChart data={chartData} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
                <Line type="natural" dataKey="environmental" stroke="#00BCD4" strokeWidth={2} dot={false} />
                <XAxis dataKey="date" tickLine={false} axisLine={false} tick={false} />
                <YAxis tickLine={false} axisLine={false} tick={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="bg-[#121212] rounded-md p-2">
            <h3 className="text-sm font-medium text-gray-200 mb-2">Emotional</h3>
            <ResponsiveContainer width="100%" height={80}>
              <LineChart data={chartData} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
                <Line type="natural" dataKey="emotional" stroke="#EA4335" strokeWidth={2} dot={false} />
                <XAxis dataKey="date" tickLine={false} axisLine={false} tick={false} />
                <YAxis tickLine={false} axisLine={false} tick={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="bg-[#121212] rounded-md p-2">
            <h3 className="text-sm font-medium text-gray-200 mb-2">Daily Living</h3>
            <ResponsiveContainer width="100%" height={80}>
              <LineChart data={chartData} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
                <Line type="natural" dataKey="daily_living" stroke="#FBBC05" strokeWidth={2} dot={false} />
                <XAxis dataKey="date" tickLine={false} axisLine={false} tick={false} />
                <YAxis tickLine={false} axisLine={false} tick={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </TabsContent>
    </Tabs>
  )
}
