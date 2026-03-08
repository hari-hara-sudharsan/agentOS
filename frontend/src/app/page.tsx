"use client"

import { useAuth0 } from "@auth0/auth0-react"
import LoginButton from "../components/LoginButton"
import LogoutButton from "../components/LogoutButton"
import ChatBox from "../components/ChatBox"

export default function Home() {

  const { isAuthenticated, isLoading, user } = useAuth0()

  if (isLoading) {
    return <div>Loading...</div>
  }

  if (!isAuthenticated) {
    return (
      <div className="h-screen flex flex-col items-center justify-center bg-gray-900 text-white">
        <h1 className="text-3xl mb-6">AgentOS</h1>
        <LoginButton />
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col items-center bg-gray-900 text-white">

      <div className="flex justify-between w-full max-w-2xl mt-6">

        <h1 className="text-2xl font-bold">AgentOS</h1>

        <LogoutButton />

      </div>

      <p className="mt-2 text-sm">
        Logged in as {user?.name}
      </p>

      <ChatBox />

    </div>
  )
}