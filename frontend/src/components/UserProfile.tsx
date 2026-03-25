"use client"

import { useAuth0 } from "@auth0/auth0-react"

export default function UserProfile(){

  const { user,isAuthenticated } = useAuth0()

  if(!isAuthenticated) return null

  return(

    <div className="flex items-center gap-4 border border-[var(--border-white)] bg-black/50 px-3 py-2 rounded-md">
      <img
        src={user?.picture}
        alt="Profile"
        className="w-9 h-9 rounded-full border border-[var(--border-red)]"
      />
      <div className="text-xs tracking-wider flex flex-col justify-center">
        <div className="text-[var(--white-bright)] font-bold">{user?.name}</div>
        <div className="text-[var(--red-dim)] font-mono opacity-80 mt-0.5">
          {user?.email}
        </div>
      </div>
    </div>

  )

}
