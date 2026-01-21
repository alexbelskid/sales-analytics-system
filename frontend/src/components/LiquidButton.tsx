import React from 'react';
import { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LiquidButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    icon?: LucideIcon;
    variant?: 'primary' | 'secondary';
    children: React.ReactNode;
}

export default function LiquidButton({
    className,
    children,
    icon: Icon,
    variant = 'primary',
    ...props
}: LiquidButtonProps) {
    return (
        <button
            className={cn(
                // MANDATORY SHAPE & SIZE
                "relative flex items-center justify-center gap-2",
                "h-11 px-6 rounded-full group", // Capsure shape, Fixed height (44px)

                // TYPOGRAPHY
                "font-medium text-[14px] tracking-wide uppercase",

                // TRANSITIONS
                "transition-all duration-300 ease-out",
                "active:scale-[0.98]",

                // VARIANTS
                variant === 'primary'
                    ? [
                        // MERCURY SKIN
                        "bg-gradient-to-b from-gray-100 to-gray-400",
                        "border border-white/40",
                        "shadow-[0_2px_10px_rgba(255,255,255,0.1),_inset_0_1px_0_rgba(255,255,255,0.5)]",
                        "text-black",
                        "hover:brightness-110 hover:shadow-[0_0_20px_rgba(255,255,255,0.4)]"
                    ]
                    : [
                        // GLASS SKIN (Secondary)
                        "bg-white/5",
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
            {children && <span>{children}</span>}
        </button>
    );
}
