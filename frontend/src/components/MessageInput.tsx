"use client"

import { useState } from "react"
import { useAuth0 } from "@auth0/auth0-react"

export default function MessageInput({ addStep, updateStep, setGoal, setSteps }: any) {

    const [message, setMessage] = useState("")
    const { getAccessTokenSilently } = useAuth0()

    async function sendMessage() {

        setGoal("")
        setSteps([])

        const token = await getAccessTokenSilently()

        const response = await fetch(
            "http://127.0.0.1:8000/api/agent/run-task-stream",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({ message })
            }
        )

        const reader = response.body?.getReader()
        const decoder = new TextDecoder()

        while (true) {

            const { done, value } = await reader!.read()

            if (done) break

            const chunk = decoder.decode(value)

            const events = chunk
                .split("\n")
                .filter(Boolean)
                .map(str => JSON.parse(str))

            events.forEach((event: any) => {

                if (event.event === "plan_created")
                    setGoal(`Planner created goal: ${event.goal}`)

                if (event.event === "step_started")
                    addStep({ tool: event.tool, status: "running" })

                if (event.event === "step_completed")
                    updateStep(event.tool, "completed", event.result)

                if (event.event === "step_failed")
                    updateStep(event.tool, "failed", event.error)

                if (event.event === "awaiting_consent")
                    updateStep(event.tool, "awaiting_consent", { task: event.task, error: "SECURITY HALT: This high-stakes action requires explicit human-in-the-loop consent. Please approve to continue." })

                if (event.event === "execution_finished")
                    setGoal((prev: string) => prev + " (Completed)")

            })

        }

    }

    return (

        <div className="flex gap-3 w-full">

            <input
                className="flex-1 px-4 py-3 bg-slate-700 text-slate-100 placeholder-slate-400 rounded-lg border border-slate-600 focus:border-amber-500 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-opacity-30 transition-all"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Ask AgentOS..."
            />

            <button
                onClick={sendMessage}
                className="px-6 py-3 bg-amber-600 hover:bg-amber-500 text-white font-medium rounded-lg transition-colors duration-200"
            >
                Send
            </button>

        </div>

    )

}