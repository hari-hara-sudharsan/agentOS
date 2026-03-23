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
              const res = await fetch(`http://localhost:8000/api/integrations/connect/${service.service}`, {
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
          const res = await fetch(`http://localhost:8000/api/integrations/disconnect/${service.service}`, {
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
        const res = await fetch(`http://localhost:8000/api/integrations/connect/${service.service}`, {
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

    <div className="bg-white p-4 rounded shadow">

      <h3 className="font-bold text-gray-800">
        {service.name || service.service}
      </h3>

      <div className="mb-3">
        {service.connected ? (
          <span className="inline-flex items-center gap-1 text-[10px] uppercase font-bold tracking-wider text-green-700 bg-green-100 px-2 py-0.5 rounded-full border border-green-300">
            <span className="w-1.5 h-1.5 rounded-full bg-green-500 shadow-[0_0_6px_#22c55e]"></span> 
            Vault Connected
          </span>
        ) : (
          <span className="inline-flex items-center gap-1 text-[10px] uppercase font-bold tracking-wider text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full border border-gray-200">
            <span className="w-1.5 h-1.5 rounded-full bg-gray-400"></span> 
            Disconnected
          </span>
        )}
      </div>

      {service.description && (
        <p className="text-xs text-gray-500 mb-4 leading-relaxed border-l-2 border-gray-200 pl-2">
          {service.description}
        </p>
      )}

      {service.connected && service.scopes && service.scopes.length > 0 && (
        <div className="mb-4">
          <p className="text-[9px] uppercase tracking-widest text-gray-400 mb-1 font-semibold">Explicit Scopes Granted</p>
          <div className="flex flex-wrap gap-1">
            {service.scopes.map((scope: string) => (
              <span key={scope} className="text-[10px] font-mono bg-blue-50 text-blue-700 border border-blue-200 px-1.5 py-0.5 rounded">
                {scope}
              </span>
            ))}
          </div>
        </div>
      )}

      {!service.connected && !isPrompting && (
        <button
          onClick={connect}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-4 py-2 rounded shadow-sm transition-colors"
        >
          Authorize Vault Access
        </button>
      )}

      {service.connected && (
        <button
          onClick={disconnect}
          className="w-full bg-white hover:bg-red-50 text-red-600 text-xs font-semibold px-4 py-2 rounded border border-red-200 hover:border-red-300 transition-colors flex items-center justify-center gap-2"
        >
          Revoke Consent & Purge Token
        </button>
      )}

      {!service.connected && isPrompting && (
          <div className="mt-3 flex gap-2">
            <input 
                type="text" 
                placeholder="Enter Vault Token Override..." 
                value={tokenInput} 
                onChange={(e) => setTokenInput(e.target.value)} 
                className="border p-1.5 rounded text-xs w-full text-black flex-1 font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
                autoFocus
            />
            <button 
                onClick={submitToken} 
                className="bg-green-600 hover:bg-green-700 text-white px-3 py-1.5 rounded text-xs shrink-0 font-semibold transition-colors"
            >
                Confirm
            </button>
          </div>
      )}

    </div>

  )

}
