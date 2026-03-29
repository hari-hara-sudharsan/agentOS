"use client"

import { useEffect, useState } from "react"
import { useAuth0 } from "@auth0/auth0-react"

interface Approval {
  approval_id: string
  tool: string
  binding_message: string
  created_at: string
  expires_at: string
  approved: boolean
}

import { withAuthenticationRequired } from "@auth0/auth0-react"

function Approvals() {
  const [approvals, setApprovals] = useState<Approval[]>([])
  const [loading, setLoading] = useState(true)
  const { getAccessTokenSilently } = useAuth0()

  async function loadApprovals() {
    try {
      const token = await getAccessTokenSilently()
      const res = await fetch("http://localhost:8000/api/approvals", {
        headers: { Authorization: `Bearer ${token}` }
      })
      const data = await res.json()
      setApprovals(Array.isArray(data) ? data : [])
    } catch (e: any) {
      console.error("Failed to load approvals", e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadApprovals()
    const interval = setInterval(loadApprovals, 7000)
    return () => clearInterval(interval)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function approve(id: string) {
    try {
      const token = await getAccessTokenSilently()
      await fetch(`http://localhost:8000/api/approvals/approve/${id}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      loadApprovals()
    } catch (e) {
      console.error("Failed to approve", e)
    }
  }

  return (
    <div className="min-h-screen py-16 px-4 sm:px-8 lg:px-16 max-w-6xl mx-auto">
      <h1 className="text-4xl font-bold mb-6">Pending Step-Up Approvals</h1>

      {loading ? (
        <p>Loading…</p>
      ) : approvals.length === 0 ? (
        <p>No pending approvals at this time.</p>
      ) : (
        <div className="space-y-4">
          {approvals.map((a) => (
            <div key={a.approval_id} className="px-5 py-4 bg-slate-800 border border-slate-700 rounded-lg">
              <h2 className="text-lg font-semibold">{a.tool}</h2>
              <p className="text-sm mt-2">{a.binding_message}</p>
              <p className="text-xs mt-1 text-slate-400">Expires: {new Date(a.expires_at).toLocaleString()}</p>
              <button
                className="mt-3 px-3 py-2 bg-emerald-600 hover:bg-emerald-500 rounded-md text-white"
                onClick={() => approve(a.approval_id)}
              >
                Approve
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default withAuthenticationRequired(Approvals, {
  onRedirecting: () => (
    <div className="min-h-screen flex items-center justify-center bg-[#090d14]">
      <div className="animate-pulse flex flex-col items-center">
        <div className="h-12 w-12 rounded-full border-4 border-indigo-500 border-t-transparent animate-spin mb-4"></div>
        <p className="text-slate-400 font-mono text-sm tracking-widest uppercase">Authenticating...</p>
      </div>
    </div>
  )
})
