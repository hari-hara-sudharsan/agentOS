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
      className="bg-transparent border border-amber-600 hover:border-amber-400 text-amber-200 hover:text-white hover:bg-red-700/30 px-5 py-2 text-sm uppercase tracking-widest font-medium transition-all duration-300 rounded-lg hover:shadow-lg"
    >
      Logout
    </button>
  )
}