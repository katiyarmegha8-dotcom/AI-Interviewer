/** Animated dots to indicate the AI is composing a response. */
export function TypingIndicator() {
  return (
    <div className="flex justify-start" aria-label="AI is typing">
      <div className="flex items-center gap-1.5 rounded-xl rounded-tl-sm bg-accent/10 px-4 py-3">
        <span className="inline-block h-2 w-2 animate-bounce rounded-full bg-content-muted [animation-delay:0ms]" />
        <span className="inline-block h-2 w-2 animate-bounce rounded-full bg-content-muted [animation-delay:150ms]" />
        <span className="inline-block h-2 w-2 animate-bounce rounded-full bg-content-muted [animation-delay:300ms]" />
      </div>
    </div>
  );
}
