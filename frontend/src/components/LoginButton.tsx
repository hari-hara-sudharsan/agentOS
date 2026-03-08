"use client"

import { useAuth0 } from "@auth0/auth0-react"

export default function LoginButton() {

  const { loginWithRedirect } = useAuth0()

  return (
    <button
      onClick={() => loginWithRedirect()}
      className="bg-blue-500 px-4 py-2 rounded"
    >
      Login
    </button>
  )
}