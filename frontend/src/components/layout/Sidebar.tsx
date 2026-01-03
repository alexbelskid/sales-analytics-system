'use client';

import { useState, memo } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    LayoutDashboard,
    Mail,
    TrendingUp,
    FileText,
    Calculator,
    Settings,
    ChevronLeft,
    ChevronRight,
    Sparkles
} from 'lucide-react';

const navigation = [
    { name: 'Дашборд', href: '/', icon: LayoutDashboard },
    { name: 'Автоответы', href: '/emails', icon: Mail },
    { name: 'AI Ассистент', href: '/ai-assistant', icon: TrendingUp },
    { name: 'КП', href: '/proposals', icon: FileText },
    { name: 'Зарплаты', href: '/salary', icon: Calculator },
];

const NavItem = memo(({
    item,
    isActive,
    isCollapsed
}: {
    item: { name: string, href: string, icon: any },
    isActive: boolean,
    isCollapsed: boolean
}) => (
    <Link
        href={item.href}
        title={isCollapsed ? item.name : ''}
        className={`flex items-center gap-3 px-3 py-2 text-sm rounded transition-all duration-200 ${isActive
            ? 'bg-white text-black font-medium shadow-sm'
            : 'text-[#808080] hover:text-white hover:bg-[#1A1A1A]'
            } ${isCollapsed ? 'justify-center px-2' : ''}`}
    >
        <item.icon className="h-4 w-4 shrink-0" />
        {!isCollapsed && <span className="truncate">{item.name}</span>}
    </Link>
));

NavItem.displayName = 'NavItem';

export default function Sidebar() {
    const pathname = usePathname();
    const [isCollapsed, setIsCollapsed] = useState(false);

    return (
        <aside
            className={`hidden border-r border-[#2A2A2A] bg-[#0A0A0A] md:flex flex-col overflow-hidden transition-all duration-300 ease-in-out ${isCollapsed ? 'w-16' : 'w-64'
                }`}
        >
            <div className="flex h-full flex-col">
                {/* Logo Section */}
                <div className={`flex h-16 items-center border-b border-[#2A2A2A] shrink-0 px-4 ${isCollapsed ? 'justify-center' : 'justify-between'
                    }`}>
                    {!isCollapsed && (
                        <div className="flex items-center gap-2 overflow-hidden">
                            <Sparkles className="h-5 w-5 text-white shrink-0" />
                            <span className="text-lg font-bold text-white truncate">Alterini AI</span>
                        </div>
                    )}
                    {isCollapsed && <Sparkles className="h-6 w-6 text-white" />}

                    <button
                        onClick={() => setIsCollapsed(!isCollapsed)}
                        className="p-1.5 rounded bg-[#1A1A1A] border border-[#2A2A2A] text-[#808080] hover:text-white transition-colors ml-1"
                    >
                        {isCollapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
                    </button>
                </div>

                {/* Navigation */}
                <nav className="flex-1 space-y-1 p-3 overflow-y-auto overflow-x-hidden">
                    {navigation.map((item) => (
                        <NavItem
                            key={item.name}
                            item={item}
                            isActive={pathname === item.href}
                            isCollapsed={isCollapsed}
                        />
                    ))}
                </nav>

                {/* Settings */}
                <div className="border-t border-[#2A2A2A] p-3 shrink-0">
                    <NavItem
                        item={{ name: 'Настройки', href: '/settings', icon: Settings }}
                        isActive={pathname === '/settings'}
                        isCollapsed={isCollapsed}
                    />
                </div>
            </div>
        </aside>
    );
}
