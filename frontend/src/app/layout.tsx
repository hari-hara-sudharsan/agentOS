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
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
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

            /* ── Spacing scale ── */
            --space-xs:  8px;
            --space-sm:  16px;
            --space-md:  24px;
            --space-lg:  40px;
            --space-xl:  64px;

            /* ── Layout widths ── */
            --content-max:  1400px;
            --content-pad-x: clamp(20px, 4vw, 56px);
            --content-pad-y: clamp(24px, 3vw, 40px);
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

          .bg-grid {
            position: absolute;
            inset: 0;
            background-image:
              linear-gradient(rgba(239,68,68,0.06) 1px, transparent 1px),
              linear-gradient(90deg, rgba(239,68,68,0.06) 1px, transparent 1px);
            background-size: 48px 48px;
            mask-image: radial-gradient(ellipse 90% 90% at 50% 50%, black 30%, transparent 100%);
          }

          .bg-glow--1 {
            position: absolute;
            top: -20%; left: -10%;
            width: 70vw; height: 70vh;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(239,68,68,0.15) 0%, transparent 65%);
            animation: glow-breathe 6s ease-in-out infinite;
          }

          .bg-glow--2 {
            position: absolute;
            bottom: -15%; right: -5%;
            width: 50vw; height: 60vh;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(220,38,38,0.1) 0%, transparent 65%);
            animation: glow-breathe 8s ease-in-out infinite reverse;
          }

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
             CORNER MARKS  — perfectly inset from edges
          ══════════════════════════════════════════ */
          .corner {
            position: fixed;
            width: 18px; height: 18px;
            z-index: 999;
            pointer-events: none;
            opacity: 0.45;
          }

          /* Offset = topline height (2px) + gap (10px) = 12px; sides 14px */
          .corner--tl { top: 12px;  left: 14px;
            border-top:    1.5px solid var(--red-hot);
            border-left:   1.5px solid var(--red-hot); }

          .corner--tr { top: 12px;  right: 14px;
            border-top:    1.5px solid var(--red-hot);
            border-right:  1.5px solid var(--red-hot); }

          .corner--bl { bottom: 14px; left: 14px;
            border-bottom: 1.5px solid var(--red-hot);
            border-left:   1.5px solid var(--red-hot); }

          .corner--br { bottom: 14px; right: 14px;
            border-bottom: 1.5px solid var(--red-hot);
            border-right:  1.5px solid var(--red-hot); }

          /* ══════════════════════════════════════════
             LAYOUT STRUCTURE
          ══════════════════════════════════════════ */
          .layout-main {
            position: relative;
            z-index: 1;
            /* Ensures content never bleeds under corner marks */
            padding-left:  calc(var(--content-pad-x) + 14px);
            padding-right: calc(var(--content-pad-x) + 14px);
          }

          .layout-content {
            padding: var(--content-pad-y) 0 var(--xl, 72px);
            max-width: var(--content-max);
            /* True optical center — slightly left-weighted grids look off */
            margin: 0 auto;
            animation: content-enter 0.55s cubic-bezier(0.22, 1, 0.36, 1) both;
          }

          @keyframes content-enter {
            from {
              opacity: 0;
              transform: translateY(16px);
              filter: blur(3px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
              filter: blur(0);
            }
          }

          /* ══════════════════════════════════════════
             GLOBAL TYPOGRAPHY
          ══════════════════════════════════════════ */
          h1, h2, h3, h4, h5, h6 {
            font-family: var(--font-display);
            letter-spacing: 0.06em;
            color: var(--white-bright);
            /* Prevent headings from collapsing margin with container */
            margin-block-start: 0;
          }

          /* ══════════════════════════════════════════
             GLOBAL INTERACTIVE STATES
          ══════════════════════════════════════════ */
          ::selection {
            background: rgba(255,45,45,0.35);
            color: #ffffff;
          }

          :focus-visible {
            outline: 1.5px solid rgba(255,45,45,0.7);
            outline-offset: 3px;
          }

          /* Scrollbar */
          ::-webkit-scrollbar       { width: 4px; height: 4px; }
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