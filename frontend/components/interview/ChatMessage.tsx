import type { ChatMessage as ChatMessageType } from "@/types/interview";

type ChatMessageProps = {
  message: ChatMessageType;
};

/** AI message bubble — left-aligned with accent background. */
function AiBubble({ content }: { content: string }) {
  return (
    <div className="flex justify-start">
      <div className="max-w-[80%] rounded-xl rounded-tl-sm bg-accent/10 px-4 py-3 sm:max-w-[70%]">
        <p className="whitespace-pre-wrap text-sm leading-relaxed text-content sm:text-base">
          {content}
        </p>
      </div>
    </div>
  );
}

/** Candidate message bubble — right-aligned with surface background. */
function CandidateBubble({ content }: { content: string }) {
  return (
    <div className="flex justify-end">
      <div className="max-w-[80%] rounded-xl rounded-tr-sm border border-border bg-surface px-4 py-3 sm:max-w-[70%]">
        <p className="whitespace-pre-wrap text-sm leading-relaxed text-content sm:text-base">
          {content}
        </p>
      </div>
    </div>
  );
}

/** Renders a single chat message with role-appropriate styling. */
export function ChatMessage({ message }: ChatMessageProps) {
  if (message.role === "ai") {
    return <AiBubble content={message.content} />;
  }
  return <CandidateBubble content={message.content} />;
}
