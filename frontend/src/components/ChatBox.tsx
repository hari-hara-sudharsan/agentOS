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
        @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@300;400;500&display=swap');

        :root {
          --void:      #0a0c14;
          --deep:      #10141e;
          --surface:   #1a1f2e;
          --raised:    #252d3d;
          --primary:   #8b5cf6;
          --primary-light: #a78bfa;
          --accent:    #06b6d4;
          --accent-light: #22d3ee;
          --off-white: rgba(240,245,250,0.95);
          --muted:     rgba(203,213,225,0.68);
          --dim:       rgba(148,163,184,0.5);
          --green:     #4ade80;
          --yellow:    #fbbf24;
          --red:       #f87171;
          --border:    rgba(139,92,246,0.2);
          --border-hot:rgba(6,182,212,0.5);
        }

        /* ══ SHELL ══ */
        .cb-shell {
          width: 100%;
          max-width: 920px;
          display: flex;
          flex-direction: column;
          gap: 0;
          font-family: 'DM Mono', monospace;
          border: 1px solid var(--border);
          border-radius: 14px;
          overflow: hidden;
          background: rgba(16,20,30,0.95);
          backdrop-filter: blur(24px);
          -webkit-backdrop-filter: blur(24px);
          box-shadow:
            0 0 0 1px rgba(255,255,255,0.05) inset,
            0 32px 80px rgba(0,0,0,0.6),
            0 0 100px rgba(139,92,246,0.1);
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
          position: absolute; top: 0; left: 0; right: 0; height: 2px;
          background: linear-gradient(90deg,
            transparent 0%,
            rgba(139,92,246,0.2) 10%,
            rgba(139,92,246,0.7) 30%,
            rgba(6,182,212,0.9) 50%,
            rgba(139,92,246,0.7) 70%,
            rgba(139,92,246,0.2) 90%,
            transparent 100%
          );
          box-shadow: 0 0 24px rgba(139,92,246,0.4);
          z-index: 2;
        }

        /* ══ TITLE BAR ══ */
        .cb-titlebar {
          display: flex; align-items: center; justify-content: space-between;
          padding: 18px 26px;
          background: rgba(10,12,20,0.85);
          border-bottom: 1px solid var(--border);
          position: relative; z-index: 1;
        }

        .cb-titlebar-left {
          display: flex; align-items: center; gap: 16px;
        }

        /* Traffic-light dots */
        .cb-dots {
          display: flex; gap: 6px; align-items: center;
        }
        .cb-dot {
          width: 10px; height: 10px; border-radius: 50%;
        }
        .cb-dot--red    { background: var(--red);  box-shadow: 0 0 6px rgba(248,113,113,0.7); }
        .cb-dot--yellow { background: var(--yellow); opacity: 0.6; }
        .cb-dot--green  { background: var(--green);  opacity: 0.5; }

        .cb-titlebar-id {
          font-size: 10px; letter-spacing: 0.3em; text-transform: uppercase;
          color: rgba(139,92,246,0.8);
          font-weight: 500;
        }

        .cb-titlebar-right {
          display: flex; align-items: center; gap: 16px;
        }

        /* Live pulse badge */
        .cb-live {
          display: flex; align-items: center; gap: 7px;
          padding: 5px 12px;
          border-radius: 100px;
          border: 1px solid rgba(6,182,212,0.25);
          background: rgba(6,182,212,0.08);
          font-size: 8px; letter-spacing: 0.25em; text-transform: uppercase;
          color: rgba(6,182,212,0.75);
        }
        .cb-live-dot {
          width: 6px; height: 6px; border-radius: 50%;
          background: var(--accent);
          box-shadow: 0 0 8px var(--accent), 0 0 16px rgba(6,182,212,0.5);
          animation: live-pulse 2s ease-in-out infinite;
        }
        @keyframes live-pulse {
          0%,100% { opacity:1; box-shadow: 0 0 8px var(--accent), 0 0 18px rgba(6,182,212,0.5); }
          50%      { opacity:0.6; box-shadow: 0 0 4px var(--accent); }
        }

        .cb-seq {
          font-size: 8px; letter-spacing: 0.18em; color: var(--dim);
        }

        /* ══ STATUS BAR ══ */
        .cb-statusbar {
          display: flex; align-items: stretch;
          border-bottom: 1px solid var(--border);
          background: rgba(10,12,20,0.55);
          gap: 0;
        }

        .cb-stat {
          flex: 1;
          display: flex; flex-direction: column; align-items: center;
          justify-content: center;
          padding: 16px 14px;
          border-right: 1px solid var(--border);
          gap: 6px;
          transition: background 0.25s ease;
        }
        .cb-stat:last-child { border-right: none; }
        .cb-stat:hover { background: rgba(139,92,246,0.06); }

        .cb-stat-label {
          font-size: 8px; letter-spacing: 0.32em; text-transform: uppercase;
          color: rgba(148,163,184,0.68);
          font-weight: 500;
        }
        .cb-stat-val {
          font-family: 'Bebas Neue', sans-serif;
          font-size: 26px; letter-spacing: 0.06em;
          color: rgba(240,245,250,0.94); line-height: 1;
          transition: color 0.2s ease;
          font-weight: bold;
        }
        .cb-stat-val.red    { color: #f87171; }
        .cb-stat-val.green  { color: #4ade80; }
        .cb-stat-val.yellow { color: #fbbf24; }

        /* ══ GRAPH SECTION ══ */
        .cb-section {
          border-bottom: 1px solid var(--border);
          position: relative;
        }

        .cb-section-header {
          display: flex; align-items: center; justify-content: space-between;
          padding: 14px 26px;
          border-bottom: 1px solid rgba(139,92,246,0.1);
          background: rgba(10,12,20,0.5);
        }
        .cb-section-title {
          display: flex; align-items: center; gap: 10px;
          font-size: 9px; letter-spacing: 0.32em; text-transform: uppercase;
          color: rgba(6,182,212,0.8);
          font-weight: 600;
        }
        .cb-section-title::before {
          content: '';
          width: 5px; height: 5px; border-radius: 50%;
          background: var(--primary);
        }
        .cb-section-badge {
          font-size: 8px; letter-spacing: 0.2em; text-transform: uppercase;
          padding: 4px 12px; border-radius: 100px;
          border: 1px solid var(--border);
          color: rgba(148,163,184,0.68);
          background: rgba(15,19,29,0.5);
        }
        .cb-section-badge.hot {
          border-color: rgba(139,92,246,0.35);
          color: rgba(139,92,246,0.85);
          background: rgba(139,92,246,0.1);
          font-weight: 600;
        }

        .cb-section-body {
          padding: 26px;
        }

        /* ══ DIVIDER SLASH ══ */
        .cb-slash-divider {
          height: 2px;
          background: linear-gradient(90deg,
            transparent 0%,
            rgba(139,92,246,0.3) 15%,
            rgba(139,92,246,0.7) 40%,
            rgba(6,182,212,0.8) 50%,
            rgba(139,92,246,0.7) 60%,
            rgba(139,92,246,0.3) 85%,
            transparent 100%
          );
          box-shadow: 0 0 16px rgba(139,92,246,0.3);
        }

        /* ══ INPUT SECTION ══ */
        .cb-input-section {
          background: rgba(10,12,20,0.65);
          position: relative;
        }

        .cb-input-section::before {
          content: '';
          position: absolute; top: 0; left: 3%; right: 3%; height: 1px;
          background: linear-gradient(90deg, transparent, rgba(6,182,212,0.2), transparent);
        }

        .cb-input-inner {
          padding: 22px 26px 26px;
        }

        /* ══ FOOTER ══ */
        .cb-footer {
          display: flex; align-items: center; justify-content: space-between;
          padding: 14px 26px;
          border-top: 1px solid rgba(139,92,246,0.12);
          background: rgba(10,12,20,0.75);
        }

        .cb-footer-left {
          display: flex; align-items: center; gap: 10px;
          font-size: 8px; letter-spacing: 0.22em; text-transform: uppercase;
          color: rgba(148,163,184,0.6);
          font-weight: 500;
        }
        .cb-footer-left::before {
          content: '';
          width: 16px; height: 2px;
          background: linear-gradient(90deg, rgba(139,92,246,0.6), transparent);
        }

        .cb-footer-right {
          font-size: 8px; letter-spacing: 0.18em;
          color: rgba(148,163,184,0.45);
        }

        /* ══ CLEAR SESSION BUTTON ══ */
        .cb-clear-btn {
          font-size: 8px; letter-spacing: 0.15em; text-transform: uppercase;
          padding: 4px 10px; border-radius: 4px;
          border: 1px solid var(--border);
          color: rgba(148,163,184,0.65);
          background: transparent;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        .cb-clear-btn:hover {
          border-color: var(--red);
          color: var(--red);
          background: rgba(239,68,68,0.1);
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