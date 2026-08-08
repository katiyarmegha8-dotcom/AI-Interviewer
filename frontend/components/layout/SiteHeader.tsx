import Link from "next/link";

const navItems = [
  { href: "/", label: "Home" },
  { href: "/interview", label: "Interview" },
  { href: "/feedback", label: "Feedback" },
] as const;

export function SiteHeader() {
  return (
    <header className="border-b border-border bg-surface">
      <div className="mx-auto flex max-w-5xl flex-col gap-4 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
        <Link href="/" className="text-lg font-semibold tracking-tight text-content">
          AI Interview Agent
        </Link>

        <nav aria-label="Main navigation">
          <ul className="flex flex-wrap gap-1 sm:gap-2">
            {navItems.map(({ href, label }) => (
              <li key={href}>
                <Link
                  href={href}
                  className="rounded-md px-3 py-2 text-sm font-medium text-content-muted transition-colors hover:bg-surface-muted hover:text-content"
                >
                  {label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </div>
    </header>
  );
}
