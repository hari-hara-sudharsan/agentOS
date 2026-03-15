"use client"

import { useState } from "react"
import MessageInput from "./MessageInput"
import ExecutionPanel from "./ExecutionPanel"
import WorkflowGraph from "./WorkflowGraph"

export default function ChatBox() {

    const [steps, setSteps] = useState<any[]>([])
    const [goal, setGoal] = useState("")

    function addStep(step: any) {
        setSteps(prev => [...prev, step])
    }

    function updateStep(tool: string, status: string) {

        setSteps(prev =>
            prev.map(s =>
                s.tool === tool ? { ...s, status } : s
            )
        )

    }

    return (

        <div className="w-full max-w-2xl mt-10">
            
            <WorkflowGraph steps={steps} />

            <ExecutionPanel goal={goal} steps={steps} />

            <MessageInput
                addStep={addStep}
                updateStep={updateStep}
                setGoal={setGoal}
                setSteps={setSteps}
            />

        </div>

    )

}