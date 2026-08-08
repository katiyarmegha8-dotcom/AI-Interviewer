import { PageContainer } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/Button";

export default function HomePage() {
  return (
    <PageContainer>
      <div className="space-y-8">
        <div className="space-y-4">
          <p className="text-sm font-medium uppercase tracking-wide text-accent">
            Hackathon prototype
          </p>
          <h1 className="text-3xl font-bold tracking-tight text-content sm:text-4xl lg:text-5xl">
            Practice interviews with an AI agent
          </h1>
          <p className="max-w-2xl text-base leading-relaxed text-content-muted sm:text-lg">
            AI Interview Agent helps you rehearse real interview conversations,
            receive structured feedback, and improve with every session.
          </p>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <Button href="/interview">Start interview</Button>
          <Button href="/feedback" variant="secondary">
            View feedback preview
          </Button>
        </div>

        <div className="grid gap-4 sm:grid-cols-3">
          {[
            {
              title: "Simulated interview",
              description: "Walk through a guided interview experience.",
            },
            {
              title: "Thoughtful prompts",
              description: "Answer questions in a focused, distraction-free flow.",
            },
            {
              title: "Actionable feedback",
              description: "Review strengths and areas to improve afterward.",
            },
          ].map((item) => (
            <article
              key={item.title}
              className="rounded-xl border border-border bg-surface p-5"
            >
              <h2 className="text-base font-semibold text-content">{item.title}</h2>
              <p className="mt-2 text-sm leading-relaxed text-content-muted">
                {item.description}
              </p>
            </article>
          ))}
        </div>
      </div>
    </PageContainer>
  );
}
