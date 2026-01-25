import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { LucideIcon } from 'lucide-react';
import { cn } from "@/lib/utils"

/**
 * UNIFIED BUTTON COMPONENT
 * 
 * Consolidates all button styles into a single, consistent component.
 * Replaces: LiquidButton, Button (shadcn), and inline button classes.
 */

const buttonVariants = cva(
  // Base styles - Applied to all buttons
  [
    "relative inline-flex items-center justify-center gap-2",
    "font-medium whitespace-nowrap",
    "transition-all duration-300 ease-out",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
    "disabled:pointer-events-none disabled:opacity-50",
    "active:scale-[0.98]",
    "[&_svg]:pointer-events-none [&_svg]:shrink-0"
  ],
  {
    variants: {
      variant: {
        // Primary - Mercury/Metallic style (main CTAs)
        primary: [
          "bg-gradient-to-b from-gray-100 to-gray-400",
          "border border-white/40",
          "text-black font-semibold",
          "shadow-[0_2px_10px_rgba(255,255,255,0.1),_inset_0_1px_0_rgba(255,255,255,0.5)]",
          "hover:brightness-110 hover:shadow-[0_0_20px_rgba(255,255,255,0.4)]",
        ],
        
        // Secondary - Glass style (secondary actions)
        secondary: [
          "bg-white/5 backdrop-blur-sm",
          "border border-white/10",
          "text-white",
          "hover:bg-white/10 hover:border-white/20",
        ],
        
        // Accent - Brand color (important actions)
        accent: [
          "bg-[hsl(var(--brand-primary))]",
          "border border-[hsl(var(--brand-primary))]",
          "text-white font-semibold",
          "hover:bg-[hsl(var(--brand-primary-hover))]",
          "shadow-lg shadow-[hsl(var(--brand-primary))]/20",
        ],
        
        // Ghost - Minimal style (tertiary actions)
        ghost: [
          "border-transparent",
          "text-white",
          "hover:bg-white/10",
        ],
        
        // Destructive - For delete/remove actions
        destructive: [
          "bg-[hsl(var(--destructive))]",
          "border border-[hsl(var(--destructive))]",
          "text-white font-semibold",
          "hover:opacity-90",
          "shadow-lg shadow-[hsl(var(--destructive))]/20",
        ],
        
        // Outline - Bordered style
        outline: [
          "border border-border",
          "bg-transparent",
          "text-white",
          "hover:bg-white/5 hover:border-white/20",
        ],
        
        // Link - Text only
        link: [
          "text-white underline-offset-4",
          "hover:underline",
          "border-transparent",
        ],
      },
      
      size: {
        sm: "h-9 px-4 text-xs rounded-full [&_svg]:size-3",
        md: "h-11 px-6 text-sm rounded-full [&_svg]:size-4", // Default: 44px height
        lg: "h-13 px-8 text-base rounded-full [&_svg]:size-5",
        icon: "h-11 w-11 rounded-full p-0 [&_svg]:size-5", // Square button for icons only
        "icon-sm": "h-9 w-9 rounded-full p-0 [&_svg]:size-4",
      },
      
      fullWidth: {
        true: "w-full",
        false: "",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
      fullWidth: false,
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
  icon?: LucideIcon
  iconPosition?: "left" | "right"
}

const UnifiedButton = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    className, 
    variant, 
    size, 
    fullWidth,
    asChild = false, 
    icon: Icon,
    iconPosition = "left",
    children,
    ...props 
  }, ref) => {
    const Comp = asChild ? Slot : "button"
    
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, fullWidth, className }))}
        ref={ref}
        {...props}
      >
        {Icon && iconPosition === "left" && <Icon />}
        {children}
        {Icon && iconPosition === "right" && <Icon />}
      </Comp>
    )
  }
)

UnifiedButton.displayName = "UnifiedButton"

export { UnifiedButton, buttonVariants }
