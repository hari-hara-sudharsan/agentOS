"use client"

import { useState } from "react"
import MessageInput from "./MessageInput"
import StepList from "./StepList"

export default function ChatBox() {

  const [steps, setSteps] = useState<any[]>([])
  const [goal, setGoal] = useState("")

  function addStep(step:any) {
    setSteps(prev => [...prev, step])
  }

  function updateStep(tool:string,status:string) {

    setSteps(prev =>
      prev.map(s =>
        s.tool === tool ? {...s,status} : s
      )
    )
  }

  return (
    <div className="w-full max-w-2xl mt-10">

      <div className="bg-gray-800 p-6 rounded-lg">

        <h2 className="text-lg mb-4">
          {goal}
        </h2>

        <StepList steps={steps} />

        <MessageInput
          addStep={addStep}
          updateStep={updateStep}
          setGoal={setGoal}
        />

      </div>

    </div>
  )
}