/**
 * GLASS SELECT COMPONENT (Legacy)
 * 
 * This component is maintained for backward compatibility.
 * For new code, please use the unified Select component:
 * import { Select } from '@/components/unified';
 */

import * as React from "react"
import { cn } from "@/lib/utils"
import { ChevronDown } from "lucide-react"

export interface GlassSelectProps
    extends React.SelectHTMLAttributes<HTMLSelectElement> { }

const GlassSelect = React.forwardRef<HTMLSelectElement, GlassSelectProps>(
    ({ className, children, ...props }, ref) => {
        return (
            <div className="relative">
                <select
                    className={cn(
                        // Aligned with unified design system
                        "h-11 w-full appearance-none rounded-full",
                        "bg-white/5 backdrop-blur-sm",
                        "border border-white/10",
                        "px-6 pr-10 text-sm text-foreground",
                        "transition-all duration-300",
                        "hover:bg-white/10 hover:border-white/20",
                        "focus:outline-none focus:ring-1 focus:ring-white/20 focus:bg-white/10 focus:border-white/30",
                        "disabled:cursor-not-allowed disabled:opacity-50",
                        className
                    )}
                    ref={ref}
                    {...props}
                >
                    {children}
                </select>
                <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
            </div>
        )
    }
)
GlassSelect.displayName = "GlassSelect"

export default GlassSelect
