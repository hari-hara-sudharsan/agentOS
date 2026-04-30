"use client"

import { useEffect, useState } from "react"
import IntegrationCard from "../../components/IntegrationCard"
import { useAuth0 } from "@auth0/auth0-react"
import { withAuthenticationRequired } from "@auth0/auth0-react"
import { API_BASE_URL } from "../../lib/api"

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
        const res = await fetch(`${API_BASE_URL}/api/integrations`, {
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
    <>
      <style>{`
        .intg-page {
          padding: 40px 0;
          max-width: 1100px;
          margin: 0 auto;
          animation: fadeUp 0.5s var(--ease-out) both;
        }
        .intg-header { margin-bottom: 40px; }
        .intg-eyebrow {
          display: inline-flex; align-items: center; gap: 8px;
          font-family: var(--font-mono);
          font-size: 10px; letter-spacing: 0.3em; text-transform: uppercase;
          color: var(--text-label);
          margin-bottom: 12px;
        }
        .intg-eyebrow::before {
          content: '';
          width: 20px; height: 2px;
          background: linear-gradient(90deg, var(--violet), var(--cyan));
        }
        .intg-title {
          font-family: var(--font-display);
          font-size: 36px; font-weight: 700; letter-spacing: -0.02em;
          line-height: 1.1;
          margin-bottom: 8px;
        }
        .intg-title span {
          background: linear-gradient(135deg, var(--violet-light), var(--cyan));
          -webkit-background-clip: text; -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        .intg-subtitle {
          font-size: 14px; color: var(--text-secondary);
          max-width: 500px;
        }
        .intg-stats {
          display: flex; gap: 24px; align-items: center;
          margin-top: 24px;
          padding: 16px 20px;
          background: var(--bg-panel);
          border: 1px solid var(--border-subtle);
          border-radius: var(--radius-lg);
          width: fit-content;
          backdrop-filter: blur(16px);
        }
        .intg-stat {
          display: flex; flex-direction: column; gap: 4px;
        }
        .intg-stat-label {
          font-family: var(--font-mono);
          font-size: 10px; letter-spacing: 0.15em; text-transform: uppercase;
          color: var(--text-muted);
        }
        .intg-stat-value {
          font-family: var(--font-display);
          font-size: 20px; font-weight: 700;
          background: linear-gradient(135deg, var(--green-light), var(--cyan));
          -webkit-background-clip: text; -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        .intg-stat-divider {
          width: 1px; height: 28px;
          background: var(--border-subtle);
        }
        .intg-divider {
          height: 1px;
          background: linear-gradient(90deg, transparent, var(--border-subtle), transparent);
          margin: 32px 0;
        }
        .intg-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(480px, 1fr));
          gap: 20px;
        }
        @media (max-width: 640px) {
          .intg-grid { grid-template-columns: 1fr; }
        }
      `}</style>

      <div className="intg-page">
        <div className="intg-header">
          <div className="intg-eyebrow">Service Connections</div>
          <h1 className="intg-title">
            Connected <span>Services</span>
          </h1>
          <p className="intg-subtitle">
            Manage your system integrations and authorized service connections.
          </p>

          {loaded && (
            <div className="intg-stats">
              <div className="intg-stat">
                <span className="intg-stat-label">Status</span>
                <span className="intg-stat-value">Vault Active</span>
              </div>
              <div className="intg-stat-divider" />
              <div className="intg-stat">
                <span className="intg-stat-label">Integrations</span>
                <span className="intg-stat-value">{String(services.length).padStart(2, "0")} Available</span>
              </div>
            </div>
          )}
        </div>

        <div className="intg-divider" />

        <div className="intg-grid">
          {services.map((s: any) => (
            <div key={s.service}>
              <IntegrationCard service={s} />
            </div>
          ))}
        </div>
      </div>
    </>
  )
}

export default withAuthenticationRequired(Integrations, {
  onRedirecting: () => (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
        <div style={{ width: 40, height: 40, borderRadius: '50%', border: '3px solid rgba(139,92,246,0.2)', borderTopColor: 'var(--violet)', animation: 'spin 1s linear infinite' }} />
        <p style={{ fontFamily: 'var(--font-mono)', fontSize: 11, letterSpacing: '0.2em', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Authenticating...</p>
      </div>
    </div>
  )
})