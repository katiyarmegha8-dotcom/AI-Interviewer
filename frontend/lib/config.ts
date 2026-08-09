/**
 * Frontend configuration.
 *
 * Reads the backend API base URL from the NEXT_PUBLIC_API_URL environment
 * variable.  Defaults to "" (same-origin) so that API calls are proxied
 * through the Next.js dev server via next.config.ts rewrites.  This avoids
 * cross-origin issues in sandbox/preview environments where the browser
 * cannot reach localhost:8000 directly.
 *
 * For local development without the proxy, set:
 *   NEXT_PUBLIC_API_URL=http://localhost:8000
 */

/** Base URL for the FastAPI backend (no trailing slash). */
export const API_BASE_URL: string =
  process.env.NEXT_PUBLIC_API_URL ?? "";
