"use client"

import { useState, useRef } from "react"
import { useAuth0 } from "@auth0/auth0-react"

export default function MessageInput({ addStep, updateStep, setGoal, setSteps }: any) {

    const [message, setMessage] = useState("")
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const abortControllerRef = useRef<AbortController | null>(null)
    const { getAccessTokenSilently } = useAuth0()

    async function sendMessage() {
        if (!message.trim() || isLoading) return

        // Cancel any previous request
        if (abortControllerRef.current) {
            abortControllerRef.current.abort()
        }
        
        // Create new abort controller with 2 minute timeout
        abortControllerRef.current = new AbortController()
        const timeoutId = setTimeout(() => {
            abortControllerRef.current?.abort()
        }, 120000) // 2 minute timeout

        setGoal("")
        setSteps([])
        setError(null)
        setIsLoading(true)

        try {
            const token = await getAccessTokenSilently()

            const response = await fetch(
                "http://localhost:8000/api/agent/run-task-stream",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`
                    },
                    body: JSON.stringify({ message }),
                    signal: abortControllerRef.current.signal
                }
            )

            if (!response.ok) {
                const errorText = await response.text().catch(() => "Unknown error")
                throw new Error(`Server error: ${response.status} - ${errorText}`)
            }

            const reader = response.body?.getReader()
            if (!reader) {
                throw new Error("No response body received")
            }
            
            const decoder = new TextDecoder()

            while (true) {
                const { done, value } = await reader.read()
                if (done) break

                const chunk = decoder.decode(value)

                const events = chunk
                    .split("\n")
                    .filter(Boolean)
                    .map(str => {
                        try {
                            return JSON.parse(str)
                        } catch {
                            return null
                        }
                    })
                    .filter(Boolean)

                events.forEach((event: any) => {
                    if (event.event === "plan_created")
                        setGoal(`Planner created goal: ${event.goal}`)

                    if (event.event === "step_started")
                        addStep({ tool: event.tool, status: "running" })

                    if (event.event === "step_completed")
                        updateStep(event.tool, "completed", event.result)

                    if (event.event === "step_failed")
                        updateStep(event.tool, "failed", event.error)

                    if (event.event === "awaiting_consent" || event.event === "pending_approval")
                        updateStep(event.tool, "awaiting_consent", {
                            task: event.task,
                            approval_id: event.approval_id,
                            binding_message: event.binding_message,
                            error: "SECURITY HALT: This high-stakes action requires explicit human-in-the-loop consent. Please approve to continue."
                        })

                    if (event.event === "execution_finished")
                        setGoal((prev: string) => prev + " (Completed)")
                })
            }
        } catch (err: any) {
            if (err.name === 'AbortError') {
                setError("Request timed out. Please try again.")
            } else if (err.message?.includes('Failed to fetch') || err.message?.includes('network')) {
                setError("Cannot connect to backend. Make sure the server is running on port 8000.")
            } else {
                setError(err.message || "An unexpected error occurred")
            }
            setGoal((prev: string) => prev ? prev + " (Failed)" : "Task Failed")
        } finally {
            clearTimeout(timeoutId)
            setIsLoading(false)
        }
    }

    function cancelRequest() {
        if (abortControllerRef.current) {
            abortControllerRef.current.abort()
            setIsLoading(false)
            setGoal((prev: string) => prev ? prev + " (Cancelled)" : "")
        }
    }

    return (
        <div className="flex flex-col gap-3 w-full">
            {/* Error display */}
            {error && (
                <div className="px-4 py-3 bg-red-900/50 border border-red-500/50 rounded-lg text-red-300 text-sm">
                    <span className="font-medium">Error:</span> {error}
                </div>
            )}
            
            <div className="flex gap-3 w-full">
                <input
                    className="flex-1 px-4 py-3 bg-slate-700 text-slate-100 placeholder-slate-400 rounded-lg border border-slate-600 focus:border-amber-500 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-opacity-30 transition-all disabled:opacity-50"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder={isLoading ? "Processing..." : "Ask AgentOS..."}
                    disabled={isLoading}
                    onKeyDown={(e) => e.key === "Enter" && !isLoading && sendMessage()}
                />

                {isLoading ? (
                    <button
                        onClick={cancelRequest}
                        className="px-6 py-3 bg-red-600 hover:bg-red-500 text-white font-medium rounded-lg transition-colors duration-200 flex items-center gap-2"
                    >
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                        Cancel
                    </button>
                ) : (
                    <button
                        onClick={sendMessage}
                        disabled={!message.trim()}
                        className="px-6 py-3 bg-amber-600 hover:bg-amber-500 text-white font-medium rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Send
                    </button>
                )}
            </div>
        </div>
    )

}