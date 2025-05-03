"use client"

import { useContext } from "react"
import { DateRangeContext } from "@/components/date-range-picker"

export function useDateRange() {
  const context = useContext(DateRangeContext)
  if (!context) {
    throw new Error("useDateRange must be used within a DateRangeProvider")
  }
  return context
}
