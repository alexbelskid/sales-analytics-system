import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

/**
 * UNIFIED INPUT COMPONENT
 * 
 * Consolidates all input styles into a single, consistent component.
 * Replaces: Input (shadcn), GlassInput, and inline input styles.
 */

const inputVariants = cva(
  [
    // Base styles
    "flex w-full items-center",
    "px-4 py-2",
    "text-sm text-foreground",
    "placeholder:text-muted-foreground",
    "transition-all duration-300",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1",
    "disabled:cursor-not-allowed disabled:opacity-50",
    "file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground",
  ],
  {
    variants: {
      variant: {
        default: [
          "bg-input/50 backdrop-blur-sm",
          "border border-border",
          "rounded-2xl",
          "hover:border-border-emphasis",
          "focus:border-ring focus:bg-input/70",
        ],
        glass: [
          "bg-white/5 backdrop-blur-md",
          "border border-white/10",
          "rounded-2xl",
          "hover:bg-white/10 hover:border-white/20",
          "focus:bg-white/10 focus:border-white/30",
        ],
        flat: [
          "bg-card",
          "border border-border",
          "rounded-lg",
          "hover:border-border-emphasis",
          "focus:border-ring",
        ],
      },
      inputSize: {
        sm: "h-9 text-xs px-3",
        md: "h-11 text-sm px-4",
        lg: "h-13 text-base px-5",
      },
    },
    defaultVariants: {
      variant: "glass",
      inputSize: "md",
    },
  }
)

export interface InputProps
  extends Omit<React.ComponentProps<"input">, "size">,
    VariantProps<typeof inputVariants> {}

const UnifiedInput = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, variant, inputSize, type = "text", ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(inputVariants({ variant, inputSize }), className)}
        ref={ref}
        {...props}
      />
    )
  }
)

UnifiedInput.displayName = "UnifiedInput"

export { UnifiedInput, inputVariants }
