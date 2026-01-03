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
    { name: 'Дашборд', href: '/' },
    { name: 'Загрузка данных', href: '/upload' },
    { name: 'Автоответы', href: '/emails' },
    { name: 'КП', href: '/proposals' },
    { name: 'Прогнозы', href: '/forecast' },
    { name: 'Зарплаты', href: '/salary' },
];

export default function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="hidden w-64 border-r border-[#2A2A2A] bg-[#0A0A0A] md:block">
            <div className="flex h-full flex-col">
                {/* Logo */}
                <div className="flex h-16 items-center px-6 border-b border-[#2A2A2A]">
                    <span className="text-lg font-semibold">SalesAI</span>
                </div>

                {/* Navigation */}
                <nav className="flex-1 space-y-1 p-4">
                    {navigation.map((item) => {
                        const isActive = pathname === item.href;
                        return (
                            <Link
                                key={item.name}
                                href={item.href}
                                className={`block px-3 py-2 text-sm rounded transition-colors ${isActive
                                        ? 'bg-white text-black font-medium'
                                        : 'text-[#808080] hover:text-white hover:bg-[#1A1A1A]'
                                    }`}
                            >
                                {item.name}
                            </Link>
                        );
                    })}
                </nav>

                {/* Settings */}
                <div className="border-t border-[#2A2A2A] p-4">
                    <Link
                        href="/settings"
                        className="block px-3 py-2 text-sm text-[#808080] hover:text-white hover:bg-[#1A1A1A] rounded transition-colors"
                    >
                        Настройки
                    </Link>
                </div>
            </div>
        </aside>
    );
}
