"use client"

import { useState, useEffect, useCallback } from "react"
import { useAuth0 } from "@auth0/auth0-react"
import MessageInput from "./MessageInput"
import ExecutionPanel from "./ExecutionPanel"
import WorkflowGraph from "./WorkflowGraph"
import { API_BASE_URL } from "../lib/api"

// Session storage keys for state persistence
const STORAGE_KEYS = {
  steps: "agentos_steps",
  goal: "agentos_goal",
  tick: "agentos_tick"
}

export default function ChatBox() {
  // Initialize state from sessionStorage if available
  const [steps, setSteps] = useState<any[]>(() => {
    if (typeof window !== "undefined") {
      const saved = sessionStorage.getItem(STORAGE_KEYS.steps)
      return saved ? JSON.parse(saved) : []
    }
    return []
  })
  const [goal, setGoal] = useState(() => {
    if (typeof window !== "undefined") {
      return sessionStorage.getItem(STORAGE_KEYS.goal) || ""
    }
    return ""
  })
  const [tick, setTick] = useState(() => {
    if (typeof window !== "undefined") {
      const saved = sessionStorage.getItem(STORAGE_KEYS.tick)
      return saved ? parseInt(saved, 10) : 0
    }
    return 0
  })
  const { getAccessTokenSilently } = useAuth0()

  // Persist state to sessionStorage whenever it changes
  useEffect(() => {
    sessionStorage.setItem(STORAGE_KEYS.steps, JSON.stringify(steps))
  }, [steps])

  useEffect(() => {
    sessionStorage.setItem(STORAGE_KEYS.goal, goal)
  }, [goal])

  useEffect(() => {
    sessionStorage.setItem(STORAGE_KEYS.tick, tick.toString())
  }, [tick])

  // Check for pending approvals that have been approved
  const checkAndResumeApprovals = useCallback(async () => {
    const pendingSteps = steps.filter(s => s.status === "awaiting_consent" && s.approval_id)
    
    if (pendingSteps.length === 0) return

    try {
      const token = await getAccessTokenSilently()
      
      for (const step of pendingSteps) {
        // Check if this approval was granted
        const res = await fetch(`${API_BASE_URL}/api/approvals/status/${step.approval_id}`, {
          headers: { "Authorization": `Bearer ${token}` }
        })
        
        if (res.ok) {
          const data = await res.json()
          if (data.approved) {
            // Auto-resume this task!
            handleResume(step.tool, step.task)
          }
        }
      }
    } catch (e) {
      console.log("Error checking approvals:", e)
    }
  }, [steps, getAccessTokenSilently])

  // Check for approved tasks when component mounts or steps change
  useEffect(() => {
    checkAndResumeApprovals()
  }, [])  // Only on mount - we'll also trigger this after navigation

  // Poll for approval status every 5 seconds for pending items
  useEffect(() => {
    const hasPending = steps.some(s => s.status === "awaiting_consent")
    if (!hasPending) return

    const interval = setInterval(checkAndResumeApprovals, 5000)
    return () => clearInterval(interval)
  }, [steps, checkAndResumeApprovals])

  async function handleResume(tool: string, task: any) {
    updateStep(tool, "running");
    try {
      const token = await getAccessTokenSilently();
      const res = await fetch(`${API_BASE_URL}/api/agent/resume-task`, {
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

  function clearSession() {
    setSteps([])
    setGoal("")
    setTick(0)
    sessionStorage.removeItem(STORAGE_KEYS.steps)
    sessionStorage.removeItem(STORAGE_KEYS.goal)
    sessionStorage.removeItem(STORAGE_KEYS.tick)
  }

  const activeCount  = steps.filter(s => s.status === "running").length
  const doneCount    = steps.filter(s => s.status === "done" || s.status === "success").length
  const failCount    = steps.filter(s => s.status === "error" || s.status === "failed").length
  const pendingCount = steps.filter(s => !s.status || s.status === "pending").length

  return (
    <>
      <style>{`
        /* ══ SHELL ══ */
        .cb-shell {
          width: 100%;
          display: flex; flex-direction: column;
          font-family: var(--font-body);
          border: 1px solid var(--border-subtle);
          border-radius: var(--radius-xl);
          overflow: hidden;
          background: rgba(15,18,28,0.92);
          backdrop-filter: blur(24px);
          -webkit-backdrop-filter: blur(24px);
          box-shadow:
            0 0 0 1px rgba(255,255,255,0.04) inset,
            var(--shadow-xl),
            0 0 60px rgba(139,92,246,0.06);
          position: relative;
          animation: fadeUp 0.55s var(--ease-out) both;
        }
        /* Prismatic top edge */
        .cb-shell::before {
          content: '';
          position: absolute; top: 0; left: 0; right: 0; height: 2px;
          background: linear-gradient(90deg,
            transparent 0%, rgba(139,92,246,0.3) 15%,
            rgba(139,92,246,0.7) 35%, var(--cyan) 55%,
            rgba(6,182,212,0.3) 85%, transparent 100%);
          z-index: 2;
        }

        /* ══ TITLE BAR ══ */
        .cb-titlebar {
          display: flex; align-items: center; justify-content: space-between;
          padding: 14px 22px;
          background: rgba(10,13,20,0.7);
          border-bottom: 1px solid var(--border-subtle);
          position: relative; z-index: 1;
        }
        .cb-titlebar-left {
          display: flex; align-items: center; gap: 12px;
        }
        .cb-dots { display: flex; gap: 6px; align-items: center; }
        .cb-dot { width: 10px; height: 10px; border-radius: 50%; }
        .cb-dot--red    { background: var(--red); box-shadow: 0 0 6px rgba(239,68,68,0.6); }
        .cb-dot--yellow { background: var(--yellow); opacity: 0.55; }
        .cb-dot--green  { background: var(--green); opacity: 0.45; }
        .cb-titlebar-id {
          font-family: var(--font-mono);
          font-size: 10px; letter-spacing: 0.2em;
          color: var(--text-label);
          font-weight: 500;
        }
        .cb-titlebar-right {
          display: flex; align-items: center; gap: 14px;
        }
        .cb-live {
          display: flex; align-items: center; gap: 6px;
          padding: 4px 10px;
          border-radius: var(--radius-full);
          border: 1px solid rgba(16,185,129,0.25);
          background: rgba(16,185,129,0.08);
          font-family: var(--font-mono);
          font-size: 9px; letter-spacing: 0.2em; text-transform: uppercase;
          color: rgba(52,211,153,0.8);
        }
        .cb-live-dot {
          width: 5px; height: 5px; border-radius: 50%;
          background: var(--green);
          box-shadow: 0 0 6px var(--green);
          animation: pulse-dot 2.5s ease-in-out infinite;
        }
        .cb-seq {
          font-family: var(--font-mono);
          font-size: 9px; letter-spacing: 0.15em; color: var(--text-muted);
        }

        /* ══ STATUS BAR ══ */
        .cb-statusbar {
          display: flex; align-items: stretch;
          border-bottom: 1px solid var(--border-subtle);
          background: rgba(10,13,20,0.4);
        }
        .cb-stat {
          flex: 1;
          display: flex; flex-direction: column; align-items: center;
          justify-content: center;
          padding: 14px 12px;
          border-right: 1px solid var(--border-subtle);
          gap: 5px;
          transition: background 0.2s ease;
        }
        .cb-stat:last-child { border-right: none; }
        .cb-stat:hover { background: rgba(139,92,246,0.05); }
        .cb-stat-label {
          font-family: var(--font-mono);
          font-size: 9px; letter-spacing: 0.28em; text-transform: uppercase;
          color: var(--text-muted);
          font-weight: 500;
        }
        .cb-stat-val {
          font-family: var(--font-display);
          font-size: 22px; font-weight: 700; letter-spacing: 0.02em;
          color: var(--text-base); line-height: 1;
        }
        .cb-stat-val.red    { color: var(--red); }
        .cb-stat-val.green  { color: var(--green); }
        .cb-stat-val.yellow { color: var(--yellow); }
        .cb-stat-val.violet { color: var(--violet-light); }

        /* ══ SECTION ══ */
        .cb-section {
          border-bottom: 1px solid var(--border-subtle);
          position: relative;
        }
        .cb-section-header {
          display: flex; align-items: center; justify-content: space-between;
          padding: 12px 22px;
          border-bottom: 1px solid rgba(139,92,246,0.06);
          background: rgba(10,13,20,0.35);
        }
        .cb-section-title {
          display: flex; align-items: center; gap: 8px;
          font-family: var(--font-mono);
          font-size: 10px; letter-spacing: 0.25em; text-transform: uppercase;
          color: var(--text-label);
          font-weight: 600;
        }
        .cb-section-title::before {
          content: '';
          width: 4px; height: 4px; border-radius: 50%;
          background: var(--violet);
          box-shadow: 0 0 6px var(--violet);
        }
        .cb-section-badge {
          font-family: var(--font-mono);
          font-size: 9px; letter-spacing: 0.15em; text-transform: uppercase;
          padding: 3px 10px; border-radius: var(--radius-full);
          border: 1px solid var(--border-subtle);
          color: var(--text-muted);
          background: rgba(10,13,20,0.5);
        }
        .cb-section-badge.hot {
          border-color: rgba(139,92,246,0.35);
          color: var(--violet-light);
          background: var(--violet-subtle);
          font-weight: 600;
        }
        .cb-section-body { padding: 20px 22px; }

        /* ══ DIVIDER ══ */
        .cb-slash-divider {
          height: 1px;
          background: linear-gradient(90deg,
            transparent, rgba(139,92,246,0.35) 30%, var(--cyan) 50%,
            rgba(139,92,246,0.35) 70%, transparent);
        }

        /* ══ INPUT SECTION ══ */
        .cb-input-section {
          background: rgba(10,13,20,0.5);
          position: relative;
        }
        .cb-input-inner { padding: 18px 22px 22px; }

        /* ══ FOOTER ══ */
        .cb-footer {
          display: flex; align-items: center; justify-content: space-between;
          padding: 10px 22px;
          border-top: 1px solid var(--border-subtle);
          background: rgba(10,13,20,0.6);
        }
        .cb-footer-left {
          display: flex; align-items: center; gap: 8px;
          font-family: var(--font-mono);
          font-size: 9px; letter-spacing: 0.18em; text-transform: uppercase;
          color: var(--text-muted);
        }
        .cb-footer-left::before {
          content: '';
          width: 12px; height: 1px;
          background: linear-gradient(90deg, var(--violet), transparent);
        }
        .cb-footer-right {
          font-family: var(--font-mono);
          font-size: 9px; letter-spacing: 0.12em;
          color: var(--text-muted);
        }

        /* ══ CLEAR SESSION ══ */
        .cb-clear-btn {
          font-family: var(--font-mono);
          font-size: 9px; letter-spacing: 0.12em; text-transform: uppercase;
          padding: 4px 10px; border-radius: var(--radius-xs);
          border: 1px solid var(--border-subtle);
          color: var(--text-muted);
          background: transparent;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        .cb-clear-btn:hover {
          border-color: var(--violet);
          color: var(--violet-light);
          background: var(--violet-subtle);
        }

        /* ══ EMPTY GRAPH ══ */
        .cb-graph-empty {
          display: flex; flex-direction: column; align-items: center;
          justify-content: center; gap: 12px;
          padding: 48px 24px;
        }
        .cb-graph-empty-icon {
          font-family: var(--font-display);
          font-size: 32px; font-weight: 800; letter-spacing: 0.04em;
          background: linear-gradient(135deg, rgba(139,92,246,0.15), rgba(6,182,212,0.1));
          -webkit-background-clip: text; -webkit-text-fill-color: transparent;
          background-clip: text;
          line-height: 1;
        }
        .cb-graph-empty-text {
          font-family: var(--font-mono);
          font-size: 10px; letter-spacing: 0.28em; text-transform: uppercase;
          color: var(--text-muted);
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
            <span className="cb-titlebar-id">agent_runtime · session</span>
          </div>
          <div className="cb-titlebar-right">
            {steps.length > 0 && (
              <button className="cb-clear-btn" onClick={clearSession}>
                New Session
              </button>
            )}
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
            { label: "Total",   val: steps.length,  cls: steps.length > 0 ? "violet" : "" },
            { label: "Active",  val: activeCount,   cls: activeCount  > 0 ? "yellow" : "" },
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