'use client';

import { useState, useEffect, useCallback, memo } from 'react';
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
    Sparkles,
    X,
    Menu,
    FileSpreadsheet
} from 'lucide-react';

const navigation = [
    { name: 'Аналитика агентов', href: '/', icon: TrendingUp },
    { name: 'Обзор продаж', href: '/sales-dashboard', icon: LayoutDashboard },
    { name: 'Автоответы', href: '/emails', icon: Mail },
    { name: 'AI Ассистент', href: '/ai-assistant', icon: Sparkles },
    { name: 'КП', href: '/proposals', icon: FileText },
    { name: 'Зарплаты', href: '/salary', icon: Calculator },
    { name: 'Файлы', href: '/files', icon: FileSpreadsheet },
];

interface NavItemProps {
    item: { name: string; href: string; icon: any };
    isActive: boolean;
    isCollapsed: boolean;
    onClick?: () => void;
}

const NavItem = memo(({ item, isActive, isCollapsed, onClick }: NavItemProps) => (
    <Link
        href={item.href}
        onClick={onClick}
        title={isCollapsed ? item.name : ''}
        className={`flex items-center gap-3 px-3 py-3 text-sm rounded-2xl transition-all duration-150 min-h-[44px] ${isActive
            ? 'bg-white text-black font-medium shadow-sm'
            : 'text-muted-foreground hover:text-foreground hover:opacity-90'
            } ${isCollapsed ? 'justify-center px-2' : ''}`}
    >
        <item.icon className="h-5 w-5 shrink-0" />
        {!isCollapsed && <span className="truncate">{item.name}</span>}
    </Link>
));

NavItem.displayName = 'NavItem';

interface SidebarProps {
    isMobileOpen?: boolean;
    onMobileClose?: () => void;
}

export default function Sidebar({ isMobileOpen = false, onMobileClose }: SidebarProps) {
    const pathname = usePathname();
    const [isCollapsed, setIsCollapsed] = useState(false);

    // Close mobile sidebar when route changes
    useEffect(() => {
        if (onMobileClose) {
            onMobileClose();
        }
    }, [pathname]);

    // Handle escape key
    useEffect(() => {
        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === 'Escape' && isMobileOpen && onMobileClose) {
                onMobileClose();
            }
        };
        document.addEventListener('keydown', handleEscape);
        return () => document.removeEventListener('keydown', handleEscape);
    }, [isMobileOpen, onMobileClose]);

    // Prevent body scroll when mobile sidebar is open
    useEffect(() => {
        if (isMobileOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
        return () => {
            document.body.style.overflow = '';
        };
    }, [isMobileOpen]);

    const handleNavClick = useCallback(() => {
        if (onMobileClose) {
            onMobileClose();
        }
    }, [onMobileClose]);

    const sidebarContent = (
        <div className="flex h-full flex-col">
            {/* Logo Section */}
            <div className={`flex h-16 items-center border-b border-[#333333] shrink-0 px-4 ${isCollapsed ? 'justify-center' : 'justify-between'
                }`}>
                {!isCollapsed && (
                    <div className="flex items-center gap-2 overflow-hidden">
                        <Sparkles className="h-5 w-5 text-white shrink-0" />
                        <span className="text-lg font-bold text-white truncate">Alterini AI</span>
                    </div>
                )}
                {isCollapsed && <Sparkles className="h-6 w-6 text-white" />}

                {/* Collapse button - only on desktop */}
                <button
                    onClick={() => setIsCollapsed(!isCollapsed)}
                    className="hidden lg:flex p-2 rounded-lg bg-[#262626] border border-[#333333] text-[#808080] hover:text-white transition-colors min-h-[44px] min-w-[44px] items-center justify-center"
                >
                    {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
                </button>

                {/* Close button - only on mobile */}
                {onMobileClose && (
                    <button
                        onClick={onMobileClose}
                        className="lg:hidden p-2 rounded-lg bg-[#262626] border border-[#333333] text-[#808080] hover:text-white transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
                    >
                        <X size={20} />
                    </button>
                )}
            </div>

            {/* Navigation */}
            <nav className="flex-1 space-y-1 p-3 overflow-y-auto overflow-x-hidden">
                {navigation.map((item) => (
                    <NavItem
                        key={item.name}
                        item={item}
                        isActive={pathname === item.href}
                        isCollapsed={isCollapsed}
                        onClick={handleNavClick}
                    />
                ))}
            </nav>

            {/* Settings */}
            <div className="border-t border-[#333333] p-3 shrink-0">
                <NavItem
                    item={{ name: 'Настройки', href: '/settings', icon: Settings }}
                    isActive={pathname === '/settings'}
                    isCollapsed={isCollapsed}
                    onClick={handleNavClick}
                />
            </div>
        </div>
    );

    return (
        <>
            {/* Desktop Sidebar */}
            <aside
                className={`hidden lg:flex border-r border-[#333333] bg-[#202020] flex-col overflow-hidden transition-all duration-300 ease-in-out ${isCollapsed ? 'w-16' : 'w-64'
                    }`}
            >
                {sidebarContent}
            </aside>

            {/* Mobile Overlay */}
            {isMobileOpen && (
                <div
                    className="lg:hidden fixed inset-0 z-40 bg-black/60 backdrop-blur-sm transition-opacity duration-300"
                    onClick={onMobileClose}
                />
            )}

            {/* Mobile Sidebar */}
            <aside
                className={`lg:hidden fixed inset-y-0 left-0 z-50 w-72 bg-[#202020] border-r border-[#333333] transform transition-transform duration-300 ease-in-out ${isMobileOpen ? 'translate-x-0' : '-translate-x-full'
                    }`}
            >
                {sidebarContent}
            </aside>
        </>
    );
}

// Export MobileMenuButton for use in layout
export function MobileMenuButton({ onClick }: { onClick: () => void }) {
    return (
        <button
            onClick={onClick}
            className="lg:hidden p-2 rounded-lg bg-[#262626] border border-[#333333] text-[#808080] hover:text-white transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
            aria-label="Открыть меню"
        >
            <Menu size={20} />
        </button>
    );
}
