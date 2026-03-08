"use client"

import ChatBox from "../components/ChatBox"

export default function Home() {

  return (
    <div className="h-screen flex flex-col items-center bg-gray-900 text-white">

      <h1 className="text-3xl mt-6 font-bold">
        AgentOS
      </h1>

      <ChatBox />

    </div>
  )
}