"use client"

import { useEffect, useState } from "react"
import IntegrationCard from "../../components/IntegrationCard"
import { useAuth0 } from "@auth0/auth0-react"
import { withAuthenticationRequired } from "@auth0/auth0-react"

const DEFAULT_SERVICES = [
  { service: "google", name: "Google", scopes: ["gmail.readonly", "gmail.compose", "drive.file", "calendar.events"], description: "Unified Google access for Gmail/Drive/Calendar." },
  { service: "gmail", name: "Gmail (Read & Send)", scopes: ["gmail.readonly", "gmail.compose"], description: "Allows agent to read your inbox and send emails on your behalf." },
  { service: "pic_tools", name: "Pic Tools", scopes: [], description: "AI image generation and transformation." },
  { service: "slack", name: "Slack", scopes: ["chat:write", "channels:read"], description: "Send and receive messages in Slack." },
]

function Integrations() {
  const [services, setServices] = useState<any[]>(DEFAULT_SERVICES)
  const [loaded, setLoaded] = useState(false)
  const { getAccessTokenSilently } = useAuth0()

  useEffect(() => {
    async function loadServices() {
      try {
        const token = await getAccessTokenSilently()
        const res = await fetch("http://localhost:8000/api/integrations", {
          headers: { Authorization: `Bearer ${token}` },
        })

        if (res.ok) {
          const data = await res.json()
          if (Array.isArray(data) && data.length > 0) {
            setServices(data)
          }
        }
      } catch (e: any) {
        console.error("Failed to load services", e)
      } finally {
        setLoaded(true)
      }
    }
    loadServices()
  }, [getAccessTokenSilently])

  return (
    <div className="min-h-screen py-16 px-4 max-w-6xl mx-auto">
      
      <div className="mb-12">
        <h1 className="font-display text-4xl sm:text-6xl mb-4">
          Connected <span className="text-amber-500">Services</span>
        </h1>
        <p className="text-slate-400 max-w-2xl text-lg">
          Manage your system integrations and authorized service connections.
        </p>

        {loaded && (
           <div className="mt-8 flex gap-8 items-center bg-slate-800/50 p-6 rounded-lg border border-slate-700 w-fit">
              <div className="flex flex-col">
                <span className="text-xs uppercase text-slate-500 font-bold">Status</span>
                <span className="text-2xl font-display text-emerald-400 uppercase">Vault Active</span>
              </div>
              <div className="h-8 w-px bg-slate-700" />
              <div className="flex flex-col">
                <span className="text-xs uppercase text-slate-500 font-bold">Integrations</span>
                <span className="text-2xl font-display">{String(services.length).padStart(2, "0")} Available</span>
              </div>
           </div>
        )}
      </div>

      <hr className="my-12 border-slate-800" />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {services.map((s: any) => (
           <div key={s.service}>
              <IntegrationCard service={s} />
           </div>
        ))}
      </div>
    </div>
  )
}

export default withAuthenticationRequired(Integrations, {
  onRedirecting: () => (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-pulse flex flex-col items-center">
        <div className="h-12 w-12 rounded-full border-4 border-amber-500 border-t-transparent animate-spin mb-4"></div>
        <p className="text-slate-400 font-mono text-sm tracking-widest uppercase">Authenticating...</p>
      </div>
    </div>
  )
})