"use client"

import { useAuth0 } from "@auth0/auth0-react"
import LoginButton from "../components/LoginButton"
import LogoutButton from "../components/LogoutButton"
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
        @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@300;400;500&display=swap');
        .load-root {
          height: 100vh; display: flex; flex-direction: column;
          align-items: center; justify-content: center;
          background: #02030a; gap: 28px; font-family: 'DM Mono', monospace;
        }
        .load-ring {
          width: 56px; height: 56px; border-radius: 50%;
          background: conic-gradient(from 0deg, transparent 0%, #ff2828 45%, #ff6060 55%, transparent 100%);
          animation: spin 1s linear infinite;
          display: flex; align-items: center; justify-content: center;
          box-shadow: 0 0 40px rgba(255,40,40,0.4), 0 0 80px rgba(255,40,40,0.12);
        }
        .load-core { width: 42px; height: 42px; border-radius: 50%; background: #02030a; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .load-label {
          font-size: 9px; letter-spacing: 0.45em; color: rgba(255,40,40,0.6);
          text-transform: uppercase;
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
        @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@300;400;500&display=swap');
        :root {
          --red: #ef4444; --red-dim: #7f1d1d;
          --void: #0f1419; --off-white: rgba(240,245,250,0.95);
          --muted: rgba(203,213,225,0.65);
        }
        .gate-root {
          height: 100vh; display: flex; flex-direction: column;
          align-items: center; justify-content: center;
          background: var(--void); position: relative;
          overflow: hidden; font-family: 'DM Mono', monospace;
        }
        .gate-root::before {
          content: '';
          position: absolute; inset: 0; pointer-events: none;
          background:
            radial-gradient(ellipse 80% 70% at 50% 0%, rgba(239,68,68,0.12) 0%, transparent 60%),
            radial-gradient(ellipse 60% 60% at 50% 100%, rgba(192,20,20,0.08) 0%, transparent 55%);
        }
        .gate-root::after {
          content: '';
          position: absolute; inset: 0; pointer-events: none;
          background-image:
            linear-gradient(rgba(239,68,68,0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(239,68,68,0.05) 1px, transparent 1px);
          background-size: 52px 52px;
          mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, black 20%, transparent 100%);
        }
        .gate-inner {
          position: relative; z-index: 1;
          display: flex; flex-direction: column; align-items: center; gap: 0;
          animation: gate-in 0.7s cubic-bezier(0.22,1,0.36,1) both;
        }
        @keyframes gate-in {
          from { opacity: 0; transform: translateY(30px); filter: blur(8px); }
          to   { opacity: 1; transform: translateY(0);    filter: blur(0); }
        }
        .gate-slash {
          font-family: 'Bebas Neue', sans-serif;
          font-size: 11px; letter-spacing: 0.5em;
          background: linear-gradient(90deg, var(--red), rgba(239,68,68,0.5));
          -webkit-background-clip: text; -webkit-text-fill-color: transparent;
          background-clip: text;
          margin-bottom: 10px;
        }
        .gate-logo {
          font-family: 'Bebas Neue', sans-serif;
          font-size: clamp(72px, 14vw, 120px);
          letter-spacing: 0.12em;
          line-height: 0.88;
          color: #ffffff;
          text-align: center;
          position: relative;
        }
        /* Red underline slash */
        .gate-logo::after {
          content: '';
          display: block;
          height: 3px;
          background: linear-gradient(90deg, transparent 0%, var(--red-dim) 15%, var(--red) 45%, rgba(239,68,68,0.9) 55%, var(--red-dim) 85%, transparent 100%);
          box-shadow: 0 0 16px rgba(239,68,68,0.6);
          margin-top: 6px;
        }
        .gate-tagline {
          margin-top: 20px; margin-bottom: 48px;
          font-size: 10px; letter-spacing: 0.28em; text-transform: uppercase;
          color: var(--muted); text-align: center;
        }
        .gate-corner { position: fixed; width: 22px; height: 22px; pointer-events: none; opacity: 0.5; }
        .gate-corner--tl { top: 14px; left: 14px;  border-top: 1.5px solid var(--red); border-left: 1.5px solid var(--red); }
        .gate-corner--tr { top: 14px; right: 14px; border-top: 1.5px solid var(--red); border-right: 1.5px solid var(--red); }
        .gate-corner--bl { bottom: 14px; left: 14px;  border-bottom: 1.5px solid var(--red); border-left: 1.5px solid var(--red); }
        .gate-corner--br { bottom: 14px; right: 14px; border-bottom: 1.5px solid var(--red); border-right: 1.5px solid var(--red); }
        .gate-topline {
          position: fixed; top: 0; left: 0; right: 0; height: 2px;
          background: linear-gradient(90deg, transparent, var(--red-dim) 15%, var(--red) 45%, rgba(255,90,90,0.9) 55%, var(--red-dim) 85%, transparent);
          box-shadow: 0 0 20px rgba(255,40,40,0.7);
        }
        .gate-version {
          position: fixed; bottom: 18px; right: 22px;
          font-size: 8px; letter-spacing: 0.25em; color: rgba(140,132,118,0.25);
        }
      `}</style>

      {/* Fixed chrome */}
      <div className="gate-topline" aria-hidden="true" />
      <div className="gate-corner gate-corner--tl" aria-hidden="true" />
      <div className="gate-corner gate-corner--tr" aria-hidden="true" />
      <div className="gate-corner gate-corner--bl" aria-hidden="true" />
      <div className="gate-corner gate-corner--br" aria-hidden="true" />
      <div className="gate-version">AGENT_OS // v2.4</div>

      <div className="gate-inner">
        <div className="gate-slash">// System Access</div>
        <div className="gate-logo">AgentOS</div>
        <p className="gate-tagline">Autonomous Intelligence Platform — Authenticate to proceed</p>
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

  if (isLoading)      return <LoadingScreen />
  if (!isAuthenticated) return <LoginGate />

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@300;400;500&display=swap');
        :root {
          --void:   #0f1419;
          --deep:   #1a1f2e;
          --surface:#252d3d;
          --red:    #ef4444;
          --red-dim:#7f1d1d;
          --off-white: rgba(240,245,250,0.95);
          --muted:  rgba(203,213,225,0.65);
          --dim:    rgba(148,163,184,0.48);
        }

        .home-root {
          min-height: 100vh;
          display: flex; flex-direction: column;
          background: var(--void);
          font-family: 'DM Mono', monospace;
          color: var(--off-white);
          position: relative; overflow: hidden;
        }

        /* ── Background ── */
        .home-bg {
          position: fixed; inset: 0; pointer-events: none; z-index: 0;
        }
        .home-bg-glow1 {
          position: absolute; top: -20%; left: -10%;
          width: 65vw; height: 65vh; border-radius: 50%;
          background: radial-gradient(circle, rgba(255,40,40,0.1) 0%, transparent 65%);
          animation: bg-breathe 7s ease-in-out infinite;
        }
        .home-bg-glow2 {
          position: absolute; bottom: -15%; right: -5%;
          width: 50vw; height: 55vh; border-radius: 50%;
          background: radial-gradient(circle, rgba(200,20,20,0.07) 0%, transparent 60%);
          animation: bg-breathe 9s ease-in-out infinite reverse;
        }
        .home-bg-grid {
          position: absolute; inset: 0;
          background-image:
            linear-gradient(rgba(255,40,40,0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,40,40,0.03) 1px, transparent 1px);
          background-size: 52px 52px;
          mask-image: radial-gradient(ellipse 88% 88% at 50% 50%, black 20%, transparent 100%);
        }
        .home-bg-vignette {
          position: absolute; inset: 0;
          background: radial-gradient(ellipse 100% 100% at 50% 50%,
            transparent 35%, rgba(2,3,10,0.55) 75%, rgba(2,3,10,0.92) 100%);
        }
        @keyframes bg-breathe {
          0%,100% { opacity:1; transform: scale(1); }
          50%      { opacity:0.65; transform: scale(1.06); }
        }

        /* ── Top bar ── */
        .home-topline {
          position: fixed; top: 0; left: 0; right: 0; height: 2px; z-index: 100;
          background: linear-gradient(90deg,
            transparent, var(--red-dim) 15%, var(--red) 45%,
            rgba(255,80,80,0.9) 55%, var(--red-dim) 85%, transparent);
          box-shadow: 0 0 20px rgba(255,40,40,0.7);
        }

        /* ── Corners ── */
        .corner { position: fixed; width: 20px; height: 20px; pointer-events: none; opacity: 0.4; z-index: 99; }
        .c-tl { top:14px; left:14px;   border-top:1.5px solid var(--red); border-left:1.5px solid var(--red); }
        .c-tr { top:14px; right:14px;  border-top:1.5px solid var(--red); border-right:1.5px solid var(--red); }
        .c-bl { bottom:14px; left:14px;  border-bottom:1.5px solid var(--red); border-left:1.5px solid var(--red); }
        .c-br { bottom:14px; right:14px; border-bottom:1.5px solid var(--red); border-right:1.5px solid var(--red); }

        /* ── Header ── */
        .home-header {
          position: relative; z-index: 1;
          display: flex; align-items: center; justify-content: space-between;
          padding: 28px 44px 24px;
          border-bottom: 1px solid rgba(255,40,40,0.1);
          background: rgba(2,3,10,0.6);
          backdrop-filter: blur(20px);
          animation: hdr-in 0.6s cubic-bezier(0.22,1,0.36,1) both;
        }

        @keyframes hdr-in {
          from { opacity: 0; transform: translateY(-12px); }
          to   { opacity: 1; transform: translateY(0); }
        }

        .home-brand {
          display: flex; flex-direction: column; gap: 2px;
        }
        .home-brand-slash {
          font-size: 8px; letter-spacing: 0.42em; text-transform: uppercase;
          background: linear-gradient(90deg, var(--red), rgba(255,40,40,0.4));
          -webkit-background-clip: text; -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        .home-brand-name {
          font-family: 'Bebas Neue', sans-serif;
          font-size: 28px; letter-spacing: 0.12em;
          color: #ffffff; line-height: 1;
        }

        .home-user-bar {
          display: flex; align-items: center; gap: 18px;
        }
        .home-user-id {
          display: flex; flex-direction: column; align-items: flex-end; gap: 2px;
        }
        .home-user-label {
          font-size: 7px; letter-spacing: 0.3em; text-transform: uppercase;
          color: var(--dim);
        }
        .home-user-name {
          font-size: 11px; letter-spacing: 0.1em; color: var(--muted);
        }
        .home-user-dot {
          width: 7px; height: 7px; border-radius: 50%;
          background: var(--red);
          box-shadow: 0 0 8px var(--red), 0 0 18px rgba(255,40,40,0.4);
          animation: dot-pulse 2.5s ease-in-out infinite;
          flex-shrink: 0;
        }
        @keyframes dot-pulse {
          0%,100% { opacity:1; box-shadow: 0 0 8px var(--red), 0 0 18px rgba(255,40,40,0.4); }
          50%      { opacity:0.55; box-shadow: 0 0 4px var(--red); }
        }
        .home-sep { width:1px; height:24px; background: rgba(255,40,40,0.12); }

        /* ── Main content ── */
        .home-body {
          position: relative; z-index: 1;
          flex: 1; display: flex; flex-direction: column; align-items: center;
          padding: 40px 44px 60px;
          animation: body-in 0.7s 0.1s cubic-bezier(0.22,1,0.36,1) both;
        }
        @keyframes body-in {
          from { opacity: 0; transform: translateY(20px); filter: blur(4px); }
          to   { opacity: 1; transform: translateY(0);    filter: blur(0); }
        }

        /* Section label */
        .home-section-label {
          align-self: flex-start; max-width: 780px; width: 100%;
          margin-bottom: 20px;
          display: flex; align-items: center; gap: 14px;
        }
        .home-section-line {
          height: 1px; width: 32px;
          background: linear-gradient(90deg, var(--red), transparent);
        }
        .home-section-text {
          font-size: 8px; letter-spacing: 0.38em; text-transform: uppercase;
          color: rgba(255,40,40,0.55);
        }

        /* Chat container */
        .home-chat-shell {
          width: 100%; max-width: 780px;
          border: 1px solid rgba(255,40,40,0.14);
          border-radius: 14px;
          overflow: hidden;
          background: rgba(6,7,15,0.75);
          backdrop-filter: blur(24px);
          box-shadow:
            0 0 0 1px rgba(255,255,255,0.03) inset,
            0 24px 64px rgba(0,0,0,0.7),
            0 0 60px rgba(255,40,40,0.05);
          position: relative;
        }

        /* Top edge shimmer */
        .home-chat-shell::before {
          content: '';
          position: absolute; top: 0; left: 5%; right: 5%; height: 1px;
          background: linear-gradient(90deg,
            transparent, rgba(255,40,40,0.15) 20%,
            rgba(255,80,80,0.4) 50%,
            rgba(255,40,40,0.15) 80%, transparent);
        }

        /* Chat panel chrome bar */
        .home-chat-bar {
          display: flex; align-items: center; justify-content: space-between;
          padding: 12px 20px;
          border-bottom: 1px solid rgba(255,40,40,0.08);
          background: rgba(2,3,10,0.5);
        }
        .chat-bar-left {
          display: flex; align-items: center; gap: 8px;
        }
        .chat-bar-dot {
          width: 6px; height: 6px; border-radius: 50%;
          background: var(--red);
          box-shadow: 0 0 6px var(--red);
          animation: dot-pulse 2s ease-in-out infinite;
        }
        .chat-bar-label {
          font-size: 8px; letter-spacing: 0.3em; text-transform: uppercase;
          color: rgba(255,40,40,0.55);
        }
        .chat-bar-right {
          font-size: 8px; letter-spacing: 0.18em; color: var(--dim);
        }

        .home-chat-inner { padding: 0; }
      `}</style>

      {/* ── Fixed chrome ── */}
      <div className="home-topline" aria-hidden="true" />
      <div className="corner c-tl" aria-hidden="true" />
      <div className="corner c-tr" aria-hidden="true" />
      <div className="corner c-bl" aria-hidden="true" />
      <div className="corner c-br" aria-hidden="true" />

      {/* ── Background ── */}
      <div className="home-bg" aria-hidden="true">
        <div className="home-bg-glow1" />
        <div className="home-bg-glow2" />
        <div className="home-bg-grid" />
        <div className="home-bg-vignette" />
      </div>

      <div className="home-root">

        {/* ── Header ── */}
        <header className="home-header">
          <div className="home-brand">
            <span className="home-brand-slash">// Autonomous Intelligence</span>
            <span className="home-brand-name">AgentOS</span>
          </div>

          <div className="home-user-bar">
            <div className="home-user-dot" />
            <div className="home-user-id">
              <span className="home-user-label">Authenticated Operator</span>
              <span className="home-user-name">{user?.name ?? user?.email}</span>
            </div>
            <div className="home-sep" />
            <LogoutButton />
          </div>
        </header>

        {/* ── Body ── */}
        <main className="home-body">

          <div className="home-section-label">
            <div className="home-section-line" />
            <span className="home-section-text">Active Session — Command Interface</span>
          </div>

          <div className="home-chat-shell">
            <div className="home-chat-bar">
              <div className="chat-bar-left">
                <div className="chat-bar-dot" />
                <span className="chat-bar-label">Live Channel</span>
              </div>
              <span className="chat-bar-right">ENCRYPTED · TLS 1.3</span>
            </div>
            <div className="home-chat-inner">
              <ChatBox />
            </div>
          </div>

        </main>
      </div>
    </>
  )
}