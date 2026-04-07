"use client";

import { useAuth0 } from "@auth0/auth0-react";
import { useCallback } from "react";

/**
 * Hook that wraps getAccessTokenSilently with proper error handling.
 * Handles "Consent required" and "Login required" errors by triggering re-auth.
 */
export function useAuthToken() {
  const { getAccessTokenSilently, loginWithRedirect, logout } = useAuth0();

  const getToken = useCallback(async (): Promise<string | null> => {
    try {
      return await getAccessTokenSilently();
    } catch (error: any) {
      const errorMessage = error?.message || error?.error || "";

      // Handle consent/login required errors by clearing cache and re-authenticating
      if (
        errorMessage.includes("Consent required") ||
        errorMessage.includes("consent_required") ||
        errorMessage.includes("Login required") ||
        errorMessage.includes("login_required")
      ) {
        console.warn(
          "[Auth] Token error, clearing cache and re-authenticating:",
          errorMessage,
        );

        // Clear Auth0 localStorage cache to remove stale tokens
        Object.keys(localStorage).forEach((key) => {
          if (key.startsWith("@@auth0")) {
            localStorage.removeItem(key);
          }
        });

        // Redirect to login
        await loginWithRedirect();
        return null;
      }

      // For other errors, log and return null
      console.error("[Auth] Failed to get token:", error);
      return null;
    }
  }, [getAccessTokenSilently, loginWithRedirect]);

  const clearAuthCache = useCallback(() => {
    Object.keys(localStorage).forEach((key) => {
      if (key.startsWith("@@auth0")) {
        localStorage.removeItem(key);
      }
    });
  }, []);

  return { getToken, clearAuthCache };
}
