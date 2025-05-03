"use client"

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, XAxis, YAxis } from "recharts"

import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"

const data = [
  { hour: "12 AM", time: 2.8 },
  { hour: "3 AM", time: 2.5 },
  { hour: "6 AM", time: 3.2 },
  { hour: "9 AM", time: 3.8 },
  { hour: "12 PM", time: 4.2 },
  { hour: "3 PM", time: 3.9 },
  { hour: "6 PM", time: 3.5 },
  { hour: "9 PM", time: 3.0 },
]

export function ResponseTimeChart() {
  return (
    <ChartContainer
      config={{
        time: {
          label: "Response Time (min)",
          color: "hsl(var(--chart-1))",
        },
      }}
      className="h-[250px]"
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          margin={{
            top: 16,
            right: 16,
            left: 0,
            bottom: 0,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" className="stroke-muted" vertical={false} />
          <XAxis
            dataKey="hour"
            tickLine={false}
            axisLine={false}
            tickMargin={8}
            className="text-xs text-muted-foreground"
          />
          <YAxis tickLine={false} axisLine={false} tickMargin={8} className="text-xs text-muted-foreground" />
          <ChartTooltip content={<ChartTooltipContent indicator="bar" />} />
          <Bar dataKey="time" fill="hsl(var(--chart-1))" radius={[4, 4, 0, 0]} maxBarSize={40} />
        </BarChart>
      </ResponsiveContainer>
    </ChartContainer>
  )
}
