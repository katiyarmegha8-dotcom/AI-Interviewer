"use client";

import { useState, useCallback, useRef, useEffect } from "react";

import type {
  ChatMessage,
  ChatRole,
  InterviewFeedback,
  Candidate,
} from "@/types/interview";
import {
  interviewApi,
  InterviewApiError,
} from "@/lib/api";

// ---------------------------------------------------------------------------
// ID generation
// ---------------------------------------------------------------------------

/** Incrementing counter for unique message ids. */
let nextId = 0;

/** Create a unique message id. */
function createId(): string {
  nextId += 1;
  return `msg-${nextId}`;
}

// ---------------------------------------------------------------------------
// Session ID generation
// ---------------------------------------------------------------------------

/** Create a new unique session ID. */
function createSessionId(): string {
  return `session-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

// ---------------------------------------------------------------------------
// Default candidate profile
// ---------------------------------------------------------------------------

/**
 * Default candidate profile for the interview.
 *
 * This is used when no specific candidate is selected.
 * The backend StubLLMService / prompt builder will accept any valid Candidate shape.
 */
const DEFAULT_CANDIDATE: Candidate = {
  member: {
    id: "CAND-UI-001",
    name: "Interview Candidate",
    jobRole: "Software Developer",
    yearsExperience: 3,
    education: "Bachelor's in Computer Science",
    status: "ACTIVE",
  },
  missions: [],
  signals: {
    commitDays: 0,
    missionsCompleted: 0,
    missionsFirstTry: 0,
  },
};

// ---------------------------------------------------------------------------
// Hook return type
// ---------------------------------------------------------------------------

/** Interview session state. */
export type InterviewStatus = "idle" | "active" | "completed";

/** Return value of the useInterviewChat hook. */
export interface UseInterviewChatReturn {
  /** Current list of chat messages. */
  messages: ChatMessage[];
  /** Whether the AI is currently "typing" a response (i.e. an API call is in flight). */
  isAiTyping: boolean;
  /** Send a candidate message to the backend. */
  sendMessage: (content: string) => void;
  /** Ref to attach to the scroll anchor element at the bottom of the chat. */
  scrollAnchorRef: React.RefObject<HTMLDivElement | null>;
  /** Current interview session ID. */
  sessionId: string;
  /** Whether the interview has ended. */
  isInterviewDone: boolean;
  /** End the interview and request feedback. */
  endInterview: () => void;
  /** Final feedback (null until interview ends and feedback is returned). */
  feedback: InterviewFeedback | null;
  /** Last error message (null when no error). */
  error: string | null;
  /** Dismiss the current error. */
  dismissError: () => void;
  /** Start a new interview session. */
  startNewInterview: () => void;
  /** Whether the interview is starting up (first API call in flight). */
  isStarting: boolean;
}

// ---------------------------------------------------------------------------
// Hook implementation
// ---------------------------------------------------------------------------

/**
 * Custom hook that manages interview chat state with real API integration:
 * - Session ID lifecycle
 * - Starting the interview via POST /api/interview
 * - Sending candidate messages and receiving AI replies
 * - Ending the interview and receiving feedback
 * - Error handling and retry
 * - Auto-scroll
 */
export function useInterviewChat(): UseInterviewChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isAiTyping, setIsAiTyping] = useState(false);
  const [isStarting, setIsStarting] = useState(false);
  const [sessionId, setSessionId] = useState(createSessionId);
  const [isInterviewDone, setIsInterviewDone] = useState(false);
  const [feedback, setFeedback] = useState<InterviewFeedback | null>(null);
  const [error, setError] = useState<string | null>(null);

  const scrollAnchorRef = useRef<HTMLDivElement | null>(null);

  /** Whether the component is still mounted — guards async state updates after unmount. */
  const isMountedRef = useRef(true);

  /** Scroll the conversation to the bottom. */
  const scrollToBottom = useCallback(() => {
    requestAnimationFrame(() => {
      scrollAnchorRef.current?.scrollIntoView({ behavior: "smooth" });
    });
  }, []);

  /** Add a message to the conversation and scroll. */
  const addMessage = useCallback(
    (role: ChatRole, content: string) => {
      const message: ChatMessage = { id: createId(), role, content };
      setMessages((prev) => [...prev, message]);
      scrollToBottom();
    },
    [scrollToBottom],
  );

  /** Handle an API error: set the error state and stop loading. */
  const handleError = useCallback(
    (err: unknown) => {
      setIsAiTyping(false);
      setIsStarting(false);
      if (err instanceof InterviewApiError) {
        setError(err.message);
      } else if (err instanceof Error) {
        setError("An unexpected error occurred. Please try again.");
      } else {
        setError("An unknown error occurred. Please try again.");
      }
    },
    [],
  );

  /** Start the interview by calling the backend. */
  const startSession = useCallback(
    async (sid: string) => {
      setIsStarting(true);
      setIsAiTyping(true);
      setError(null);

      try {
        const response = await interviewApi({
          sessionId: sid,
          candidate: DEFAULT_CANDIDATE,
        });
        if (!isMountedRef.current) return;
        setIsStarting(false);
        setIsAiTyping(false);
        addMessage("ai", response.reply);
      } catch (err) {
        if (!isMountedRef.current) return;
        handleError(err);
      }
    },
    [addMessage, handleError],
  );

  /** Send a candidate message and get the AI reply. */
  const sendMessage = useCallback(
    (content: string) => {
      if (isInterviewDone || isAiTyping) return;

      // Add the candidate message to the UI immediately.
      addMessage("candidate", content);

      // Show typing indicator.
      setIsAiTyping(true);
      setError(null);
      scrollToBottom();

      // Send to the backend.
      interviewApi({ sessionId, message: content })
        .then((response) => {
          if (!isMountedRef.current) return;
          setIsAiTyping(false);

          if (response.done) {
            addMessage("ai", response.reply);
            setIsInterviewDone(true);
            if (response.feedback) {
              setFeedback(response.feedback);
            }
          } else {
            addMessage("ai", response.reply);
          }
        })
        .catch((err) => {
          if (!isMountedRef.current) return;
          handleError(err);
        });
    },
    [sessionId, isInterviewDone, isAiTyping, addMessage, scrollToBottom, handleError],
  );

  /** End the interview and request feedback. */
  const endInterview = useCallback(() => {
    if (isInterviewDone || isAiTyping) return;

    setIsAiTyping(true);
    setError(null);

    interviewApi({ sessionId, done: true })
      .then((response) => {
        if (!isMountedRef.current) return;
        setIsAiTyping(false);
        addMessage("ai", response.reply);
        setIsInterviewDone(true);
        if (response.feedback) {
          setFeedback(response.feedback);
        }
      })
      .catch((err) => {
        if (!isMountedRef.current) return;
        handleError(err);
      });
  }, [sessionId, isInterviewDone, isAiTyping, addMessage, handleError]);

  /** Start a brand-new interview (reset all state). */
  const startNewInterview = useCallback(() => {
    const newSessionId = createSessionId();
    setSessionId(newSessionId);
    setMessages([]);
    setIsInterviewDone(false);
    setFeedback(null);
    setError(null);
    setIsAiTyping(false);
    setIsStarting(false);

    // Start the session on the backend.
    startSession(newSessionId);
  }, [startSession]);

  /** Dismiss the current error. */
  const dismissError = useCallback(() => {
    setError(null);
  }, []);

  // On first mount, automatically start the interview.
  // Using useEffect (not render-time) ensures state updates happen after commit,
  // avoiding "Can't perform a React state update on a component that hasn't mounted yet."
  // hasInitiatedRef prevents double-firing in React Strict Mode.
  const hasInitiatedRef = useRef(false);

  useEffect(() => {
    isMountedRef.current = true;

    if (!hasInitiatedRef.current) {
      hasInitiatedRef.current = true;
      startSession(sessionId);
    }

    return () => {
      isMountedRef.current = false;
    };
    // We intentionally only run this on mount. startSession and sessionId are
    // captured at first render — re-triggering on their changes would restart
    // the interview, which is not desired.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return {
    messages,
    isAiTyping,
    sendMessage,
    scrollAnchorRef,
    sessionId,
    isInterviewDone,
    endInterview,
    feedback,
    error,
    dismissError,
    startNewInterview,
    isStarting,
  };
}
