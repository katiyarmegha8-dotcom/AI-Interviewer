import Link from "next/link";
import type { ComponentPropsWithoutRef } from "react";

type ButtonVariant = "primary" | "secondary" | "ghost";

const variantStyles: Record<ButtonVariant, string> = {
  primary:
    "bg-accent text-white hover:bg-accent-hover focus-visible:ring-accent",
  secondary:
    "border border-border bg-surface text-content hover:bg-surface-muted focus-visible:ring-content-muted",
  ghost:
    "text-content-muted hover:bg-surface hover:text-content focus-visible:ring-content-muted",
};

type BaseProps = {
  variant?: ButtonVariant;
  className?: string;
};

type ButtonAsButton = BaseProps &
  ComponentPropsWithoutRef<"button"> & {
    href?: undefined;
  };

type ButtonAsLink = BaseProps &
  Omit<ComponentPropsWithoutRef<typeof Link>, "className"> & {
    href: string;
  };

type ButtonProps = ButtonAsButton | ButtonAsLink;

const baseStyles =
  "inline-flex items-center justify-center rounded-lg px-4 py-2.5 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50";

export function Button({
  variant = "primary",
  className = "",
  ...props
}: ButtonProps) {
  const classes = `${baseStyles} ${variantStyles[variant]} ${className}`.trim();

  if ("href" in props && props.href) {
    const { href, ...linkProps } = props;
    return <Link href={href} className={classes} {...linkProps} />;
  }

  return <button className={classes} {...props} />;
}
