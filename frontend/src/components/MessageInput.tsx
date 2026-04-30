"use client"

import { useState, useRef } from "react"
import { useAuth0 } from "@auth0/auth0-react"
import { API_BASE_URL } from "../lib/api"

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
                `${API_BASE_URL}/api/agent/run-task-stream`,
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

                    if (event.event === "awaiting_consent" || event.event === "pending_approval") {
                        // Store task and approval_id at top level for resumption
                        setSteps((prev: any[]) => 
                            prev.map(s => s.tool === event.tool ? { 
                                ...s, 
                                status: "awaiting_consent",
                                task: event.task,
                                approval_id: event.approval_id,
                                result: {
                                    task: event.task,
                                    approval_id: event.approval_id,
                                    binding_message: event.binding_message,
                                    error: "SECURITY HALT: This high-stakes action requires explicit human-in-the-loop consent. Please approve to continue."
                                }
                            } : s)
                        )
                    }

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
        <>
            <style>{`
                .mi-wrap {
                    display: flex; flex-direction: column; gap: 12px; width: 100%;
                }
                .mi-error {
                    padding: 10px 14px;
                    background: rgba(239,68,68,0.1);
                    border: 1px solid rgba(239,68,68,0.25);
                    border-radius: var(--radius-md);
                    color: var(--red-light);
                    font-size: 13px;
                    font-family: var(--font-body);
                }
                .mi-error strong {
                    color: var(--red); font-weight: 600;
                }
                .mi-row {
                    display: flex; gap: 10px; width: 100%;
                }
                .mi-input {
                    flex: 1;
                    padding: 12px 16px;
                    background: var(--bg-raised);
                    color: var(--text-primary);
                    border: 1px solid var(--border-subtle);
                    border-radius: var(--radius-md);
                    font-family: var(--font-body);
                    font-size: 14px;
                    outline: none;
                    transition: all 0.2s ease;
                }
                .mi-input::placeholder {
                    color: var(--text-muted);
                }
                .mi-input:focus {
                    border-color: var(--violet);
                    box-shadow: 0 0 0 3px var(--violet-subtle), 0 0 20px rgba(139,92,246,0.1);
                }
                .mi-input:disabled {
                    opacity: 0.5; cursor: not-allowed;
                }
                .mi-send {
                    padding: 12px 22px;
                    border: none;
                    border-radius: var(--radius-md);
                    background: linear-gradient(135deg, var(--violet) 0%, var(--cyan-dim) 100%);
                    color: #fff;
                    font-family: var(--font-body);
                    font-size: 13px; font-weight: 600;
                    cursor: pointer;
                    transition: all 0.25s ease;
                    box-shadow: var(--shadow-violet);
                    white-space: nowrap;
                }
                .mi-send:hover:not(:disabled) {
                    transform: translateY(-1px);
                    box-shadow: 0 6px 28px rgba(139,92,246,0.35);
                }
                .mi-send:disabled {
                    opacity: 0.4; cursor: not-allowed;
                    transform: none;
                }
                .mi-cancel {
                    padding: 12px 22px;
                    border: none;
                    border-radius: var(--radius-md);
                    background: var(--red);
                    color: #fff;
                    font-family: var(--font-body);
                    font-size: 13px; font-weight: 600;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    display: flex; align-items: center; gap: 6px;
                    white-space: nowrap;
                }
                .mi-cancel:hover {
                    background: var(--red-light);
                }
                .mi-cancel svg { width: 14px; height: 14px; }
            `}</style>

            <div className="mi-wrap">
                {/* Error display */}
                {error && (
                    <div className="mi-error">
                        <strong>Error:</strong> {error}
                    </div>
                )}
                
                <div className="mi-row">
                    <input
                        className="mi-input"
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        placeholder={isLoading ? "Processing..." : "Ask AgentOS anything..."}
                        disabled={isLoading}
                        onKeyDown={(e) => e.key === "Enter" && !isLoading && sendMessage()}
                    />

                    {isLoading ? (
                        <button className="mi-cancel" onClick={cancelRequest}>
                            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                            Cancel
                        </button>
                    ) : (
                        <button
                            className="mi-send"
                            onClick={sendMessage}
                            disabled={!message.trim()}
                        >
                            Send
                        </button>
                    )}
                </div>
            </div>
        </>
    )
}