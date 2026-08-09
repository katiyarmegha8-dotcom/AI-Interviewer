"use client";

import { useEffect, type RefObject } from "react";

import type { ChatMessage } from "@/types/interview";

import { ChatMessage as ChatMessageBubble } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
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
};

/** Full interview chat interface: message list + typing indicator + input. */
export function ChatContainer({
  messages,
  isAiTyping,
  onSendMessage,
  scrollAnchorRef,
}: ChatContainerProps) {
  // Auto-scroll whenever messages change or typing state changes.
  useEffect(() => {
    scrollAnchorRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isAiTyping, scrollAnchorRef]);

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-xl border border-border bg-surface">
      {/* Conversation area */}
      <div className="flex-1 overflow-y-auto px-4 py-4 sm:px-6">
        <div className="space-y-3">
          {messages.map((msg) => (
            <ChatMessageBubble key={msg.id} message={msg} />
          ))}
          {isAiTyping && <TypingIndicator />}
          {/* Scroll anchor — always at the bottom of the conversation. */}
          <div ref={scrollAnchorRef} />
        </div>
      </div>

      {/* Input area */}
      <ChatInput onSend={onSendMessage} disabled={isAiTyping} />
    </div>
  );
}
