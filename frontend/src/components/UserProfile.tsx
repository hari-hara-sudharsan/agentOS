"use client"

import { useAuth0 } from "@auth0/auth0-react"

export default function UserProfile() {
  const { user, isAuthenticated } = useAuth0()

  if (!isAuthenticated) return null

  return (
    <div className="flex items-center gap-2.5 border border-amber-700 bg-slate-800/80 px-3 py-1.5 rounded-lg hover:bg-slate-700 transition-colors">

      {/* Avatar */}
      <img
        src={user?.picture}
        alt="Profile"
        className="w-7 h-7 rounded-full border border-amber-500 shrink-0"
      />

      {/* Identity */}
      <div className="flex flex-col gap-0.5 overflow-hidden">
        <span className="text-amber-100 text-xs font-semibold tracking-wider leading-none truncate max-w-[160px]">
          {user?.name}
        </span>
        <span className="text-amber-200/75 text-[10px] font-mono leading-none truncate max-w-[160px]">
          {user?.email}
        </span>
      </div>

    </div>
  )
}