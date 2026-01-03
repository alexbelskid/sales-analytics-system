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

import { memo } from 'react';

const navigation = [
    { name: 'Дашборд', href: '/' },
    { name: 'Автоответы', href: '/emails' },
    { name: 'AI Ассистент', href: '/ai-assistant' },
    { name: 'КП', href: '/proposals' },
    { name: 'Зарплаты', href: '/salary' },
];

const NavItem = memo(({ item, isActive }: { item: typeof navigation[0], isActive: boolean }) => (
    <Link
        href={item.href}
        className={`block px-3 py-2 text-sm rounded transition-colors ${isActive
            ? 'bg-white text-black font-medium'
            : 'text-[#808080] hover:text-white hover:bg-[#1A1A1A]'
            }`}
    >
        {item.name}
    </Link>
));

NavItem.displayName = 'NavItem';

export default function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="hidden w-64 border-r border-[#2A2A2A] bg-[#0A0A0A] md:block overflow-y-auto">
            <div className="flex h-full flex-col">
                {/* Logo */}
                <div className="flex h-16 items-center px-6 border-b border-[#2A2A2A] shrink-0">
                    <span className="text-lg font-semibold">SalesAI</span>
                </div>

                {/* Navigation */}
                <nav className="flex-1 space-y-1 p-4">
                    {navigation.map((item) => (
                        <NavItem
                            key={item.name}
                            item={item}
                            isActive={pathname === item.href}
                        />
                    ))}
                </nav>

                {/* Settings */}
                <div className="border-t border-[#2A2A2A] p-4 shrink-0">
                    <NavItem
                        item={{ name: 'Настройки', href: '/settings' }}
                        isActive={pathname === '/settings'}
                    />
                </div>
            </div>
        </aside>
    );
}
