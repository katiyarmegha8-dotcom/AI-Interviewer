import type { Metadata } from "next";

import {
  PlaceholderBlock,
  PlaceholderPanel,
} from "@/components/interview/PlaceholderPanel";
import { PageContainer } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/Button";

export const metadata: Metadata = {
  title: "Feedback",
  description: "Placeholder screen for post-interview feedback.",
};

export default function FeedbackPage() {
  return (
    <PageContainer>
      <div className="space-y-6">
        <div className="space-y-2">
          <h1 className="text-2xl font-bold tracking-tight text-content sm:text-3xl">
            Interview feedback
          </h1>
          <p className="text-sm text-content-muted sm:text-base">
            This screen will summarize performance after an interview. It is a
            placeholder until scoring and insights are implemented.
          </p>
        </div>

        <PlaceholderPanel
          title="Feedback summary"
          description="Scores, highlights, and improvement suggestions will be displayed here."
        >
          <PlaceholderBlock label="Overall score" height="sm" />
          <PlaceholderBlock label="Strengths & improvements" height="md" />
          <PlaceholderBlock label="Detailed notes" height="lg" />
        </PlaceholderPanel>

        <div className="flex flex-col gap-3 sm:flex-row">
          <Button href="/interview" variant="secondary">
            Back to interview
          </Button>
          <Button href="/">Return home</Button>
        </div>
      </div>
    </PageContainer>
  );
}
