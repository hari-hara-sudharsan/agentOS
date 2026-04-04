"use client"

import { useEffect, useState, useCallback } from "react"
import { useAuth0 } from "@auth0/auth0-react"

interface Approval {
  approval_id: string
  tool: string
  binding_message: string
  created_at: string
  expires_at: string
  approved: boolean
  approved_at?: string
}

const TOOL_ICONS: Record<string, string> = {
  send_gmail: "📧",
  create_calendar_event: "📅",
  upload_to_drive: "📁",
  send_slack_message: "💬",
  browser_login: "🔐",
  browser_download_file: "⬇️",
  default: "⚡"
}

function getTimeRemaining(expiresAt: string): { minutes: number; seconds: number; expired: boolean } {
  const now = new Date().getTime()
  const expires = new Date(expiresAt).getTime()
  const diff = expires - now
  
  if (diff <= 0) return { minutes: 0, seconds: 0, expired: true }
  
  const minutes = Math.floor(diff / 60000)
  const seconds = Math.floor((diff % 60000) / 1000)
  return { minutes, seconds, expired: false }
}

import { withAuthenticationRequired } from "@auth0/auth0-react"

function Approvals() {
  const [pendingApprovals, setPendingApprovals] = useState<Approval[]>([])
  const [historyApprovals, setHistoryApprovals] = useState<Approval[]>([])
  const [loading, setLoading] = useState(true)
  const [approving, setApproving] = useState<string | null>(null)
  const [mounted, setMounted] = useState(false)
  const [, forceUpdate] = useState(0)
  const { getAccessTokenSilently } = useAuth0()

  const loadApprovals = useCallback(async () => {
    try {
      const token = await getAccessTokenSilently()
      
      // Fetch pending approvals
      const pendingRes = await fetch("http://localhost:8000/api/approvals", {
        headers: { Authorization: `Bearer ${token}` }
      })
      const pendingData = await pendingRes.json()
      setPendingApprovals(Array.isArray(pendingData) ? pendingData : [])
      
      // Fetch approval history
      const historyRes = await fetch("http://localhost:8000/api/approvals/history", {
        headers: { Authorization: `Bearer ${token}` }
      })
      const historyData = await historyRes.json()
      // Filter to only show approved ones in history
      setHistoryApprovals(Array.isArray(historyData) ? historyData.filter((a: Approval) => a.approved) : [])
    } catch (e: any) {
      console.error("Failed to load approvals", e)
    } finally {
      setLoading(false)
    }
  }, [getAccessTokenSilently])

  useEffect(() => {
    setMounted(true)
    loadApprovals()
    const interval = setInterval(loadApprovals, 5000)
    return () => clearInterval(interval)
  }, [loadApprovals])
  
  // Update countdown every second
  useEffect(() => {
    const timer = setInterval(() => forceUpdate(n => n + 1), 1000)
    return () => clearInterval(timer)
  }, [])

  async function approve(id: string) {
    setApproving(id)
    try {
      const token = await getAccessTokenSilently()
      await fetch(`http://localhost:8000/api/approvals/approve/${id}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
      })
      await loadApprovals()
    } catch (e) {
      console.error("Failed to approve", e)
    } finally {
      setApproving(null)
    }
  }

  function formatTimeAgo(dateStr: string): string {
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    
    if (diffMins < 1) return "just now"
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    return date.toLocaleDateString()
  }

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Syne:wght@600;700;800&display=swap');

        @keyframes fadeSlideIn {
          from { opacity: 0; transform: translateY(10px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse-dot {
          0%, 100% { opacity: 1; transform: scale(1); }
          50%      { opacity: 0.5; transform: scale(0.9); }
        }
        @keyframes pulse-glow {
          0%, 100% { box-shadow: 0 0 20px rgba(249, 115, 22, 0.2); }
          50%      { box-shadow: 0 0 30px rgba(249, 115, 22, 0.4); }
        }
        
        .approval-card {
          transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .approval-card:hover {
          transform: translateY(-2px);
        }
        
        .approve-btn {
          transition: all 0.2s ease;
        }
        .approve-btn:hover:not(:disabled) {
          transform: scale(1.02);
          box-shadow: 0 4px 20px rgba(74, 222, 128, 0.3);
        }
        .approve-btn:active:not(:disabled) {
          transform: scale(0.98);
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
          position: "absolute", top: -120, left: "20%",
          width: 600, height: 600,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(249,115,22,0.07) 0%, transparent 70%)",
          pointerEvents: "none",
        }} />
        <div style={{
          position: "absolute", bottom: -80, right: "20%",
          width: 400, height: 400,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(74,222,128,0.05) 0%, transparent 70%)",
          pointerEvents: "none",
        }} />

        <div style={{ maxWidth: 900, margin: "0 auto", position: "relative" }}>
          
          {/* Header */}
          <div style={{
            animation: mounted ? "fadeSlideIn 0.5s ease both" : "none",
            marginBottom: 32,
          }}>
            <div style={{
              display: "inline-flex", alignItems: "center", gap: 8,
              background: "rgba(249,115,22,0.12)", border: "1px solid rgba(249,115,22,0.25)",
              borderRadius: 20, padding: "4px 12px", marginBottom: 12,
            }}>
              <span style={{
                width: 6, height: 6, borderRadius: "50%",
                background: "#f97316",
                animation: pendingApprovals.length > 0 ? "pulse-dot 1.5s ease-in-out infinite" : "none",
                display: "inline-block",
              }} />
              <span style={{ fontSize: 11, color: "#f97316", letterSpacing: "0.1em", fontFamily: "'IBM Plex Mono', monospace" }}>
                HUMAN-IN-THE-LOOP
              </span>
            </div>
            
            <h2 style={{
              fontSize: 28, fontWeight: 800, color: "#f1f5f9",
              letterSpacing: "-0.02em", margin: 0, lineHeight: 1,
            }}>
              Step-Up Approvals
            </h2>
            <p style={{
              marginTop: 6, fontSize: 13, color: "rgba(148,163,184,0.7)",
              fontFamily: "'IBM Plex Mono', monospace", fontWeight: 400,
            }}>
              {loading ? "Loading..." : 
                pendingApprovals.length > 0 
                  ? `${pendingApprovals.length} action${pendingApprovals.length > 1 ? "s" : ""} awaiting your approval`
                  : "No pending approvals"}
            </p>
          </div>

          {/* Pending Approvals Section */}
          {loading ? (
            <div style={{
              padding: "60px 20px",
              textAlign: "center",
              color: "rgba(148,163,184,0.5)",
              fontFamily: "'IBM Plex Mono', monospace",
            }}>
              <div style={{
                width: 40, height: 40, margin: "0 auto 16px",
                border: "3px solid rgba(249,115,22,0.2)",
                borderTopColor: "#f97316",
                borderRadius: "50%",
                animation: "spin 1s linear infinite",
              }} />
              Loading approvals...
            </div>
          ) : pendingApprovals.length === 0 ? (
            <div style={{
              background: "rgba(15,22,36,0.9)",
              border: "1px solid rgba(255,255,255,0.07)",
              borderRadius: 18,
              padding: "60px 20px",
              textAlign: "center",
              animation: mounted ? "fadeSlideIn 0.5s 0.1s ease both" : "none",
            }}>
              <div style={{ fontSize: 48, marginBottom: 16 }}>✓</div>
              <div style={{
                fontSize: 16, fontWeight: 600, color: "#4ade80",
                marginBottom: 8,
              }}>
                All Clear
              </div>
              <div style={{
                fontSize: 13, color: "rgba(148,163,184,0.5)",
                fontFamily: "'IBM Plex Mono', monospace",
              }}>
                No high-stakes actions pending approval. Your agent is operating within safe boundaries.
              </div>
            </div>
          ) : (
            <div style={{
              display: "flex", flexDirection: "column", gap: 16,
              animation: mounted ? "fadeSlideIn 0.5s 0.1s ease both" : "none",
            }}>
              {pendingApprovals.map((a, i) => {
                const time = getTimeRemaining(a.expires_at)
                const icon = TOOL_ICONS[a.tool] || TOOL_ICONS.default
                const isApproving = approving === a.approval_id
                
                return (
                  <div
                    key={a.approval_id}
                    className="approval-card"
                    style={{
                      background: "rgba(15,22,36,0.9)",
                      border: "1px solid rgba(249,115,22,0.2)",
                      borderRadius: 16,
                      padding: "24px",
                      animation: time.expired ? "none" : "pulse-glow 3s ease-in-out infinite",
                    }}
                  >
                    {/* Header row */}
                    <div style={{
                      display: "flex", justifyContent: "space-between", alignItems: "flex-start",
                      marginBottom: 16,
                    }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                        <div style={{
                          width: 48, height: 48, borderRadius: 12,
                          background: "rgba(249,115,22,0.15)",
                          border: "1px solid rgba(249,115,22,0.3)",
                          display: "flex", alignItems: "center", justifyContent: "center",
                          fontSize: 24,
                        }}>
                          {icon}
                        </div>
                        <div>
                          <div style={{
                            fontSize: 16, fontWeight: 700, color: "#f1f5f9",
                            marginBottom: 4,
                          }}>
                            {a.tool.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())}
                          </div>
                          <div style={{
                            fontSize: 11, color: "rgba(148,163,184,0.5)",
                            fontFamily: "'IBM Plex Mono', monospace",
                          }}>
                            requested {formatTimeAgo(a.created_at)}
                          </div>
                        </div>
                      </div>
                      
                      {/* Countdown */}
                      <div style={{
                        background: time.expired ? "rgba(239,68,68,0.15)" : "rgba(249,115,22,0.15)",
                        border: `1px solid ${time.expired ? "rgba(239,68,68,0.3)" : "rgba(249,115,22,0.3)"}`,
                        borderRadius: 10,
                        padding: "8px 14px",
                        textAlign: "center",
                      }}>
                        <div style={{
                          fontSize: 10, color: time.expired ? "#ef4444" : "#f97316",
                          fontFamily: "'IBM Plex Mono', monospace",
                          letterSpacing: "0.1em",
                          marginBottom: 2,
                        }}>
                          {time.expired ? "EXPIRED" : "EXPIRES IN"}
                        </div>
                        <div style={{
                          fontSize: 18, fontWeight: 700,
                          color: time.expired ? "#ef4444" : (time.minutes < 5 ? "#facc15" : "#f97316"),
                          fontFamily: "'IBM Plex Mono', monospace",
                        }}>
                          {time.expired ? "—" : `${time.minutes}:${String(time.seconds).padStart(2, '0')}`}
                        </div>
                      </div>
                    </div>
                    
                    {/* Binding message */}
                    <div style={{
                      background: "rgba(0,0,0,0.3)",
                      borderRadius: 10,
                      padding: "16px",
                      marginBottom: 20,
                      borderLeft: "3px solid #f97316",
                    }}>
                      <div style={{
                        fontSize: 13, color: "rgba(226,232,240,0.9)",
                        fontFamily: "'IBM Plex Mono', monospace",
                        lineHeight: 1.6,
                      }}>
                        {a.binding_message}
                      </div>
                    </div>
                    
                    {/* Action buttons */}
                    <div style={{ display: "flex", gap: 12 }}>
                      <button
                        className="approve-btn"
                        onClick={() => approve(a.approval_id)}
                        disabled={isApproving || time.expired}
                        style={{
                          flex: 1,
                          padding: "14px 24px",
                          borderRadius: 10,
                          border: "none",
                          background: time.expired 
                            ? "rgba(148,163,184,0.2)" 
                            : "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)",
                          color: time.expired ? "rgba(148,163,184,0.5)" : "#fff",
                          fontSize: 14,
                          fontWeight: 700,
                          cursor: time.expired ? "not-allowed" : "pointer",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          gap: 8,
                        }}
                      >
                        {isApproving ? (
                          <>
                            <span style={{
                              width: 16, height: 16,
                              border: "2px solid rgba(255,255,255,0.3)",
                              borderTopColor: "#fff",
                              borderRadius: "50%",
                              animation: "spin 0.8s linear infinite",
                            }} />
                            Approving...
                          </>
                        ) : time.expired ? (
                          "Expired"
                        ) : (
                          <>✓ Approve Action</>
                        )}
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>
          )}

          {/* Approval History Section */}
          {historyApprovals.length > 0 && (
            <div style={{
              marginTop: 48,
              animation: mounted ? "fadeSlideIn 0.5s 0.3s ease both" : "none",
            }}>
              <h3 style={{
                fontSize: 18, fontWeight: 700, color: "#f1f5f9",
                marginBottom: 16,
              }}>
                Recent Approvals
              </h3>
              
              <div style={{
                background: "rgba(15,22,36,0.9)",
                border: "1px solid rgba(255,255,255,0.07)",
                borderRadius: 14,
                overflow: "hidden",
              }}>
                {historyApprovals.slice(0, 10).map((a, i) => {
                  const icon = TOOL_ICONS[a.tool] || TOOL_ICONS.default
                  return (
                    <div
                      key={a.approval_id}
                      style={{
                        padding: "14px 20px",
                        display: "flex", alignItems: "center", gap: 14,
                        borderBottom: i < historyApprovals.length - 1 ? "1px solid rgba(255,255,255,0.04)" : "none",
                      }}
                    >
                      <span style={{ fontSize: 18 }}>{icon}</span>
                      <div style={{ flex: 1 }}>
                        <div style={{
                          fontSize: 13, fontWeight: 500, color: "#e2e8f0",
                        }}>
                          {a.tool.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())}
                        </div>
                        <div style={{
                          fontSize: 11, color: "rgba(148,163,184,0.5)",
                          fontFamily: "'IBM Plex Mono', monospace",
                        }}>
                          approved {a.approved_at ? formatTimeAgo(a.approved_at) : formatTimeAgo(a.created_at)}
                        </div>
                      </div>
                      <div style={{
                        display: "flex", alignItems: "center", gap: 6,
                        background: "rgba(74,222,128,0.1)",
                        border: "1px solid rgba(74,222,128,0.2)",
                        borderRadius: 20,
                        padding: "4px 10px",
                      }}>
                        <span style={{
                          width: 6, height: 6, borderRadius: "50%",
                          background: "#22c55e",
                        }} />
                        <span style={{
                          fontSize: 10, color: "#4ade80",
                          fontFamily: "'IBM Plex Mono', monospace",
                          letterSpacing: "0.05em",
                        }}>
                          APPROVED
                        </span>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
          
        </div>
      </div>
      
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </>
  )
}

export default withAuthenticationRequired(Approvals, {
  onRedirecting: () => (
    <div className="min-h-screen flex items-center justify-center bg-[#090d14]">
      <div className="animate-pulse flex flex-col items-center">
        <div className="h-12 w-12 rounded-full border-4 border-orange-500 border-t-transparent animate-spin mb-4"></div>
        <p className="text-slate-400 font-mono text-sm tracking-widest uppercase">Authenticating...</p>
      </div>
    </div>
  )
})
