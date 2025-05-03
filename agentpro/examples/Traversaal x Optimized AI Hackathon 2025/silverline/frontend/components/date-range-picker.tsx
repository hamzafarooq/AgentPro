"use client"

import * as React from "react"
import { CalendarIcon } from "lucide-react"
import { addDays, format } from "date-fns"
import type { DateRange } from "react-day-picker"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"

// Create a context to share the date range across components
export const DateRangeContext = React.createContext<{
  dateRange: DateRange | undefined
  setDateRange: React.Dispatch<React.SetStateAction<DateRange | undefined>>
}>({
  dateRange: undefined,
  setDateRange: () => {},
})

export function DateRangeProvider({ children }: { children: React.ReactNode }) {
  // Set dateRange to undefined to not restrict data
  const [dateRange, setDateRange] = React.useState<DateRange | undefined>(undefined);

  return <DateRangeContext.Provider value={{ dateRange, setDateRange }}>{children}</DateRangeContext.Provider>
}

export function useDateRange() {
  const context = React.useContext(DateRangeContext)
  if (!context) {
    throw new Error("useDateRange must be used within a DateRangeProvider")
  }
  return context
}

export function DateRangePicker() {
  const { dateRange, setDateRange } = useDateRange()

  return (
    <div className="grid gap-2">
      <Popover>
        <PopoverTrigger asChild>
          <Button
            id="date"
            variant={"outline"}
            size="sm"
            className={cn("justify-start text-left font-normal", !dateRange && "text-muted-foreground")}
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {dateRange?.from ? (
              dateRange.to ? (
                <>
                  {format(dateRange.from, "LLL dd, y")} - {format(dateRange.to, "LLL dd, y")}
                </>
              ) : (
                format(dateRange.from, "LLL dd, y")
              )
            ) : (
              <span>Pick a date</span>
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <Calendar
            initialFocus
            mode="range"
            defaultMonth={dateRange?.from}
            selected={dateRange}
            onSelect={setDateRange}
            numberOfMonths={2}
          />
        </PopoverContent>
      </Popover>
    </div>
  )
}
