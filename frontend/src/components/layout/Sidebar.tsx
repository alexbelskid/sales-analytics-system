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
        <aside className="hidden w-64 border-r border-border bg-card md:block">
            <div className="flex h-full flex-col">
                {/* Logo */}
                <div className="flex h-16 items-center border-b border-border px-6">
                    <div className="flex items-center gap-2">
                        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
                            <TrendingUp className="h-5 w-5 text-white" />
                        </div>
                        <span className="text-lg font-bold gradient-text">SalesAI</span>
                    </div>
                </div>

                {/* Navigation */}
                <nav className="flex-1 space-y-1 p-4">
                    {navigation.map((item) => {
                        const isActive = pathname === item.href;
                        return (
                            <Link
                                key={item.name}
                                href={item.href}
                                className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all ${isActive
                                        ? 'bg-primary text-primary-foreground'
                                        : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
                                    }`}
                            >
                                <item.icon className="h-5 w-5" />
                                {item.name}
                            </Link>
                        );
                    })}
                </nav>

                {/* Settings */}
                <div className="border-t border-border p-4">
                    <Link
                        href="/settings"
                        className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-muted-foreground hover:bg-secondary hover:text-foreground"
                    >
                        <Settings className="h-5 w-5" />
                        Настройки
                    </Link>
                </div>
            </div>
        </aside>
    );
}
