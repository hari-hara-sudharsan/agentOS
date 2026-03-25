"use client"

import { useState } from "react"
import { useAuth0 } from "@auth0/auth0-react"

export default function IntegrationCard({service}:any){
  const { getAccessTokenSilently, loginWithPopup } = useAuth0()
  const [isPrompting, setIsPrompting] = useState(false)
  const [tokenInput, setTokenInput] = useState("")

  const connect = async () => {
      if (["gmail", "drive", "calendar"].includes(service.service)) {
          try {
              // Trigger Auth0 OAuth flow for Google to store tokens in the Auth0 Token Vault
              await loginWithPopup({
                  authorizationParams: {
                      connection: "google-oauth2",
                      prompt: "consent",
                      access_type: "offline",
                      connection_scope: "https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/calendar.events"
                  }
              })
              
              // Tell backend to mark it as connected (Token Vault is the real source)
              const auth0Token = await getAccessTokenSilently()
              const res = await fetch(`http://127.0.0.1:8000/api/integrations/connect/${service.service}`, {
                  method: "POST",
                  headers: {
                      "Authorization": `Bearer ${auth0Token}`,
                      "Content-Type": "application/json"
                  },
                  body: JSON.stringify({ token: "auth0-vault-linked" })
              })
              
              if (res.ok) {
                  window.location.reload()
              }
          } catch(e) {
              console.error(`Failed to connect ${service.service} via Auth0 Token Vault`, e)
          }
      } else {
          setIsPrompting(true)
      }
  }

  const disconnect = async () => {
      try {
          const auth0Token = await getAccessTokenSilently()
          const res = await fetch(`http://127.0.0.1:8000/api/integrations/disconnect/${service.service}`, {
              method: "DELETE",
              headers: { "Authorization": `Bearer ${auth0Token}` }
          })
          if (res.ok) window.location.reload()
      } catch(e) {
          console.error("Failed to disconnect", e)
      }
  }

  const submitToken = async () => {
    if (!tokenInput) {
        setIsPrompting(false)
        return
    }

    try {
        const auth0Token = await getAccessTokenSilently()
        const res = await fetch(`http://127.0.0.1:8000/api/integrations/connect/${service.service}`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${auth0Token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ token: tokenInput })
        })
        if (res.ok) {
            window.location.reload()
        }
    } catch(e) {
        console.error("Failed to connect", e)
    }

  }

  return(
    <div className="elevated flex flex-col h-full border border-slate-600 dark:border-slate-500 rounded-lg bg-slate-800 p-6 relative overflow-hidden group hover:border-slate-400 transition-all">
      
      {/* Subtle top glow based on connection status */}
      <div className={`absolute top-0 left-0 right-0 h-1.5 ${service.connected ? 'bg-emerald-500' : 'bg-slate-700'}`} />

      <h3 className="font-display font-semibold text-xl text-slate-100 text-balance pr-12 mt-2">
        {service.name || service.service}
      </h3>

      <div className="mt-4 mb-4 flex items-center gap-2">
        {service.connected ? (
          <span className="inline-flex items-center gap-2 text-xs uppercase font-bold tracking-wider text-emerald-300 bg-emerald-500/15 px-3 py-1.5 rounded-full border border-emerald-500/30">
            <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_6px_#4ade80] animate-pulse"></span> 
            Vault Connected
          </span>
        ) : (
          <span className="inline-flex items-center gap-2 text-xs uppercase font-bold tracking-wider text-slate-400 bg-slate-700/50 px-3 py-1.5 rounded-full border border-slate-600">
            <span className="w-2 h-2 rounded-full bg-slate-500"></span> 
            Disconnected
          </span>
        )}
      </div>

      {service.description && (
        <p className="text-sm text-slate-300 mb-6 leading-relaxed flex-grow">
          {service.description}
        </p>
      )}

      {service.connected && service.scopes && service.scopes.length > 0 && (
        <div className="mb-6 bg-slate-700/50 border border-slate-600 px-4 py-3 rounded-md">
          <p className="text-xs uppercase tracking-widest text-slate-400 mb-3 font-semibold">Explicit Scopes Granted</p>
          <div className="flex flex-wrap gap-2">
            {service.scopes.map((scope: string) => (
              <span key={scope} className="text-xs font-mono bg-blue-500/15 text-blue-300 border border-blue-500/30 px-2.5 py-1 rounded-md">
                {scope}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="mt-auto pt-6 relative z-10">
        {!service.connected && !isPrompting && (
          <button
            onClick={connect}
            className="w-full bg-amber-600 hover:bg-amber-500 text-white text-sm font-semibold px-4 py-2.5 rounded-lg shadow-md transition-all transform hover:shadow-lg active:shadow-sm"
          >
            Authorize Vault Access
          </button>
        )}

        {service.connected && (
          <button
            onClick={disconnect}
            className="w-full bg-transparent hover:bg-red-600/20 text-red-400 text-sm font-semibold px-4 py-2.5 rounded-lg border border-red-500/40 hover:border-red-400 transition-colors flex items-center justify-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
            Revoke Consent & Purge Token
          </button>
        )}

        {!service.connected && isPrompting && (
            <div className="flex flex-col gap-3">
              <input 
                  type="text" 
                  placeholder="Enter Vault Token Override..." 
                  value={tokenInput} 
                  onChange={(e) => setTokenInput(e.target.value)} 
                  className="w-full font-mono text-sm bg-slate-700 text-slate-100 placeholder-slate-400 border border-slate-600 rounded-lg px-3 py-2 focus:border-amber-500 focus:outline-none focus:ring-2 focus:ring-amber-500/30"
                  autoFocus
              />
              <div className="flex gap-2">
                <button 
                  onClick={() => setIsPrompting(false)} 
                  className="flex-1 bg-slate-700 hover:bg-slate-600 text-slate-300 text-xs font-semibold px-3 py-2 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button 
                    onClick={submitToken} 
                    className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-2 rounded-lg text-xs font-semibold transition-all shadow-md"
                >
                    Confirm
                </button>
              </div>
            </div>
        )}
      </div>
    </div>
  )
}
