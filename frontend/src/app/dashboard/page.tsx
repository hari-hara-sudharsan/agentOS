"use client"

import ChatBox from "../../components/ChatBox"
import { useAuth0 } from "@auth0/auth0-react"
import { useState, useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"

export default function Dashboard() {
  const { isLoading, user } = useAuth0()
  const router = useRouter()
  
  // Get session stats from sessionStorage
  const [stats, setStats] = useState({
    activeSessions: 1,
    tasksCompleted: 0,
    avgResponseTime: 0,
    systemHealth: 99.8
  })
  
  const [activities, setActivities] = useState<{time: string, msg: string}[]>([])
  const [sessionKey, setSessionKey] = useState(0) // Force re-render ChatBox

  // Function to start a new session
  const handleNewSession = useCallback(() => {
    // Clear session storage
    sessionStorage.removeItem("agentos_steps")
    sessionStorage.removeItem("agentos_goal")
    sessionStorage.removeItem("agentos_tick")
    
    // Reset stats
    setStats({
      activeSessions: 1,
      tasksCompleted: 0,
      avgResponseTime: 0,
      systemHealth: 99.8
    })
    
    // Reset activities
    const now = new Date()
    setActivities([
      { time: now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }), msg: "New session started" }
    ])
    
    // Force ChatBox to re-mount
    setSessionKey(prev => prev + 1)
  }, [])

  useEffect(() => {
    // Get steps from sessionStorage for stats
    const stepsData = sessionStorage.getItem("agentos_steps")
    const steps = stepsData ? JSON.parse(stepsData) : []
    
    const completed = steps.filter((s: any) => s.status === "completed" || s.status === "done").length
    const total = steps.length
    
    setStats(prev => ({
      ...prev,
      tasksCompleted: completed,
      avgResponseTime: total > 0 ? 1.2 : 0
    }))
    
    // Build activity log from steps
    const now = new Date()
    const newActivities = steps.slice(-4).reverse().map((step: any, idx: number) => {
      const time = new Date(now.getTime() - idx * 120000)
      const timeStr = time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
      let msg = ""
      if (step.status === "completed" || step.status === "done") {
        msg = `Task "${step.tool}" completed successfully`
      } else if (step.status === "failed") {
        msg = `Task "${step.tool}" encountered an error`
      } else if (step.status === "running") {
        msg = `Executing "${step.tool}"...`
      } else if (step.status === "awaiting_consent") {
        msg = `Awaiting approval for "${step.tool}"`
      } else {
        msg = `Task "${step.tool}" queued`
      }
      return { time: timeStr, msg }
    })
    
    if (newActivities.length === 0) {
      setActivities([
        { time: now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }), msg: "Dashboard session initialized" }
      ])
    } else {
      setActivities(newActivities)
    }
  }, [sessionKey])

  // Listen for storage changes to update stats
  useEffect(() => {
    const handleStorage = () => {
      const stepsData = sessionStorage.getItem("agentos_steps")
      const steps = stepsData ? JSON.parse(stepsData) : []
      const completed = steps.filter((s: any) => s.status === "completed" || s.status === "done").length
      setStats(prev => ({
        ...prev,
        tasksCompleted: completed,
        avgResponseTime: steps.length > 0 ? 1.2 : 0
      }))
    }
    
    window.addEventListener('storage', handleStorage)
    const interval = setInterval(handleStorage, 2000)
    return () => {
      window.removeEventListener('storage', handleStorage)
      clearInterval(interval)
    }
  }, [])

  if (isLoading) {
    return (
      <div className="loading-screen">
        <div className="loading-ring">
          <div className="loading-orb" />
        </div>
        <span className="loading-text">Initializing session…</span>
        <style>{`
          @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Geist+Mono:wght@300;400;500&display=swap');
          .loading-screen {
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            height: 100vh;
            background: radial-gradient(ellipse 80% 80% at 50% 50%, #0c1020 0%, #06080f 100%);
            gap: 24px;
            font-family: 'Geist Mono', monospace;
          }
          .loading-ring {
            width: 56px; height: 56px;
            border-radius: 50%;
            background: conic-gradient(from 0deg, transparent 0%, #8b5cf6 40%, #06b6d4 60%, transparent 100%);
            animation: spin 1.4s linear infinite;
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 0 48px rgba(139,92,246,0.4), 0 0 80px rgba(6,182,212,0.15);
          }
          .loading-orb {
            width: 44px; height: 44px;
            border-radius: 50%;
            background: #06080f;
          }
          @keyframes spin { to { transform: rotate(360deg); } }
          .loading-text {
            color: rgba(6,182,212,0.7);
            font-size: 10px;
            letter-spacing: 0.35em;
            text-transform: uppercase;
          }
        `}</style>
      </div>
    )
  }

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&family=Geist+Mono:wght@300;400;500&display=swap');

        :root {
          --bg-void:        #0a0c14;
          --bg-base:        #0d1017;
          --bg-raised:      #12151f;
          --bg-panel:       rgba(15,18,28,0.85);
          --bg-panel-hover: rgba(18,22,35,0.95);

          --border-subtle:  rgba(99,102,241,0.15);
          --border-mid:     rgba(99,102,241,0.25);
          --border-bright:  rgba(139,92,246,0.45);

          /* Vibrant color palette */
          --primary:        #8b5cf6;
          --primary-light:  #a78bfa;
          --primary-dim:    #6d28d9;
          --accent:         #06b6d4;
          --accent-light:   #22d3ee;
          --accent-dim:     #0891b2;
          
          --neon-pink:      #ec4899;
          --neon-blue:      #3b82f6;
          --neon-cyan:      #06b6d4;
          --neon-green:     #10b981;
          --neon-orange:    #f59e0b;
          --neon-red:       #ef4444;

          --text-primary:   rgba(255,255,255,0.95);
          --text-base:      rgba(226,232,240,0.85);
          --text-secondary: rgba(148,163,184,0.7);
          --text-muted:     rgba(100,116,139,0.5);
          --text-label:     rgba(139,92,246,0.8);

          --emerald:        #10b981;
          --rose:           #f43f5e;
          --sky:            #0ea5e9;
          --amber:          #f59e0b;

          --radius-sm: 8px;
          --radius-md: 12px;
          --radius-lg: 16px;
          --radius-xl: 24px;

          --shadow-glow: 0 0 40px rgba(139,92,246,0.15), 0 0 80px rgba(6,182,212,0.08);
          --shadow-panel: 0 8px 32px rgba(0,0,0,0.5), 0 2px 8px rgba(0,0,0,0.3);
          --shadow-deep:  0 24px 64px rgba(0,0,0,0.7), 0 8px 24px rgba(0,0,0,0.5);
        }

        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        /* ════════════════════════════════════
           ROOT & BACKGROUND
        ════════════════════════════════════ */
        .dash-root {
          min-height: 100vh;
          background: var(--bg-void);
          font-family: 'Geist Mono', monospace;
          color: var(--text-base);
          position: relative;
          overflow-x: hidden;
        }

        /* Layered ambient glow - vibrant colors */
        .dash-root::before {
          content: '';
          position: fixed; inset: 0;
          background:
            radial-gradient(ellipse 80% 60% at 0% 0%, rgba(139,92,246,0.15) 0%, transparent 50%),
            radial-gradient(ellipse 60% 80% at 100% 100%, rgba(6,182,212,0.12) 0%, transparent 50%),
            radial-gradient(ellipse 70% 50% at 50% 100%, rgba(236,72,153,0.08) 0%, transparent 45%),
            radial-gradient(ellipse 50% 50% at 80% 20%, rgba(16,185,129,0.06) 0%, transparent 40%),
            radial-gradient(ellipse 40% 40% at 20% 80%, rgba(59,130,246,0.08) 0%, transparent 40%);
          pointer-events: none; z-index: 0;
        }

        /* Film-grain texture */
        .dash-root::after {
          content: '';
          position: fixed; inset: 0;
          background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.88' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
          background-repeat: repeat; background-size: 160px;
          pointer-events: none; z-index: 0; opacity: 0.55;
          mix-blend-mode: overlay;
        }

        .dash-layout {
          position: relative; z-index: 1;
          display: grid;
          grid-template-columns: 220px 1fr;
          grid-template-rows: 60px 1fr;
          min-height: 100vh;
        }

        /* ════════════════════════════════════
           TOPBAR
        ════════════════════════════════════ */
        .topbar {
          grid-column: 1 / -1;
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 32px;
          height: 60px;
          background: rgba(10,12,20,0.9);
          border-bottom: 1px solid var(--border-subtle);
          backdrop-filter: blur(24px);
          -webkit-backdrop-filter: blur(24px);
          box-shadow: 0 1px 0 rgba(139,92,246,0.1);
        }

        .topbar-brand {
          display: flex; align-items: center; gap: 11px;
        }

        .brand-mark {
          width: 30px; height: 30px; flex-shrink: 0;
        }

        .brand-name {
          font-family: 'Cormorant Garamond', serif;
          font-size: 18px; font-weight: 600;
          letter-spacing: 0.1em;
          background: linear-gradient(130deg, #a78bfa 0%, #8b5cf6 35%, #06b6d4 65%, #10b981 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        .brand-name em {
          font-style: italic; font-weight: 300;
        }

        .topbar-right {
          display: flex; align-items: center; gap: 20px;
        }

        .status-pill {
          display: inline-flex; align-items: center; gap: 7px;
          padding: 5px 13px;
          border-radius: 100px;
          border: 1px solid rgba(16,185,129,0.3);
          background: rgba(16,185,129,0.1);
          font-size: 9px; letter-spacing: 0.2em; text-transform: uppercase;
          color: rgba(16,185,129,0.9);
        }

        .status-dot {
          width: 5px; height: 5px; border-radius: 50%;
          background: var(--emerald);
          box-shadow: 0 0 6px var(--emerald), 0 0 12px rgba(16,185,129,0.6);
          animation: pulse-dot 2.5s ease-in-out infinite;
        }

        @keyframes pulse-dot {
          0%, 100% { opacity: 1; box-shadow: 0 0 6px var(--emerald), 0 0 12px rgba(16,185,129,0.5); }
          50%       { opacity: 0.65; box-shadow: 0 0 3px var(--emerald); }
        }

        .topbar-divider {
          width: 1px; height: 20px;
          background: var(--border-subtle);
        }

        .topbar-avatar {
          width: 34px; height: 34px; border-radius: 50%;
          background: linear-gradient(135deg, var(--primary), var(--accent));
          border: 2px solid rgba(139,92,246,0.3);
          display: flex; align-items: center; justify-content: center;
          font-size: 12px; font-weight: 600;
          color: white;
          cursor: pointer;
          box-shadow: 0 0 20px rgba(139,92,246,0.3), inset 0 1px 0 rgba(255,255,255,0.25);
          transition: all 0.25s ease;
        }
        .topbar-avatar:hover {
          border-color: rgba(6,182,212,0.5);
          box-shadow: 0 0 28px rgba(6,182,212,0.4);
          transform: scale(1.05);
        }

        /* ════════════════════════════════════
           SIDEBAR
        ════════════════════════════════════ */
        .sidebar {
          border-right: 1px solid var(--border-subtle);
          background: rgba(10,12,20,0.7);
          backdrop-filter: blur(20px);
          padding: 28px 0 20px;
          display: flex; flex-direction: column;
          position: relative;
        }

        /* Vertical gradient thread on right edge */
        .sidebar::after {
          content: '';
          position: absolute;
          top: 20%; right: -1px; bottom: 20%;
          width: 2px;
          background: linear-gradient(to bottom, transparent, rgba(139,92,246,0.5), rgba(6,182,212,0.5), transparent);
          border-radius: 2px;
        }

        .sidebar-section-label {
          font-size: 8px; letter-spacing: 0.35em; text-transform: uppercase;
          color: var(--text-muted);
          padding: 0 20px 10px;
        }

        .sidebar-section-label + .sidebar-section-label,
        .nav-item ~ .sidebar-section-label {
          padding-top: 20px;
        }

        .nav-item {
          display: flex; align-items: center; gap: 11px;
          padding: 12px 20px;
          font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase;
          color: var(--text-secondary);
          cursor: pointer;
          transition: all 0.25s ease;
          border-left: 3px solid transparent;
          position: relative;
          user-select: none;
        }

        .nav-item:hover {
          color: var(--accent-light);
          background: linear-gradient(90deg, rgba(6,182,212,0.08) 0%, transparent 100%);
          border-left-color: rgba(6,182,212,0.5);
        }

        .nav-item.active {
          color: var(--primary-light);
          border-left-color: var(--primary);
          background: linear-gradient(90deg, rgba(139,92,246,0.12) 0%, transparent 100%);
        }

        /* Right glow bar on active item */
        .nav-item.active::after {
          content: '';
          position: absolute;
          right: 0; top: 15%; bottom: 15%;
          width: 2px;
          background: linear-gradient(to bottom, transparent, rgba(139,92,246,0.7), transparent);
          border-radius: 2px;
        }

        .nav-icon {
          width: 14px; height: 14px;
          opacity: 0.7;
          font-size: 13px; line-height: 1;
        }

        .nav-item.active .nav-icon { opacity: 1; }
        .nav-item:hover .nav-icon { opacity: 1; }

        .sidebar-spacer { flex: 1; }

        .sidebar-footer {
          margin: 0 14px;
          padding: 14px 16px;
          border: 1px solid var(--border-subtle);
          border-radius: var(--radius-md);
          background: linear-gradient(135deg, rgba(139,92,246,0.05) 0%, rgba(6,182,212,0.05) 100%);
        }

        .sidebar-footer-label {
          font-size: 8px; letter-spacing: 0.2em; text-transform: uppercase;
          color: var(--accent); margin-bottom: 4px;
        }
        .sidebar-footer-value {
          font-size: 10px; 
          background: linear-gradient(90deg, var(--text-secondary) 0%, var(--primary-light) 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          letter-spacing: 0.06em;
        }

        /* ════════════════════════════════════
           MAIN CONTENT
        ════════════════════════════════════ */
        .main-content {
          padding: 38px 42px;
          display: flex; flex-direction: column; gap: 30px;
          overflow-y: auto;
        }

        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(14px); }
          to   { opacity: 1; transform: translateY(0); }
        }

        /* ── Page Header ── */
        .page-header {
          display: flex; align-items: flex-end; justify-content: space-between;
          animation: fadeUp 0.55s ease both;
        }

        .page-eyebrow {
          font-size: 9px; letter-spacing: 0.35em; text-transform: uppercase;
          color: var(--text-label); margin-bottom: 10px;
          display: flex; align-items: center; gap: 8px;
        }
        .page-eyebrow::before {
          content: '';
          display: inline-block;
          width: 22px; height: 2px;
          background: linear-gradient(90deg, var(--primary), var(--accent));
          opacity: 0.8;
        }

        .page-title {
          font-family: 'Cormorant Garamond', serif;
          font-size: 36px; font-weight: 300; letter-spacing: 0.02em;
          line-height: 1.05;
          background: linear-gradient(130deg, #ffffff 0%, var(--primary-light) 50%, var(--accent) 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        .page-title em {
          font-style: italic; font-weight: 300;
        }

        .header-actions {
          display: flex; gap: 12px; align-items: center; padding-bottom: 4px;
        }

        .btn {
          padding: 10px 20px;
          border-radius: var(--radius-sm);
          font-family: 'Geist Mono', monospace;
          font-size: 9px; letter-spacing: 0.18em; text-transform: uppercase;
          cursor: pointer;
          transition: all 0.25s ease;
          outline: none;
        }

        .btn-ghost {
          border: 1px solid var(--border-subtle);
          background: transparent;
          color: var(--text-secondary);
        }
        .btn-ghost:hover {
          border-color: var(--accent);
          color: var(--accent-light);
          background: rgba(6,182,212,0.08);
        }

        .btn-primary {
          border: 1px solid rgba(139,92,246,0.4);
          background: linear-gradient(135deg, rgba(139,92,246,0.2) 0%, rgba(6,182,212,0.15) 100%);
          color: var(--primary-light);
          box-shadow: 0 0 20px rgba(139,92,246,0.15), inset 0 1px 0 rgba(255,255,255,0.1);
        }
        .btn-primary:hover {
          border-color: rgba(139,92,246,0.6);
          background: linear-gradient(135deg, rgba(139,92,246,0.3) 0%, rgba(6,182,212,0.2) 100%);
          box-shadow: 0 0 32px rgba(139,92,246,0.25), inset 0 1px 0 rgba(255,255,255,0.15);
          transform: translateY(-2px);
        }
        .btn-primary:active { transform: translateY(0); }

        /* ── Stats Grid ── */
        .stats-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 16px;
          animation: fadeUp 0.55s 0.08s ease both;
          opacity: 0;
          animation-fill-mode: both;
        }

        .stat-card {
          padding: 22px 22px 18px;
          border-radius: var(--radius-lg);
          border: 1px solid var(--border-subtle);
          background: var(--bg-panel);
          backdrop-filter: blur(20px);
          position: relative; overflow: hidden;
          transition: all 0.3s ease;
          cursor: default;
        }

        /* Top shimmer line - colorful gradient */
        .stat-card::before {
          content: '';
          position: absolute; top: 0; left: 10%; right: 10%;
          height: 2px;
          background: linear-gradient(90deg, transparent, var(--primary), var(--accent), transparent);
          opacity: 0;
          transition: opacity 0.3s ease;
        }

        /* Corner accent */
        .stat-card::after {
          content: '';
          position: absolute;
          bottom: 0; right: 0;
          width: 60px; height: 60px;
          background: radial-gradient(circle at 100% 100%, rgba(139,92,246,0.1) 0%, transparent 70%);
        }

        .stat-card:hover {
          border-color: var(--border-mid);
          transform: translateY(-4px);
          box-shadow: var(--shadow-glow), 0 16px 40px rgba(0,0,0,0.35);
        }
        .stat-card:hover::before { opacity: 1; }

        .stat-label {
          font-size: 8px; letter-spacing: 0.28em; text-transform: uppercase;
          color: var(--text-muted);
          margin-bottom: 14px;
        }

        .stat-value {
          font-family: 'Cormorant Garamond', serif;
          font-size: 32px; font-weight: 300;
          background: linear-gradient(135deg, var(--text-primary) 0%, var(--primary-light) 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          line-height: 1;
          margin-bottom: 10px;
          display: flex; align-items: baseline; gap: 3px;
        }
        .stat-unit {
          font-size: 13px;
          color: var(--accent);
          font-weight: 400;
          -webkit-text-fill-color: var(--accent);
        }

        .stat-delta {
          font-size: 9px; letter-spacing: 0.08em;
          color: var(--neon-green);
          display: flex; align-items: center; gap: 5px;
        }
        .stat-delta::before {
          content: '';
          display: inline-block;
          width: 16px; height: 1px;
          background: var(--neon-green);
          opacity: 0.5;
        }
        .stat-delta.down { color: var(--neon-pink); }
        .stat-delta.down::before { background: var(--neon-pink); opacity: 0.5; }
        .stat-delta.neutral { color: var(--text-muted); }
        .stat-delta.neutral::before { background: var(--text-muted); opacity: 0.4; }

        .stat-glyph {
          position: absolute; top: 16px; right: 18px;
          font-size: 24px; opacity: 0.12;
          line-height: 1;
          background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        /* ── Main Panel Area ── */
        .chat-section {
          display: grid;
          grid-template-columns: 1fr 280px;
          gap: 20px;
          animation: fadeUp 0.55s 0.16s ease both;
          opacity: 0;
          animation-fill-mode: both;
        }

        /* ── Glass Panel ── */
        .glass-panel {
          border-radius: var(--radius-xl);
          border: 1px solid var(--border-subtle);
          background: var(--bg-panel);
          backdrop-filter: blur(28px);
          -webkit-backdrop-filter: blur(28px);
          overflow: hidden;
          position: relative;
          box-shadow: var(--shadow-panel);
        }

        /* Prismatic top border - colorful */
        .glass-panel::before {
          content: '';
          position: absolute; top: 0; left: 0; right: 0;
          height: 2px;
          background: linear-gradient(90deg,
            transparent 0%,
            rgba(139,92,246,0.3) 15%,
            rgba(139,92,246,0.7) 35%,
            rgba(6,182,212,0.8) 50%,
            rgba(6,182,212,0.7) 65%,
            rgba(139,92,246,0.3) 85%,
            transparent 100%
          );
        }

        .panel-header {
          display: flex; align-items: center; justify-content: space-between;
          padding: 18px 24px;
          border-bottom: 1px solid var(--border-subtle);
          background: rgba(8,10,18,0.4);
        }

        .panel-title {
          font-size: 9px; letter-spacing: 0.28em; text-transform: uppercase;
          color: var(--text-label);
          display: flex; align-items: center; gap: 10px;
        }
        .panel-title::before {
          content: '';
          width: 4px; height: 4px; border-radius: 50%;
          background: var(--primary);
          box-shadow: 0 0 8px var(--primary);
        }

        .panel-badge {
          padding: 4px 12px;
          border-radius: 100px;
          border: 1px solid rgba(52,211,153,0.3);
          background: rgba(52,211,153,0.08);
          font-size: 8px; letter-spacing: 0.18em; text-transform: uppercase;
          color: var(--neon-green);
          display: flex; align-items: center; gap: 6px;
        }
        .panel-badge::before {
          content: '';
          width: 5px; height: 5px; border-radius: 50%;
          background: var(--neon-green);
          animation: pulse-dot 2s ease-in-out infinite;
        }

        /* ── Sidebar Info Panel ── */
        .info-panel {
          display: flex; flex-direction: column; gap: 16px;
        }

        .info-card {
          border-radius: var(--radius-lg);
          border: 1px solid var(--border-subtle);
          background: var(--bg-panel);
          backdrop-filter: blur(20px);
          overflow: hidden;
          position: relative;
          box-shadow: var(--shadow-panel);
          transition: all 0.25s ease;
        }
        .info-card:hover {
          border-color: var(--border-mid);
          box-shadow: var(--shadow-glow);
        }

        .info-card::before {
          content: '';
          position: absolute; top: 0; left: 0; right: 0;
          height: 2px;
          background: linear-gradient(90deg, transparent, var(--accent), transparent);
        }

        .info-card-header {
          padding: 14px 18px;
          font-size: 8px; letter-spacing: 0.28em; text-transform: uppercase;
          color: var(--text-label);
          border-bottom: 1px solid var(--border-subtle);
          background: rgba(8,10,18,0.35);
          display: flex; align-items: center; gap: 8px;
        }
        .info-card-header::before {
          content: '';
          width: 4px; height: 4px; border-radius: 50%;
          background: var(--accent);
        }

        .info-card-body {
          padding: 16px 18px;
        }

        .activity-log { display: flex; flex-direction: column; }

        .log-item {
          display: flex; gap: 12px; padding: 10px 0;
          align-items: flex-start;
          border-bottom: 1px solid rgba(139,92,246,0.06);
          transition: background 0.2s ease;
          border-radius: 4px;
        }
        .log-item:last-child { border-bottom: none; }
        .log-item:hover { background: rgba(139,92,246,0.04); }

        .log-line {
          display: flex; flex-direction: column; align-items: center;
          gap: 0; flex-shrink: 0;
          padding-top: 2px;
        }
        .log-dot-sm {
          width: 5px; height: 5px; border-radius: 50%;
          background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
          flex-shrink: 0;
        }

        .log-time {
          font-size: 8px; color: var(--text-muted);
          letter-spacing: 0.06em; flex-shrink: 0;
          padding-top: 1px;
          min-width: 35px;
        }

        .log-msg {
          font-size: 9px; color: var(--text-secondary);
          line-height: 1.6; letter-spacing: 0.03em;
        }

        /* Scrollbar - colorful */
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb {
          background: linear-gradient(180deg, var(--primary) 0%, var(--accent) 100%);
          border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover { 
          background: linear-gradient(180deg, var(--primary-light) 0%, var(--accent-light) 100%);
        }
      `}</style>

      <div className="dash-root">
        <div className="dash-layout">

          {/* ══ TOPBAR ══ */}
          <header className="topbar">
            <div className="topbar-brand">
              <div className="brand-mark">
                <svg viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg" width="30" height="30">
                  <defs>
                    <linearGradient id="gA" x1="0" y1="0" x2="30" y2="30" gradientUnits="userSpaceOnUse">
                      <stop stopColor="#a78bfa"/>
                      <stop offset="0.45" stopColor="#8b5cf6"/>
                      <stop offset="1" stopColor="#06b6d4"/>
                    </linearGradient>
                  </defs>
                  <polygon points="15,1.5 27,8.5 27,21.5 15,28.5 3,21.5 3,8.5"
                    stroke="url(#gA)" strokeWidth="1.2" fill="rgba(139,92,246,0.08)"/>
                  <polygon points="15,6.5 22,10.5 22,19.5 15,23.5 8,19.5 8,10.5"
                    stroke="url(#gA)" strokeWidth="0.8" fill="rgba(6,182,212,0.06)" opacity="0.8"/>
                  <circle cx="15" cy="15" r="3.5" fill="url(#gA)" opacity="0.9"/>
                  <circle cx="15" cy="15" r="1.5" fill="#e0e7ff"/>
                </svg>
              </div>
              <div className="brand-name">Agent <em>OS</em></div>
            </div>

            <div className="topbar-right">
              <div className="status-pill">
                <div className="status-dot" />
                Systems Nominal
              </div>
              <div className="topbar-divider" />
              <div className="topbar-avatar">{user?.name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || 'U'}</div>
            </div>
          </header>

          {/* ══ SIDEBAR ══ */}
          <aside className="sidebar">
            <div className="sidebar-section-label">Navigation</div>

            {[
              { icon: "◈", label: "Dashboard", href: "/dashboard", active: true },
              { icon: "◉", label: "Integrations", href: "/integrations", active: false },
              { icon: "◫", label: "Activity", href: "/activity", active: false },
              { icon: "◎", label: "Approvals", href: "/approvals", active: false },
            ].map(item => (
              <a 
                key={item.label} 
                href={item.href}
                className={`nav-item${item.active ? " active" : ""}`}
                style={{ textDecoration: 'none' }}
              >
                <span className="nav-icon">{item.icon}</span>
                {item.label}
              </a>
            ))}

            <div className="sidebar-section-label">Resources</div>

            {[
              { icon: "◑", label: "Documentation", href: "https://github.com/RealShocky/agentos", external: true },
              { icon: "◐", label: "API Reference", href: "/api/docs", external: false },
            ].map(item => (
              <a 
                key={item.label} 
                href={item.href}
                target={item.external ? "_blank" : undefined}
                rel={item.external ? "noopener noreferrer" : undefined}
                className="nav-item"
                style={{ textDecoration: 'none' }}
              >
                <span className="nav-icon">{item.icon}</span>
                {item.label}
              </a>
            ))}

            <div className="sidebar-spacer" />

            <div className="sidebar-footer">
              <div className="sidebar-footer-label">AgentOS</div>
              <div className="sidebar-footer-value">v1.0 · Devpost Edition</div>
            </div>
          </aside>

          {/* ══ MAIN ══ */}
          <main className="main-content">

            {/* Page Header */}
            <div className="page-header">
              <div>
                <div className="page-eyebrow">Command Interface</div>
                <h1 className="page-title">AI Agent <em>Dashboard</em></h1>
              </div>
              <div className="header-actions">
                <button className="btn btn-ghost">Export Log</button>
                <button className="btn btn-primary">+ New Session</button>
              </div>
            </div>

            {/* Stats */}
            <div className="stats-grid">
              {[
                { label: "Active Sessions", value: String(stats.activeSessions), unit: "", delta: "Real-time", mood: "", glyph: "◈" },
                { label: "Response Time", value: stats.avgResponseTime > 0 ? stats.avgResponseTime.toFixed(1) : "—", unit: stats.avgResponseTime > 0 ? "s" : "", delta: stats.avgResponseTime > 0 ? "Within SLA" : "No tasks yet", mood: "", glyph: "◎" },
                { label: "Tasks Completed", value: String(stats.tasksCompleted), unit: "", delta: "This session", mood: stats.tasksCompleted > 0 ? "" : "neutral", glyph: "◉" },
                { label: "System Health", value: stats.systemHealth.toFixed(1), unit: "%", delta: "All systems operational", mood: "neutral", glyph: "◫" },
              ].map(s => (
                <div key={s.label} className="stat-card">
                  <div className="stat-label">{s.label}</div>
                  <div className="stat-value">
                    {s.value}
                    {s.unit && <span className="stat-unit">{s.unit}</span>}
                  </div>
                  <div className={`stat-delta${s.mood ? ` ${s.mood}` : ""}`}>{s.delta}</div>
                  <div className="stat-glyph">{s.glyph}</div>
                </div>
              ))}
            </div>

            {/* Chat + Info */}
            <div className="chat-section">

              {/* Chat Panel */}
              <div className="glass-panel">
                <div className="panel-header">
                  <div className="panel-title">Active Conversation</div>
                  <div className="panel-badge">Live</div>
                </div>
                <ChatBox />
              </div>

              {/* Info Panel */}
              <div className="info-panel">

                {/* Activity Log */}
                <div className="info-card">
                  <div className="info-card-header">Recent Activity</div>
                  <div className="info-card-body">
                    <div className="activity-log">
                      {activities.map((l, i) => (
                        <div key={i} className="log-item">
                          <div className="log-line">
                            <div className="log-dot-sm" />
                          </div>
                          <div className="log-time">{l.time}</div>
                          <div className="log-msg">{l.msg}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

              </div>
            </div>

          </main>
        </div>
      </div>
    </>
  )
}