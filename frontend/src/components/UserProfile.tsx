"use client"

import { useAuth0 } from "@auth0/auth0-react"

export default function UserProfile(){

  const { user,isAuthenticated } = useAuth0()

  if(!isAuthenticated) return null

  return(

    <div className="flex items-center gap-4 border border-amber-700 bg-slate-800/70 px-4 py-2 rounded-lg hover:bg-slate-700 transition-colors">
      <img
        src={user?.picture}
        alt="Profile"
        className="w-9 h-9 rounded-full border border-amber-500"
      />
      <div className="text-xs tracking-wider flex flex-col justify-center">
        <div className="text-amber-100 font-bold">{user?.name}</div>
        <div className="text-amber-200 font-mono opacity-75 mt-0.5 text-xs">
          {user?.email}
        </div>
      </div>
    </div>

  )

}
