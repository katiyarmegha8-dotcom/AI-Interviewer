import type { ReactNode } from "react";

type PlaceholderPanelProps = {
  title: string;
  description: string;
  children?: ReactNode;
};

export function PlaceholderPanel({
  title,
  description,
  children,
}: PlaceholderPanelProps) {
  return (
    <section className="rounded-xl border border-dashed border-border bg-surface p-6 sm:p-8">
      <h2 className="text-xl font-semibold text-content sm:text-2xl">{title}</h2>
      <p className="mt-2 text-sm leading-relaxed text-content-muted sm:text-base">
        {description}
      </p>
      {children ? <div className="mt-6 space-y-4">{children}</div> : null}
    </section>
  );
}

type PlaceholderBlockProps = {
  label: string;
  height?: "sm" | "md" | "lg";
};

const heightStyles = {
  sm: "h-20",
  md: "h-32",
  lg: "h-40",
} as const;

export function PlaceholderBlock({ label, height = "md" }: PlaceholderBlockProps) {
  return (
    <div
      aria-hidden="true"
      className={`flex items-center justify-center rounded-lg border border-border bg-surface-muted ${heightStyles[height]}`}
    >
      <span className="text-xs font-medium uppercase tracking-wide text-content-muted">
        {label}
      </span>
    </div>
  );
}
