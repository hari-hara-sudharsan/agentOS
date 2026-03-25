import "./globals.css"
import AuthProvider from "../components/AuthProvider"
import Navbar from "../components/Navbar"

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link
          rel="preconnect"
          href="https://fonts.googleapis.com"
        />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@300;400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="layout-body">

        {/* ── Layered background system ── */}
        <div className="bg-field" aria-hidden="true">
          <div className="bg-grid" />
          <div className="bg-glow bg-glow--1" />
          <div className="bg-glow bg-glow--2" />
          <div className="bg-glow bg-glow--3" />
          <div className="bg-scanline" />
          <div className="bg-vignette" />
        </div>

        {/* ── Horizontal rule at very top ── */}
        <div className="layout-topline" aria-hidden="true" />

        <AuthProvider>
          <Navbar />

          <div className="layout-main">
            <div className="layout-content">
              {children}
            </div>
          </div>
        </AuthProvider>

        {/* ── Corner marks ── */}
        <div className="corner corner--tl" aria-hidden="true" />
        <div className="corner corner--tr" aria-hidden="true" />
        <div className="corner corner--bl" aria-hidden="true" />
        <div className="corner corner--br" aria-hidden="true" />

        <style>{`
          /* ══════════════════════════════════════════
             FONTS & TOKENS
          ══════════════════════════════════════════ */
          :root {
            --void:        #0f1419;
            --abyss:       #1a1f2e;
            --deep:        #252d3d;
            --surface:     #2d3647;

            --red-hot:     #ef4444;
            --red-mid:     #dc2626;
            --red-dim:     #7f1d1d;
            --red-ember:   rgba(239,68,68,0.12);

            --white-bright: #ffffff;
            --white-base:   rgba(240,245,250,0.95);
            --white-muted:  rgba(203,213,225,0.65);
            --white-dim:    rgba(148,163,184,0.48);

            --font-display: 'Bebas Neue', 'Impact', sans-serif;
            --font-mono:    'DM Mono', 'Courier New', monospace;

            --border-red:   rgba(239,68,68,0.22);
            --border-white: rgba(255,255,255,0.08);

            --shadow-red:   0 0 40px rgba(239,68,68,0.2), 0 0 80px rgba(239,68,68,0.08);
            --shadow-deep:  0 32px 80px rgba(0,0,0,0.7);
          }

          /* ══════════════════════════════════════════
             BODY
          ══════════════════════════════════════════ */
          .layout-body {
            min-height: 100vh;
            background: var(--void);
            font-family: var(--font-mono);
            color: var(--white-base);
            position: relative;
            overflow-x: hidden;
            -webkit-font-smoothing: antialiased;
            cursor: default;
          }

          /* ══════════════════════════════════════════
             BACKGROUND LAYERS
          ══════════════════════════════════════════ */
          .bg-field {
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: 0;
          }

          /* Tight perspective grid */
          .bg-grid {
            position: absolute;
            inset: 0;
            background-image:
              linear-gradient(rgba(239,68,68,0.06) 1px, transparent 1px),
              linear-gradient(90deg, rgba(239,68,68,0.06) 1px, transparent 1px);
            background-size: 48px 48px;
            mask-image: radial-gradient(ellipse 90% 90% at 50% 50%, black 30%, transparent 100%);
          }

          /* Large red glow — top left */
          .bg-glow--1 {
            position: absolute;
            top: -20%; left: -10%;
            width: 70vw; height: 70vh;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(239,68,68,0.15) 0%, transparent 65%);
            animation: glow-breathe 6s ease-in-out infinite;
          }

          /* Smaller glow — bottom right */
          .bg-glow--2 {
            position: absolute;
            bottom: -15%; right: -5%;
            width: 50vw; height: 60vh;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(220,38,38,0.1) 0%, transparent 65%);
            animation: glow-breathe 8s ease-in-out infinite reverse;
          }

          /* Deep center glow */
          .bg-glow--3 {
            position: absolute;
            top: 30%; left: 30%;
            width: 40vw; height: 40vh;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(239,68,68,0.06) 0%, transparent 60%);
            animation: glow-drift 12s ease-in-out infinite;
          }

          @keyframes glow-breathe {
            0%, 100% { opacity: 1; transform: scale(1); }
            50%       { opacity: 0.7; transform: scale(1.05); }
          }

          @keyframes glow-drift {
            0%, 100% { transform: translate(0, 0); }
            33%       { transform: translate(5%, -5%); }
            66%       { transform: translate(-4%, 4%); }
          }

          /* CRT scanline sweep */
          .bg-scanline {
            position: absolute;
            inset: 0;
            background: repeating-linear-gradient(
              to bottom,
              transparent 0px,
              transparent 3px,
              rgba(0,0,0,0.06) 3px,
              rgba(0,0,0,0.06) 4px
            );
            pointer-events: none;
          }

          /* Vignette */
          .bg-vignette {
            position: absolute;
            inset: 0;
            background: radial-gradient(ellipse 100% 100% at 50% 50%,
              transparent 40%,
              rgba(15,20,30,0.5) 80%,
              rgba(15,20,30,0.9) 100%
            );
          }

          /* ══════════════════════════════════════════
             TOP LINE
          ══════════════════════════════════════════ */
          .layout-topline {
            position: fixed;
            top: 0; left: 0; right: 0;
            height: 2px;
            background: linear-gradient(90deg,
              transparent 0%,
              var(--red-dim) 10%,
              var(--red-hot) 35%,
              #f87171 50%,
              var(--red-hot) 65%,
              var(--red-dim) 90%,
              transparent 100%
            );
            z-index: 1000;
            box-shadow: 0 0 20px rgba(239,68,68,0.9), 0 0 60px rgba(239,68,68,0.35);
            animation: line-pulse 3s ease-in-out infinite;
          }

          @keyframes line-pulse {
            0%, 100% { opacity: 1; }
            50%       { opacity: 0.7; }
          }

          /* ══════════════════════════════════════════
             CORNER MARKS
          ══════════════════════════════════════════ */
          .corner {
            position: fixed;
            width: 20px; height: 20px;
            z-index: 999;
            pointer-events: none;
            opacity: 0.45;
          }

          .corner--tl { top: 12px; left: 12px;
            border-top: 1.5px solid var(--red-hot);
            border-left: 1.5px solid var(--red-hot); }
          .corner--tr { top: 12px; right: 12px;
            border-top: 1.5px solid var(--red-hot);
            border-right: 1.5px solid var(--red-hot); }
          .corner--bl { bottom: 12px; left: 12px;
            border-bottom: 1.5px solid var(--red-hot);
            border-left: 1.5px solid var(--red-hot); }
          .corner--br { bottom: 12px; right: 12px;
            border-bottom: 1.5px solid var(--red-hot);
            border-right: 1.5px solid var(--red-hot); }

          /* ══════════════════════════════════════════
             LAYOUT STRUCTURE
          ══════════════════════════════════════════ */
          .layout-main {
            position: relative;
            z-index: 1;
          }

          .layout-content {
            padding: 32px 40px 60px;
            max-width: 1400px;
            margin: 0 auto;
            animation: content-enter 0.6s cubic-bezier(0.22, 1, 0.36, 1) both;
          }

          @keyframes content-enter {
            from {
              opacity: 0;
              transform: translateY(20px);
              filter: blur(4px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
              filter: blur(0);
            }
          }

          /* ══════════════════════════════════════════
             GLOBAL TYPOGRAPHY OVERRIDES
          ══════════════════════════════════════════ */
          h1, h2, h3, h4, h5, h6 {
            font-family: var(--font-display);
            letter-spacing: 0.06em;
            color: var(--white-bright);
          }

          /* Selection */
          ::selection {
            background: rgba(255,45,45,0.35);
            color: #ffffff;
          }

          /* Focus rings */
          :focus-visible {
            outline: 1.5px solid rgba(255,45,45,0.7);
            outline-offset: 3px;
          }

          /* Scrollbar */
          ::-webkit-scrollbar { width: 4px; height: 4px; }
          ::-webkit-scrollbar-track { background: var(--void); }
          ::-webkit-scrollbar-thumb {
            background: rgba(255,45,45,0.25);
            border-radius: 4px;
          }
          ::-webkit-scrollbar-thumb:hover {
            background: rgba(255,45,45,0.5);
          }
        `}</style>
      </body>
    </html>
  )
}