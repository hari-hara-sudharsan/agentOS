"use client"

import { useState } from "react"
import { useAuth0 } from "@auth0/auth0-react"
import MessageInput from "./MessageInput"
import ExecutionPanel from "./ExecutionPanel"
import WorkflowGraph from "./WorkflowGraph"

export default function ChatBox() {
  const [steps, setSteps] = useState<any[]>([])
  const [goal, setGoal] = useState("")
  const [tick, setTick] = useState(0)
  const { getAccessTokenSilently } = useAuth0()

  async function handleResume(tool: string, task: any) {
    updateStep(tool, "running");
    try {
      const token = await getAccessTokenSilently();
      const res = await fetch("http://127.0.0.1:8000/api/agent/resume-task", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ task })
      });
      const data = await res.json();
      if (data.status === "success" || data.result) {
        updateStep(tool, "completed", data.result || "Action successfully performed.");
      } else {
        updateStep(tool, "failed", data.error || "Unknown error occurred.");
      }
    } catch (e: any) {
      updateStep(tool, "failed", e.message);
    }
  }

  function addStep(step: any) {
    setSteps(prev => [...prev, step])
    setTick(t => t + 1)
  }

  function updateStep(tool: string, status: string, result?: any) {
    setSteps(prev =>
      prev.map(s => s.tool === tool ? { ...s, status, result } : s)
    )
  }

  const activeCount  = steps.filter(s => s.status === "running").length
  const doneCount    = steps.filter(s => s.status === "done" || s.status === "success").length
  const failCount    = steps.filter(s => s.status === "error" || s.status === "failed").length
  const pendingCount = steps.filter(s => !s.status || s.status === "pending").length

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@300;400;500&display=swap');

        :root {
          --void:      #0f1419;
          --deep:      #1a1f2e;
          --surface:   #252d3d;
          --raised:    #2d3647;
          --red:       #ef4444;
          --red-dim:   #7f1d1d;
          --red-ember: rgba(239,68,68,0.12);
          --off-white: rgba(240,245,250,0.95);
          --muted:     rgba(203,213,225,0.65);
          --dim:       rgba(148,163,184,0.48);
          --green:     #22c55e;
          --yellow:    #eab308;
          --border:    rgba(239,68,68,0.18);
          --border-hot:rgba(239,68,68,0.45);
        }

        /* ══ SHELL ══ */
        .cb-shell {
          width: 100%;
          max-width: 900px;
          display: flex;
          flex-direction: column;
          gap: 0;
          font-family: 'DM Mono', monospace;
          border: 1px solid var(--border);
          border-radius: 12px;
          overflow: hidden;
          background: rgba(26,31,46,0.95);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          box-shadow:
            0 0 0 1px rgba(255,255,255,0.05) inset,
            0 32px 80px rgba(0,0,0,0.6),
            0 0 80px rgba(239,68,68,0.08);
          position: relative;
          animation: shell-in 0.65s cubic-bezier(0.22,1,0.36,1) both;
        }

        @keyframes shell-in {
          from { opacity:0; transform: translateY(24px) scale(0.98); filter: blur(6px); }
          to   { opacity:1; transform: translateY(0)    scale(1);    filter: blur(0);   }
        }

        /* Prismatic top edge */
        .cb-shell::before {
          content: '';
          position: absolute; top: 0; left: 0; right: 0; height: 1px;
          background: linear-gradient(90deg,
            transparent 0%,
            rgba(255,40,40,0.15) 10%,
            rgba(255,80,80,0.55) 35%,
            rgba(255,120,120,0.75) 50%,
            rgba(255,80,80,0.55) 65%,
            rgba(255,40,40,0.15) 90%,
            transparent 100%
          );
          box-shadow: 0 0 20px rgba(255,40,40,0.4);
          z-index: 2;
        }

        /* ══ TITLE BAR ══ */
        .cb-titlebar {
          display: flex; align-items: center; justify-content: space-between;
          padding: 16px 24px;
          background: rgba(15,19,29,0.8);
          border-bottom: 1px solid var(--border);
          position: relative; z-index: 1;
        }

        .cb-titlebar-left {
          display: flex; align-items: center; gap: 14px;
        }

        /* Traffic-light dots */
        .cb-dots {
          display: flex; gap: 6px; align-items: center;
        }
        .cb-dot {
          width: 10px; height: 10px; border-radius: 50%;
        }
        .cb-dot--red    { background: var(--red);  box-shadow: 0 0 6px rgba(255,40,40,0.8); }
        .cb-dot--yellow { background: var(--yellow); opacity: 0.55; }
        .cb-dot--green  { background: var(--green);  opacity: 0.45; }

        .cb-titlebar-id {
          font-size: 10px; letter-spacing: 0.3em; text-transform: uppercase;
          color: rgba(239,68,68,0.7);
          font-weight: 500;
        }

        .cb-titlebar-right {
          display: flex; align-items: center; gap: 16px;
        }

        /* Live pulse badge */
        .cb-live {
          display: flex; align-items: center; gap: 7px;
          padding: 4px 11px;
          border-radius: 100px;
          border: 1px solid rgba(255,40,40,0.22);
          background: rgba(255,40,40,0.06);
          font-size: 8px; letter-spacing: 0.25em; text-transform: uppercase;
          color: rgba(255,40,40,0.65);
        }
        .cb-live-dot {
          width: 5px; height: 5px; border-radius: 50%;
          background: var(--red);
          box-shadow: 0 0 6px var(--red), 0 0 12px rgba(255,40,40,0.5);
          animation: live-pulse 2s ease-in-out infinite;
        }
        @keyframes live-pulse {
          0%,100% { opacity:1; box-shadow: 0 0 6px var(--red), 0 0 14px rgba(255,40,40,0.5); }
          50%      { opacity:0.5; box-shadow: 0 0 3px var(--red); }
        }

        .cb-seq {
          font-size: 8px; letter-spacing: 0.18em; color: var(--dim);
        }

        /* ══ STATUS BAR ══ */
        .cb-statusbar {
          display: flex; align-items: stretch;
          border-bottom: 1px solid var(--border);
          background: rgba(15,19,29,0.5);
          gap: 0;
        }

        .cb-stat {
          flex: 1;
          display: flex; flex-direction: column; align-items: center;
          justify-content: center;
          padding: 14px 12px;
          border-right: 1px solid var(--border);
          gap: 6px;
          transition: background 0.2s ease;
        }
        .cb-stat:last-child { border-right: none; }
        .cb-stat:hover { background: rgba(239,68,68,0.05); }

        .cb-stat-label {
          font-size: 8px; letter-spacing: 0.32em; text-transform: uppercase;
          color: rgba(148,163,184,0.65);
          font-weight: 500;
        }
        .cb-stat-val {
          font-family: 'Bebas Neue', sans-serif;
          font-size: 24px; letter-spacing: 0.06em;
          color: rgba(240,245,250,0.92); line-height: 1;
          transition: color 0.2s ease;
          font-weight: bold;
        }
        .cb-stat-val.red    { color: #ef4444; }
        .cb-stat-val.green  { color: #22c55e; }
        .cb-stat-val.yellow { color: #eab308; }

        /* ══ GRAPH SECTION ══ */
        .cb-section {
          border-bottom: 1px solid var(--border);
          position: relative;
        }

        .cb-section-header {
          display: flex; align-items: center; justify-content: space-between;
          padding: 12px 24px;
          border-bottom: 1px solid rgba(239,68,68,0.08);
          background: rgba(15,19,29,0.4);
        }
        .cb-section-title {
          display: flex; align-items: center; gap: 10px;
          font-size: 9px; letter-spacing: 0.32em; text-transform: uppercase;
          color: rgba(239,68,68,0.65);
          font-weight: 600;
        }
        .cb-section-title::before {
          content: '';
          width: 4px; height: 4px; border-radius: 50%;
          background: var(--red);
        }
        .cb-section-badge {
          font-size: 8px; letter-spacing: 0.2em; text-transform: uppercase;
          padding: 4px 10px; border-radius: 100px;
          border: 1px solid var(--border);
          color: rgba(148,163,184,0.65);
          background: rgba(15,19,29,0.5);
        }
        .cb-section-badge.hot {
          border-color: rgba(239,68,68,0.3);
          color: rgba(239,68,68,0.75);
          background: rgba(239,68,68,0.08);
          font-weight: 600;
        }

        .cb-section-body {
          padding: 24px;
        }

        /* ══ DIVIDER SLASH ══ */
        .cb-slash-divider {
          height: 1px;
          background: linear-gradient(90deg,
            transparent 0%,
            var(--red-dim) 15%,
            rgba(255,40,40,0.55) 45%,
            rgba(255,80,80,0.7) 50%,
            rgba(255,40,40,0.55) 55%,
            var(--red-dim) 85%,
            transparent 100%
          );
          box-shadow: 0 0 12px rgba(255,40,40,0.25);
        }

        /* ══ INPUT SECTION ══ */
        .cb-input-section {
          background: rgba(15,19,29,0.6);
          position: relative;
        }

        .cb-input-section::before {
          content: '';
          position: absolute; top: 0; left: 3%; right: 3%; height: 1px;
          background: linear-gradient(90deg, transparent, rgba(239,68,68,0.15), transparent);
        }

        .cb-input-inner {
          padding: 20px 24px 24px;
        }

        /* ══ FOOTER ══ */
        .cb-footer {
          display: flex; align-items: center; justify-content: space-between;
          padding: 12px 24px;
          border-top: 1px solid rgba(239,68,68,0.1);
          background: rgba(15,19,29,0.7);
        }

        .cb-footer-left {
          display: flex; align-items: center; gap: 8px;
          font-size: 8px; letter-spacing: 0.22em; text-transform: uppercase;
          color: rgba(148,163,184,0.55);
          font-weight: 500;
        }
        .cb-footer-left::before {
          content: '';
          width: 12px; height: 1px;
          background: linear-gradient(90deg, rgba(239,68,68,0.5), transparent);
        }

        .cb-footer-right {
          font-size: 8px; letter-spacing: 0.18em;
          color: rgba(148,163,184,0.45);
        }

        /* ══ EMPTY GRAPH STATE ══ */
        .cb-graph-empty {
          display: flex; flex-direction: column; align-items: center;
          justify-content: center; gap: 12px;
          padding: 48px 24px;
        }
        .cb-graph-empty-icon {
          font-family: 'Bebas Neue', sans-serif;
          font-size: 36px; letter-spacing: 0.1em;
          color: rgba(239,68,68,0.18);
          line-height: 1;
        }
        .cb-graph-empty-text {
          font-size: 9px; letter-spacing: 0.3em; text-transform: uppercase;
          color: rgba(148,163,184,0.5);
          font-weight: 500;
        }
      `}</style>

      <div className="cb-shell">

        {/* ══ TITLE BAR ══ */}
        <div className="cb-titlebar">
          <div className="cb-titlebar-left">
            <div className="cb-dots">
              <div className="cb-dot cb-dot--red" />
              <div className="cb-dot cb-dot--yellow" />
              <div className="cb-dot cb-dot--green" />
            </div>
            <span className="cb-titlebar-id">// agent_runtime · session</span>
          </div>
          <div className="cb-titlebar-right">
            <div className="cb-live">
              <div className="cb-live-dot" />
              Live
            </div>
            <span className="cb-seq">SEQ_{String(tick).padStart(4, "0")}</span>
          </div>
        </div>

        {/* ══ STATUS BAR ══ */}
        <div className="cb-statusbar">
          {[
            { label: "Total",   val: steps.length,  cls: steps.length > 0 ? "red" : "" },
            { label: "Active",  val: activeCount,   cls: activeCount  > 0 ? "red"    : "" },
            { label: "Done",    val: doneCount,     cls: doneCount    > 0 ? "green"  : "" },
            { label: "Pending", val: pendingCount,  cls: pendingCount > 0 ? "yellow" : "" },
            { label: "Failed",  val: failCount,     cls: failCount    > 0 ? "red"    : "" },
          ].map(s => (
            <div key={s.label} className="cb-stat">
              <span className="cb-stat-label">{s.label}</span>
              <span className={`cb-stat-val${s.cls ? ` ${s.cls}` : ""}`}>
                {String(s.val).padStart(2, "0")}
              </span>
            </div>
          ))}
        </div>

        {/* ══ WORKFLOW GRAPH ══ */}
        <div className="cb-section">
          <div className="cb-section-header">
            <div className="cb-section-title">Workflow Graph</div>
            <span className={`cb-section-badge${steps.length > 0 ? " hot" : ""}`}>
              {steps.length > 0 ? `${steps.length} nodes` : "standby"}
            </span>
          </div>
          <div className="cb-section-body">
            {steps.length === 0 ? (
              <div className="cb-graph-empty">
                <div className="cb-graph-empty-icon">NO_OPS</div>
                <span className="cb-graph-empty-text">Awaiting mission directive</span>
              </div>
            ) : (
              <WorkflowGraph steps={steps} />
            )}
          </div>
        </div>

        <div className="cb-slash-divider" />

        {/* ══ EXECUTION PANEL ══ */}
        <div className="cb-section">
          <div className="cb-section-header">
            <div className="cb-section-title">Execution Log</div>
            <span className={`cb-section-badge${activeCount > 0 ? " hot" : ""}`}>
              {activeCount > 0 ? "running" : "idle"}
            </span>
          </div>
          <div className="cb-section-body">
            <ExecutionPanel goal={goal} steps={steps} onResume={handleResume} />
          </div>
        </div>

        <div className="cb-slash-divider" />

        {/* ══ MESSAGE INPUT ══ */}
        <div className="cb-input-section">
          <div className="cb-section-header">
            <div className="cb-section-title">Mission Input</div>
            <span className="cb-section-badge hot">armed</span>
          </div>
          <div className="cb-input-inner">
            <MessageInput
              addStep={addStep}
              updateStep={updateStep}
              setGoal={setGoal}
              setSteps={setSteps}
            />
          </div>
        </div>

        {/* ══ FOOTER ══ */}
        <div className="cb-footer">
          <span className="cb-footer-left">
            AGENT_OS · ChatBox Runtime
          </span>
          <span className="cb-footer-right">
            {goal ? `GOAL: ${goal.slice(0, 32)}${goal.length > 32 ? "…" : ""}` : "NO ACTIVE GOAL"}
          </span>
        </div>

      </div>
    </>
  )
}