/** Animated dots to indicate the AI is composing a response. */
export function TypingIndicator() {
  return (
    <div
      className="flex justify-start"
      aria-label="AI is typing a response"
      role="status"
    >
      <div className="flex items-center gap-1.5 rounded-xl rounded-tl-sm bg-accent/10 px-4 py-3">
        <span className="mb-1 text-[11px] font-medium uppercase tracking-wider text-accent">
          Interviewer
        </span>
        <span
          className="inline-block h-1.5 w-1.5 rounded-full bg-accent"
          style={{ animation: "typing-dot 1.4s ease-in-out infinite", animationDelay: "0ms" }}
        />
        <span
          className="inline-block h-1.5 w-1.5 rounded-full bg-accent"
          style={{ animation: "typing-dot 1.4s ease-in-out infinite", animationDelay: "200ms" }}
        />
        <span
          className="inline-block h-1.5 w-1.5 rounded-full bg-accent"
          style={{ animation: "typing-dot 1.4s ease-in-out infinite", animationDelay: "400ms" }}
        />
      </div>
    </div>
  );
}
