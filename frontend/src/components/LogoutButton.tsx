"use client"

import { useAuth0 } from "@auth0/auth0-react"

export default function LogoutButton() {

  const { logout } = useAuth0()

  return (
    <button
      onClick={() =>
        logout({
          logoutParams: {
            returnTo: window.location.origin,
          },
        })
      }
      className="bg-transparent border border-[var(--red-dim)] hover:border-[var(--red-hot)] text-[var(--red-hot)] hover:text-white hover:bg-[var(--red-dim)] hover:shadow-[var(--shadow-red)] px-5 py-2 text-sm uppercase tracking-widest transition-all duration-300 rounded-sm"
    >
      Logout
    </button>
  )
}