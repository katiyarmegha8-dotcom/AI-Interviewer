"use client";

import { useState, useCallback, type KeyboardEvent } from "react";

type ChatInputProps = {
  /** Called when the candidate sends a non-empty message. */
  onSend: (content: string) => void;
  /** Whether the input should be disabled (e.g. while AI is typing). */
  disabled?: boolean;
};

/** Candidate message input with textarea and send button. */
export function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  const [value, setValue] = useState("");

  /** Send the current message if it's non-empty. */
  const handleSend = useCallback(() => {
    const trimmed = value.trim();
    if (trimmed.length === 0) return;
    onSend(trimmed);
    setValue("");
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
    <div className="flex items-end gap-2 border-t border-border bg-surface px-4 py-3 sm:gap-3 sm:px-6">
      <textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        placeholder="Type your answer…"
        rows={1}
        aria-label="Interview response input"
        className="flex-1 resize-none rounded-lg border border-border bg-surface-muted px-3 py-2.5 text-sm text-content placeholder:text-content-muted focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent disabled:cursor-not-allowed disabled:opacity-50 sm:text-base"
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
