/**
 * Interview API client.
 *
 * Thin service layer that communicates with the FastAPI backend.
 * All request/response types are defined in @/types/interview and
 * match the backend Pydantic models exactly.
 */

import { API_BASE_URL } from "./config";
import type {
  InterviewRequest,
  InterviewResponse,
  ApiErrorResponse,
} from "@/types/interview";

/** Full URL for the interview endpoint. */
const INTERVIEW_ENDPOINT = `${API_BASE_URL}/api/interview`;

/**
 * Custom error class for API failures.
 *
 * Carries a user-friendly message and the HTTP status code (if available).
 */
export class InterviewApiError extends Error {
  /** HTTP status code, or 0 for network/parse failures. */
  readonly status: number;

  constructor(message: string, status = 0) {
    super(message);
    this.name = "InterviewApiError";
    this.status = status;
  }
}

/**
 * Send a request to the interview API.
 *
 * @param request - One of the three interview request shapes.
 * @returns The interview response from the backend.
 * @throws {InterviewApiError} On network failure, non-2xx, or invalid response.
 */
export async function interviewApi(
  request: InterviewRequest,
): Promise<InterviewResponse> {
  let response: Response;

  try {
    response = await fetch(INTERVIEW_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });
  } catch {
    // Network failure (server unreachable, CORS, etc.)
    throw new InterviewApiError(
      "Unable to reach the interview server. Please check your connection and try again.",
    );
  }

  // Non-2xx response
  if (!response.ok) {
    let detail = "";
    try {
      const body: ApiErrorResponse = await response.json();
      detail = body.detail ?? "";
    } catch {
      // Response body is not JSON or cannot be parsed
    }

    if (response.status === 404) {
      throw new InterviewApiError(
        detail || "Interview session not found. It may have expired.",
        response.status,
      );
    }

    if (response.status >= 500) {
      throw new InterviewApiError(
        "The interview server encountered an error. Please try again shortly.",
        response.status,
      );
    }

    throw new InterviewApiError(
      detail || `Request failed (${response.status}). Please try again.`,
      response.status,
    );
  }

  // Parse the success response
  let data: InterviewResponse;
  try {
    data = await response.json();
  } catch {
    throw new InterviewApiError(
      "Received an invalid response from the server.",
    );
  }

  // Validate the expected shape minimally
  if (typeof data.reply !== "string" || typeof data.done !== "boolean") {
    throw new InterviewApiError(
      "Received an unexpected response format from the server.",
    );
  }

  return data;
}

// ---------------------------------------------------------------------------
// Convenience functions for each request shape
// ---------------------------------------------------------------------------

/** Start a new interview session. */
export async function startInterview(
  sessionId: string,
  candidate: InterviewRequest extends { candidate: infer C } ? C : never,
): Promise<InterviewResponse> {
  return interviewApi({ sessionId, candidate } as InterviewRequest);
}

/** Continue an existing interview session with a candidate message. */
export async function continueInterview(
  sessionId: string,
  message: string,
): Promise<InterviewResponse> {
  return interviewApi({ sessionId, message });
}

/** End an interview session and request feedback. */
export async function endInterview(
  sessionId: string,
): Promise<InterviewResponse> {
  return interviewApi({ sessionId, done: true });
}
