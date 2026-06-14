import { cn } from "@/lib/utils";

type StatusBadgeProps = {
  label: string;
  variant?: "default" | "success" | "warning" | "danger" | "info";
  className?: string;
};

const variantStyles: Record<NonNullable<StatusBadgeProps["variant"]>, string> = {
  default: "border-border bg-surface text-text-secondary",
  success: "border-success/30 bg-success/10 text-success",
  warning: "border-warning/30 bg-warning/10 text-warning",
  danger: "border-destructive/30 bg-destructive/10 text-destructive",
  info: "border-primary/30 bg-primary/10 text-primary",
};

export function StatusBadge({
  label,
  variant = "default",
  className,
}: StatusBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium",
        variantStyles[variant],
        className,
      )}
    >
      {label}
    </span>
  );
}
