import React from 'react';
import { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface GlassInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
    icon?: LucideIcon;
}

export default function GlassInput({
    className,
    icon: Icon,
    ...props
}: GlassInputProps) {
    return (
        <div className="relative group w-full">
            {Icon && (
                <Icon className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500 group-focus-within:text-gray-200 transition-colors duration-300 z-10" />
            )}
            <input
                className={cn(
                    // Base Background & Border
                    "bg-[#050505]/60 border border-gray-800",

                    // Shape (Capsule to match LiquidButton)
                    "rounded-full w-full h-11",

                    // Text
                    "text-gray-100 placeholder:text-gray-600 text-sm",

                    // Shadow (Engraved/Sunken effect)
                    "shadow-[inset_0_2px_4px_rgba(0,0,0,0.5)]",

                    // Transitions
                    "transition-all duration-300",

                    // Focus State
                    "focus:border-gray-600 focus:ring-1 focus:ring-gray-600/50 focus:bg-gray-900/80 focus:outline-none",

                    // Padding (adjust for icon)
                    Icon ? "pl-11 pr-4" : "px-4",

                    className
                )}
                {...props}
            />
        </div>
    );
}
