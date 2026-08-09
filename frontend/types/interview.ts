/** Chat message role – who sent the message. */
export type ChatRole = "ai" | "candidate";

/** A single message in the interview conversation. */
export interface ChatMessage {
  /** Unique message identifier. */
  id: string;
  /** Who sent this message. */
  role: ChatRole;
  /** The message text content. */
  content: string;
}
