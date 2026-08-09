/**
 * Frontend configuration.
 *
 * Reads the backend API base URL from the NEXT_PUBLIC_API_URL environment
 * variable.  Defaults to http://localhost:8000 for local development.
 */

/** Base URL for the FastAPI backend (no trailing slash). */
export const API_BASE_URL: string =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
