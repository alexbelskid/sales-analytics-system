/**
 * LIQUID BUTTON (Legacy)
 * 
 * This component is maintained for backward compatibility.
 * For new code, please use the unified Button component:
 * import { Button } from '@/components/unified';
 */

import React, { forwardRef } from 'react';
import { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LiquidButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    icon?: LucideIcon;
    variant?: 'primary' | 'secondary';
    children?: React.ReactNode;
}

const LiquidButton = forwardRef<HTMLButtonElement, LiquidButtonProps>(({
    className,
    children,
    icon: Icon,
    variant = 'primary',
    ...props
}, ref) => {
    return (
        <button
            ref={ref}
            className={cn(
                // Base styles - aligned with unified design system
                "relative flex items-center justify-center gap-2",
                "h-11 px-6 rounded-full group",
                "font-medium text-sm",
                "transition-all duration-300 ease-out",
                "active:scale-[0.98]",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
                "disabled:pointer-events-none disabled:opacity-50",

                // Variants - using design system colors
                variant === 'primary'
                    ? [
                        // Mercury/Metallic style (Primary)
                        "bg-gradient-to-b from-gray-100 to-gray-400",
                        "border border-white/40",
                        "shadow-[0_2px_10px_rgba(255,255,255,0.1),_inset_0_1px_0_rgba(255,255,255,0.5)]",
                        "text-black font-semibold",
                        "hover:brightness-110 hover:shadow-[0_0_20px_rgba(255,255,255,0.4)]"
                    ]
                    : [
                        // Glass style (Secondary)
                        "bg-white/5 backdrop-blur-sm",
                        "border border-white/10",
                        "text-white",
                        "hover:bg-white/10 hover:border-white/20"
                    ],

                className
            )}
            {...props}
        >
            {Icon && <Icon className={cn(
                "w-4 h-4 transition-transform group-hover:scale-110",
                variant === 'primary' ? "text-gray-800" : "text-gray-300"
            )} />}
            {children}
        </button>
    );
});

LiquidButton.displayName = "LiquidButton";

export default LiquidButton;
