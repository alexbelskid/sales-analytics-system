'use client';

import { Sparkles, Menu } from 'lucide-react';

interface MobileHeaderProps {
    onMenuClick: () => void;
}

export default function MobileHeader({ onMenuClick }: MobileHeaderProps) {
    return (
        <header className="lg:hidden sticky top-0 z-30 flex h-14 items-center justify-between border-b border-[#2A2A2A] bg-[#0A0A0A]/95 backdrop-blur-sm px-4">
            {/* Burger Menu Button */}
            <button
                onClick={onMenuClick}
                className="p-2 rounded-lg bg-[#1A1A1A] border border-[#2A2A2A] text-[#808080] hover:text-white active:bg-[#2A2A2A] transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
                aria-label="Открыть меню"
            >
                <Menu size={20} />
            </button>

            {/* Logo */}
            <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-white" />
                <span className="text-lg font-bold text-white">Alterini AI</span>
            </div>

            {/* Spacer for centering logo */}
            <div className="w-[44px]" />
        </header>
    );
}
