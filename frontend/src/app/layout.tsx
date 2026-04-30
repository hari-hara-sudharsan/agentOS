import "./globals.css"
import AuthProvider from "../components/AuthProvider"
import Navbar from "../components/Navbar"

export const metadata = {
  title: "AgentOS — Autonomous Intelligence Platform",
  description: "Enterprise-grade AI agent orchestration with human-in-the-loop safety. Manage integrations, execute tasks, and monitor agent activity.",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        {/* ── Ambient background system ── */}
        <div className="layout-bg" aria-hidden="true">
          <div className="layout-bg-glow layout-bg-glow--1" />
          <div className="layout-bg-glow layout-bg-glow--2" />
          <div className="layout-bg-glow layout-bg-glow--3" />
          <div className="layout-bg-grid" />
          <div className="layout-bg-vignette" />
        </div>

        {/* ── Top accent line ── */}
        <div className="layout-topline" aria-hidden="true" />

        <AuthProvider>
          <Navbar />
          <main className="layout-main">
            <div className="layout-content">
              {children}
            </div>
          </main>
        </AuthProvider>

        {/* ── Corner marks ── */}
        <div className="layout-corner layout-corner--tl" aria-hidden="true" />
        <div className="layout-corner layout-corner--tr" aria-hidden="true" />
        <div className="layout-corner layout-corner--bl" aria-hidden="true" />
        <div className="layout-corner layout-corner--br" aria-hidden="true" />

        <style>{`
          /* ══════════════════════════════════════
             BACKGROUND LAYERS
          ══════════════════════════════════════ */
          .layout-bg {
            position: fixed; inset: 0;
            pointer-events: none; z-index: 0;
          }
          .layout-bg-glow {
            position: absolute; border-radius: 50%;
          }
          .layout-bg-glow--1 {
            top: -25%; left: -10%;
            width: 70vw; height: 70vh;
            background: radial-gradient(circle, rgba(139,92,246,0.12) 0%, transparent 65%);
            animation: glow-breathe 7s ease-in-out infinite;
          }
          .layout-bg-glow--2 {
            bottom: -20%; right: -5%;
            width: 55vw; height: 60vh;
            background: radial-gradient(circle, rgba(6,182,212,0.09) 0%, transparent 60%);
            animation: glow-breathe 9s ease-in-out infinite reverse;
          }
          .layout-bg-glow--3 {
            top: 35%; left: 35%;
            width: 40vw; height: 40vh;
            background: radial-gradient(circle, rgba(236,72,153,0.05) 0%, transparent 55%);
            animation: glow-breathe 11s ease-in-out infinite;
          }
          .layout-bg-grid {
            position: absolute; inset: 0;
            background-image:
              linear-gradient(rgba(139,92,246,0.04) 1px, transparent 1px),
              linear-gradient(90deg, rgba(139,92,246,0.04) 1px, transparent 1px);
            background-size: 52px 52px;
            mask-image: radial-gradient(ellipse 85% 85% at 50% 50%, black 25%, transparent 100%);
          }
          .layout-bg-vignette {
            position: absolute; inset: 0;
            background: radial-gradient(ellipse 100% 100% at 50% 50%,
              transparent 35%, rgba(6,8,16,0.55) 75%, rgba(6,8,16,0.92) 100%);
          }

          /* ══════════════════════════════════════
             TOP LINE
          ══════════════════════════════════════ */
          .layout-topline {
            position: fixed;
            top: 0; left: 0; right: 0;
            height: 2px;
            background: linear-gradient(90deg,
              transparent 0%,
              rgba(109,40,217,0.5) 15%,
              var(--violet) 40%,
              var(--cyan) 60%,
              rgba(8,145,178,0.5) 85%,
              transparent 100%
            );
            z-index: 1000;
            box-shadow: 0 0 20px rgba(139,92,246,0.6), 0 0 60px rgba(6,182,212,0.2);
          }

          /* ══════════════════════════════════════
             CORNER MARKS
          ══════════════════════════════════════ */
          .layout-corner {
            position: fixed;
            width: 16px; height: 16px;
            z-index: 999;
            pointer-events: none;
            opacity: 0.35;
          }
          .layout-corner--tl { top: 12px; left: 14px;
            border-top: 1.5px solid var(--violet); border-left: 1.5px solid var(--violet); }
          .layout-corner--tr { top: 12px; right: 14px;
            border-top: 1.5px solid var(--cyan); border-right: 1.5px solid var(--cyan); }
          .layout-corner--bl { bottom: 14px; left: 14px;
            border-bottom: 1.5px solid var(--violet); border-left: 1.5px solid var(--violet); }
          .layout-corner--br { bottom: 14px; right: 14px;
            border-bottom: 1.5px solid var(--cyan); border-right: 1.5px solid var(--cyan); }

          /* ══════════════════════════════════════
             LAYOUT STRUCTURE
          ══════════════════════════════════════ */
          .layout-main {
            position: relative;
            z-index: 1;
            padding-left: clamp(24px, 4vw, 60px);
            padding-right: clamp(24px, 4vw, 60px);
          }
          .layout-content {
            padding: clamp(24px, 3vw, 40px) 0 72px;
            max-width: var(--max-width);
            margin: 0 auto;
            animation: fadeUp 0.5s var(--ease-out) both;
          }
        `}</style>
      </body>
    </html>
  )
}