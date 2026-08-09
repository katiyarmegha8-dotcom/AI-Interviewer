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

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-xl border border-border bg-surface">
      {/* Conversation area */}
      <div className="flex-1 overflow-y-auto px-4 py-4 sm:px-6">
        <div className="space-y-3">
          {/* Starting indicator */}
          {isStarting && messages.length === 0 && (
            <div className="flex justify-start">
              <div className="rounded-xl rounded-tl-sm bg-accent/10 px-4 py-3">
                <p className="text-sm text-content-muted">
                  Starting interview…
                </p>
              </div>
            </div>
          )}

          {messages.map((msg) => (
            <ChatMessageBubble key={msg.id} message={msg} />
          ))}

          {/* Typing indicator */}
          {isAiTyping && !isStarting && <TypingIndicator />}

          {/* Error message */}
          {error && (
            <div className="flex justify-center">
              <div className="max-w-[90%] rounded-xl border border-red-300 bg-red-50 px-4 py-3 sm:max-w-[80%]">
                <p className="text-sm leading-relaxed text-red-800 sm:text-base">
                  {error}
                </p>
                <button
                  type="button"
                  onClick={onDismissError}
                  className="mt-2 text-xs font-medium text-red-600 underline hover:text-red-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-400"
                >
                  Dismiss
                </button>
              </div>
            </div>
          )}

          {/* Feedback panel */}
          {isInterviewDone && feedback && (
            <FeedbackPanel feedback={feedback} />
          )}

          {/* End-interview controls */}
          {isInterviewDone && (
            <div className="flex justify-center pt-2">
              <button
                type="button"
                onClick={onStartNewInterview}
                className="inline-flex items-center justify-center rounded-lg bg-accent px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-accent-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2"
              >
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
        <div className="flex flex-col gap-0">
          {/* End interview button */}
          <div className="flex justify-end border-t border-border bg-surface-muted px-4 pt-2 sm:px-6">
            <button
              type="button"
              onClick={onEndInterview}
              disabled={isAiTyping || isStarting || messages.length === 0}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-content-muted transition-colors hover:text-content focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-40"
            >
              End interview
            </button>
          </div>
          <ChatInput onSend={onSendMessage} disabled={inputDisabled} />
        </div>
      )}
    </div>
  );
}
