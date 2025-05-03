export default function LandingPage() {
  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-gradient-to-b from-background to-background/80">
      {/* Background elements - scaled down */}
      <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[30rem] h-[30rem] bg-primary/5 rounded-full blur-3xl opacity-60"></div>
        <div className="absolute bottom-1/4 left-1/2 -translate-x-1/2 w-[20rem] h-[20rem] bg-primary/5 rounded-full blur-3xl opacity-40"></div>
      </div>

      {/* Centered content - scaled down */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-xl px-6 z-10">
        <div className="grid place-items-center text-center">
          {/* Logo and title - smaller */}
          <div className="flex items-center justify-center gap-2 mb-10">
            <div className="relative flex h-14 w-14 items-center justify-center rounded-full bg-primary/10 ring-1 ring-primary/20">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="h-7 w-7 text-primary"
              >
                <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
              </svg>
              <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-primary text-xs font-bold text-primary-foreground">
                SL
              </span>
            </div>
            <h1 className="text-3xl font-semibold tracking-tight">SilverLine</h1>
          </div>

          {/* Headline and description - smaller text and spacing */}
          <div className="grid place-items-center gap-4 mb-10 w-full">
            <h2 className="text-xl font-medium text-muted-foreground max-w-md">
              Enhancing safety through real-time emergency monitoring
            </h2>
            <p className="text-muted-foreground text-sm max-w-md">
              Empowering caregivers and responders with actionable insights to deliver faster response times and
              improved care for those in need.
            </p>
          </div>

          {/* CTA Button - smaller */}
          <a
            href="/dashboard"
            className="inline-flex items-center justify-center rounded-md text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-6 py-2 transition-all group"
          >
            Get Started
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1"
            >
              <path d="M5 12h14" />
              <path d="m12 5 7 7-7 7" />
            </svg>
          </a>
        </div>
      </div>

      {/* Footer - smaller */}
      <footer className="absolute bottom-4 left-0 right-0 text-center text-xs text-muted-foreground">
        <p>© 2025 SilverLine. All rights reserved.</p>
      </footer>
    </div>
  )
}
