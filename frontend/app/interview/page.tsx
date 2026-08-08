import type { Metadata } from "next";

import {
  PlaceholderBlock,
  PlaceholderPanel,
} from "@/components/interview/PlaceholderPanel";
import { PageContainer } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/Button";

export const metadata: Metadata = {
  title: "Interview",
  description: "Placeholder screen for the AI interview experience.",
};

export default function InterviewPage() {
  return (
    <PageContainer>
      <div className="space-y-6">
        <div className="space-y-2">
          <h1 className="text-2xl font-bold tracking-tight text-content sm:text-3xl">
            Interview
          </h1>
          <p className="text-sm text-content-muted sm:text-base">
            This screen will host the live interview flow. For now, it shows the
            layout areas we plan to build.
          </p>
        </div>

        <PlaceholderPanel
          title="Interview session"
          description="Question prompts, answer input, and session controls will appear here in a later milestone."
        >
          <PlaceholderBlock label="Question area" height="md" />
          <PlaceholderBlock label="Answer input" height="lg" />
          <PlaceholderBlock label="Session controls" height="sm" />
        </PlaceholderPanel>

        <div className="flex flex-col gap-3 sm:flex-row">
          <Button href="/feedback">Continue to feedback</Button>
          <Button href="/" variant="secondary">
            Back to home
          </Button>
        </div>
      </div>
    </PageContainer>
  );
}
