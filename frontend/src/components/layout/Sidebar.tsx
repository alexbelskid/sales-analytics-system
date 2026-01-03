'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    LayoutDashboard,
    Upload,
    Mail,
    FileText,
    TrendingUp,
    Calculator,
    Settings
} from 'lucide-react';

const navigation = [
    { name: 'Дашборд', href: '/', icon: LayoutDashboard },
    { name: 'Загрузка данных', href: '/upload', icon: Upload },
    { name: 'Автоответы', href: '/emails', icon: Mail },
    { name: 'КП', href: '/proposals', icon: FileText },
    { name: 'Прогнозы', href: '/forecast', icon: TrendingUp },
    { name: 'Зарплаты', href: '/salary', icon: Calculator },
];

export default function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="hidden w-72 border-r border-border/50 bg-charcoal md:block diagonal-slide">
            <div className="flex h-full flex-col">
                {/* Logo - Editorial Style */}
                <div className="flex h-20 items-center border-b border-border/30 px-8 relative">
                    <div className="flex items-center gap-3">
                        <div className="relative flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-amber-500 to-yellow-600 glow-pulse">
                            <TrendingUp className="h-6 w-6 text-obsidian" strokeWidth={2.5} />
                        </div>
                        <div>
                            <span className="text-2xl font-bold gradient-text tracking-tight">SalesAI</span>
                            <div className="text-[10px] text-muted-foreground uppercase tracking-widest font-mono">
                                Analytics
                            </div>
                        </div>
                    </div>
                    {/* Diagonal accent */}
                    <div className="absolute bottom-0 left-0 w-full h-[2px] bg-gradient-to-r from-amber-500/50 via-amber-500 to-transparent"
                        style={{ transform: `skewY(${-2}deg)` }} />
                </div>

                {/* Navigation - Large Editorial Labels */}
                <nav className="flex-1 space-y-2 p-6">
                    {navigation.map((item, index) => {
                        const isActive = pathname === item.href;
                        return (
                            <Link
                                key={item.name}
                                href={item.href}
                                className={`group relative flex items-center gap-4 rounded-lg px-4 py-4 text-base font-medium transition-all duration-300 stagger-in ${isActive
                                        ? 'text-amber-400'
                                        : 'text-muted-foreground hover:text-foreground'
                                    }`}
                                style={{ animationDelay: `${index * 100 + 200}ms` }}
                            >
                                {/* Diagonal Active Indicator */}
                                {isActive && (
                                    <div
                                        className="absolute left-0 top-0 w-1 h-full bg-gradient-to-b from-transparent via-amber-500 to-transparent"
                                        style={{ transform: `skewY(8deg)`, transformOrigin: 'top left' }}
                                    />
                                )}

                                {/* Icon with Glow */}
                                <div className={`relative ${isActive ? 'text-amber-400' : 'text-muted-foreground group-hover:text-foreground'} transition-colors`}>
                                    <item.icon className="h-5 w-5" strokeWidth={2} />
                                    {isActive && (
                                        <div className="absolute inset-0 blur-md bg-amber-500/30" />
                                    )}
                                </div>

                                {/* Label */}
                                <span className="relative">
                                    {item.name}
                                    {/* Hover underline */}
                                    <span className={`absolute bottom-0 left-0 h-[1px] bg-amber-500 transition-all duration-300 ${isActive ? 'w-full' : 'w-0 group-hover:w-full'
                                        }`} />
                                </span>
                            </Link>
                        );
                    })}
                </nav>

                {/* Settings - Bottom */}
                <div className="border-t border-border/30 p-6">
                    <Link
                        href="/settings"
                        className="group flex items-center gap-4 rounded-lg px-4 py-4 text-base font-medium text-muted-foreground hover:text-foreground transition-all duration-300"
                    >
                        <Settings className="h-5 w-5 group-hover:rotate-90 transition-transform duration-500" strokeWidth={2} />
                        <span className="relative">
                            Настройки
                            <span className="absolute bottom-0 left-0 h-[1px] w-0 bg-amber-500 group-hover:w-full transition-all duration-300" />
                        </span>
                    </Link>

                    {/* Version Badge */}
                    <div className="mt-4 px-4">
                        <div className="text-[10px] font-mono text-muted-foreground/50 uppercase tracking-widest">
                            Version 1.0.0
                        </div>
                        <div className="mt-1 h-[1px] w-12 bg-gradient-to-r from-amber-500/50 to-transparent" />
                    </div>
                </div>
            </div>
        </aside>
    );
}
