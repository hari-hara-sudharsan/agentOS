"use client"

import { useEffect, useState } from "react"
import { useAuth0 } from "@auth0/auth0-react"
import { API_BASE_URL } from "../../lib/api"

type ActivityRow = {
  id: string
  type: "tool_execution" | "approval"
  task_name: string
  status: string
  execution_time: number
  created_at: string | null
  tool_name?: string | null
  binding_message?: string
  approved_at?: string | null
  error?: string | null
}

type ActivitySummary = {
  total_executions: number
  successful: number
  failed: number
  pending_approvals: number
  approved_count: number
}

const STATUS_CONFIG: Record<string, { label: string; color: string; dot: string; bg: string }> = {
  success:   { label: "Success",   color: "#4ade80", dot: "#22c55e", bg: "rgba(74,222,128,0.08)"  },
  completed: { label: "Completed", color: "#4ade80", dot: "#22c55e", bg: "rgba(74,222,128,0.08)"  },
  running:   { label: "Running",   color: "#facc15", dot: "#eab308", bg: "rgba(250,204,21,0.08)"  },
  pending:   { label: "Pending",   color: "#f97316", dot: "#ea580c", bg: "rgba(249,115,22,0.08)" },
  approved:  { label: "Approved",  color: "#4ade80", dot: "#22c55e", bg: "rgba(74,222,128,0.08)"  },
  failed:    { label: "Failed",    color: "#f87171", dot: "#ef4444", bg: "rgba(248,113,113,0.08)" },
  error:     { label: "Error",     color: "#f87171", dot: "#ef4444", bg: "rgba(248,113,113,0.08)" },
}

const TYPE_CONFIG: Record<string, { icon: string; color: string }> = {
  tool_execution: { icon: "⚡", color: "#818cf8" },
  approval: { icon: "🔐", color: "#f97316" },
}

function getStatus(s: string) {
  return STATUS_CONFIG[s?.toLowerCase()] ?? STATUS_CONFIG["pending"]
}

function formatTimeAgo(dateStr: string | null): string {
  if (!dateStr) return "—"
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return "just now"
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return date.toLocaleDateString()
}

function SkeletonRow() {
  return (
    <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
      {[60, 40, 30, 20].map((w, i) => (
        <td key={i} style={{ padding: "16px 20px" }}>
          <div
            style={{
              height: 13,
              width: `${w}%`,
              borderRadius: 6,
              background: "linear-gradient(90deg, rgba(255,255,255,0.05) 25%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0.05) 75%)",
              backgroundSize: "200% 100%",
              animation: "shimmer 1.6s infinite",
            }}
          />
        </td>
      ))}
    </tr>
  )
}

import { withAuthenticationRequired } from "@auth0/auth0-react"

function Activity() {
  const [data, setData] = useState<ActivityRow[]>([])
  const [summary, setSummary] = useState<ActivitySummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [mounted, setMounted] = useState(false)
  const { getAccessTokenSilently } = useAuth0()

  useEffect(() => {
    setMounted(true)
    async function loadData() {
      try {
        const token = await getAccessTokenSilently()
        
        // Fetch both activity and summary in parallel
        const [activityRes, summaryRes] = await Promise.all([
          fetch(`${API_BASE_URL}/api/activity`, {
            headers: { Authorization: `Bearer ${token}` },
          }),
          fetch(`${API_BASE_URL}/api/activity/summary`, {
            headers: { Authorization: `Bearer ${token}` },
          })
        ])
        
        const jsonData = await activityRes.json()
        setData(Array.isArray(jsonData) ? jsonData : [])
        
        if (summaryRes.ok) {
          const summaryData = await summaryRes.json()
          setSummary(summaryData)
        }
      } catch (e: any) {
        console.error("Failed to fetch activity", e)
        setData([])
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [getAccessTokenSilently])

  const toolExecutions = data.filter(d => d.type === "tool_execution")
  const approvalItems = data.filter(d => d.type === "approval")
  const successCount = data.filter(d => ["success","completed","approved"].includes(d.status?.toLowerCase())).length
  const pendingCount = data.filter(d => d.status?.toLowerCase() === "pending").length
  const failedCount  = data.filter(d => ["failed","error"].includes(d.status?.toLowerCase())).length

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Syne:wght@600;700;800&display=swap');

        @keyframes shimmer {
          0%   { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }
        @keyframes fadeSlideIn {
          from { opacity: 0; transform: translateY(10px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse-dot {
          0%, 100% { opacity: 1;   transform: scale(1); }
          50%       { opacity: 0.4; transform: scale(0.85); }
        }
        @keyframes scanline {
          0%   { transform: translateY(-100%); }
          100% { transform: translateY(100vh); }
        }

        .activity-row {
          border-bottom: 1px solid rgba(255,255,255,0.04);
          transition: background 0.2s ease;
          cursor: default;
        }
        .activity-row:hover {
          background: rgba(255,255,255,0.03) !important;
        }
        .activity-row td {
          padding: 15px 20px;
          font-family: 'IBM Plex Mono', monospace;
          font-size: 13px;
          color: rgba(226,232,240,0.85);
          vertical-align: middle;
        }
        .stat-card {
          transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .stat-card:hover {
          transform: translateY(-2px);
        }
      `}</style>

      <div
        style={{
          minHeight: "100vh",
          background: "#090d14",
          padding: "40px 32px",
          fontFamily: "'Syne', sans-serif",
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* Ambient glow */}
        <div style={{
          position: "absolute", top: -120, left: "30%",
          width: 600, height: 600,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(99,102,241,0.07) 0%, transparent 70%)",
          pointerEvents: "none",
        }} />
        <div style={{
          position: "absolute", bottom: -80, right: "10%",
          width: 400, height: 400,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(20,184,166,0.05) 0%, transparent 70%)",
          pointerEvents: "none",
        }} />

        <div style={{ maxWidth: 1000, margin: "0 auto", position: "relative" }}>

          {/* ── Header ── */}
          <div style={{
            display: "flex", alignItems: "flex-start",
            justifyContent: "space-between", marginBottom: 32,
            animation: mounted ? "fadeSlideIn 0.5s ease both" : "none",
          }}>
            <div>
              <div style={{
                display: "inline-flex", alignItems: "center", gap: 8,
                background: "rgba(99,102,241,0.12)", border: "1px solid rgba(99,102,241,0.25)",
                borderRadius: 20, padding: "4px 12px", marginBottom: 12,
              }}>
                <span style={{
                  width: 6, height: 6, borderRadius: "50%",
                  background: "#818cf8",
                  animation: "pulse-dot 2s ease-in-out infinite",
                  display: "inline-block",
                }} />
                <span style={{ fontSize: 11, color: "#818cf8", letterSpacing: "0.1em", fontFamily: "'IBM Plex Mono', monospace" }}>
                  LIVE MONITOR
                </span>
              </div>
              <h2 style={{
                fontSize: 28, fontWeight: 800, color: "#f1f5f9",
                letterSpacing: "-0.02em", margin: 0, lineHeight: 1,
              }}>
                Agent Activity
              </h2>
              <p style={{
                marginTop: 6, fontSize: 13, color: "rgba(148,163,184,0.7)",
                fontFamily: "'IBM Plex Mono', monospace", fontWeight: 400,
              }}>
                {loading ? "Fetching activity logs…" : `${toolExecutions.length} tool executions · ${approvalItems.length} approvals`}
              </p>
            </div>

            {/* Refresh indicator */}
            <div style={{
              fontFamily: "'IBM Plex Mono', monospace", fontSize: 11,
              color: "rgba(148,163,184,0.4)", textAlign: "right", paddingTop: 4,
            }}>
              <div style={{ marginBottom: 2 }}>last sync</div>
              <div style={{ color: "rgba(148,163,184,0.7)" }}>
                {new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              </div>
            </div>
          </div>

          {/* ── Stat Cards ── */}
          {!loading && (
            <div style={{
              display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12,
              marginBottom: 28,
              animation: mounted ? "fadeSlideIn 0.5s 0.1s ease both" : "none",
              opacity: mounted ? 1 : 0,
            }}>
              {[
                { label: "Tool Executions", value: summary?.total_executions ?? toolExecutions.length, accent: "#818cf8", bg: "rgba(99,102,241,0.08)", border: "rgba(99,102,241,0.2)" },
                { label: "Successful",      value: summary?.successful ?? successCount, accent: "#4ade80", bg: "rgba(74,222,128,0.08)", border: "rgba(74,222,128,0.2)" },
                { label: "Pending Approvals", value: summary?.pending_approvals ?? pendingCount, accent: "#f97316", bg: "rgba(249,115,22,0.08)", border: "rgba(249,115,22,0.2)" },
                { label: "Failed",          value: summary?.failed ?? failedCount, accent: "#f87171", bg: "rgba(248,113,113,0.08)", border: "rgba(248,113,113,0.2)" },
              ].map((stat, i) => (
                <div key={i} className="stat-card" style={{
                  background: stat.bg,
                  border: `1px solid ${stat.border}`,
                  borderRadius: 14,
                  padding: "18px 20px",
                }}>
                  <div style={{
                    fontSize: 11, color: "rgba(148,163,184,0.6)", letterSpacing: "0.08em",
                    fontFamily: "'IBM Plex Mono', monospace", marginBottom: 8, textTransform: "uppercase",
                  }}>
                    {stat.label}
                  </div>
                  <div style={{
                    fontSize: 26, fontWeight: 800, color: stat.accent, lineHeight: 1,
                  }}>
                    {stat.value}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* ── Table Card ── */}
          <div style={{
            background: "rgba(15,22,36,0.9)",
            border: "1px solid rgba(255,255,255,0.07)",
            borderRadius: 18,
            overflow: "hidden",
            boxShadow: "0 24px 64px rgba(0,0,0,0.5), 0 1px 0 rgba(255,255,255,0.05) inset",
            animation: mounted ? "fadeSlideIn 0.5s 0.2s ease both" : "none",
            opacity: mounted ? 1 : 0,
          }}>

            {/* Table header bar */}
            <div style={{
              padding: "14px 20px",
              background: "rgba(255,255,255,0.02)",
              borderBottom: "1px solid rgba(255,255,255,0.06)",
              display: "flex", alignItems: "center", gap: 8,
            }}>
              {["#ef4444","#facc15","#4ade80"].map((c, i) => (
                <div key={i} style={{ width: 10, height: 10, borderRadius: "50%", background: c, opacity: 0.7 }} />
              ))}
              <span style={{
                marginLeft: 8, fontSize: 11, color: "rgba(148,163,184,0.4)",
                fontFamily: "'IBM Plex Mono', monospace", letterSpacing: "0.06em",
              }}>
                unified_activity_log.json
              </span>
            </div>

            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
                  {["Type", "Task / Action", "Status", "Time"].map((h, i) => (
                    <th key={i} style={{
                      padding: "13px 20px",
                      textAlign: "left",
                      fontSize: 10,
                      fontWeight: 600,
                      letterSpacing: "0.12em",
                      textTransform: "uppercase",
                      color: "rgba(148,163,184,0.45)",
                      fontFamily: "'IBM Plex Mono', monospace",
                      background: "rgba(255,255,255,0.01)",
                    }}>
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>

              <tbody>
                {loading
                  ? Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} />)
                  : data.length === 0
                    ? (
                      <tr>
                        <td colSpan={4} style={{
                          padding: "48px 20px", textAlign: "center",
                          fontFamily: "'IBM Plex Mono', monospace", fontSize: 13,
                          color: "rgba(148,163,184,0.3)",
                        }}>
                          <div style={{ fontSize: 28, marginBottom: 12 }}>◌</div>
                          No activity recorded yet. Start chatting with your agent!
                        </td>
                      </tr>
                    )
                    : data.map((d, i) => {
                        const s = getStatus(d.status)
                        const t = TYPE_CONFIG[d.type] || TYPE_CONFIG.tool_execution
                        return (
                          <tr
                            key={d.id || i}
                            className="activity-row"
                            style={{
                              animation: mounted ? `fadeSlideIn 0.4s ${0.05 * i}s ease both` : "none",
                            }}
                          >
                            {/* Type */}
                            <td>
                              <div style={{
                                display: "inline-flex", alignItems: "center", gap: 8,
                                background: `${t.color}15`,
                                border: `1px solid ${t.color}30`,
                                borderRadius: 8,
                                padding: "6px 10px",
                              }}>
                                <span style={{ fontSize: 14 }}>{t.icon}</span>
                                <span style={{
                                  fontSize: 10,
                                  color: t.color,
                                  textTransform: "uppercase",
                                  letterSpacing: "0.08em",
                                  fontWeight: 500,
                                }}>
                                  {d.type === "tool_execution" ? "Tool" : "Approval"}
                                </span>
                              </div>
                            </td>
                            
                            {/* Task name */}
                            <td>
                              <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                                <span style={{ color: "#e2e8f0", fontWeight: 500 }}>
                                  {d.task_name}
                                </span>
                                {d.tool_name && (
                                  <span style={{
                                    fontSize: 11,
                                    color: "rgba(148,163,184,0.5)",
                                  }}>
                                    tool: {d.tool_name}
                                  </span>
                                )}
                                {d.error && (
                                  <span style={{
                                    fontSize: 11,
                                    color: "#f87171",
                                  }}>
                                    {d.error}
                                  </span>
                                )}
                              </div>
                            </td>

                            {/* Status badge */}
                            <td>
                              <span style={{
                                display: "inline-flex", alignItems: "center", gap: 6,
                                background: s.bg,
                                border: `1px solid ${s.color}30`,
                                color: s.color,
                                padding: "4px 10px",
                                borderRadius: 20,
                                fontSize: 11,
                                fontWeight: 500,
                                letterSpacing: "0.04em",
                                textTransform: "capitalize",
                              }}>
                                <span style={{
                                  width: 5, height: 5, borderRadius: "50%",
                                  background: s.dot, flexShrink: 0,
                                  animation: d.status?.toLowerCase() === "running" || d.status?.toLowerCase() === "pending"
                                    ? "pulse-dot 1.2s ease-in-out infinite" : "none",
                                }} />
                                {s.label}
                              </span>
                            </td>

                            {/* Time */}
                            <td>
                              <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
                                <span style={{ color: "rgba(226,232,240,0.8)", fontSize: 12 }}>
                                  {formatTimeAgo(d.created_at)}
                                </span>
                                {d.execution_time > 0 && (
                                  <span style={{ color: "rgba(148,163,184,0.4)", fontSize: 10 }}>
                                    {d.execution_time}s exec
                                  </span>
                                )}
                              </div>
                            </td>
                          </tr>
                        )
                      })
                }
              </tbody>
            </table>

            {/* Footer */}
            {!loading && data.length > 0 && (
              <div style={{
                padding: "12px 20px",
                borderTop: "1px solid rgba(255,255,255,0.04)",
                display: "flex", justifyContent: "space-between", alignItems: "center",
              }}>
                <span style={{
                  fontFamily: "'IBM Plex Mono', monospace", fontSize: 11,
                  color: "rgba(148,163,184,0.3)",
                }}>
                  {data.length} rows · showing latest 50
                </span>
                {pendingCount > 0 && (
                  <span style={{
                    fontFamily: "'IBM Plex Mono', monospace", fontSize: 11,
                    color: "rgba(249,115,22,0.8)",
                  }}>
                    🔐 {pendingCount} pending approval{pendingCount > 1 ? "s" : ""} — go to Approvals page
                  </span>
                )}
                {failedCount > 0 && pendingCount === 0 && (
                  <span style={{
                    fontFamily: "'IBM Plex Mono', monospace", fontSize: 11,
                    color: "rgba(248,113,113,0.6)",
                  }}>
                    ⚠ {failedCount} failure{failedCount > 1 ? "s" : ""} detected
                  </span>
                )}
              </div>
            )}
          </div>

        </div>
      </div>
    </>
  )
}

export default withAuthenticationRequired(Activity, {
  onRedirecting: () => (
    <div className="min-h-screen flex items-center justify-center bg-[#090d14]">
      <div className="animate-pulse flex flex-col items-center">
        <div className="h-12 w-12 rounded-full border-4 border-indigo-500 border-t-transparent animate-spin mb-4"></div>
        <p className="text-slate-400 font-mono text-sm tracking-widest uppercase">Authenticating...</p>
      </div>
    </div>
  )
})