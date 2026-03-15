"use client"

import ChatBox from "../../components/ChatBox"
import { useAuth0 } from "@auth0/auth0-react"

export default function Dashboard(){

  const { isLoading } = useAuth0()

  if(isLoading){
    return(
      <div className="flex items-center justify-center h-screen">
        Loading session...
      </div>
    )
  }

  return(

    <div>

      <h2 className="text-xl font-bold mb-4">
        AI Agent Dashboard
      </h2>

      <div className="bg-white p-6 rounded shadow max-w-3xl">
        <ChatBox/>
      </div>

    </div>

  )

}
