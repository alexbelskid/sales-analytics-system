/**
 * BUTTON COMPONENT (Legacy - Shadcn)
 * 
 * This component is maintained for backward compatibility.
 * For new code, please use the unified Button component:
 * import { Button } from '@/components/unified';
 */

import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  // Updated to align with unified design system
  [
    "inline-flex items-center justify-center gap-2",
    "whitespace-nowrap font-medium",
    "rounded-full transition-all duration-300",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
    "disabled:pointer-events-none disabled:opacity-50",
    "active:scale-[0.98]",
    "[&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0"
  ],
  {
    variants: {
      variant: {
        default: [
          "bg-gradient-to-b from-gray-100 to-gray-400",
          "border border-white/40",
          "text-black font-semibold",
          "shadow-[0_2px_10px_rgba(255,255,255,0.1)]",
          "hover:brightness-110"
        ],
        destructive: [
          "bg-[hsl(var(--destructive))] text-white",
          "hover:opacity-90"
        ],
        outline: [
          "border border-border bg-transparent text-white",
          "hover:bg-white/10"
        ],
        secondary: [
          "bg-white/5 backdrop-blur-sm border border-white/10 text-white",
          "hover:bg-white/10"
        ],
        ghost: [
          "text-white hover:bg-white/10"
        ],
        link: [
          "text-white underline-offset-4 hover:underline"
        ],
      },
      size: {
        default: "h-11 px-6 text-sm",
        sm: "h-9 px-4 text-xs",
        lg: "h-13 px-8 text-base",
        icon: "h-11 w-11",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
