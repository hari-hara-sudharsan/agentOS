"use client"

import { Auth0Provider } from "@auth0/auth0-react"

const DOMAIN    = process.env.NEXT_PUBLIC_AUTH0_DOMAIN!
const CLIENT_ID = process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID!
const AUDIENCE  = process.env.NEXT_PUBLIC_AUTH0_AUDIENCE

/*
 ██████╗  █████╗ ███╗   ██╗ ██████╗ ███████╗██████╗  ██████╗ ██╗   ██╗███████╗
 ██╔══██╗██╔══██╗████╗  ██║██╔════╝ ██╔════╝██╔══██╗██╔═══██╗██║   ██║██╔════╝
 ██║  ██║███████║██╔██╗ ██║██║  ███╗█████╗  ██████╔╝██║   ██║██║   ██║███████╗
 ██║  ██║██╔══██║██║╚██╗██║██║   ██║██╔══╝  ██╔══██╗██║   ██║██║   ██║╚════██║
 ██████╔╝██║  ██║██║ ╚████║╚██████╔╝███████╗██║  ██║╚██████╔╝╚██████╔╝███████║
 ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚══════╝
  AGENT_OS // AUTH LAYER v2.4 — MAXIMUM CLEARANCE
*/

/**
 * OAUTH SCOPE MANIFEST
 * Full-spectrum access grants for autonomous agent operation.
 * Each scope is a loaded weapon — handle accordingly.
 */
const OPENID_SCOPES = "openid profile email offline_access"

// Google scopes are requested per-integration, not at Auth0 level
// This prevents "consent required" errors during initial login
const GOOGLE_SCOPES = [
  // Gmail
  "https://www.googleapis.com/auth/gmail.readonly",
  "https://www.googleapis.com/auth/gmail.send",
  "https://www.googleapis.com/auth/gmail.compose",
  "https://www.googleapis.com/auth/gmail.modify",
  "https://www.googleapis.com/auth/gmail.labels",
  // Calendar
  "https://www.googleapis.com/auth/calendar",
  "https://www.googleapis.com/auth/calendar.events",
  // Drive
  "https://www.googleapis.com/auth/drive",
  "https://www.googleapis.com/auth/drive.file",
  "https://www.googleapis.com/auth/drive.metadata",
  "https://www.googleapis.com/auth/drive.readonly",
  // Contacts
  "https://www.googleapis.com/auth/contacts",
  "https://www.googleapis.com/auth/contacts.readonly",
]

// For initial Auth0 auth, request ALL scopes to ensure the identity is fully authorized
// This prevents "Metadata Only" errors by forcing consent during primary login
const ALL_SCOPES = `${OPENID_SCOPES} https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.compose https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/calendar.events`

/** Redirect target — window-safe for SSR/SSG */
const REDIRECT_URI =
  typeof window !== "undefined" ? window.location.origin : undefined

export default function AuthProvider({ children }: { children: React.ReactNode }) {
  return (
    <Auth0Provider
      domain={DOMAIN}
      clientId={CLIENT_ID}

      /**
       * PERSISTENCE STRATEGY
       * localstorage: tokens survive tab/window close.
       * refresh tokens keep the agent alive without re-auth.
       * Silent SSO fallback prevents hard interruptions.
       */
      cacheLocation="localstorage"
      useRefreshTokens={true}
      useRefreshTokensFallback={true}

      authorizationParams={{
        audience:      AUDIENCE,
        redirect_uri:  REDIRECT_URI,
        scope:         ALL_SCOPES,

        /**
         * LOGIN PROMPT
         * - "login": Always show login screen (no SSO cache)
         * - "none": Use SSO if available, error if not authenticated
         * - "consent": Force consent screen (commented out)
         * 
         * Using default (no prompt) allows smooth SSO + incremental consent
         * per integration (Gmail/Calendar scopes requested when connecting)
         */
        access_type:   "offline",
        response_type: "code",
      }}

      /**
       * SESSION POLICY
       * sessionCheckExpiryDays=7 → maintain session up to 7 days.
       * Agents shouldn't need to re-authenticate mid-operation.
       */
      sessionCheckExpiryDays={7}

      /**
       * ERROR BOUNDARY & REDIRECT
       * After Auth0 completes authorization, redirect to the app.
       * Maintains return state from before login attempt.
       */
      onRedirectCallback={(appState) => {
        if (process.env.NODE_ENV === "development") {
          console.groupCollapsed("[AGENT_OS] Auth redirect callback")
          console.log("AppState:", appState)
          console.groupEnd()
        }
        // Redirect to the intended page or dashboard
        const returnTo = appState?.returnTo || "/dashboard"
        window.location.replace(returnTo)
      }}
    >
      {children}
    </Auth0Provider>
  )
}

/**
 * Export Google scopes for use in integration endpoints
 * These are requested per-integration to avoid consent fatigue
 */
export const INTEGRATION_SCOPES = {
  GMAIL: GOOGLE_SCOPES.filter(s => s.includes("gmail")).join(" "),
  CALENDAR: GOOGLE_SCOPES.filter(s => s.includes("calendar")).join(" "),
  DRIVE: GOOGLE_SCOPES.filter(s => s.includes("drive")).join(" "),
  CONTACTS: GOOGLE_SCOPES.filter(s => s.includes("contacts")).join(" "),
  ALL_GOOGLE: GOOGLE_SCOPES.join(" "),
}