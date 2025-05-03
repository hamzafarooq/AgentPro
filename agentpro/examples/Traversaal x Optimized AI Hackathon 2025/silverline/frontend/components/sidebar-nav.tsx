"use client"

import { useState } from "react"
import { ChevronLeft, ChevronRight, Home, Phone, FileText } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

export function SidebarNav() {
  const [collapsed, setCollapsed] = useState(false)
  
  // Access environment variables
  console.log("NEXT_PUBLIC_DIALPAD_URL", process.env.NEXT_PUBLIC_DIALPAD_URL)
  console.log("NEXT_PUBLIC_LOG_VIEWER_URL", process.env.NEXT_PUBLIC_LOG_VIEWER_URL)
  const dialpadUrl = process.env.NEXT_PUBLIC_DIALPAD_URL || "http://localhost:3001/dialer"
  const logViewerUrl = process.env.NEXT_PUBLIC_LOG_VIEWER_URL || "http://localhost:3002/gen-log"

  return (
    <div
      className={cn(
        "flex h-full flex-col border-r bg-background transition-all duration-300 ease-in-out relative",
        collapsed ? "w-16" : "w-64",
      )}
    >
      <Button
        variant="ghost"
        size="icon"
        className="absolute -right-3 top-6 h-6 w-6 rounded-full border bg-background shadow-md z-10"
        onClick={() => setCollapsed(!collapsed)}
      >
        {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
      </Button>

      <div className="flex-1 overflow-auto py-8">
        <nav className="grid items-start px-2 text-sm font-medium">
          <Button
            variant="ghost"
            size="sm"
            className={cn("justify-start gap-2 mb-1", collapsed && "justify-center px-0")}
            asChild
          >
            <Link href="/dashboard">
              <Home className="h-4 w-4" />
              {!collapsed && <span>Dashboard</span>}
            </Link>
          </Button>
          
          <Button
            variant="ghost"
            size="sm"
            className={cn("justify-start gap-2 mb-1", collapsed && "justify-center px-0")}
            asChild
          >
            <Link href={dialpadUrl} target="_blank" rel="noopener noreferrer">
              <Phone className="h-4 w-4" />
              {!collapsed && <span>Dialer</span>}
            </Link>
          </Button>
          
          <Button
            variant="ghost"
            size="sm"
            className={cn("justify-start gap-2 mb-1", collapsed && "justify-center px-0")}
            asChild
          >
            <Link href={logViewerUrl} target="_blank" rel="noopener noreferrer">
              <FileText className="h-4 w-4" />
              {!collapsed && <span>Log Viewer</span>}
            </Link>
          </Button>
        </nav>
      </div>
    </div>
  )
}
