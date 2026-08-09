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
    <div className="mx-auto flex h-[calc(100vh-8rem)] w-full max-w-3xl flex-col px-4 py-4 sm:px-6 sm:py-6 lg:px-8">
      {/* Header */}
      <div className="mb-3 flex-shrink-0 sm:mb-4">
        <h1 className="text-xl font-bold tracking-tight text-content sm:text-2xl">
          Interview
        </h1>
        <p className="mt-1 text-xs text-content-muted sm:text-sm">
          {isInterviewDone
            ? "Interview completed — see your feedback below."
            : "Respond to the AI interviewer\u2019s questions below."}
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
