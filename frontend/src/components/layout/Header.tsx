'use client';

import { Search, User } from 'lucide-react';

export default function Header() {
    return (
        <header className="flex h-16 items-center justify-between border-b border-[#2A2A2A] bg-[#0A0A0A] px-8">
            {/* Search */}
            <div className="relative w-96">
                <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-[#808080]" />
                <input
                    type="text"
                    placeholder="Поиск..."
                    className="w-full rounded bg-[#1A1A1A] border border-[#2A2A2A] py-2 pl-11 pr-4 text-sm text-white placeholder:text-[#404040] focus:outline-none focus:border-white transition-colors"
                />
            </div>

            {/* User */}
            <div className="flex items-center gap-3">
                <div className="text-right">
                    <p className="text-sm font-medium">Администратор</p>
                    <p className="text-xs text-[#808080]">admin@company.ru</p>
                </div>
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white">
                    <User className="h-4 w-4 text-black" />
                </div>
            </div>
        </header>
    );
}
