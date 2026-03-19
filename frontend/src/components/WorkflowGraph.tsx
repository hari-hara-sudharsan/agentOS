"use client"

import ReactFlow from "reactflow"
import "reactflow/dist/style.css"

export default function WorkflowGraph({ steps }: any) {
  const nodes = [
    {
      id: "planner",
      data: { label: "Planner" },
      position: { x: -150, y: 50 },
      style: { background: "#60a5fa" }
    },
    ...steps.map((s: any, i: number) => ({
      id: String(i),
      data: { label: s.tool },
      style: {
        background:
          s.status === "completed"
            ? "#4ade80"
            : s.status === "running"
              ? "#facc15"
              : "#e5e7eb"
      },
      position: { x: i * 200, y: 50 }
    }))
  ];

  const edges = [
    ...(steps.length > 0 ? [{ id: "e-planner", source: "planner", target: "0" }] : []),
    ...steps.slice(1).map((_: any, i: number) => ({
      id: `e${i}`,
      source: String(i),
      target: String(i + 1)
    }))
  ];

  return (
    <div style={{ height: 200 }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
      />
    </div>
  )
}
