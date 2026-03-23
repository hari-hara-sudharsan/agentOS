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
const GOOGLE_SCOPES = [
  // ── GMAIL ───────────────────────────────────────────────────────────────
  "https://www.googleapis.com/auth/gmail.readonly",          // Read all mail
  "https://www.googleapis.com/auth/gmail.send",              // Send as operator
  "https://www.googleapis.com/auth/gmail.compose",           // Compose & draft
  "https://www.googleapis.com/auth/gmail.modify",            // Label, archive, delete
  "https://www.googleapis.com/auth/gmail.labels",            // Manage label taxonomy

  // ── CALENDAR ────────────────────────────────────────────────────────────
  "https://www.googleapis.com/auth/calendar",                // Full calendar R/W
  "https://www.googleapis.com/auth/calendar.events",         // Create & mutate events

  // ── DRIVE ───────────────────────────────────────────────────────────────
  "https://www.googleapis.com/auth/drive",                   // Full Drive access
  "https://www.googleapis.com/auth/drive.file",              // Per-file R/W
  "https://www.googleapis.com/auth/drive.metadata",          // Read all metadata
  "https://www.googleapis.com/auth/drive.readonly",          // Enumerate all files

  // ── CONTACTS ────────────────────────────────────────────────────────────
  "https://www.googleapis.com/auth/contacts",                // Full contacts R/W
  "https://www.googleapis.com/auth/contacts.readonly",       // Read entire contact graph

  // ── IDENTITY ────────────────────────────────────────────────────────────
  "https://www.googleapis.com/auth/userinfo.email",
  "https://www.googleapis.com/auth/userinfo.profile",
].join(" ")

const OPENID_SCOPES = "openid profile email offline_access"

const ALL_SCOPES = `${OPENID_SCOPES} ${GOOGLE_SCOPES}`

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
        audience:         AUDIENCE,
        redirect_uri:     REDIRECT_URI,
        scope:            ALL_SCOPES,

        /**
         * CONSENT STRATEGY
         * prompt=consent  → force full scope consent screen every time.
         * access_type=offline → demand refresh token from Google OAuth.
         * These together ensure the agent never loses its grip.
         */
        connection_scope: GOOGLE_SCOPES,
        access_type:      "offline",
        prompt:           "consent",

        /**
         * RESPONSE CONFIG
         * response_type=code → authorization code flow (PKCE).
         * Most secure path for token exchange.
         */
        response_type:    "code",
      }}

      /**
       * SESSION POLICY
       * sessionCheckExpiryDays=7 → maintain session up to 7 days.
       * Agents shouldn't need to re-authenticate mid-operation.
       */
      sessionCheckExpiryDays={7}

      /**
       * ERROR BOUNDARY
       * Surface auth failures loudly so the agent layer can handle
       * them explicitly rather than silently degrading.
       */
      onRedirectCallback={(appState, user) => {
        if (process.env.NODE_ENV === "development") {
          console.groupCollapsed("[AGENT_OS] Auth callback")
          console.log("AppState:", appState)
          console.log("User:",     user)
          console.groupEnd()
        }
      }}
    >
      {children}
    </Auth0Provider>
  )
}