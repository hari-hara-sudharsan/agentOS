"use client"

type StepStatus = "pending" | "running" | "completed" | "failed" | "awaiting_consent"

interface ExecutionStep {
  tool: string
  status: StepStatus
  result?: any
}

interface ExecutionPanelProps {
  goal?: string
  steps: ExecutionStep[]
  onResume?: (tool: string, task: any) => void
}

/* ── Status config ── */
const STATUS: Record<string, {
  label: string
  color: string
  glow: string
  bg: string
  border: string
  dot: string
}> = {
  pending: {
    label: "STANDBY",
    color: "rgba(148,163,184,0.75)",
    glow:  "transparent",
    bg:    "rgba(15,19,29,0.7)",
    border:"rgba(148,163,184,0.15)",
    dot:   "rgba(148,163,184,0.5)",
  },
  running: {
    label: "EXECUTING",
    color: "#fbbf24",
    glow:  "rgba(251,191,36,0.3)",
    bg:    "rgba(251,191,36,0.08)",
    border:"rgba(251,191,36,0.25)",
    dot:   "#fbbf24",
  },
  completed: {
    label: "COMPLETE",
    color: "#4ade80",
    glow:  "rgba(74,222,128,0.25)",
    bg:    "rgba(74,222,128,0.08)",
    border:"rgba(74,222,128,0.25)",
    dot:   "#4ade80",
  },
  failed: {
    label: "FAILURE",
    color: "#f87171",
    glow:  "rgba(248,113,113,0.35)",
    bg:    "rgba(248,113,113,0.1)",
    border:"rgba(248,113,113,0.3)",
    dot:   "#f87171",
  },
  awaiting_consent: {
    label: "AWAITING CONSENT",
    color: "#c084fc",
    glow:  "rgba(192,132,252,0.35)",
    bg:    "rgba(192,132,252,0.1)",
    border:"rgba(192,132,252,0.3)",
    dot:   "#c084fc",
  },
}

function ResultBlock({ tool, result, onResume }: { tool: string, result: any, onResume?: (tool: string, task: any) => void }) {
  if (!result) return null

  if (typeof result === "string") {
    return (
      <div className="ep-result ep-result--text">
        <span className="ep-result-label">OUTPUT</span>
        <p className="ep-result-body">{result}</p>
      </div>
    )
  }

  if (result.error) {
    if (result.task) {
      const binding = result.binding_message || "Human authorization required for dangerous operation."
      return (
        <div className="ep-result ep-result--error">
          <span className="ep-result-label" style={{ color: "#a855f7" }}>// SECURITY HALT (STEP-UP AUTH)</span>
          <p className="ep-result-body ep-result-body--error" style={{ color: "rgba(168,85,247,0.85)" }}>{binding}</p>
          <p className="ep-result-body ep-result-body--error" style={{ color: "rgba(255,255,255,0.75)", marginTop: "0.3rem" }}><strong>Approval ID</strong> {result.approval_id || "unknown"}</p>
          {onResume && (
            <button 
              style={{ marginTop: "10px", padding: "6px 12px", background: "rgba(168,85,247,0.15)", border: "1px solid rgba(168,85,247,0.4)", color: "#c084fc", borderRadius: "4px", fontSize: "9px", letterSpacing: "0.15em", textTransform: "uppercase", cursor: "pointer", alignSelf: "flex-start" }}
              onClick={() => onResume(tool, { ...result.task, params: { ...result.task.params, consent_granted: true, approval_id: result.approval_id } })}
              onMouseOver={(e) => e.currentTarget.style.background = "rgba(168,85,247,0.3)"}
              onMouseOut={(e) => e.currentTarget.style.background = "rgba(168,85,247,0.15)"}
            >
              [ Authorize Token Vault Step-Up ]
            </button>
          )}
        </div>
      )
    }

    return (
      <div className="ep-result ep-result--error">
        <span className="ep-result-label">// ERROR TRACE</span>
        <p className="ep-result-body ep-result-body--error">{result.error}</p>
      </div>
    )
  }

  // Gmail Messages - Rich display with clickable links
  if (result.type === "gmail_messages" && result.messages) {
    return (
      <div className="ep-result ep-result--gmail">
        <span className="ep-result-label">// EMAIL RESULTS</span>
        {result.summary && (
          <p className="ep-result-summary">{result.summary}</p>
        )}
        <div className="ep-result-items">
          {result.messages.map((email: any, idx: number) => (
            <a 
              key={email.id || idx}
              href={email.link}
              target="_blank"
              rel="noopener noreferrer"
              className="ep-result-item ep-result-item--email"
            >
              <div className="ep-item-header">
                <span className="ep-item-icon">✉</span>
                <span className="ep-item-from">{email.from?.split('<')[0]?.trim() || email.from}</span>
                {email.date && <span className="ep-item-date">{new Date(email.date).toLocaleDateString()}</span>}
              </div>
              <div className="ep-item-subject">{email.subject}</div>
              {email.snippet && <div className="ep-item-snippet">{email.snippet}...</div>}
              <span className="ep-item-link-hint">Click to open in Gmail →</span>
            </a>
          ))}
        </div>
      </div>
    )
  }

  // Google Drive files - Rich display with clickable links
  if (result.type === "drive_files" && result.files) {
    const getFileIcon = (mimeType: string) => {
      if (!mimeType) return "◉"
      if (mimeType.includes("folder")) return "◫"
      if (mimeType.includes("spreadsheet")) return "▦"
      if (mimeType.includes("document")) return "☰"
      if (mimeType.includes("presentation")) return "▣"
      if (mimeType.includes("image")) return "▨"
      if (mimeType.includes("pdf")) return "▤"
      return "◉"
    }
    
    return (
      <div className="ep-result ep-result--drive">
        <span className="ep-result-label">// DRIVE FILES</span>
        {result.summary && (
          <p className="ep-result-summary">{result.summary}</p>
        )}
        <div className="ep-result-items">
          {result.files.map((file: any, idx: number) => (
            <a 
              key={file.id || idx}
              href={file.link}
              target="_blank"
              rel="noopener noreferrer"
              className="ep-result-item ep-result-item--file"
            >
              <span className="ep-item-icon">{getFileIcon(file.type)}</span>
              <div className="ep-item-details">
                <span className="ep-item-name">{file.name}</span>
                {file.modified && (
                  <span className="ep-item-date">Modified: {new Date(file.modified).toLocaleDateString()}</span>
                )}
              </div>
              <span className="ep-item-link-hint">Open in Drive →</span>
            </a>
          ))}
        </div>
      </div>
    )
  }

  // GitHub repos - Rich display with clickable links
  if (result.repos && Array.isArray(result.repos)) {
    return (
      <div className="ep-result ep-result--github">
        <span className="ep-result-label">// GITHUB REPOSITORIES</span>
        <p className="ep-result-summary">Found {result.repos.length} repositories</p>
        <div className="ep-result-items">
          {result.repos.map((repo: any, idx: number) => (
            <a 
              key={idx}
              href={repo.url}
              target="_blank"
              rel="noopener noreferrer"
              className="ep-result-item ep-result-item--repo"
            >
              <span className="ep-item-icon">⬡</span>
              <span className="ep-item-name">{repo.name}</span>
              <span className="ep-item-link-hint">View on GitHub →</span>
            </a>
          ))}
        </div>
      </div>
    )
  }

  // Drive file uploaded
  if (result.file_id && result.link && result.file_name) {
    return (
      <div className="ep-result ep-result--success">
        <span className="ep-result-label">// FILE UPLOADED</span>
        <p className="ep-result-summary">{result.message}</p>
        <a 
          href={result.link}
          target="_blank"
          rel="noopener noreferrer"
          className="ep-result-item ep-result-item--file"
        >
          <span className="ep-item-icon">◉</span>
          <span className="ep-item-name">{result.file_name}</span>
          <span className="ep-item-link-hint">View in Drive →</span>
        </a>
      </div>
    )
  }

  // Browser action with link (open site, login, etc.)
  if (result.url && result.link && result.status === "success") {
    return (
      <div className="ep-result ep-result--success">
        <span className="ep-result-label">// BROWSER ACTION</span>
        <p className="ep-result-summary">{result.message}</p>
        <a 
          href={result.link}
          target="_blank"
          rel="noopener noreferrer"
          className="ep-result-item ep-result-item--link"
        >
          <span className="ep-item-icon">◎</span>
          <span className="ep-item-name">{result.title || result.url}</span>
          <span className="ep-item-link-hint">Open in browser →</span>
        </a>
      </div>
    )
  }

  // GitHub issue created
  if (result.issue_number && result.url) {
    return (
      <div className="ep-result ep-result--success">
        <span className="ep-result-label">// ISSUE CREATED</span>
        <p className="ep-result-summary">{result.message}</p>
        <a 
          href={result.url}
          target="_blank"
          rel="noopener noreferrer"
          className="ep-result-item ep-result-item--link"
        >
          <span className="ep-item-icon">◉</span>
          <span className="ep-item-name">Issue #{result.issue_number}</span>
          <span className="ep-item-link-hint">View on GitHub →</span>
        </a>
      </div>
    )
  }

  // Linear issue created
  if (result.identifier && result.url) {
    return (
      <div className="ep-result ep-result--success">
        <span className="ep-result-label">// LINEAR ISSUE CREATED</span>
        <p className="ep-result-summary">{result.message}</p>
        <a 
          href={result.url}
          target="_blank"
          rel="noopener noreferrer"
          className="ep-result-item ep-result-item--link"
        >
          <span className="ep-item-icon">▣</span>
          <span className="ep-item-name">{result.identifier}</span>
          <span className="ep-item-link-hint">View in Linear →</span>
        </a>
      </div>
    )
  }

  // Calendar event created
  if (result.event_id && result.link) {
    return (
      <div className="ep-result ep-result--success">
        <span className="ep-result-label">// EVENT CREATED</span>
        <p className="ep-result-summary">{result.message}</p>
        <a 
          href={result.link}
          target="_blank"
          rel="noopener noreferrer"
          className="ep-result-item ep-result-item--calendar"
        >
          <span className="ep-item-icon">◈</span>
          <span className="ep-item-name">View Calendar Event</span>
          <span className="ep-item-link-hint">Open in Google Calendar →</span>
        </a>
        {result.start && (
          <p className="ep-result-meta">
            Scheduled: {new Date(result.start).toLocaleString()}
          </p>
        )}
      </div>
    )
  }

  // LeetCode problem / submission
  if (result.problem_title && result.url) {
    const statusLabel = result.status === "submitted" ? "SOLUTION SUBMITTED" : "PROBLEM FOUND"
    return (
      <div className="ep-result ep-result--success">
        <span className="ep-result-label">// {statusLabel}</span>
        <p className="ep-result-summary">{result.message}</p>
        {result.result && (
          <p className="ep-result-meta" style={{ color: result.result.toLowerCase().includes('accepted') ? 'rgba(74,222,128,0.9)' : 'rgba(251,191,36,0.9)' }}>
            Result: {result.result}
          </p>
        )}
        <a 
          href={result.url}
          target="_blank"
          rel="noopener noreferrer"
          className="ep-result-item ep-result-item--link"
        >
          <span className="ep-item-icon">▣</span>
          <span className="ep-item-name">{result.problem_title}</span>
          <span className="ep-item-link-hint">View on LeetCode →</span>
        </a>
      </div>
    )
  }

  // Email sent success
  if (result.message_id && result.thread_id) {
    return (
      <div className="ep-result ep-result--success">
        <span className="ep-result-label">// EMAIL SENT</span>
        <p className="ep-result-summary">{result.message}</p>
        <a 
          href={`https://mail.google.com/mail/u/0/#sent/${result.message_id}`}
          target="_blank"
          rel="noopener noreferrer"
          className="ep-result-item ep-result-item--email"
        >
          <span className="ep-item-icon">✉</span>
          <span className="ep-item-name">View Sent Email</span>
          <span className="ep-item-link-hint">Open in Gmail →</span>
        </a>
      </div>
    )
  }

  if (result.summary) {
    return (
      <div className="ep-result ep-result--summary">
        <span className="ep-result-label">// INTEL SUMMARY</span>
        <p className="ep-result-body">{result.summary}</p>
      </div>
    )
  }

  if (result.text) {
    return (
      <div className="ep-result ep-result--data">
        <span className="ep-result-label">// RAW OUTPUT</span>
        <div className="ep-result-scroll">
          <pre className="ep-result-pre">{result.text}</pre>
        </div>
      </div>
    )
  }

  if (result.messages) {
    return (
      <div className="ep-result ep-result--meta">
        <span className="ep-result-label">// API RESPONSE</span>
        <p className="ep-result-body">
          {result.messages.length} records retrieved from endpoint.
        </p>
      </div>
    )
  }

  // Success status messages
  if (result.status === "success" && result.message) {
    return (
      <div className="ep-result ep-result--success">
        <span className="ep-result-label">// SUCCESS</span>
        <p className="ep-result-body" style={{ color: "rgba(74,222,128,0.9)" }}>{result.message}</p>
      </div>
    )
  }

  return (
    <div className="ep-result ep-result--json">
      <span className="ep-result-label">// JSON PAYLOAD</span>
      <div className="ep-result-scroll">
        <pre className="ep-result-pre">{JSON.stringify(result, null, 2)}</pre>
      </div>
    </div>
  )
}

export default function ExecutionPanel({ goal, steps, onResume }: ExecutionPanelProps) {
  const running   = steps.filter(s => s.status === "running" || s.status === "awaiting_consent").length
  const completed = steps.filter(s => s.status === "completed").length
  const failed    = steps.filter(s => s.status === "failed").length

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@300;400;500&display=swap');

        /* ══ PANEL ══ */
        .ep-panel {
          font-family: 'DM Mono', monospace;
          display: flex;
          flex-direction: column;
          gap: 0;
        }

        /* ── Goal header ── */
        .ep-goal {
          padding: 18px 0 16px;
          border-bottom: 1px solid rgba(139,92,246,0.15);
          margin-bottom: 18px;
        }

        .ep-goal-eyebrow {
          font-size: 8px; letter-spacing: 0.38em; text-transform: uppercase;
          color: rgba(6,182,212,0.7);
          margin-bottom: 8px;
          display: flex; align-items: center; gap: 8px;
          font-weight: 600;
        }
        .ep-goal-eyebrow::before {
          content: '';
          display: inline-block;
          width: 24px; height: 2px;
          background: linear-gradient(90deg, rgba(139,92,246,0.8), rgba(6,182,212,0.5), transparent);
        }

        .ep-goal-text {
          font-family: 'Bebas Neue', sans-serif;
          font-size: 26px; letter-spacing: 0.06em;
          background: linear-gradient(135deg, rgba(240,245,250,0.95) 0%, rgba(167,139,250,0.9) 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          line-height: 1.1;
        }

        .ep-goal-text.empty {
          color: rgba(148,163,184,0.45);
          font-size: 16px;
          letter-spacing: 0.14em;
          background: none;
          -webkit-text-fill-color: rgba(148,163,184,0.45);
        }

        /* ── Step counter row ── */
        .ep-counts {
          display: flex; gap: 0;
          border: 1px solid rgba(139,92,246,0.2);
          border-radius: 10px;
          overflow: hidden;
          margin-bottom: 22px;
          background: rgba(15,19,29,0.5);
        }

        .ep-count-seg {
          flex: 1;
          padding: 14px 0;
          display: flex; flex-direction: column; align-items: center; gap: 5px;
          border-right: 1px solid rgba(139,92,246,0.12);
          transition: background 0.25s ease;
        }
        .ep-count-seg:hover {
          background: rgba(139,92,246,0.08);
        }
        .ep-count-seg:last-child { border-right: none; }

        .ep-count-label {
          font-size: 8px; letter-spacing: 0.3em; text-transform: uppercase;
          color: rgba(148,163,184,0.6);
          font-weight: 600;
        }
        .ep-count-val {
          font-family: 'Bebas Neue', sans-serif;
          font-size: 26px; letter-spacing: 0.04em;
          line-height: 1;
        }
        .ep-count-val.wh { color: rgba(203,213,225,0.9); }
        .ep-count-val.yw { color: #fbbf24; }
        .ep-count-val.gr { color: #4ade80; }
        .ep-count-val.rd { color: #f87171; }

        /* ── Steps list ── */
        .ep-steps {
          display: flex; flex-direction: column; gap: 12px;
        }

        /* ── Step card ── */
        .ep-step {
          border-radius: 10px;
          border: 1px solid;
          overflow: hidden;
          transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .ep-step:hover {
          transform: translateX(4px);
          box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }

        .ep-step-head {
          display: flex; align-items: center;
          padding: 12px 16px;
          gap: 12px;
        }

        /* Index badge */
        .ep-step-idx {
          font-size: 10px; letter-spacing: 0.2em;
          color: rgba(148,163,184,0.55);
          min-width: 24px; flex-shrink: 0;
          font-family: 'Bebas Neue', sans-serif;
          font-weight: 600;
        }

        /* Status dot */
        .ep-step-dot {
          width: 8px; height: 8px; border-radius: 50%;
          flex-shrink: 0;
        }
        .ep-step-dot.running {
          animation: dot-throb 1s ease-in-out infinite;
        }
        @keyframes dot-throb {
          0%,100% { opacity: 1; transform: scale(1); }
          50%      { opacity: 0.5; transform: scale(0.8); }
        }

        /* Tool name */
        .ep-step-tool {
          flex: 1;
          font-size: 13px; letter-spacing: 0.08em;
          color: rgba(240,245,250,0.95);
          white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
          font-weight: 500;
        }

        /* Status badge */
        .ep-step-badge {
          font-size: 8px; letter-spacing: 0.24em; text-transform: uppercase;
          padding: 4px 10px;
          border-radius: 100px;
          border: 1px solid;
          flex-shrink: 0;
          font-weight: 600;
        }

        /* Running spinner text */
        .ep-step-badge.running-anim {
          animation: badge-flash 1.2s ease-in-out infinite;
        }
        @keyframes badge-flash {
          0%,100% { opacity: 1; }
          50%      { opacity: 0.55; }
        }

        /* ── Progress bar (running only) ── */
        .ep-step-progress {
          height: 2px;
          background: rgba(251,191,36,0.15);
          overflow: hidden;
        }
        .ep-step-progress-fill {
          height: 100%;
          background: linear-gradient(90deg, transparent, #fbbf24, rgba(139,92,246,0.9), #06b6d4, transparent);
          background-size: 200% 100%;
          animation: progress-sweep 1.4s linear infinite;
        }
        @keyframes progress-sweep {
          0%   { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }

        /* ── Result blocks ── */
        .ep-result {
          padding: 14px 18px 16px;
          display: flex; flex-direction: column; gap: 10px;
          border-top: 1px solid rgba(139,92,246,0.1);
          background: rgba(15,19,29,0.4);
        }

        .ep-result-label {
          font-size: 8px; letter-spacing: 0.32em; text-transform: uppercase;
          color: rgba(6,182,212,0.75);
          font-weight: 600;
        }

        .ep-result-body {
          font-size: 12px; line-height: 1.65; letter-spacing: 0.02em;
          color: rgba(203,213,225,0.88);
        }
        .ep-result-body--error { color: rgba(248,113,113,0.9); }

        .ep-result--summary .ep-result-label { color: rgba(139,92,246,0.75); }
        .ep-result--summary .ep-result-body  { color: rgba(196,181,253,0.9); }
        .ep-result--error   .ep-result-label { color: rgba(248,113,113,0.8); }

        .ep-result-scroll {
          max-height: 160px;
          overflow-y: auto;
        }
        .ep-result-scroll::-webkit-scrollbar { width: 4px; }
        .ep-result-scroll::-webkit-scrollbar-thumb {
          background: linear-gradient(180deg, rgba(139,92,246,0.4), rgba(6,182,212,0.4));
          border-radius: 4px;
        }

        .ep-result-pre {
          font-family: 'DM Mono', monospace;
          font-size: 10px; line-height: 1.65;
          color: rgba(180,190,210,0.65);
          white-space: pre-wrap; word-break: break-all;
          margin: 0;
        }

        /* ── Rich Result Items ── */
        .ep-result-summary {
          font-size: 11px;
          color: rgba(203,213,225,0.88);
          margin-bottom: 12px;
          line-height: 1.55;
        }

        .ep-result-items {
          display: flex;
          flex-direction: column;
          gap: 10px;
          max-height: 300px;
          overflow-y: auto;
        }

        .ep-result-item {
          display: flex;
          flex-direction: column;
          gap: 5px;
          padding: 12px 14px;
          border-radius: 8px;
          border: 1px solid rgba(139,92,246,0.15);
          background: rgba(15,19,29,0.55);
          cursor: pointer;
          transition: all 0.25s ease;
          text-decoration: none;
          color: inherit;
        }

        .ep-result-item:hover {
          border-color: rgba(6,182,212,0.4);
          background: rgba(6,182,212,0.08);
          transform: translateX(6px);
          box-shadow: 0 0 16px rgba(6,182,212,0.15);
        }

        .ep-item-header {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .ep-item-icon {
          font-size: 14px;
          background: linear-gradient(135deg, rgba(139,92,246,0.9), rgba(6,182,212,0.9));
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          flex-shrink: 0;
        }

        .ep-item-from {
          font-size: 11px;
          font-weight: 500;
          color: rgba(240,245,250,0.92);
          flex: 1;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .ep-item-date {
          font-size: 9px;
          color: rgba(148,163,184,0.65);
          flex-shrink: 0;
        }

        .ep-item-subject {
          font-size: 10px;
          font-weight: 500;
          color: rgba(203,213,225,0.92);
          line-height: 1.45;
        }

        .ep-item-snippet {
          font-size: 9px;
          color: rgba(148,163,184,0.65);
          line-height: 1.45;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }

        .ep-item-name {
          font-size: 11px;
          color: rgba(240,245,250,0.92);
          flex: 1;
        }

        .ep-item-link-hint {
          font-size: 8px;
          letter-spacing: 0.15em;
          text-transform: uppercase;
          color: rgba(6,182,212,0.6);
          align-self: flex-end;
          opacity: 0;
          transition: opacity 0.25s ease;
        }

        .ep-result-item:hover .ep-item-link-hint {
          opacity: 1;
          color: rgba(6,182,212,0.9);
        }

        .ep-result-item--repo,
        .ep-result-item--link,
        .ep-result-item--calendar,
        .ep-result-item--file {
          flex-direction: row;
          align-items: center;
          gap: 12px;
        }

        .ep-item-details {
          display: flex;
          flex-direction: column;
          flex: 1;
          gap: 2px;
        }

        .ep-result-meta {
          font-size: 9px;
          color: rgba(148,163,184,0.6);
          margin-top: 8px;
        }

        .ep-result--success .ep-result-label {
          color: rgba(74,222,128,0.7);
        }

        .ep-result--gmail .ep-result-label {
          color: rgba(96,165,250,0.7);
        }

        .ep-result--github .ep-result-label {
          color: rgba(168,85,247,0.7);
        }

        .ep-result--drive .ep-result-label {
          color: rgba(251,191,36,0.7);
        }

        /* ── Empty state ── */
        .ep-empty {
          display: flex; flex-direction: column;
          align-items: center; justify-content: center;
          padding: 40px 0; gap: 10px;
        }
        .ep-empty-glyph {
          font-family: 'Bebas Neue', sans-serif;
          font-size: 36px; letter-spacing: 0.12em;
          color: rgba(255,40,40,0.08);
          line-height: 1;
        }
        .ep-empty-text {
          font-size: 8px; letter-spacing: 0.34em; text-transform: uppercase;
          color: rgba(130,122,108,0.3);
        }
      `}</style>

      <div className="ep-panel">

        {/* ── Goal ── */}
        <div className="ep-goal">
          <div className="ep-goal-eyebrow">Mission Objective</div>
          <div className={`ep-goal-text${!goal ? " empty" : ""}`}>
            {goal || "NO_GOAL_DEFINED"}
          </div>
        </div>

        {/* ── Counts ── */}
        {steps.length > 0 && (
          <div className="ep-counts">
            {[
              { label: "Total",     val: steps.length, cls: "wh" },
              { label: "Running",   val: running,      cls: running   > 0 ? "yw" : "wh" },
              { label: "Completed", val: completed,    cls: completed > 0 ? "gr" : "wh" },
              { label: "Failed",    val: failed,       cls: failed    > 0 ? "rd" : "wh" },
            ].map(seg => (
              <div key={seg.label} className="ep-count-seg">
                <span className="ep-count-label">{seg.label}</span>
                <span className={`ep-count-val ${seg.cls}`}>
                  {String(seg.val).padStart(2, "0")}
                </span>
              </div>
            ))}
          </div>
        )}

        {/* ── Steps ── */}
        <div className="ep-steps">
          {steps.length === 0 ? (
            <div className="ep-empty">
              <div className="ep-empty-glyph">IDLE</div>
              <span className="ep-empty-text">No operations dispatched</span>
            </div>
          ) : (
            steps.map((step, i) => {
              const s = STATUS[step.status] ?? STATUS.pending
              return (
                <div
                  key={`${step.tool}-${i}`}
                  className={`ep-step${step.status === "running" ? " running" : ""}`}
                  style={{
                    background:   s.bg,
                    borderColor:  s.border,
                    boxShadow:    step.status !== "pending"
                      ? `0 0 16px ${s.glow}, inset 0 1px 0 rgba(255,255,255,0.03)`
                      : "none",
                    animationDelay: `${i * 0.05}s`,
                  }}
                >
                  {/* Head row */}
                  <div className="ep-step-head">
                    <span className="ep-step-idx">{String(i + 1).padStart(2, "0")}</span>

                    <div
                      className={`ep-step-dot${step.status === "running" ? " running" : ""}`}
                      style={{
                        background: s.dot,
                        boxShadow: step.status !== "pending" ? `0 0 6px ${s.dot}` : "none",
                      }}
                    />

                    <code className="ep-step-tool">{step.tool}</code>

                    <span
                      className={`ep-step-badge${step.status === "running" ? " running-anim" : ""}`}
                      style={{ color: s.color, borderColor: s.border }}
                    >
                      {s.label}
                    </span>
                  </div>

                  {/* Running progress bar */}
                  {step.status === "running" && (
                    <div className="ep-step-progress">
                      <div className="ep-step-progress-fill" />
                    </div>
                  )}

                  {/* Result */}
                  {step.result && (
                    <ResultBlock tool={step.tool} result={step.result} onResume={onResume} />
                  )}
                </div>
              )
            })
          )}
        </div>
      </div>
    </>
  )
}