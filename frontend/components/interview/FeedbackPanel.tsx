import type { InterviewFeedback } from "@/types/interview";

type FeedbackPanelProps = {
  feedback: InterviewFeedback;
};

/** Renders structured interview feedback with distinct sections. */
export function FeedbackPanel({ feedback }: FeedbackPanelProps) {
  return (
    <div className="rounded-xl border border-accent/30 bg-accent/5 p-5 sm:p-6">
      <h2 className="text-lg font-semibold text-content sm:text-xl">
        Interview Feedback
      </h2>

      {/* Summary */}
      <div className="mt-4">
        <h3 className="text-sm font-medium uppercase tracking-wide text-content-muted">
          Summary
        </h3>
        <p className="mt-1 whitespace-pre-wrap text-sm leading-relaxed text-content sm:text-base">
          {feedback.summary}
        </p>
      </div>

      {/* Strengths */}
      {feedback.strengths.length > 0 && (
        <div className="mt-4">
          <h3 className="text-sm font-medium uppercase tracking-wide text-content-muted">
            Strengths
          </h3>
          <ul className="mt-1 list-inside list-disc space-y-1">
            {feedback.strengths.map((item, i) => (
              <li
                key={i}
                className="text-sm leading-relaxed text-content sm:text-base"
              >
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Gaps */}
      {feedback.gaps.length > 0 && (
        <div className="mt-4">
          <h3 className="text-sm font-medium uppercase tracking-wide text-content-muted">
            Areas to Improve
          </h3>
          <ul className="mt-1 list-inside list-disc space-y-1">
            {feedback.gaps.map((item, i) => (
              <li
                key={i}
                className="text-sm leading-relaxed text-content sm:text-base"
              >
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommended next steps */}
      {feedback.next.length > 0 && (
        <div className="mt-4">
          <h3 className="text-sm font-medium uppercase tracking-wide text-content-muted">
            Recommended Next Steps
          </h3>
          <ul className="mt-1 list-inside list-disc space-y-1">
            {feedback.next.map((item, i) => (
              <li
                key={i}
                className="text-sm leading-relaxed text-content sm:text-base"
              >
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
