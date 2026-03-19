"use client"

import { ReactNode } from "react"

type StepStatus = "pending" | "running" | "completed" | "failed"

interface ExecutionStep {
  tool: string
  status: StepStatus
}

interface ExecutionPanelProps {
  goal?: string
  steps: ExecutionStep[]
}

const iconMap: Record<string, string> = {
  pending: "⏳",
  running: "⏳",
  completed: "✓",
  failed: "✗"
}

const colorMap: Record<string, string> = {
  pending: "bg-gray-200 text-gray-800",
  running: "bg-yellow-200 text-yellow-800",
  completed: "bg-green-200 text-green-800",
  failed: "bg-red-200 text-red-800"
}

export default function ExecutionPanel({ goal, steps }: ExecutionPanelProps) {
  return (
    <div className="bg-gray-800/80 backdrop-blur-sm p-5 rounded-xl border border-gray-700/50 mb-6 shadow-lg">
      <h2 className="text-xl font-semibold text-gray-100 mb-4 tracking-tight">
        {goal || "Execution Progress"}
      </h2>

      <div className="space-y-2.5">
        {steps.map((step, index) => {
          return (
            <div
              key={`${step.tool}-${index}`}
              className={`flex items-center justify-between p-2 rounded ${colorMap[step.status] || colorMap.pending}`}
            >
              <div className="flex items-center gap-3 min-w-0">
                <span className="font-mono text-xs opacity-70 min-w-[1.5rem]">
                  {index + 1}
                </span>
                <code className="font-mono text-sm truncate">
                  {step.tool}
                </code>
              </div>

              <span className={step.status === "running" ? "animate-pulse font-bold text-xl" : "font-bold text-xl"}>
                {iconMap[step.status] || iconMap.pending}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}