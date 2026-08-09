"use client";

import { useState, useCallback, useRef } from "react";

import type { ChatMessage, ChatRole } from "@/types/interview";

/** Incrementing counter for unique message ids. */
let nextId = 0;

/** Create a unique message id. */
function createId(): string {
  nextId += 1;
  return `msg-${nextId}`;
}

/** Mock AI responses to cycle through when the candidate sends a message. */
const MOCK_AI_RESPONSES = [
  "That's a great answer! Can you elaborate on how you would handle edge cases in that scenario?",
  "Interesting approach. How does this compare to alternative solutions you've considered?",
  "Good point. Let's move on — can you describe your experience with system design patterns?",
  "Well explained. What trade-offs would you consider when scaling this solution?",
  "Thanks for sharing that. Could you walk me through a time you applied this in a real project?",
] as const;

let mockResponseIndex = 0;

/**
 * Produce the next mock AI response.
 * Kept as a separate function so it can be replaced by a real API call later.
 */
function getMockResponse(): string {
  const response = MOCK_AI_RESPONSES[mockResponseIndex % MOCK_AI_RESPONSES.length];
  mockResponseIndex += 1;
  return response;
}

/** Delay in milliseconds before a mock AI response appears. */
const TYPING_DELAY_MS = 1200;

/** Initial mock messages so the interface is immediately visible. */
const INITIAL_MESSAGES: ChatMessage[] = [
  {
    id: createId(),
    role: "ai",
    content:
      "Welcome! I'll be conducting your technical interview today. Let's start — can you tell me about your background and experience?",
  },
  {
    id: createId(),
    role: "candidate",
    content:
      "Hi! I'm a software developer with three years of experience, primarily working with Python and JavaScript.",
  },
  {
    id: createId(),
    role: "ai",
    content:
      "Great to hear! Let's dive into some technical questions. Can you explain the difference between synchronous and asynchronous programming?",
  },
];

/** Return value of the useInterviewChat hook. */
export interface UseInterviewChatReturn {
  /** Current list of chat messages. */
  messages: ChatMessage[];
  /** Whether the AI is currently "typing" a response. */
  isAiTyping: boolean;
  /** Send a candidate message and trigger a mock AI response. */
  sendMessage: (content: string) => void;
  /** Ref to attach to the scroll anchor element at the bottom of the chat. */
  scrollAnchorRef: React.RefObject<HTMLDivElement | null>;
}

/**
 * Custom hook that manages interview chat state:
 * - Messages list
 * - AI typing indicator
 * - Mock AI responses on a delay
 * - Auto-scroll to the latest message
 */
export function useInterviewChat(): UseInterviewChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>(INITIAL_MESSAGES);
  const [isAiTyping, setIsAiTyping] = useState(false);
  const scrollAnchorRef = useRef<HTMLDivElement | null>(null);

  /** Scroll the conversation to the bottom. */
  const scrollToBottom = useCallback(() => {
    // Use requestAnimationFrame so the DOM has rendered the new content first.
    requestAnimationFrame(() => {
      scrollAnchorRef.current?.scrollIntoView({ behavior: "smooth" });
    });
  }, []);

  /** Add a message to the conversation. */
  const addMessage = useCallback(
    (role: ChatRole, content: string) => {
      const message: ChatMessage = { id: createId(), role, content };
      setMessages((prev) => [...prev, message]);
      scrollToBottom();
    },
    [scrollToBottom],
  );

  /** Send a candidate message and schedule a mock AI response. */
  const sendMessage = useCallback(
    (content: string) => {
      // Add the candidate message immediately.
      addMessage("candidate", content);

      // Show the typing indicator.
      setIsAiTyping(true);
      scrollToBottom();

      // Schedule the mock AI response.
      setTimeout(() => {
        const aiResponse = getMockResponse();
        setIsAiTyping(false);
        addMessage("ai", aiResponse);
      }, TYPING_DELAY_MS);
    },
    [addMessage, scrollToBottom],
  );

  return { messages, isAiTyping, sendMessage, scrollAnchorRef };
}
