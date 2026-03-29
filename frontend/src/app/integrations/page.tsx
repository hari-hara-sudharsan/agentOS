"use client"

import { useEffect, useState } from "react"
import IntegrationCard from "../../components/IntegrationCard"
import { useAuth0 } from "@auth0/auth0-react"

import { withAuthenticationRequired } from "@auth0/auth0-react"

function Integrations() {
  const [services, setServices] = useState<any[]>([])
  const [loaded, setLoaded] = useState(false)
  const { getAccessTokenSilently } = useAuth0()

  useEffect(() => {
    async function loadServices() {
      try {
        const token = await getAccessTokenSilently()
        const res = await fetch("http://localhost:8000/api/integrations", {
          headers: { Authorization: `Bearer ${token}` },
        })
        const data = await res.json()
        setServices(Array.isArray(data) ? data : [])
      } catch (e: any) {
        console.error("Failed to load services", e)
      } finally {
        setLoaded(true)
      }
    }
    loadServices()
  }, [getAccessTokenSilently])

  return (
    <div className="min-h-screen py-16 px-4 sm:px-8 lg:px-16 max-w-6xl mx-auto">
      
      {/* Header Section */}
      <div className="mb-12 text-center sm:text-left">
        <div className="flex items-center justify-center sm:justify-start gap-4 mb-4">
          <div className="h-px w-12 accent-gradient" />
          <span className="text-sm font-semibold tracking-widest uppercase text-accent">System Integrations</span>
        </div>
        <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl mb-4 text-balance">
          Connected <span className="text-accent">Services</span>
        </h1>
        <p className="text-secondary max-w-2xl mx-auto sm:mx-0 text-lg">
          Live pipeline integrations and authorized service connections.
          All channels are encrypted, authenticated, and controlled by your strict consent.
        </p>

        {/* Stat Bar */}
        {loaded && services.length > 0 && (
          <div className="mt-8 inline-flex items-center gap-6 px-6 py-4 surface shadow-sm">
            <div className="flex flex-col">
              <span className="text-xs uppercase tracking-wider text-muted font-semibold">Total</span>
              <span className="text-2xl font-display font-medium">{String(services.length).padStart(2, "0")}</span>
            </div>
            <div className="w-px h-8 bg-black/10 dark:bg-white/10" />
            <div className="flex flex-col">
              <span className="text-xs uppercase tracking-wider text-muted font-semibold">Active</span>
              <span className="text-2xl font-display font-medium text-success">
                {String(services.filter((s:any) => s.status === "active" || s.connected).length).padStart(2,"0")}
              </span>
            </div>
            <div className="w-px h-8 bg-black/10 dark:bg-white/10" />
            <div className="flex flex-col">
              <span className="text-xs uppercase tracking-wider text-muted font-semibold">Security</span>
              <span className="text-2xl font-display font-medium text-info">Auth0 Vault</span>
            </div>
          </div>
        )}
      </div>

      <hr className="my-12 opacity-50" />

      {/* Grid Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 lg:gap-8">
        {!loaded ? (
          Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-48 surface animate-pulse border border-black/5 dark:border-white/5" style={{ animationDelay: `${i * 100}ms` }} />
          ))
        ) : services.length === 0 ? (
          <div className="col-span-1 md:col-span-2 py-20 text-center surface flex flex-col items-center justify-center border border-black/5 dark:border-white/5">
            <svg width={64} height={64} className="text-muted mb-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244" />
            </svg>
            <h3 className="text-xl font-display font-medium mb-2">No active connections</h3>
            <p className="text-sm text-secondary">Connect services to enable agent capabilities.</p>
          </div>
        ) : (
          services.map((s: any, i: number) => (
            <div key={s.service} className="transform transition-all duration-500 hover:-translate-y-1" style={{ animation: `fadeInUp 0.6s ease-out ${i * 0.1}s both` }}>
              <IntegrationCard service={s} />
            </div>
          ))
        )}
      </div>

      <style>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  )
}

export default withAuthenticationRequired(Integrations, {
  onRedirecting: () => (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-pulse flex flex-col items-center">
        <div className="h-12 w-12 rounded-full border-4 border-accent border-t-transparent animate-spin mb-4"></div>
        <p className="text-secondary font-mono text-sm tracking-widest uppercase">Authenticating...</p>
      </div>
    </div>
  )
})