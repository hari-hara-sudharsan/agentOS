"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useAuth0 } from "@auth0/auth0-react"

const NAV_LINKS = [
  { href: "/dashboard",    label: "Dashboard",    icon: "◈" },
  { href: "/integrations", label: "Integrations", icon: "◎" },
  { href: "/activity",     label: "Activity",     icon: "◉" },
  { href: "/approvals",    label: "Approvals",    icon: "◇" },
]

export default function Navbar() {
  const pathname = usePathname()
  const { isAuthenticated, user, logout } = useAuth0()

  if (!isAuthenticated) return null

  return (
    <>
      <style>{`
        .nav-root {
          position: sticky; top: 2px; z-index: 50;
          display: flex; align-items: center; justify-content: space-between;
          padding: 0 clamp(24px, 4vw, 56px);
          height: 56px;
          background: rgba(10,13,20,0.85);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border-bottom: 1px solid var(--border-subtle);
          font-family: var(--font-body);
        }
        .nav-brand {
          display: flex; align-items: center; gap: 10px;
          text-decoration: none;
        }
        .nav-brand-icon {
          width: 28px; height: 28px; border-radius: 8px;
          background: linear-gradient(135deg, var(--violet) 0%, var(--cyan) 100%);
          display: flex; align-items: center; justify-content: center;
          font-size: 13px; color: white; font-weight: 700;
          box-shadow: 0 0 16px rgba(139,92,246,0.3);
        }
        .nav-brand-text {
          font-size: 16px; font-weight: 700; letter-spacing: 0.06em;
          background: linear-gradient(130deg, var(--text-primary) 0%, var(--violet-light) 60%, var(--cyan) 100%);
          -webkit-background-clip: text; -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        .nav-links {
          display: flex; align-items: center; gap: 2px;
        }
        .nav-link {
          display: flex; align-items: center; gap: 6px;
          padding: 8px 14px;
          border-radius: var(--radius-md);
          font-size: 12px; font-weight: 500; letter-spacing: 0.04em;
          color: var(--text-secondary);
          text-decoration: none;
          transition: all 0.2s ease;
          position: relative;
        }
        .nav-link:hover {
          color: var(--text-primary);
          background: rgba(139,92,246,0.08);
        }
        .nav-link.active {
          color: var(--violet-light);
          background: rgba(139,92,246,0.12);
        }
        .nav-link.active::after {
          content: '';
          position: absolute; bottom: -1px; left: 20%; right: 20%;
          height: 2px;
          background: linear-gradient(90deg, var(--violet), var(--cyan));
          border-radius: 2px;
        }
        .nav-link-icon {
          font-size: 11px; opacity: 0.7;
        }
        .nav-link.active .nav-link-icon { opacity: 1; }
        .nav-right {
          display: flex; align-items: center; gap: 14px;
        }
        .nav-status {
          display: flex; align-items: center; gap: 6px;
          padding: 4px 10px;
          border-radius: var(--radius-full);
          border: 1px solid rgba(16,185,129,0.25);
          background: rgba(16,185,129,0.08);
          font-size: 10px; letter-spacing: 0.08em;
          color: rgba(52,211,153,0.85);
          font-family: var(--font-mono);
        }
        .nav-status-dot {
          width: 5px; height: 5px; border-radius: 50%;
          background: var(--green);
          box-shadow: 0 0 6px var(--green);
          animation: pulse-dot 2.5s ease-in-out infinite;
        }
        .nav-divider {
          width: 1px; height: 20px;
          background: var(--border-subtle);
        }
        .nav-avatar {
          width: 30px; height: 30px; border-radius: 50%;
          background: linear-gradient(135deg, var(--violet) 0%, var(--cyan) 100%);
          border: 1.5px solid rgba(139,92,246,0.3);
          display: flex; align-items: center; justify-content: center;
          font-size: 11px; font-weight: 600; color: white;
          box-shadow: 0 0 12px rgba(139,92,246,0.2);
          transition: all 0.2s ease;
          cursor: default;
          overflow: hidden;
        }
        .nav-avatar img {
          width: 100%; height: 100%; object-fit: cover; border-radius: 50%;
        }
        .nav-logout {
          font-family: var(--font-mono);
          font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase;
          padding: 6px 12px;
          border-radius: var(--radius-sm);
          border: 1px solid var(--border-subtle);
          background: transparent;
          color: var(--text-secondary);
          cursor: pointer;
          transition: all 0.2s ease;
        }
        .nav-logout:hover {
          border-color: var(--red);
          color: var(--red-light);
          background: rgba(239,68,68,0.08);
        }
        @media (max-width: 768px) {
          .nav-links { display: none; }
          .nav-status { display: none; }
        }
      `}</style>

      <nav className="nav-root">
        <Link href="/" className="nav-brand">
          <div className="nav-brand-icon">A</div>
          <span className="nav-brand-text">AgentOS</span>
        </Link>

        <div className="nav-links">
          {NAV_LINKS.map(({ href, label, icon }) => (
            <Link
              key={href}
              href={href}
              className={`nav-link${pathname === href ? " active" : ""}`}
            >
              <span className="nav-link-icon">{icon}</span>
              {label}
            </Link>
          ))}
        </div>

        <div className="nav-right">
          <div className="nav-status">
            <span className="nav-status-dot" />
            Online
          </div>
          <div className="nav-divider" />
          <div className="nav-avatar">
            {user?.picture ? (
              <img src={user.picture} alt="" />
            ) : (
              user?.name?.[0]?.toUpperCase() || "U"
            )}
          </div>
          <button
            className="nav-logout"
            onClick={() => logout({ logoutParams: { returnTo: typeof window !== 'undefined' ? window.location.origin : '' } })}
          >
            Logout
          </button>
        </div>
      </nav>
    </>
  )
}