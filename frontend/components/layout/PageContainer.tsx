import type { ReactNode } from "react";

type PageContainerProps = {
  children: ReactNode;
  className?: string;
};

export function PageContainer({ children, className = "" }: PageContainerProps) {
  return (
    <div
      className={`mx-auto w-full max-w-3xl px-4 py-8 sm:px-6 sm:py-12 lg:px-8 ${className}`.trim()}
    >
      {children}
    </div>
  );
}
