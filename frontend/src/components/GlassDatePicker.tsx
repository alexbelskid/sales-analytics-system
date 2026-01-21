import * as React from "react"
import { cn } from "@/lib/utils"
import { Calendar as CalendarIcon } from "lucide-react"

export interface GlassDatePickerProps
    extends React.InputHTMLAttributes<HTMLInputElement> { }

const GlassDatePicker = React.forwardRef<HTMLInputElement, GlassDatePickerProps>(
    ({ className, ...props }, ref) => {
        return (
            <div className="relative">
                <input
                    type="date"
                    className={cn(
                        // COMPLIANCE: Capsule Regime
                        "h-11 w-full appearance-none rounded-full bg-white/5 border border-white/10 px-6 pl-10 text-sm text-gray-100 transition-colors uppercase tracking-wide",
                        "focus:outline-none focus:ring-1 focus:ring-white/20 focus:bg-white/10",
                        "disabled:cursor-not-allowed disabled:opacity-50",
                        // FORCE DARK MODE for native picker
                        "[color-scheme:dark]",
                        className
                    )}
                    ref={ref}
                    {...props}
                />
                <CalendarIcon className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
            </div>
        )
    }
)
GlassDatePicker.displayName = "GlassDatePicker"

export default GlassDatePicker
