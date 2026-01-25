/**
 * GLASS INPUT COMPONENT (Legacy)
 * 
 * This component is maintained for backward compatibility.
 * For new code, please use the unified Input component:
 * import { Input } from '@/components/unified';
 */

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
                <Icon className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground group-focus-within:text-foreground-secondary transition-colors duration-300 z-10" />
            )}
            <input
                className={cn(
                    // Aligned with unified design system
                    "h-11 w-full rounded-full",
                    "bg-white/5 backdrop-blur-sm",
                    "border border-white/10",
                    "text-foreground placeholder:text-muted-foreground text-sm",
                    "shadow-[inset_0_2px_4px_rgba(0,0,0,0.3)]",
                    "transition-all duration-300",
                    "hover:bg-white/10 hover:border-white/20",
                    "focus:border-white/30 focus:ring-1 focus:ring-white/20 focus:bg-white/10 focus:outline-none",
                    // Padding (adjust for icon)
                    Icon ? "pl-11 pr-4" : "px-4",
                    className
                )}
                {...props}
            />
        </div>
    );
}
