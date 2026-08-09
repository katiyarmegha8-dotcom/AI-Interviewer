// ---------------------------------------------------------------------------
// Chat / UI types
// ---------------------------------------------------------------------------

/** Chat message role – who sent the message. */
export type ChatRole = "ai" | "candidate";

/** A single message in the interview conversation. */
export interface ChatMessage {
  /** Unique message identifier. */
  id: string;
  /** Who sent this message. */
  role: ChatRole;
  /** The message text content. */
  content: string;
}

// ---------------------------------------------------------------------------
// API request types — mirror the FastAPI Pydantic models exactly
// ---------------------------------------------------------------------------

/** Candidate member identity (matches CandidateMember Pydantic model). */
export interface CandidateMember {
  id: string;
  name: string;
  jobRole: string;
  yearsExperience: number;
  education: string;
  status: string;
}

/** A single mission record (matches Mission Pydantic model). */
export interface Mission {
  day: number;
  title: string;
  passed: boolean | null;
  attempts: number | null;
  skipped: boolean | null;
}

/** Aggregate engagement signals (matches Signals Pydantic model). */
export interface Signals {
  commitDays: number;
  missionsCompleted: number;
  missionsFirstTry: number;
}

/** Full candidate profile (matches Candidate Pydantic model). */
export interface Candidate {
  member: CandidateMember;
  missions: Mission[];
  signals: Signals;
}

/** Interview feedback returned when done=true (matches Feedback Pydantic model). */
export interface InterviewFeedback {
  summary: string;
  strengths: string[];
  gaps: string[];
  next: string[];
}

// ---------------------------------------------------------------------------
// API request shapes
// ---------------------------------------------------------------------------

/** Start interview: sessionId + candidate. */
export interface StartInterviewRequest {
  sessionId: string;
  candidate: Candidate;
}

/** Continue interview: sessionId + message. */
export interface ContinueInterviewRequest {
  sessionId: string;
  message: string;
}

/** End interview: sessionId + done=true. */
export interface EndInterviewRequest {
  sessionId: string;
  done: true;
}

/** Union of all interview request shapes. */
export type InterviewRequest =
  | StartInterviewRequest
  | ContinueInterviewRequest
  | EndInterviewRequest;

// ---------------------------------------------------------------------------
// API response type — matches InterviewResponse Pydantic model
// ---------------------------------------------------------------------------

/** Response from POST /api/interview (matches InterviewResponse Pydantic model). */
export interface InterviewResponse {
  reply: string;
  done: boolean;
  feedback: InterviewFeedback | null;
  progress: InterviewProgress;
}

/** Interview progress tracking returned in every response. */
export interface InterviewProgress {
  questionsAsked: number;
  questionsAnswered: number;
  curriculumDaysCovered: number;
  currentDay: number;
  totalDays: number;
}

// ---------------------------------------------------------------------------
// API error response
// ---------------------------------------------------------------------------

/** Error response shape from the FastAPI exception handlers. */
export interface ApiErrorResponse {
  detail: string;
}
