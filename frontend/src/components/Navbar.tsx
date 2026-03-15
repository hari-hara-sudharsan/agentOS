"use client"

import Link from "next/link"
import UserProfile from "./UserProfile"
import LogoutButton from "./LogoutButton"

export default function Navbar() {

  return (
    <div className="flex justify-between items-center p-4 bg-gray-900 text-white">

      <h1 className="font-bold text-lg">AgentOS</h1>

      <div className="flex gap-6 items-center">
        <Link href="/dashboard">Dashboard</Link>
        <Link href="/integrations">Integrations</Link>
        <Link href="/activity">Activity</Link>

        <UserProfile/>
        
        <LogoutButton/>
      </div>

    </div>
  )

}
