'use client';

import { Search, User } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useDebounce } from 'use-debounce';

export default function Header() {
    const [searchQuery, setSearchQuery] = useState('');
    const [debouncedSearchQuery] = useDebounce(searchQuery, 500);

    useEffect(() => {
        if (debouncedSearchQuery) {
            console.log('Searching for:', debouncedSearchQuery);
            // Here you would typically call an API or filter data
        }
    }, [debouncedSearchQuery]);

    return (
        <header className="flex h-16 items-center justify-between border-b border-[#333333] bg-[#202020] px-4 md:px-8 shrink-0">
            {/* Search */}
            <div className="relative w-full max-w-xs md:w-96">
                <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-[#808080]" />
                <input
                    type="text"
                    placeholder="Поиск..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full rounded bg-[#262626] border border-[#333333] py-2 pl-11 pr-4 text-sm text-white placeholder:text-[#404040] focus:outline-none focus:border-white transition-colors"
                />
            </div>

            {/* User */}
            <div className="flex items-center gap-3">
                <div className="text-right hidden md:block">
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
