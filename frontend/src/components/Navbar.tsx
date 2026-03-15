"use client"

import Link from "next/link"

export default function Navbar() {

  return (
    <div className="flex justify-between items-center p-4 bg-gray-900 text-white">

      <h1 className="font-bold text-lg">AgentOS</h1>

      <div className="flex gap-6">
        <Link href="/dashboard">Dashboard</Link>
        <Link href="/integrations">Integrations</Link>
        <Link href="/activity">Activity</Link>
      </div>

    </div>
  )

}
