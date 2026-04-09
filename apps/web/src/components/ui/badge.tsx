import { type HTMLAttributes } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-3 py-1 text-xs font-medium",
  {
    variants: {
      variant: {
        default: "bg-primary-light text-primary",
        secondary: "bg-secondary-light text-secondary",
        outline: "border border-border text-foreground",
        success: "bg-success-light text-success",
        warning: "bg-warning-light text-warning",
        info: "bg-info-light text-info",
        destructive: "bg-destructive-light text-destructive",
        "match-excellent": "bg-match-excellent text-white",
        "match-good": "bg-match-good text-white",
        "match-moderate": "bg-match-moderate text-white",
        "match-low": "bg-match-low text-white",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant, className }))} {...props} />
  );
}

export { Badge, badgeVariants };
