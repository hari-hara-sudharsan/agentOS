"use client"

import { useAuth0 } from "@auth0/auth0-react"
import LoginButton from "../components/LoginButton"
import ChatBox from "../components/ChatBox"

/* ── Loading ── */
function LoadingScreen() {
  return (
    <div className="load-root">
      <div className="load-ring">
        <div className="load-core" />
      </div>
      <span className="load-label">INITIALIZING</span>
      <style>{`
        .load-root {
          height: 100vh;
          display: flex; flex-direction: column;
          align-items: center; justify-content: center;
          background: var(--bg-void);
          gap: 24px;
          font-family: var(--font-mono);
        }
        .load-ring {
          width: 52px; height: 52px; border-radius: 50%;
          background: conic-gradient(from 0deg, transparent 0%, var(--violet) 40%, var(--cyan) 60%, transparent 100%);
          animation: spin 1.2s linear infinite;
          display: flex; align-items: center; justify-content: center;
          box-shadow: 0 0 40px rgba(139,92,246,0.4), 0 0 80px rgba(6,182,212,0.15);
        }
        .load-core { width: 38px; height: 38px; border-radius: 50%; background: var(--bg-void); }
        .load-label {
          font-size: 9px; letter-spacing: 0.45em;
          color: rgba(139,92,246,0.6); text-transform: uppercase;
        }
      `}</style>
    </div>
  )
}

/* ── Login Gate ── */
function LoginGate() {
  return (
    <div className="gate-root">
      <style>{`
        .gate-root {
          height: 100vh;
          display: flex; flex-direction: column;
          align-items: center; justify-content: center;
          background: var(--bg-void);
          position: relative; overflow: hidden;
          font-family: var(--font-body);
        }
        .gate-root::before {
          content: '';
          position: absolute; inset: 0; pointer-events: none;
          background:
            radial-gradient(ellipse 80% 70% at 50% 0%, rgba(139,92,246,0.12) 0%, transparent 60%),
            radial-gradient(ellipse 60% 60% at 50% 100%, rgba(6,182,212,0.08) 0%, transparent 55%);
        }
        .gate-root::after {
          content: '';
          position: absolute; inset: 0; pointer-events: none;
          background-image:
            linear-gradient(rgba(139,92,246,0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(139,92,246,0.04) 1px, transparent 1px);
          background-size: 52px 52px;
          mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, black 20%, transparent 100%);
        }
        .gate-inner {
          position: relative; z-index: 1;
          display: flex; flex-direction: column;
          align-items: center; gap: 0;
          animation: fadeUp 0.7s var(--ease-out) both;
        }
        .gate-eyebrow {
          font-family: var(--font-mono);
          font-size: 10px; letter-spacing: 0.4em; text-transform: uppercase;
          background: linear-gradient(90deg, var(--violet), var(--cyan));
          -webkit-background-clip: text; -webkit-text-fill-color: transparent;
          background-clip: text;
          margin-bottom: 12px;
        }
        .gate-logo {
          font-family: var(--font-display);
          font-size: clamp(64px, 14vw, 110px);
          font-weight: 800; letter-spacing: -0.02em;
          line-height: 0.9;
          background: linear-gradient(135deg, #ffffff 0%, var(--violet-light) 50%, var(--cyan) 100%);
          -webkit-background-clip: text; -webkit-text-fill-color: transparent;
          background-clip: text;
          text-align: center;
          position: relative;
        }
        .gate-logo::after {
          content: '';
          display: block;
          height: 3px;
          background: linear-gradient(90deg,
            transparent 0%, var(--violet-dim) 15%, var(--violet) 40%,
            var(--cyan) 60%, var(--cyan-dim) 85%, transparent 100%);
          box-shadow: 0 0 16px rgba(139,92,246,0.5), 0 0 32px rgba(6,182,212,0.3);
          margin-top: 8px;
          border-radius: 2px;
        }
        .gate-tagline {
          margin-top: 20px; margin-bottom: 44px;
          font-size: 13px; letter-spacing: 0.04em;
          color: var(--text-secondary); text-align: center;
          max-width: 400px; line-height: 1.6;
        }
        .gate-topline {
          position: fixed; top: 0; left: 0; right: 0; height: 2px;
          background: linear-gradient(90deg,
            transparent, var(--violet-dim) 20%, var(--violet) 40%,
            var(--cyan) 60%, var(--cyan-dim) 80%, transparent);
          box-shadow: 0 0 20px rgba(139,92,246,0.6), 0 0 40px rgba(6,182,212,0.3);
          z-index: 100;
        }
        .gate-corner {
          position: fixed; width: 16px; height: 16px;
          pointer-events: none; opacity: 0.35; z-index: 99;
        }
        .gate-corner--tl { top: 14px; left: 14px;
          border-top: 1.5px solid var(--violet); border-left: 1.5px solid var(--violet); }
        .gate-corner--tr { top: 14px; right: 14px;
          border-top: 1.5px solid var(--cyan); border-right: 1.5px solid var(--cyan); }
        .gate-corner--bl { bottom: 14px; left: 14px;
          border-bottom: 1.5px solid var(--violet); border-left: 1.5px solid var(--violet); }
        .gate-corner--br { bottom: 14px; right: 14px;
          border-bottom: 1.5px solid var(--cyan); border-right: 1.5px solid var(--cyan); }
        .gate-version {
          position: fixed; bottom: 18px; right: 22px;
          font-size: 9px; letter-spacing: 0.2em;
          color: var(--text-muted);
          font-family: var(--font-mono);
        }
      `}</style>

      <div className="gate-topline" aria-hidden="true" />
      <div className="gate-corner gate-corner--tl" aria-hidden="true" />
      <div className="gate-corner gate-corner--tr" aria-hidden="true" />
      <div className="gate-corner gate-corner--bl" aria-hidden="true" />
      <div className="gate-corner gate-corner--br" aria-hidden="true" />
      <div className="gate-version">AGENT_OS // v2.4</div>

      <div className="gate-inner">
        <div className="gate-eyebrow">Autonomous Intelligence</div>
        <div className="gate-logo">AgentOS</div>
        <p className="gate-tagline">Enterprise-grade AI agent orchestration with human-in-the-loop safety controls</p>
        <LoginButton />
      </div>
    </div>
  )
}

/* ══════════════════════════════════════════
   MAIN AUTHENTICATED HOME
══════════════════════════════════════════ */
export default function Home() {
  const { isAuthenticated, isLoading, user } = useAuth0()

  if (isLoading)        return <LoadingScreen />
  if (!isAuthenticated) return <LoginGate />

  return (
    <>
      <style>{`
        .home-root {
          min-height: calc(100vh - 60px);
          display: flex; flex-direction: column;
          font-family: var(--font-body);
          color: var(--text-base);
          position: relative;
        }
        .home-body {
          position: relative; z-index: 1;
          flex: 1;
          display: flex; flex-direction: column; align-items: center;
          padding: var(--space-10) 0 var(--space-16);
          animation: fadeUp 0.6s var(--ease-out) both;
        }
        .home-section-label {
          align-self: center;
          width: 100%; max-width: 920px;
          margin-bottom: 16px;
          display: flex; align-items: center; gap: 12px;
        }
        .home-section-line {
          height: 2px; width: 24px; flex-shrink: 0;
          background: linear-gradient(90deg, var(--violet), var(--cyan));
          border-radius: 2px;
        }
        .home-section-text {
          font-family: var(--font-mono);
          font-size: 10px; letter-spacing: 0.3em; text-transform: uppercase;
          color: var(--text-label);
        }
        .home-chat-shell {
          width: 100%; max-width: 920px;
        }
      `}</style>

      <div className="home-root">
        <div className="home-body">
          <div className="home-section-label">
            <div className="home-section-line" />
            <span className="home-section-text">Active Session — Command Interface</span>
          </div>
          <div className="home-chat-shell">
            <ChatBox />
          </div>
        </div>
      </div>
    </>
  )
}