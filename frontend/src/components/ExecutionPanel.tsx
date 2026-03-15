"use client"

import { ReactNode } from "react"

type StepStatus = "pending" | "running" | "completed" | "failed"

interface ExecutionStep {
  tool: string
  status: StepStatus
  // Optional future fields you can add later:
  // input?: string
  // output?: string
  // error?: string
  // durationMs?: number
}

interface ExecutionPanelProps {
  goal?: string
  steps: ExecutionStep[]
}

const statusConfig: Record<
  StepStatus,
  {
    icon: string | ReactNode
    color: string
    animation?: string
  }
> = {
  pending: {
    icon: "⏳",
    color: "text-gray-400",
    animation: "animate-pulse",
  },
  running: {
    icon: <span className="inline-block animate-spin">⚙️</span>,
    color: "text-blue-400",
    animation: "animate-pulse",
  },
  completed: {
    icon: "✓",
    color: "text-green-500",
  },
  failed: {
    icon: "✗",
    color: "text-red-500",
  },
}

export default function ExecutionPanel({ goal, steps }: ExecutionPanelProps) {
  return (
    <div className="bg-gray-800/80 backdrop-blur-sm p-5 rounded-xl border border-gray-700/50 mb-6 shadow-lg">
      <h2 className="text-xl font-semibold text-gray-100 mb-4 tracking-tight">
        {goal || "Execution Progress"}
      </h2>

      <div className="space-y-2.5">
        {steps.length === 0 ? (
          <div className="text-gray-500 text-center py-6 italic text-sm">
            No steps executed yet...
          </div>
        ) : (
          steps.map((step, index) => {
            const config = statusConfig[step.status] ?? statusConfig.pending
            const isActive = step.status === "running" || step.status === "pending"

            return (
              <div
                key={`${step.tool}-${index}`}
                className={`
                  group flex items-center justify-between
                  bg-gray-750 px-4 py-3 rounded-lg border border-gray-700/60
                  transition-all duration-200
                  hover:bg-gray-700/70
                  ${isActive ? "ring-1 ring-blue-500/40 bg-blue-950/20" : ""}
                  ${step.status === "failed" ? "bg-red-950/30 border-red-800/50" : ""}
                `}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <span className="text-gray-500 font-mono text-xs opacity-70 min-w-[1.5rem]">
                    {index + 1}
                  </span>
                  <code className="text-blue-300 font-mono text-sm truncate">
                    {step.tool}
                  </code>
                </div>

                <span
                  className={`
                    flex items-center justify-center
                    w-8 h-8 rounded-full text-xl font-bold
                    transition-all duration-300
                    ${config.color}
                    ${config.animation || ""}
                    ${isActive ? "scale-110" : "scale-100"}
                    group-hover:scale-110
                  `}
                >
                  {config.icon}
                </span>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}