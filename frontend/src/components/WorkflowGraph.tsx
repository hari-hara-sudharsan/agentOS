"use client"

import ReactFlow from "reactflow"
import "reactflow/dist/style.css"

export default function WorkflowGraph({ steps }: any) {
  const nodes = [
    {
      id: "planner",
      data: { label: "Planner" },
      position: { x: -150, y: 50 },
      style: { 
        background: "#3b82f6",
        color: "#ffffff",
        border: "2px solid #1e40af",
        borderRadius: "8px",
        padding: "10px 15px",
        fontSize: "13px",
        fontWeight: "600"
      }
    },
    ...steps.map((s: any, i: number) => ({
      id: String(i),
      data: { label: s.tool },
      style: {
        background:
          s.status === "completed"
            ? "#4ade80"
            : s.status === "running"
              ? "#fbbf24"
              : s.status === "failed"
                ? "#f87171"
                : "#94a3b8",
        color: "#ffffff",
        border: 
          s.status === "completed"
            ? "2px solid #16a34a"
            : s.status === "running"
              ? "2px solid #d97706"
              : s.status === "failed"
                ? "2px solid #dc2626"
                : "2px solid #64748b",
        borderRadius: "8px",
        padding: "10px 15px",
        fontSize: "13px",
        fontWeight: "600",
        boxShadow: s.status === "running" ? "0 0 10px rgba(251,191,36,0.5)" : "none"
      },
      position: { x: i * 200, y: 50 }
    }))
  ];

  const edges = [
    ...(steps.length > 0 ? [{ id: "e-planner", source: "planner", target: "0", animated: true, style: { stroke: "#3b82f6", strokeWidth: 2 } }] : []),
    ...steps.slice(1).map((_: any, i: number) => ({
      id: `e${i}`,
      source: String(i),
      target: String(i + 1),
      animated: false,
      style: { stroke: "#64748b", strokeWidth: 2 }
    }))
  ];

  return (
    <div style={{ height: 240, background: "rgba(15,19,29,0.3)", borderRadius: "8px", border: "1px solid rgba(239,68,68,0.1)" }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
      />
    </div>
  )
}
