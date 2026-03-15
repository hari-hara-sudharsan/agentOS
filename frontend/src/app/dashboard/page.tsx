"use client"

import ChatBox from "../../components/ChatBox"

export default function Dashboard(){

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
