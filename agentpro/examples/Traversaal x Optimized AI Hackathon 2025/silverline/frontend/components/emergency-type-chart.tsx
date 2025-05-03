"use client"

import { useEffect, useState } from "react"
import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { getCallTypes } from "@/lib/api"
import { useDateRange } from "@/components/date-range-picker"
import { format } from "date-fns"

export function EmergencyTypeChart() {
  const [chartData, setChartData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { dateRange } = useDateRange()

  useEffect(() => {
    async function fetchCallTypesData() {
      try {
        setLoading(true)
        setError(null)

        // Do not pass date parameters
        const data = await getCallTypes()

        // Transform API data to chart format
        const formattedData = data.data.map((item) => ({
          name: item.name,
          value: item.value,
          color: getColorForType(item.name),
        }))

        setChartData(formattedData)
      } catch (error) {
        console.error("Failed to fetch call types data:", error)
        setError("Failed to load chart data. Please check API connection.")
        setChartData([])
      } finally {
        setLoading(false)
      }
    }

    fetchCallTypesData()
  }, [])

  function getColorForType(type: string): string {
    // Enhanced color palette with distinct colors for each type
    switch (type) {
      case "Medical":
        return "#4285F4" // Blue
      case "Environmental":
        return "#34A853" // Green
      case "Emotional":
        return "#00BCD4" // Cyan/Teal
      case "Daily Living":
        return "#EA4335" // Red
      case "Not Sure":
        return "#9C27B0" // Purple
      case "Other":
        return "#FF9800" // Orange
      default:
        return "#757575" // Gray for any unlisted types
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[250px]">
        <div className="animate-pulse bg-muted h-[200px] w-[200px] rounded-full mx-auto"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-[250px] border border-red-200 bg-red-50 rounded-md">
        <div className="text-center p-4 text-red-800">
          <p className="font-semibold">Error Loading Chart Data</p>
          <p className="text-sm mt-1">{error}</p>
        </div>
      </div>
    )
  }

  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-[250px]">
        <p className="text-muted-foreground">No data available</p>
      </div>
    )
  }

  // Create config object for the chart
  const config = chartData.reduce((acc, item) => {
    const key = item.name.toLowerCase().replace(/\s+/g, "")
    acc[key] = {
      label: item.name,
      color: item.color,
    }
    return acc
  }, {})

  return (
    <ChartContainer config={config} className="h-[250px]">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            paddingAngle={2}
            dataKey="value"
            nameKey="name"
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            labelLine={false}
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <ChartTooltip content={<ChartTooltipContent indicator="dot" />} />
        </PieChart>
      </ResponsiveContainer>
    </ChartContainer>
  )
}
