"use client"

import { useAuth0 } from "@auth0/auth0-react"

export default function LoginButton() {

  const { loginWithRedirect } = useAuth0()

  return (
    <button
      onClick={() => loginWithRedirect()}
      className="bg-amber-600 hover:bg-amber-500 text-white px-6 py-2 rounded-lg font-medium text-sm uppercase tracking-wider transition-colors duration-200"
    >
      Login
    </button>
  )
}