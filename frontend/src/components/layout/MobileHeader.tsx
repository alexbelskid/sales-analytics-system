'use client';

import { Menu } from 'lucide-react';
import Image from 'next/image';

interface MobileHeaderProps {
    onMenuClick: () => void;
}

export default function MobileHeader({ onMenuClick }: MobileHeaderProps) {
    return (
        <header className="lg:hidden sticky top-0 z-30 flex h-14 items-center justify-between border-b border-[#333333] bg-[#202020]/95 backdrop-blur-sm px-4">
            {/* Burger Menu Button */}
            <button
                onClick={onMenuClick}
                className="p-2 rounded-lg bg-[#262626] border border-[#333333] text-[#808080] hover:text-white active:bg-[#333333] transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
                aria-label="Открыть меню"
            >
                <Menu size={20} />
            </button>

            {/* Logo */}
            <div className="flex items-center gap-2">
                <Image src="/belai_logo.png" alt="belAI Logo" width={24} height={24} className="h-6 w-6 object-contain" />
                <span className="text-lg font-bold text-white">belAI</span>
            </div>

            {/* Spacer for centering logo */}
            <div className="w-[44px]" />
        </header>
    );
}
