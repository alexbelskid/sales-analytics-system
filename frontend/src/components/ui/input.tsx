/**
 * INPUT COMPONENT (Legacy)
 * 
 * This component is maintained for backward compatibility.
 * For new code, please use the unified Input component:
 * import { Input } from '@/components/unified';
 */

import * as React from "react"
import { cn } from "@/lib/utils"

const Input = React.forwardRef<HTMLInputElement, React.ComponentProps<"input">>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          // Aligned with unified design system
          "flex h-11 w-full items-center",
          "px-4 py-2 rounded-2xl",
          "text-sm text-foreground",
          "bg-white/5 backdrop-blur-sm",
          "border border-white/10",
          "transition-all duration-300",
          "placeholder:text-muted-foreground",
          "hover:bg-white/10 hover:border-white/20",
          "focus:bg-white/10 focus:border-white/30",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1",
          "disabled:cursor-not-allowed disabled:opacity-50",
          "file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"

export { Input }
