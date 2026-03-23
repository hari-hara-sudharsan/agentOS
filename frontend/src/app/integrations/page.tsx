"use client"

import { useEffect, useState } from "react"
import IntegrationCard from "../../components/IntegrationCard"
import { useAuth0 } from "@auth0/auth0-react"

export default function Integrations() {
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
      } catch (e) {
        console.error(e)
      } finally {
        setLoaded(true)
      }
    }
    loadServices()
  }, [getAccessTokenSilently])

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@300;400;500&display=swap');

        /* ══ TOKENS ══ */
        :root {
          --void:       #02030a;
          --deep:       #07080f;
          --surface:    #0c0d1a;
          --raised:     #101220;

          --red:        #ff2828;
          --red-dim:    #8c1010;
          --red-ember:  rgba(255,40,40,0.07);
          --red-glow:   rgba(255,40,40,0.22);

          --white:      #ffffff;
          --off-white:  rgba(238,234,228,0.9);
          --muted:      rgba(190,184,172,0.5);
          --dim:        rgba(140,132,118,0.28);

          --border:     rgba(255,40,40,0.12);
          --border-hot: rgba(255,40,40,0.45);
        }

        /* ══ PAGE SHELL ══ */
        .int-page {
          min-height: 100vh;
          background: var(--void);
          padding: 48px 44px 80px;
          font-family: 'DM Mono', monospace;
          position: relative;
          overflow: hidden;
        }

        /* ── Ambient glows ── */
        .int-page::before {
          content: '';
          position: fixed; inset: 0; pointer-events: none; z-index: 0;
          background:
            radial-gradient(ellipse 70% 55% at  5% 0%,  rgba(255,40,40,0.11) 0%, transparent 60%),
            radial-gradient(ellipse 50% 60% at 95% 95%, rgba(200,20,20,0.08) 0%, transparent 55%),
            radial-gradient(ellipse 40% 30% at 50% 50%, rgba(255,60,60,0.04) 0%, transparent 50%);
        }

        /* ── Perspective grid ── */
        .int-page::after {
          content: '';
          position: fixed; inset: 0; pointer-events: none; z-index: 0;
          background-image:
            linear-gradient(rgba(255,40,40,0.035) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,40,40,0.035) 1px, transparent 1px);
          background-size: 52px 52px;
          mask-image: radial-gradient(ellipse 85% 85% at 50% 50%, black 25%, transparent 100%);
        }

        .int-inner { position: relative; z-index: 1; max-width: 1100px; margin: 0 auto; }

        /* ══ HEADER ══ */
        .int-header {
          margin-bottom: 48px;
          animation: reveal 0.6s cubic-bezier(0.22,1,0.36,1) both;
        }

        @keyframes reveal {
          from { opacity: 0; transform: translateY(18px); filter: blur(6px); }
          to   { opacity: 1; transform: translateY(0);    filter: blur(0); }
        }

        .int-eyebrow {
          display: flex; align-items: center; gap: 12px;
          margin-bottom: 14px;
        }

        .eyebrow-line {
          height: 1px; width: 40px;
          background: linear-gradient(90deg, var(--red), transparent);
        }

        .eyebrow-text {
          font-size: 9px; letter-spacing: 0.4em; text-transform: uppercase;
          color: rgba(255,40,40,0.7);
        }

        .eyebrow-count {
          margin-left: auto;
          font-size: 9px; letter-spacing: 0.2em;
          color: var(--dim);
        }

        .int-title {
          font-family: 'Bebas Neue', sans-serif;
          font-size: clamp(52px, 6vw, 80px);
          letter-spacing: 0.06em;
          line-height: 0.92;
          color: var(--white);
          position: relative;
        }

        /* Red slash accent behind title */
        .int-title-accent {
          display: block;
          font-size: 0.55em;
          letter-spacing: 0.18em;
          background: linear-gradient(90deg, var(--red), rgba(255,40,40,0.5));
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          margin-bottom: 2px;
        }

        .int-title-sub {
          margin-top: 16px;
          font-size: 11px; letter-spacing: 0.12em;
          color: var(--muted);
          max-width: 460px;
          line-height: 1.7;
        }

        /* ── Stat bar ── */
        .int-stat-bar {
          display: flex; align-items: center; gap: 0;
          margin-top: 28px;
          border: 1px solid var(--border);
          border-radius: 6px;
          overflow: hidden;
          width: fit-content;
          animation: reveal 0.6s 0.1s cubic-bezier(0.22,1,0.36,1) both;
        }

        .stat-seg {
          padding: 10px 22px;
          border-right: 1px solid var(--border);
          display: flex; flex-direction: column; gap: 3px;
        }
        .stat-seg:last-child { border-right: none; }

        .stat-seg-label {
          font-size: 8px; letter-spacing: 0.28em; text-transform: uppercase;
          color: var(--dim);
        }

        .stat-seg-value {
          font-family: 'Bebas Neue', sans-serif;
          font-size: 22px; letter-spacing: 0.06em;
          color: var(--off-white);
          line-height: 1;
        }

        .stat-seg-value.red { color: var(--red); }

        /* ══ DIVIDER ══ */
        .int-divider {
          height: 1px;
          background: linear-gradient(90deg,
            transparent 0%,
            var(--red-dim) 10%,
            rgba(255,40,40,0.5) 40%,
            rgba(255,80,80,0.6) 50%,
            rgba(255,40,40,0.5) 60%,
            var(--red-dim) 90%,
            transparent 100%
          );
          margin: 0 0 40px;
          box-shadow: 0 0 16px rgba(255,40,40,0.3);
          animation: reveal 0.6s 0.15s both;
        }

        /* ══ GRID ══ */
        .int-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 18px;
        }

        /* ── Card wrapper (stagger animation) ── */
        .int-card-wrap {
          animation: card-in 0.5s cubic-bezier(0.22,1,0.36,1) both;
        }

        @keyframes card-in {
          from { opacity: 0; transform: translateY(24px) scale(0.97); }
          to   { opacity: 1; transform: translateY(0)    scale(1); }
        }

        /* ── Skeleton ── */
        .int-skeleton {
          height: 120px;
          border-radius: 10px;
          border: 1px solid var(--border);
          background: var(--surface);
          overflow: hidden;
          position: relative;
        }

        .int-skeleton::after {
          content: '';
          position: absolute; inset: 0;
          background: linear-gradient(90deg,
            transparent 0%,
            rgba(255,40,40,0.04) 40%,
            rgba(255,40,40,0.08) 50%,
            rgba(255,40,40,0.04) 60%,
            transparent 100%
          );
          background-size: 200% 100%;
          animation: shimmer 1.8s infinite;
        }

        @keyframes shimmer {
          0%   { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }

        /* ── Empty state ── */
        .int-empty {
          grid-column: 1 / -1;
          padding: 80px 40px;
          text-align: center;
          border: 1px solid var(--border);
          border-radius: 12px;
          background: var(--red-ember);
          display: flex; flex-direction: column; align-items: center; gap: 14px;
        }

        .int-empty-icon {
          font-size: 36px; opacity: 0.2;
          font-family: 'Bebas Neue', sans-serif;
          letter-spacing: 0.1em;
          color: var(--red);
        }

        .int-empty-text {
          font-size: 11px; letter-spacing: 0.2em; text-transform: uppercase;
          color: var(--muted);
        }
      `}</style>

      <div className="int-page">
        <div className="int-inner">

          {/* ══ HEADER ══ */}
          <div className="int-header">
            <div className="int-eyebrow">
              <div className="eyebrow-line" />
              <span className="eyebrow-text">System Integrations</span>
              {loaded && (
                <span className="eyebrow-count">
                  {String(services.length).padStart(2, "0")} services
                </span>
              )}
            </div>

            <h1 className="int-title">
              <span className="int-title-accent">// Connected</span>
              Services
            </h1>

            <p className="int-title-sub">
              Live pipeline integrations and authorized service connections.
              All channels encrypted and authenticated.
            </p>

            {/* Stat bar */}
            {loaded && services.length > 0 && (
              <div className="int-stat-bar">
                <div className="stat-seg">
                  <span className="stat-seg-label">Total</span>
                  <span className="stat-seg-value">{String(services.length).padStart(2,"0")}</span>
                </div>
                <div className="stat-seg">
                  <span className="stat-seg-label">Active</span>
                  <span className="stat-seg-value red">
                    {String(services.filter((s:any) => s.status === "active" || s.connected).length).padStart(2,"0")}
                  </span>
                </div>
                <div className="stat-seg">
                  <span className="stat-seg-label">Channels</span>
                  <span className="stat-seg-value">ALL</span>
                </div>
                <div className="stat-seg">
                  <span className="stat-seg-label">Auth</span>
                  <span className="stat-seg-value red">OK</span>
                </div>
              </div>
            )}
          </div>

          {/* ══ DIVIDER ══ */}
          <div className="int-divider" />

          {/* ══ GRID ══ */}
          <div className="int-grid">
            {!loaded
              ? Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} className="int-skeleton" style={{ animationDelay: `${i * 0.07}s` }} />
                ))
              : services.length === 0
                ? (
                  <div className="int-empty">
                    <div className="int-empty-icon">NO_SIGNAL</div>
                    <p className="int-empty-text">No services connected</p>
                  </div>
                )
                : services.map((s: any, i: number) => (
                  <div
                    key={s.service}
                    className="int-card-wrap"
                    style={{ animationDelay: `${0.05 * i}s` }}
                  >
                    <IntegrationCard service={s} />
                  </div>
                ))
            }
          </div>

        </div>
      </div>
    </>
  )
}