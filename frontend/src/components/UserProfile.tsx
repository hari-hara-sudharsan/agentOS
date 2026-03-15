"use client"

import { useAuth0 } from "@auth0/auth0-react"

export default function UserProfile(){

  const { user,isAuthenticated } = useAuth0()

  if(!isAuthenticated) return null

  return(

    <div className="flex items-center gap-3">

      <img
        src={user?.picture}
        className="w-8 h-8 rounded-full"
      />

      <div className="text-sm">

        <div>{user?.name}</div>

        <div className="text-gray-500">
          {user?.email}
        </div>

      </div>

    </div>

  )

}
