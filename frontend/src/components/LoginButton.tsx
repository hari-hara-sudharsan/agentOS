"use client"

import { useAuth0 } from "@auth0/auth0-react"

export default function LoginButton() {

  const { loginWithRedirect } = useAuth0()

  return (
    <>
      <style>{`
        .login-btn {
          display: inline-flex; align-items: center; gap: 10px;
          padding: 14px 32px;
          border-radius: var(--radius-md);
          border: none;
          background: linear-gradient(135deg, var(--violet) 0%, var(--cyan-dim) 100%);
          color: #fff;
          font-family: var(--font-body);
          font-size: 14px; font-weight: 600;
          letter-spacing: 0.06em;
          cursor: pointer;
          transition: all 0.3s ease;
          box-shadow: 0 4px 24px rgba(139,92,246,0.3), 0 0 48px rgba(6,182,212,0.15);
          position: relative;
          overflow: hidden;
        }
        .login-btn::before {
          content: '';
          position: absolute; inset: 0;
          background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, transparent 50%);
          opacity: 0;
          transition: opacity 0.3s ease;
        }
        .login-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 32px rgba(139,92,246,0.4), 0 0 64px rgba(6,182,212,0.25);
        }
        .login-btn:hover::before { opacity: 1; }
        .login-btn:active { transform: translateY(0) scale(0.98); }
        .login-btn-arrow {
          font-size: 16px;
          transition: transform 0.2s ease;
        }
        .login-btn:hover .login-btn-arrow { transform: translateX(3px); }
      `}</style>
      <button
        className="login-btn"
        onClick={() => loginWithRedirect({
          authorizationParams: {
            scope: "openid profile email offline_access https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.compose https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/calendar.events",
            prompt: "consent",
            access_type: "offline"
          }
        })}
      >
        Authenticate
        <span className="login-btn-arrow">→</span>
      </button>
    </>
  )
}