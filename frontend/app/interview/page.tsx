"use client";

import { useInterviewChat } from "@/hooks/useInterviewChat";
import { ChatContainer } from "@/components/interview/ChatContainer";

export default function InterviewPage() {
  const {
    messages,
    isAiTyping,
    sendMessage,
    scrollAnchorRef,
    isInterviewDone,
    endInterview,
    feedback,
    error,
    dismissError,
    startNewInterview,
    isStarting,
  } = useInterviewChat();

  return (
    <div className="mx-auto flex h-[calc(100dvh-5rem)] w-full max-w-3xl flex-col px-3 py-3 sm:h-[calc(100dvh-6rem)] sm:px-5 sm:py-4 lg:px-8">
      {/* Header */}
      <div className="mb-2 flex-shrink-0 sm:mb-3">
        <h1 className="text-lg font-bold tracking-tight text-content sm:text-xl">
          Interview
        </h1>
        <p className="mt-0.5 text-xs leading-relaxed text-content-muted sm:text-sm">
          {isInterviewDone
            ? "Interview completed — review your feedback below."
            : isStarting
              ? "Connecting to the interviewer…"
              : "Answer the interviewer\u2019s questions to practice your skills."}
        </p>
      </div>

      {/* Chat fills the remaining space */}
      <div className="min-h-0 flex-1">
        <ChatContainer
          messages={messages}
          isAiTyping={isAiTyping}
          onSendMessage={sendMessage}
          scrollAnchorRef={scrollAnchorRef}
          isInterviewDone={isInterviewDone}
          onEndInterview={endInterview}
          feedback={feedback}
          error={error}
          onDismissError={dismissError}
          onStartNewInterview={startNewInterview}
          isStarting={isStarting}
        />
      </div>
    </div>
  );
}
