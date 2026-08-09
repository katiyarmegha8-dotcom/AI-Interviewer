"use client";

import { useState, useCallback, useRef, type KeyboardEvent } from "react";

type ChatInputProps = {
  /** Called when the candidate sends a non-empty message. */
  onSend: (content: string) => void;
  /** Whether the input should be disabled (e.g. while AI is typing). */
  disabled?: boolean;
};

/** Candidate message input with textarea and send button. */
export function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  /** Auto-resize the textarea to fit content (up to a max height). */
  const adjustHeight = useCallback(() => {
    const el = textareaRef.current;
    if (!el) return;
    // Reset height to auto to get the correct scrollHeight.
    el.style.height = "auto";
    // Clamp between single-line height and a reasonable max.
    el.style.height = `${Math.min(el.scrollHeight, 120)}px`;
  }, []);

  /** Send the current message if it's non-empty. */
  const handleSend = useCallback(() => {
    const trimmed = value.trim();
    if (trimmed.length === 0) return;
    onSend(trimmed);
    setValue("");
    // Reset textarea height after sending.
    requestAnimationFrame(() => {
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    });
  }, [value, onSend]);

  /** Handle keyboard shortcuts in the textarea. */
  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      // Enter without Shift sends the message.
      // Shift+Enter inserts a newline (default textarea behaviour).
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend],
  );

  return (
    <div className="flex items-end gap-2 border-t border-border bg-surface px-3 py-2.5 sm:gap-3 sm:px-5 sm:py-3">
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => {
          setValue(e.target.value);
          adjustHeight();
        }}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        placeholder="Type your answer…"
        rows={1}
        aria-label="Type your interview response. Press Enter to send, Shift+Enter for a new line."
        className="flex-1 resize-none rounded-lg border border-border bg-surface-muted px-3 py-2.5 text-sm leading-normal text-content placeholder:text-content-muted focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/30 disabled:cursor-not-allowed disabled:opacity-50 sm:text-base"
      />
      <button
        type="button"
        onClick={handleSend}
        disabled={disabled || value.trim().length === 0}
        aria-label="Send message"
        className="inline-flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-accent text-white transition-colors hover:bg-accent-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
      >
        {/* Send arrow icon */}
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
          className="h-5 w-5"
          aria-hidden="true"
        >
          <path d="M3.105 2.289a.75.75 0 0 0-.826.95l1.414 4.973a.75.75 0 0 0 .582.518l5.675 1.137a.25.25 0 0 1 0 .49L4.275 11.49a.75.75 0 0 0-.582.518l-1.414 4.973a.75.75 0 0 0 .826.95 19.397 19.397 0 0 0 13.79-9.34.75.75 0 0 0 0-.818A19.397 19.397 0 0 0 3.105 2.289Z" />
        </svg>
      </button>
    </div>
  );
}
