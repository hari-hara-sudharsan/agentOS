"use client"

import { useAuth0 } from "@auth0/auth0-react"

export default function LogoutButton() {

  const { logout } = useAuth0()

  return (
    <>
      <style>{`
        .logout-btn {
          font-family: var(--font-mono);
          font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase;
          padding: 7px 14px;
          border-radius: var(--radius-sm);
          border: 1px solid var(--border-subtle);
          background: transparent;
          color: var(--text-secondary);
          cursor: pointer;
          transition: all 0.25s ease;
        }
        .logout-btn:hover {
          border-color: var(--red);
          color: var(--red-light);
          background: rgba(239,68,68,0.08);
        }
      `}</style>
      <button
        className="logout-btn"
        onClick={() =>
          logout({
            logoutParams: {
              returnTo: window.location.origin,
            },
          })
        }
      >
        Logout
      </button>
    </>
  )
}