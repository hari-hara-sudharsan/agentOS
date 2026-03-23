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

      <h3 className="font-bold">
        {service.service}
      </h3>

      <p className="text-sm mb-2">

        {service.connected
          ? "Connected"
          : "Not Connected"}

      </p>

      {!service.connected && !isPrompting && (

        <button
          onClick={connect}
          className="bg-blue-500 text-white px-3 py-1 rounded"
        >
          Connect
        </button>

      )}

      {service.connected && (

        <button
          onClick={disconnect}
          className="bg-red-500 text-white px-3 py-1 rounded"
        >
          Disconnect
        </button>

      )}

      {!service.connected && isPrompting && (
          <div className="mt-3 flex gap-2">
            <input 
                type="text" 
                placeholder="Enter API Key / Token" 
                value={tokenInput} 
                onChange={(e) => setTokenInput(e.target.value)} 
                className="border p-1 rounded text-sm w-full text-black flex-1"
                autoFocus
            />
            <button 
                onClick={submitToken} 
                className="bg-green-500 text-white px-3 py-1 rounded text-sm shrink-0"
            >
                Save
            </button>
          </div>
      )}

    </div>

  )

}
