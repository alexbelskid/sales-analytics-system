import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { ChevronDown } from "lucide-react"
import { cn } from "@/lib/utils"

/**
 * UNIFIED SELECT COMPONENT
 * 
 * Consolidates all select/dropdown styles into a single component.
 * Replaces: GlassSelect and inline select styles.
 */

const selectVariants = cva(
  [
    // Base styles
    "flex w-full items-center justify-between",
    "px-4 py-2",
    "text-sm text-foreground",
    "cursor-pointer appearance-none",
    "transition-all duration-300",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1",
    "disabled:cursor-not-allowed disabled:opacity-50",
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
      selectSize: {
        sm: "h-9 text-xs px-3 pr-8",
        md: "h-11 text-sm px-4 pr-10",
        lg: "h-13 text-base px-5 pr-12",
      },
    },
    defaultVariants: {
      variant: "glass",
      selectSize: "md",
    },
  }
)

export interface SelectProps
  extends Omit<React.ComponentProps<"select">, "size">,
    VariantProps<typeof selectVariants> {
  options?: Array<{ value: string; label: string }>
}

const UnifiedSelect = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, variant, selectSize, options, children, ...props }, ref) => {
    return (
      <div className="relative inline-block w-full">
        <select
          className={cn(selectVariants({ variant, selectSize }), className)}
          ref={ref}
          {...props}
        >
          {options
            ? options.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))
            : children}
        </select>
        <ChevronDown 
          className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-muted-foreground" 
          size={16}
        />
      </div>
    )
  }
)

UnifiedSelect.displayName = "UnifiedSelect"

export { UnifiedSelect, selectVariants }
