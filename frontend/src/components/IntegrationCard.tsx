"use client"

import { useState } from "react"
import { useAuth0 } from "@auth0/auth0-react"
import { API_BASE_URL } from "../lib/api"

export default function IntegrationCard({service}:any){
  const { getAccessTokenSilently, loginWithPopup } = useAuth0()
  const [isPrompting, setIsPrompting] = useState(false)
  const [tokenInput, setTokenInput] = useState("")
  const [usernameInput, setUsernameInput] = useState("")
  const [passwordInput, setPasswordInput] = useState("")
  const [errorMessage, setErrorMessage] = useState("")

  const connect = async () => {
      setErrorMessage("")

      // Services that require manual token input
      const manualTokenServices = ["pic_tools", "slack", "github", "discord", "microsoft_azure", "salesforce", "linear"]
      
      // LeetCode requires username/password
      if (service.service === "leetcode") {
          setIsPrompting(true)
          return
      }
      
      if (manualTokenServices.includes(service.service)) {
          setIsPrompting(true)
          return
      }

      if (["google", "gmail", "drive", "calendar"].includes(service.service)) {
          try {
              const connection = "google-oauth2"
              
              // Request explicit Google API scopes
              let scopes = "openid profile email offline_access"
              if (service.service === "gmail") {
                  scopes = "openid profile email offline_access https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.compose"
              } else if (service.service === "drive") {
                  scopes = "openid profile email offline_access https://www.googleapis.com/auth/drive.file"
              } else if (service.service === "calendar") {
                  scopes = "openid profile email offline_access https://www.googleapis.com/auth/calendar.events"
              } else if (service.service === "google") {
                  scopes = "openid profile email offline_access https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.compose https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/calendar.events"
              }

              console.log(`[AgentOS] Starting OAuth flow for ${service.service} with connection: ${connection}`)
              
              await loginWithPopup({
                  authorizationParams: {
                      connection,
                      prompt: "consent",
                      access_type: "offline",
                      scope: scopes
                  }
              })

              console.log(`[AgentOS] OAuth popup completed, getting access token...`)
              
              const auth0Token = await getAccessTokenSilently()
              console.log(`[AgentOS] Got access token, length: ${auth0Token?.length || 0}`)
              
              console.log(`[AgentOS] Calling backend /api/integrations/connect/${service.service}...`)
              const res = await fetch(`${API_BASE_URL}/api/integrations/connect/${service.service}`, {
                  method: "POST",
                  headers: {
                      "Authorization": `Bearer ${auth0Token}`,
                      "Content-Type": "application/json"
                  },
                  body: JSON.stringify({ token: "auth0-vault-linked" })
              })

              console.log(`[AgentOS] Backend response: ${res.status}`)
              
              if (res.ok) {
                  console.log(`[AgentOS] Success! Reloading page...`)
                  window.location.reload()
              } else {
                  const body = await res.text().catch(() => "")
                  console.error(`[AgentOS] Backend error: ${res.status} ${body}`)
                  setErrorMessage(`Integration connect failed: ${res.status} ${body}`)
              }
          } catch (err: any) {
              const message = (err?.message || String(err)).toString()
              console.error(`[AgentOS] OAuth error:`, err)
              if (/consent/i.test(message)) {
                  setErrorMessage("Consent required: please complete provider consent and try again.")
              } else {
                  setErrorMessage(`Failed to connect ${service.service}: ${message}`)
              }
              console.error(`Failed to connect ${service.service} via Auth0 Token Vault`, err)
          }
      } else {
          setIsPrompting(true)
      }
  }

  const disconnect = async () => {
      try {
          const auth0Token = await getAccessTokenSilently()
          const res = await fetch(`${API_BASE_URL}/api/integrations/disconnect/${service.service}`, {
              method: "DELETE",
              headers: { "Authorization": `Bearer ${auth0Token}` }
          })
          if (res.ok) window.location.reload()
      } catch(e) {
          console.error("Failed to disconnect", e)
      }
  }

  const submitToken = async () => {
    // Handle LeetCode username/password
    if (service.service === "leetcode") {
        if (!usernameInput || !passwordInput) {
            setErrorMessage("Both username and password are required")
            return
        }
        
        try {
            const auth0Token = await getAccessTokenSilently()
            const res = await fetch(`${API_BASE_URL}/api/integrations/connect/${service.service}`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${auth0Token}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ username: usernameInput, password: passwordInput })
            })
            if (res.ok) {
                window.location.reload()
            } else {
                const body = await res.json().catch(() => ({}))
                setErrorMessage(body.detail || "Failed to connect LeetCode")
            }
        } catch(e) {
            console.error("Failed to connect", e)
            setErrorMessage("Failed to connect LeetCode")
        }
        return
    }
    
    if (!tokenInput) {
        setIsPrompting(false)
        return
    }

    try {
        const auth0Token = await getAccessTokenSilently()
        const res = await fetch(`${API_BASE_URL}/api/integrations/connect/${service.service}`, {
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

      {errorMessage && (
        <p className="text-xs text-red-300 mb-4 font-semibold break-words">
          {errorMessage}
        </p>
      )}

      {service.connected && service.granted_scopes && service.granted_scopes.length > 0 && (
        <div className="mb-4 bg-slate-700/50 border border-slate-600 px-4 py-3 rounded-md">
          <p className="text-xs uppercase tracking-widest text-slate-400 mb-3 font-semibold">Explicit Scopes Granted</p>
          <div className="flex flex-col gap-2">
            {service.granted_scopes.map((scope: any) => (
              <span key={scope.scope} className="text-xs font-mono bg-blue-500/15 text-blue-300 border border-blue-500/30 px-2.5 py-1 rounded-md">
                {scope.scope} - {scope.description}
              </span>
            ))}
          </div>
        </div>
      )}

      {service.connected && service.consent_timestamp && (
        <div className="mb-6 bg-slate-700/50 border border-slate-600 px-4 py-3 rounded-md">
          <p className="text-xs uppercase tracking-widest text-slate-400 mb-3 font-semibold">Consent Timestamp</p>
          <p className="text-xs text-slate-200 font-mono">{new Date(service.consent_timestamp).toLocaleString()}</p>
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
            <svg width={16} height={16} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
            Revoke Consent & Purge Token
          </button>
        )}

        {/* LeetCode: Username/Password form */}
        {!service.connected && isPrompting && service.service === "leetcode" && (
            <div className="flex flex-col gap-3">
              <input 
                  type="text" 
                  placeholder="LeetCode Username or Email"
                  value={usernameInput} 
                  onChange={(e) => setUsernameInput(e.target.value)} 
                  className="w-full font-mono text-sm bg-slate-700 text-slate-100 placeholder-slate-400 border border-slate-600 rounded-lg px-3 py-2 focus:border-amber-500 focus:outline-none focus:ring-2 focus:ring-amber-500/30"
                  autoFocus
              />
              <input 
                  type="password" 
                  placeholder="LeetCode Password"
                  value={passwordInput} 
                  onChange={(e) => setPasswordInput(e.target.value)} 
                  className="w-full font-mono text-sm bg-slate-700 text-slate-100 placeholder-slate-400 border border-slate-600 rounded-lg px-3 py-2 focus:border-amber-500 focus:outline-none focus:ring-2 focus:ring-amber-500/30"
              />
              <p className="text-xs text-slate-400">
                Credentials are stored securely for automated LeetCode submissions.
              </p>
              <div className="flex gap-2">
                <button 
                  onClick={() => { setIsPrompting(false); setUsernameInput(""); setPasswordInput(""); setErrorMessage(""); }} 
                  className="flex-1 bg-slate-700 hover:bg-slate-600 text-slate-300 text-xs font-semibold px-3 py-2 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button 
                    onClick={submitToken} 
                    className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-2 rounded-lg text-xs font-semibold transition-all shadow-md"
                >
                    Connect LeetCode
                </button>
              </div>
            </div>
        )}

        {/* Other services: Token input form */}
        {!service.connected && isPrompting && service.service !== "leetcode" && (
            <div className="flex flex-col gap-3">
              <input 
                  type="text" 
                  placeholder={
                    service.service === "slack" 
                      ? "Enter Slack Bot Token (xoxb-...)" 
                      : service.service === "github"
                      ? "Enter GitHub Personal Access Token"
                      : "Enter API Key or Token..."
                  }
                  value={tokenInput} 
                  onChange={(e) => setTokenInput(e.target.value)} 
                  className="w-full font-mono text-sm bg-slate-700 text-slate-100 placeholder-slate-400 border border-slate-600 rounded-lg px-3 py-2 focus:border-amber-500 focus:outline-none focus:ring-2 focus:ring-amber-500/30"
                  autoFocus
              />
              {service.service === "slack" && (
                <p className="text-xs text-slate-400">
                  Get token from <a href="https://api.slack.com/apps" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">api.slack.com/apps</a> → OAuth & Permissions → Bot User OAuth Token
                </p>
              )}
              {service.service === "github" && (
                <p className="text-xs text-slate-400">
                  Get PAT from <a href="https://github.com/settings/tokens" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">GitHub Settings → Tokens</a> with 'repo' scope
                </p>
              )}
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
