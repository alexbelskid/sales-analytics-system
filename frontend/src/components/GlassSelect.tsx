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
                        // COMPLIANCE: Capsule Regime
                        "h-11 w-full appearance-none rounded-full bg-white/5 border border-white/10 px-6 pr-10 text-sm text-gray-100 transition-colors",
                        "focus:outline-none focus:ring-1 focus:ring-white/20 focus:bg-white/10",
                        "disabled:cursor-not-allowed disabled:opacity-50",
                        className
                    )}
                    ref={ref}
                    {...props}
                >
                    {children}
                </select>
                <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
            </div>
        )
    }
)
GlassSelect.displayName = "GlassSelect"

export default GlassSelect
