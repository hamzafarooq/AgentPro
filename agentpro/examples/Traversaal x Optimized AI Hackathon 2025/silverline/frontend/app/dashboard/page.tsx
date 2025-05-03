import { Suspense } from "react"
import { PieChart, Menu, AlertCircle } from "lucide-react"
import Link from "next/link"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { EmergencyCallsChart } from "@/components/emergency-calls-chart"
import { EmergencyTypeChart } from "@/components/emergency-type-chart"
import { RecentCallsTable } from "@/components/recent-calls-table"
import { SidebarNav } from "@/components/sidebar-nav"
import { ThemeToggle } from "@/components/theme-toggle"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { DashboardMetrics } from "@/components/dashboard-metrics"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

export default function DashboardPage() {
  return (
    <div className="flex min-h-screen flex-col relative">
      <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary/5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 right-10 w-80 h-80 bg-primary/5 rounded-full blur-3xl"></div>
        <div className="absolute top-1/3 right-1/4 w-60 h-60 bg-primary/5 rounded-full blur-3xl"></div>
      </div>
      <header className="sticky top-0 z-10 flex h-16 items-center gap-4 border-b bg-background/80 backdrop-blur-sm px-6 shadow-sm">
        <div className="flex items-center gap-2">
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="md:hidden">
                <Menu className="h-5 w-5" />
                <span className="sr-only">Toggle menu</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="p-0">
              <SidebarNav />
            </SheetContent>
          </Sheet>
          <PieChart className="h-6 w-6 text-primary" />
          <span className="text-xl font-semibold tracking-tight">SilverLine Analytics</span>
        </div>
        <nav className="ml-auto flex items-center gap-4">
          <Button variant="ghost" size="sm" asChild>
            <Link href="/dashboard">Dashboard</Link>
          </Button>
          <ThemeToggle />
        </nav>
      </header>
      <div className="flex flex-1">
        <aside className="hidden md:block">
          <SidebarNav />
        </aside>
        <main className="flex flex-1 flex-col gap-4 p-4 md:gap-8 md:p-8">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
              <p className="text-sm text-muted-foreground">Overview of emergency call analytics and statistics.</p>
            </div>
          </div>

          <div className="space-y-4">
            <Suspense fallback={<MetricsLoadingSkeleton />}>
              <DashboardMetrics />
            </Suspense>

            <div className="grid gap-4 md:grid-cols-1 lg:grid-cols-7">
              <Card className="lg:col-span-4">
                <CardHeader>
                  <CardTitle>Call Status Breakdown</CardTitle>
                  <CardDescription>Analysis of call status</CardDescription>
                </CardHeader>
                <CardContent className="px-2">
                  <Suspense
                    fallback={
                      <div className="h-[250px] flex items-center justify-center">
                        <Skeleton className="h-[200px] w-full" />
                      </div>
                    }
                  >
                    <EmergencyCallsChart />
                  </Suspense>
                </CardContent>
              </Card>
              <Card className="lg:col-span-3">
                <CardHeader>
                  <CardTitle>Emergency Types</CardTitle>
                  <CardDescription>Distribution by category</CardDescription>
                </CardHeader>
                <CardContent>
                  <Suspense
                    fallback={
                      <div className="h-[250px] flex items-center justify-center">
                        <Skeleton className="h-[200px] w-full rounded-full" />
                      </div>
                    }
                  >
                    <EmergencyTypeChart />
                  </Suspense>
                </CardContent>
              </Card>
            </div>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle>Emergency Calls</CardTitle>
                <CardDescription className="mt-0">Scroll to view all emergency calls</CardDescription>
              </CardHeader>
              <CardContent className="pt-0">
                <Suspense fallback={<TableLoadingSkeleton />}>
                  <RecentCallsTable />
                </Suspense>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}

function MetricsLoadingSkeleton() {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {Array(4)
        .fill(0)
        .map((_, i) => (
          <Card key={i}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <Skeleton className="h-5 w-24" />
              <Skeleton className="h-4 w-4 rounded-full" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-16" />
            </CardContent>
          </Card>
        ))}
    </div>
  )
}

function TableLoadingSkeleton() {
  return (
    <div className="space-y-2">
      <Skeleton className="h-10 w-full" />
      {Array(5)
        .fill(0)
        .map((_, i) => (
          <Skeleton key={i} className="h-16 w-full" />
        ))}
    </div>
  )
}
