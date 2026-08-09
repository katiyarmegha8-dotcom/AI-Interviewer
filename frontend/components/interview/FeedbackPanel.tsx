import type { InterviewFeedback } from "@/types/interview";

type FeedbackPanelProps = {
  feedback: InterviewFeedback;
};

/** Checkmark icon for strengths. */
function CheckIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 16 16"
      fill="currentColor"
      className="h-4 w-4 flex-shrink-0 text-emerald-600"
      aria-hidden="true"
    >
      <path
        fillRule="evenodd"
        d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14Zm3.844-8.791a.75.75 0 0 0-1.188-.918l-3.7 4.79-1.258-1.307a.75.75 0 0 0-1.09 1.03l1.82 1.89a.75.75 0 0 0 1.14-.054l4.076-5.27Z"
        clipRule="evenodd"
      />
    </svg>
  );
}

/** X icon for gaps/improvements. */
function GapIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 16 16"
      fill="currentColor"
      className="h-4 w-4 flex-shrink-0 text-amber-600"
      aria-hidden="true"
    >
      <path
        fillRule="evenodd"
        d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14ZM6.47 5.22a.75.75 0 0 1 1.06 0L8 5.69l.47-.47a.75.75 0 1 1 1.06 1.06l-.47.47.47.47a.75.75 0 1 1-1.06 1.06L8 8.81l-.47.47a.75.75 0 1 1-1.06-1.06l.47-.47-.47-.47a.75.75 0 0 1 0-1.06Z"
        clipRule="evenodd"
      />
    </svg>
  );
}

/** Arrow icon for next steps. */
function NextIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 16 16"
      fill="currentColor"
      className="h-4 w-4 flex-shrink-0 text-accent"
      aria-hidden="true"
    >
      <path
        fillRule="evenodd"
        d="M6.22 4.22a.75.75 0 0 1 1.06 0l3.25 3.25a.75.75 0 0 1 0 1.06l-3.25 3.25a.75.75 0 0 1-1.06-1.06L8.94 8 6.22 5.28a.75.75 0 0 1 0-1.06Z"
        clipRule="evenodd"
      />
    </svg>
  );
}

/** Renders structured interview feedback with distinct sections. */
export function FeedbackPanel({ feedback }: FeedbackPanelProps) {
  return (
    <div
      className="rounded-xl border border-accent/20 bg-gradient-to-br from-accent/5 to-accent/[0.02] p-5 sm:p-6"
      aria-label="Interview feedback"
    >
      <div className="mb-5 flex items-center gap-2 border-b border-accent/10 pb-4">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
          className="h-5 w-5 text-accent"
          aria-hidden="true"
        >
          <path
            fillRule="evenodd"
            d="M10 1a.75.75 0 0 1 .75.75v5.562l2.606-1.506a.75.75 0 1 1 .788 1.288L10.75 8.88V10a.75.75 0 0 1-1.5 0V8.88L5.856 7.094a.75.75 0 0 1 .788-1.288L9.25 7.312V1.75A.75.75 0 0 1 10 1ZM5.06 8.982a.75.75 0 0 1 .292.892A6.48 6.48 0 0 0 5 11.5a6.48 6.48 0 0 0 6.48 6.48 6.48 6.48 0 0 0 6.48-6.48 6.48 6.48 0 0 0-.352-1.626.75.75 0 1 1 1.396-.546A7.98 7.98 0 0 1 19 11.5 7.98 7.98 0 0 1 11.5 19 7.98 7.98 0 0 1 3.5 11.5a7.98 7.98 0 0 1 .546-2.898.75.75 0 0 1 1.014-.62Z"
            clipRule="evenodd"
          />
        </svg>
        <h2 className="text-base font-semibold text-content sm:text-lg">
          Interview Feedback
        </h2>
      </div>

      {/* Summary */}
      <div className="mb-5">
        <h3 className="mb-1.5 text-xs font-semibold uppercase tracking-wider text-content-muted">
          Summary
        </h3>
        <p className="whitespace-pre-wrap text-sm leading-relaxed text-content sm:text-base">
          {feedback.summary}
        </p>
      </div>

      {/* Strengths */}
      {feedback.strengths.length > 0 && (
        <div className="mb-5">
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-content-muted">
            Strengths
          </h3>
          <ul className="space-y-1.5" role="list">
            {feedback.strengths.map((item, i) => (
              <li key={i} className="flex items-start gap-2 text-sm leading-relaxed text-content sm:text-base" role="listitem">
                <span className="mt-0.5"><CheckIcon /></span>
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Gaps */}
      {feedback.gaps.length > 0 && (
        <div className="mb-5">
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-content-muted">
            Areas to Improve
          </h3>
          <ul className="space-y-1.5" role="list">
            {feedback.gaps.map((item, i) => (
              <li key={i} className="flex items-start gap-2 text-sm leading-relaxed text-content sm:text-base" role="listitem">
                <span className="mt-0.5"><GapIcon /></span>
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommended next steps */}
      {feedback.next.length > 0 && (
        <div>
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-content-muted">
            Recommended Next Steps
          </h3>
          <ul className="space-y-1.5" role="list">
            {feedback.next.map((item, i) => (
              <li key={i} className="flex items-start gap-2 text-sm leading-relaxed text-content sm:text-base" role="listitem">
                <span className="mt-0.5"><NextIcon /></span>
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
