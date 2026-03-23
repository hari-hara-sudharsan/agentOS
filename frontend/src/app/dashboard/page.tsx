"use client"

import ChatBox from "../../components/ChatBox"
import { useAuth0 } from "@auth0/auth0-react"

export default function Dashboard() {
  const { isLoading } = useAuth0()

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
            background: conic-gradient(from 0deg, transparent 0%, #c9a84c 40%, #e8d48b 60%, transparent 100%);
            animation: spin 1.4s linear infinite;
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 0 48px rgba(201,168,76,0.35), 0 0 80px rgba(201,168,76,0.12);
          }
          .loading-orb {
            width: 44px; height: 44px;
            border-radius: 50%;
            background: #06080f;
          }
          @keyframes spin { to { transform: rotate(360deg); } }
          .loading-text {
            color: rgba(201,168,76,0.6);
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
          --bg-void:        #05070d;
          --bg-base:        #07090f;
          --bg-raised:      #0b0e1a;
          --bg-panel:       rgba(11,14,26,0.7);
          --bg-panel-hover: rgba(13,17,30,0.85);

          --border-subtle:  rgba(201,168,76,0.1);
          --border-mid:     rgba(201,168,76,0.18);
          --border-bright:  rgba(201,168,76,0.38);

          --gold-pale:    #f5e8c0;
          --gold-bright:  #e8d48b;
          --gold:         #c9a84c;
          --gold-mid:     #a07a30;
          --gold-dim:     #6b5020;
          --copper:       #c07840;
          --copper-dim:   #7a4e28;

          --text-primary: rgba(240,233,215,0.92);
          --text-base:    rgba(220,210,188,0.78);
          --text-secondary:rgba(185,172,145,0.55);
          --text-muted:   rgba(145,130,100,0.38);
          --text-label:   rgba(201,168,76,0.55);

          --emerald:      #34d399;
          --rose:         #fb7185;
          --sky:          #7dd3fc;

          --radius-sm: 6px;
          --radius-md: 10px;
          --radius-lg: 16px;
          --radius-xl: 22px;

          --shadow-gold: 0 0 40px rgba(201,168,76,0.12), 0 0 80px rgba(201,168,76,0.04);
          --shadow-panel: 0 8px 32px rgba(0,0,0,0.4), 0 2px 8px rgba(0,0,0,0.3);
          --shadow-deep:  0 24px 64px rgba(0,0,0,0.6), 0 8px 24px rgba(0,0,0,0.4);
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

        /* Layered ambient glow */
        .dash-root::before {
          content: '';
          position: fixed; inset: 0;
          background:
            radial-gradient(ellipse 100% 70% at 0% 0%,   rgba(201,168,76,0.09) 0%,  transparent 55%),
            radial-gradient(ellipse 60%  80% at 100% 100%, rgba(100,60,160,0.08) 0%, transparent 50%),
            radial-gradient(ellipse 80%  50% at 50% 110%, rgba(192,120,64,0.05)  0%, transparent 45%),
            radial-gradient(ellipse 40%  40% at 70% 30%,  rgba(52,211,153,0.03)  0%, transparent 40%);
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
          background: rgba(5,7,13,0.85);
          border-bottom: 1px solid var(--border-subtle);
          backdrop-filter: blur(24px);
          -webkit-backdrop-filter: blur(24px);
          box-shadow: 0 1px 0 rgba(201,168,76,0.06);
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
          background: linear-gradient(130deg, var(--gold-pale) 0%, var(--gold-bright) 35%, var(--gold) 65%, var(--copper) 100%);
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
          border: 1px solid rgba(52,211,153,0.2);
          background: rgba(52,211,153,0.05);
          font-size: 9px; letter-spacing: 0.2em; text-transform: uppercase;
          color: rgba(52,211,153,0.7);
        }

        .status-dot {
          width: 5px; height: 5px; border-radius: 50%;
          background: var(--emerald);
          box-shadow: 0 0 6px var(--emerald), 0 0 12px rgba(52,211,153,0.5);
          animation: pulse-dot 2.5s ease-in-out infinite;
        }

        @keyframes pulse-dot {
          0%, 100% { opacity: 1; box-shadow: 0 0 6px var(--emerald), 0 0 12px rgba(52,211,153,0.4); }
          50%       { opacity: 0.65; box-shadow: 0 0 3px var(--emerald); }
        }

        .topbar-divider {
          width: 1px; height: 20px;
          background: var(--border-subtle);
        }

        .topbar-avatar {
          width: 32px; height: 32px; border-radius: 50%;
          background: linear-gradient(135deg, var(--gold-mid), var(--copper-dim));
          border: 1px solid var(--border-mid);
          display: flex; align-items: center; justify-content: center;
          font-size: 12px; font-weight: 600;
          color: var(--gold-bright);
          cursor: pointer;
          box-shadow: 0 0 16px rgba(201,168,76,0.15), inset 0 1px 0 rgba(255,255,255,0.1);
          transition: box-shadow 0.2s ease, border-color 0.2s ease;
        }
        .topbar-avatar:hover {
          border-color: var(--border-bright);
          box-shadow: 0 0 24px rgba(201,168,76,0.3);
        }

        /* ════════════════════════════════════
           SIDEBAR
        ════════════════════════════════════ */
        .sidebar {
          border-right: 1px solid var(--border-subtle);
          background: rgba(6,8,14,0.55);
          backdrop-filter: blur(20px);
          padding: 28px 0 20px;
          display: flex; flex-direction: column;
          position: relative;
        }

        /* Vertical gold thread on right edge */
        .sidebar::after {
          content: '';
          position: absolute;
          top: 20%; right: -1px; bottom: 20%;
          width: 1px;
          background: linear-gradient(to bottom, transparent, rgba(201,168,76,0.3), transparent);
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
          padding: 10px 20px;
          font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase;
          color: var(--text-muted);
          cursor: pointer;
          transition: color 0.2s ease, background 0.2s ease;
          border-left: 2px solid transparent;
          position: relative;
          user-select: none;
        }

        .nav-item:hover {
          color: rgba(201,168,76,0.8);
          background: rgba(201,168,76,0.03);
        }

        .nav-item.active {
          color: var(--gold-bright);
          border-left-color: var(--gold);
          background: linear-gradient(90deg, rgba(201,168,76,0.08) 0%, transparent 100%);
        }

        /* Right glow bar on active item */
        .nav-item.active::after {
          content: '';
          position: absolute;
          right: 0; top: 20%; bottom: 20%;
          width: 2px;
          background: linear-gradient(to bottom, transparent, rgba(201,168,76,0.6), transparent);
          border-radius: 2px;
        }

        .nav-icon {
          width: 14px; height: 14px;
          opacity: 0.6;
          font-size: 13px; line-height: 1;
        }

        .nav-item.active .nav-icon { opacity: 1; }

        .sidebar-spacer { flex: 1; }

        .sidebar-footer {
          margin: 0 14px;
          padding: 14px 16px;
          border: 1px solid var(--border-subtle);
          border-radius: var(--radius-md);
          background: rgba(201,168,76,0.03);
        }

        .sidebar-footer-label {
          font-size: 8px; letter-spacing: 0.2em; text-transform: uppercase;
          color: var(--text-muted); margin-bottom: 4px;
        }
        .sidebar-footer-value {
          font-size: 10px; color: var(--text-secondary); letter-spacing: 0.06em;
        }

        /* ════════════════════════════════════
           MAIN CONTENT
        ════════════════════════════════════ */
        .main-content {
          padding: 36px 40px;
          display: flex; flex-direction: column; gap: 28px;
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
          width: 18px; height: 1px;
          background: var(--gold);
          opacity: 0.6;
        }

        .page-title {
          font-family: 'Cormorant Garamond', serif;
          font-size: 34px; font-weight: 300; letter-spacing: 0.02em;
          line-height: 1.05;
          background: linear-gradient(130deg, #ffffff 0%, var(--gold-bright) 50%, var(--copper) 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        .page-title em {
          font-style: italic; font-weight: 300;
        }

        .header-actions {
          display: flex; gap: 10px; align-items: center; padding-bottom: 4px;
        }

        .btn {
          padding: 8px 18px;
          border-radius: var(--radius-sm);
          font-family: 'Geist Mono', monospace;
          font-size: 9px; letter-spacing: 0.18em; text-transform: uppercase;
          cursor: pointer;
          transition: all 0.22s ease;
          outline: none;
        }

        .btn-ghost {
          border: 1px solid var(--border-subtle);
          background: transparent;
          color: var(--text-secondary);
        }
        .btn-ghost:hover {
          border-color: var(--border-mid);
          color: var(--gold);
          background: rgba(201,168,76,0.04);
        }

        .btn-primary {
          border: 1px solid rgba(201,168,76,0.35);
          background: linear-gradient(135deg, rgba(201,168,76,0.14) 0%, rgba(192,120,64,0.1) 100%);
          color: var(--gold-bright);
          box-shadow: 0 0 20px rgba(201,168,76,0.08), inset 0 1px 0 rgba(201,168,76,0.18);
        }
        .btn-primary:hover {
          border-color: rgba(201,168,76,0.55);
          background: linear-gradient(135deg, rgba(201,168,76,0.22) 0%, rgba(192,120,64,0.16) 100%);
          box-shadow: 0 0 32px rgba(201,168,76,0.2), inset 0 1px 0 rgba(201,168,76,0.3);
          transform: translateY(-1px);
        }
        .btn-primary:active { transform: translateY(0); }

        /* ── Stats Grid ── */
        .stats-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 14px;
          animation: fadeUp 0.55s 0.08s ease both;
          opacity: 0;
          animation-fill-mode: both;
        }

        .stat-card {
          padding: 20px 20px 16px;
          border-radius: var(--radius-lg);
          border: 1px solid var(--border-subtle);
          background: var(--bg-panel);
          backdrop-filter: blur(20px);
          position: relative; overflow: hidden;
          transition: border-color 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease;
          cursor: default;
        }

        /* Top shimmer line */
        .stat-card::before {
          content: '';
          position: absolute; top: 0; left: 10%; right: 10%;
          height: 1px;
          background: linear-gradient(90deg, transparent, rgba(201,168,76,0.5), transparent);
          opacity: 0;
          transition: opacity 0.3s ease;
        }

        /* Corner accent */
        .stat-card::after {
          content: '';
          position: absolute;
          bottom: 0; right: 0;
          width: 50px; height: 50px;
          background: radial-gradient(circle at 100% 100%, rgba(201,168,76,0.07) 0%, transparent 70%);
        }

        .stat-card:hover {
          border-color: var(--border-mid);
          transform: translateY(-3px);
          box-shadow: var(--shadow-gold), 0 12px 32px rgba(0,0,0,0.3);
        }
        .stat-card:hover::before { opacity: 1; }

        .stat-label {
          font-size: 8px; letter-spacing: 0.28em; text-transform: uppercase;
          color: var(--text-muted);
          margin-bottom: 14px;
        }

        .stat-value {
          font-family: 'Cormorant Garamond', serif;
          font-size: 30px; font-weight: 300;
          color: var(--text-primary);
          line-height: 1;
          margin-bottom: 10px;
          display: flex; align-items: baseline; gap: 3px;
        }
        .stat-unit {
          font-size: 13px;
          color: var(--gold);
          font-weight: 400;
        }

        .stat-delta {
          font-size: 9px; letter-spacing: 0.08em;
          color: rgba(52,211,153,0.75);
          display: flex; align-items: center; gap: 5px;
        }
        .stat-delta::before {
          content: '';
          display: inline-block;
          width: 16px; height: 1px;
          background: rgba(52,211,153,0.4);
        }
        .stat-delta.down { color: rgba(251,113,133,0.75); }
        .stat-delta.down::before { background: rgba(251,113,133,0.4); }
        .stat-delta.neutral { color: var(--text-muted); }
        .stat-delta.neutral::before { background: var(--text-muted); opacity: 0.5; }

        .stat-glyph {
          position: absolute; top: 16px; right: 18px;
          font-size: 22px; opacity: 0.08;
          line-height: 1;
        }

        /* ── Main Panel Area ── */
        .chat-section {
          display: grid;
          grid-template-columns: 1fr 260px;
          gap: 18px;
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

        /* Prismatic top border */
        .glass-panel::before {
          content: '';
          position: absolute; top: 0; left: 0; right: 0;
          height: 1px;
          background: linear-gradient(90deg,
            transparent 0%,
            rgba(201,168,76,0.2) 15%,
            rgba(232,212,139,0.55) 40%,
            rgba(255,235,160,0.65) 50%,
            rgba(232,212,139,0.55) 60%,
            rgba(201,168,76,0.2) 85%,
            transparent 100%
          );
        }

        .panel-header {
          display: flex; align-items: center; justify-content: space-between;
          padding: 16px 22px;
          border-bottom: 1px solid var(--border-subtle);
          background: rgba(5,7,13,0.3);
        }

        .panel-title {
          font-size: 9px; letter-spacing: 0.28em; text-transform: uppercase;
          color: var(--text-label);
          display: flex; align-items: center; gap: 8px;
        }
        .panel-title::before {
          content: '';
          width: 3px; height: 3px; border-radius: 50%;
          background: var(--gold);
          box-shadow: 0 0 6px var(--gold);
        }

        .panel-badge {
          padding: 3px 10px;
          border-radius: 100px;
          border: 1px solid rgba(52,211,153,0.2);
          background: rgba(52,211,153,0.05);
          font-size: 8px; letter-spacing: 0.18em; text-transform: uppercase;
          color: rgba(52,211,153,0.65);
          display: flex; align-items: center; gap: 5px;
        }
        .panel-badge::before {
          content: '';
          width: 4px; height: 4px; border-radius: 50%;
          background: var(--emerald);
          animation: pulse-dot 2s ease-in-out infinite;
        }

        /* ── Sidebar Info Panel ── */
        .info-panel {
          display: flex; flex-direction: column; gap: 14px;
        }

        .info-card {
          border-radius: var(--radius-lg);
          border: 1px solid var(--border-subtle);
          background: var(--bg-panel);
          backdrop-filter: blur(20px);
          overflow: hidden;
          position: relative;
          box-shadow: var(--shadow-panel);
          transition: border-color 0.2s ease;
        }
        .info-card:hover {
          border-color: var(--border-mid);
        }

        .info-card::before {
          content: '';
          position: absolute; top: 0; left: 0; right: 0;
          height: 1px;
          background: linear-gradient(90deg, transparent, rgba(201,168,76,0.35), transparent);
        }

        .info-card-header {
          padding: 12px 16px;
          font-size: 8px; letter-spacing: 0.28em; text-transform: uppercase;
          color: var(--text-label);
          border-bottom: 1px solid var(--border-subtle);
          background: rgba(5,7,13,0.25);
          display: flex; align-items: center; gap: 7px;
        }
        .info-card-header::before {
          content: '';
          width: 3px; height: 3px; border-radius: 50%;
          background: var(--gold-mid);
        }

        .info-card-body {
          padding: 14px 16px;
        }

        .model-indicator {
          display: flex; align-items: center; gap: 10px;
          margin-bottom: 14px;
          padding-bottom: 14px;
          border-bottom: 1px solid var(--border-subtle);
        }

        .model-orb {
          width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0;
          background: conic-gradient(from 180deg, var(--gold-dim), var(--gold), var(--gold-bright), var(--gold));
          display: flex; align-items: center; justify-content: center;
          box-shadow: 0 0 16px rgba(201,168,76,0.25);
        }
        .model-orb-inner {
          width: 22px; height: 22px; border-radius: 50%;
          background: var(--bg-raised);
          display: flex; align-items: center; justify-content: center;
        }
        .model-orb-dot {
          width: 6px; height: 6px; border-radius: 50%;
          background: var(--gold);
          box-shadow: 0 0 8px var(--gold);
          animation: pulse-dot 2s ease-in-out infinite;
        }

        .model-name {
          font-size: 11px; color: var(--text-primary);
          letter-spacing: 0.04em; margin-bottom: 2px;
        }
        .model-version {
          font-size: 8px; color: var(--text-muted);
          letter-spacing: 0.12em;
        }

        .capability-row {
          display: flex; align-items: center; justify-content: space-between;
          padding: 7px 0;
          border-bottom: 1px solid rgba(201,168,76,0.05);
          font-size: 9px;
        }
        .capability-row:last-child { border-bottom: none; }
        .cap-label { color: var(--text-muted); letter-spacing: 0.08em; }
        .cap-value {
          color: var(--gold);
          letter-spacing: 0.05em;
          font-size: 9px;
        }
        .cap-dot {
          width: 5px; height: 5px; border-radius: 50%;
          background: var(--emerald);
          box-shadow: 0 0 5px var(--emerald);
          flex-shrink: 0;
        }
        .cap-dot.warn { background: var(--gold); box-shadow: 0 0 5px var(--gold); }

        .activity-log { display: flex; flex-direction: column; }

        .log-item {
          display: flex; gap: 10px; padding: 8px 0;
          align-items: flex-start;
          border-bottom: 1px solid rgba(201,168,76,0.04);
          transition: background 0.15s ease;
          border-radius: 4px;
        }
        .log-item:last-child { border-bottom: none; }

        .log-line {
          display: flex; flex-direction: column; align-items: center;
          gap: 0; flex-shrink: 0;
          padding-top: 2px;
        }
        .log-dot-sm {
          width: 4px; height: 4px; border-radius: 50%;
          background: var(--gold-dim);
          flex-shrink: 0;
        }

        .log-time {
          font-size: 8px; color: var(--text-muted);
          letter-spacing: 0.06em; flex-shrink: 0;
          padding-top: 1px;
          min-width: 30px;
        }

        .log-msg {
          font-size: 9px; color: rgba(210,200,175,0.5);
          line-height: 1.55; letter-spacing: 0.03em;
        }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 3px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb {
          background: rgba(201,168,76,0.18); border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover { background: rgba(201,168,76,0.35); }
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
                      <stop stopColor="#f5e8c0"/>
                      <stop offset="0.45" stopColor="#c9a84c"/>
                      <stop offset="1" stopColor="#b87333"/>
                    </linearGradient>
                  </defs>
                  <polygon points="15,1.5 27,8.5 27,21.5 15,28.5 3,21.5 3,8.5"
                    stroke="url(#gA)" strokeWidth="1" fill="rgba(201,168,76,0.06)"/>
                  <polygon points="15,6.5 22,10.5 22,19.5 15,23.5 8,19.5 8,10.5"
                    stroke="url(#gA)" strokeWidth="0.6" fill="rgba(201,168,76,0.04)" opacity="0.7"/>
                  <circle cx="15" cy="15" r="3.5" fill="url(#gA)" opacity="0.9"/>
                  <circle cx="15" cy="15" r="1.5" fill="#f5e8c0"/>
                </svg>
              </div>
              <div className="brand-name">Aether <em>Intelligence</em></div>
            </div>

            <div className="topbar-right">
              <div className="status-pill">
                <div className="status-dot" />
                Systems Nominal
              </div>
              <div className="topbar-divider" />
              <div className="topbar-avatar">A</div>
            </div>
          </header>

          {/* ══ SIDEBAR ══ */}
          <aside className="sidebar">
            <div className="sidebar-section-label">Navigation</div>

            {[
              { icon: "◈", label: "Dashboard", active: true },
              { icon: "◉", label: "Agent Hub",  active: false },
              { icon: "◫", label: "Memory",     active: false },
              { icon: "◎", label: "Workflows",  active: false },
            ].map(item => (
              <div key={item.label} className={`nav-item${item.active ? " active" : ""}`}>
                <span className="nav-icon">{item.icon}</span>
                {item.label}
              </div>
            ))}

            <div className="sidebar-section-label">System</div>

            {[
              { icon: "◑", label: "Analytics" },
              { icon: "◐", label: "Settings"  },
            ].map(item => (
              <div key={item.label} className="nav-item">
                <span className="nav-icon">{item.icon}</span>
                {item.label}
              </div>
            ))}

            <div className="sidebar-spacer" />

            <div className="sidebar-footer">
              <div className="sidebar-footer-label">Version</div>
              <div className="sidebar-footer-value">v2.4.1 · Production</div>
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
                { label: "Sessions Today", value: "48",   unit: "",  delta: "↑ 12% vs yesterday", mood: "",        glyph: "◈" },
                { label: "Avg Response",   value: "1.4",  unit: "s", delta: "↓ 8% faster",        mood: "",        glyph: "◎" },
                { label: "Tokens Used",    value: "284",  unit: "K", delta: "↑ 3% this hour",     mood: "",        glyph: "◉" },
                { label: "Success Rate",   value: "99.2", unit: "%", delta: "stable",              mood: "neutral", glyph: "◫" },
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

                {/* Model Card */}
                <div className="info-card">
                  <div className="info-card-header">Active Model</div>
                  <div className="info-card-body">
                    <div className="model-indicator">
                      <div className="model-orb">
                        <div className="model-orb-inner">
                          <div className="model-orb-dot" />
                        </div>
                      </div>
                      <div>
                        <div className="model-name">Claude Sonnet</div>
                        <div className="model-version">claude-sonnet-4 · 200K ctx</div>
                      </div>
                    </div>

                    {[
                      { cap: "Reasoning", val: "Advanced", dot: "" },
                      { cap: "Vision",    val: "Enabled",  dot: "" },
                      { cap: "Tools",     val: "Active",   dot: "" },
                      { cap: "Memory",    val: "Session",  dot: "warn" },
                    ].map(c => (
                      <div key={c.cap} className="capability-row">
                        <span className="cap-label">{c.cap}</span>
                        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                          <div className={`cap-dot${c.dot ? ` ${c.dot}` : ""}`} />
                          <span className="cap-value">{c.val}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Activity Log */}
                <div className="info-card">
                  <div className="info-card-header">Recent Activity</div>
                  <div className="info-card-body">
                    <div className="activity-log">
                      {[
                        { time: "14:32", msg: "Workflow 'Data-Sync' completed" },
                        { time: "14:18", msg: "Agent spawned for task #88" },
                        { time: "13:55", msg: "Memory snapshot saved" },
                        { time: "13:40", msg: "New session initialised" },
                      ].map((l, i) => (
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