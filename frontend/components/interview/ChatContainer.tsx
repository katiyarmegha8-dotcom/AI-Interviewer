"use client";

import { useEffect, type RefObject } from "react";

import type { ChatMessage, InterviewFeedback } from "@/types/interview";

import { ChatMessage as ChatMessageBubble } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { FeedbackPanel } from "./FeedbackPanel";
import { TypingIndicator } from "./TypingIndicator";

type ChatContainerProps = {
  /** List of chat messages to render. */
  messages: ChatMessage[];
  /** Whether the AI is currently typing. */
  isAiTyping: boolean;
  /** Callback when the candidate sends a message. */
  onSendMessage: (content: string) => void;
  /** Ref for the scroll anchor element. */
  scrollAnchorRef: RefObject<HTMLDivElement | null>;
  /** Whether the interview has ended. */
  isInterviewDone: boolean;
  /** End the interview and request feedback. */
  onEndInterview: () => void;
  /** Final feedback (null until interview ends). */
  feedback: InterviewFeedback | null;
  /** Last error message. */
  error: string | null;
  /** Dismiss the current error. */
  onDismissError: () => void;
  /** Start a new interview session. */
  onStartNewInterview: () => void;
  /** Whether the interview is starting up. */
  isStarting: boolean;
};

/** Full interview chat interface with error handling, end controls, and feedback. */
export function ChatContainer({
  messages,
  isAiTyping,
  onSendMessage,
  scrollAnchorRef,
  isInterviewDone,
  onEndInterview,
  feedback,
  error,
  onDismissError,
  onStartNewInterview,
  isStarting,
}: ChatContainerProps) {
  // Auto-scroll whenever messages change or typing state changes.
  useEffect(() => {
    scrollAnchorRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isAiTyping, scrollAnchorRef]);

  /** Input is disabled when: AI typing, interview done, or starting up. */
  const inputDisabled = isAiTyping || isInterviewDone || isStarting;

  /** Whether the conversation area is effectively empty. */
  const isConversationEmpty = messages.length === 0 && !isAiTyping && !isStarting;

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-xl border border-border bg-surface">
      {/* Conversation area — role="log" for screen reader live region */}
      <div className="flex-1 overflow-y-auto px-4 py-4 sm:px-6" role="log" aria-label="Interview conversation">
        <div className="space-y-4">
          {/* Empty state — show a helpful prompt when nothing has happened yet */}
          {isConversationEmpty && !error && (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth={1.5}
                className="mb-3 h-10 w-10 text-content-muted/40"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.398 1.135 2.53 2.53 2.53H14.25c1.397 0 2.53-1.132 2.53-2.53V5.26c0-1.398-1.133-2.53-2.53-2.53H5.26c-1.397 0-2.53 1.132-2.53 2.53v7.5ZM20.25 8.25l-3.47 3.47"
                />
              </svg>
              <p className="text-sm text-content-muted">
                Waiting for the interview to start…
              </p>
            </div>
          )}

          {/* Starting indicator — skeleton shimmer */}
          {isStarting && messages.length === 0 && (
            <div className="flex justify-start">
              <div className="max-w-[70%] rounded-xl rounded-tl-sm bg-accent/10 px-4 py-3">
                <p className="mb-1 text-[11px] font-medium uppercase tracking-wider text-accent">
                  Interviewer
                </p>
                <div className="space-y-2">
                  <div
                    className="h-3 w-48 rounded-full bg-accent/10"
                    style={{
                      background: "linear-gradient(90deg, rgba(37,99,235,0.08) 25%, rgba(37,99,235,0.15) 50%, rgba(37,99,235,0.08) 75%)",
                      backgroundSize: "200% 100%",
                      animation: "shimmer 1.5s ease-in-out infinite",
                    }}
                  />
                  <div
                    className="h-3 w-32 rounded-full bg-accent/10"
                    style={{
                      background: "linear-gradient(90deg, rgba(37,99,235,0.08) 25%, rgba(37,99,235,0.15) 50%, rgba(37,99,235,0.08) 75%)",
                      backgroundSize: "200% 100%",
                      animation: "shimmer 1.5s ease-in-out infinite",
                      animationDelay: "0.3s",
                    }}
                  />
                </div>
              </div>
            </div>
          )}

          {messages.map((msg) => (
            <ChatMessageBubble key={msg.id} message={msg} />
          ))}

          {/* Typing indicator */}
          {isAiTyping && !isStarting && <TypingIndicator />}

          {/* Error message — role="alert" for screen reader announcement */}
          {error && (
            <div
              className="flex justify-center"
              role="alert"
              aria-live="assertive"
            >
              <div className="max-w-[90%] rounded-xl border border-red-200 bg-red-50 px-4 py-3 sm:max-w-[80%]">
                <div className="flex items-start gap-2">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                    className="mt-0.5 h-4 w-4 flex-shrink-0 text-red-500"
                    aria-hidden="true"
                  >
                    <path
                      fillRule="evenodd"
                      d="M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0Zm-7-4.25a.75.75 0 0 0-1.5 0v5.5a.75.75 0 0 0 1.5 0v-5.5ZM10 14a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <div>
                    <p className="text-sm leading-relaxed text-red-800 sm:text-base">
                      {error}
                    </p>
                    <button
                      type="button"
                      onClick={onDismissError}
                      className="mt-2 inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium text-red-700 transition-colors hover:bg-red-100 hover:text-red-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-400"
                    >
                      Dismiss
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Feedback panel */}
          {isInterviewDone && feedback && (
            <FeedbackPanel feedback={feedback} />
          )}

          {/* End-interview controls */}
          {isInterviewDone && (
            <div className="flex justify-center pt-3 pb-1">
              <button
                type="button"
                onClick={onStartNewInterview}
                className="inline-flex items-center justify-center gap-2 rounded-lg bg-accent px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-accent-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  className="h-4 w-4"
                  aria-hidden="true"
                >
                  <path
                    fillRule="evenodd"
                    d="M4.25 11.25a.75.75 0 0 0 0 1.5h7.5a.75.75 0 0 0 0-1.5h-7.5ZM1 10a9 9 0 1 1 18 0 9 9 0 0 1-18 0Zm9-7.5a7.5 7.5 0 1 0 0 15 7.5 7.5 0 0 0 0-15Z"
                    clipRule="evenodd"
                  />
                </svg>
                Start new interview
              </button>
            </div>
          )}

          {/* Scroll anchor */}
          <div ref={scrollAnchorRef} />
        </div>
      </div>

      {/* Input area (hidden when interview is done) */}
      {!isInterviewDone && (
        <div className="flex flex-col">
          {/* End interview button row */}
          <div className="flex items-center justify-between border-t border-border bg-surface-muted px-3 py-1.5 sm:px-5">
            <span className="text-[11px] text-content-muted/60 sm:text-xs">
              {messages.length > 0
                ? `${messages.length} message${messages.length !== 1 ? "s" : ""}`
                : ""}
            </span>
            <button
              type="button"
              onClick={onEndInterview}
              disabled={isAiTyping || isStarting || messages.length === 0}
              aria-label="End interview and receive feedback"
              className="inline-flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-xs font-medium text-content-muted transition-colors hover:bg-red-50 hover:text-red-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-1 disabled:pointer-events-none disabled:opacity-30"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 16 16"
                fill="currentColor"
                className="h-3 w-3"
                aria-hidden="true"
              >
                <path
                  fillRule="evenodd"
                  d="M3 8a5 5 0 1 1 10 0A5 5 0 0 1 3 8Zm5-6.5a6.5 6.5 0 1 0 0 13 6.5 6.5 0 0 0 0-13ZM5.22 5.22a.75.75 0 0 1 1.06 0L8 6.94l1.72-1.72a.75.75 0 1 1 1.06 1.06L9.06 8l1.72 1.72a.75.75 0 1 1-1.06 1.06L8 9.06l-1.72 1.72a.75.75 0 0 1-1.06-1.06L6.94 8 5.22 6.28a.75.75 0 0 1 0-1.06Z"
                  clipRule="evenodd"
                />
              </svg>
              End interview
            </button>
          </div>
          <ChatInput onSend={onSendMessage} disabled={inputDisabled} />
        </div>
      )}
    </div>
  );
}
