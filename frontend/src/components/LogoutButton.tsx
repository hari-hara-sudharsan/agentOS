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
      className="bg-red-500 px-4 py-2 rounded"
    >
      Logout
    </button>
  )
}