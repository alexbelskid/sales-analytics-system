'use client';

import { Bell, Search, User, Clock } from 'lucide-react';
import { useEffect, useState } from 'react';

export default function Header() {
    const [currentTime, setCurrentTime] = useState('');
    const [currentDate, setCurrentDate] = useState('');

    useEffect(() => {
        const updateTime = () => {
            const now = new Date();
            setCurrentTime(now.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }));
            setCurrentDate(now.toLocaleDateString('ru-RU', {
                weekday: 'short',
                day: 'numeric',
                month: 'short'
            }));
        };

        updateTime();
        const interval = setInterval(updateTime, 1000);
        return () => clearInterval(interval);
    }, []);

    return (
        <header className="flex h-20 items-center justify-between border-b border-border/30 px-8 glass-effect stagger-in" style={{ animationDelay: '100ms' }}>
            {/* Search */}
            <div className="relative w-96">
                <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <input
                    type="text"
                    placeholder="Поиск по системе..."
                    className="w-full rounded-lg border border-border/50 bg-obsidian/50 py-3 pl-12 pr-4 text-sm backdrop-blur-sm transition-all duration-300 placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500/50"
                />
            </div>

            {/* Right side */}
            <div className="flex items-center gap-6">
                {/* Diagonal Time Display */}
                <div
                    className="relative flex items-center gap-3 px-4 py-2 rounded-lg bg-slate/30 border border-amber-500/20"
                    style={{ transform: 'rotate(-2deg)' }}
                >
                    <Clock className="h-4 w-4 text-amber-400" />
                    <div className="font-mono text-sm">
                        <div className="text-amber-400 font-semibold">{currentTime}</div>
                        <div className="text-[10px] text-muted-foreground uppercase tracking-wider">{currentDate}</div>
                    </div>
                    {/* Glow effect */}
                    <div className="absolute inset-0 rounded-lg blur-md bg-amber-500/10 -z-10" />
                </div>

                {/* Notifications */}
                <button className="relative rounded-lg p-3 hover:bg-slate/50 transition-all duration-300 group">
                    <Bell className="h-5 w-5 text-muted-foreground group-hover:text-foreground transition-colors" />
                    <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-crimson-alert animate-pulse" />
                    <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-crimson-alert blur-sm" />
                </button>

                {/* User Profile with Ambient Glow */}
                <div className="flex items-center gap-3 group cursor-pointer">
                    <div className="text-right">
                        <p className="text-sm font-semibold text-foreground">Администратор</p>
                        <p className="text-xs text-muted-foreground font-mono">admin@company.ru</p>
                    </div>
                    <div className="relative flex h-11 w-11 items-center justify-center rounded-full bg-gradient-to-br from-amber-500 to-yellow-600 transition-all duration-300 group-hover:scale-110">
                        <User className="h-5 w-5 text-obsidian" strokeWidth={2.5} />
                        {/* Ambient glow */}
                        <div className="absolute inset-0 rounded-full blur-lg bg-amber-500/30 group-hover:bg-amber-500/50 transition-all duration-300 -z-10" />
                    </div>
                </div>
            </div>
        </header>
    );
}
