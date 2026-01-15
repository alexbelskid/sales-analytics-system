'use client';

import { useState, useEffect, useCallback, memo } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import {
    LayoutDashboard,
    Mail,
    TrendingUp,
    FileText,
    Calculator,
    Settings,
    ChevronLeft,
    Sparkles,
    ChevronRight,
    X,
    Menu,
    FileSpreadsheet,
    BarChart3,
    Package,
    ChevronDown,
    Upload
} from 'lucide-react';
import { cn } from '@/lib/utils'; // Assuming you have a utility for merging classes, if not i will use template literals

type NavItemType = {
    name: string;
    href?: string;
    icon: any;
    children?: NavItemType[];
};

const navigation: NavItemType[] = [
    { name: 'Аналитика агентов', href: '/', icon: TrendingUp },
    { name: 'Обзор продаж', href: '/sales-dashboard', icon: LayoutDashboard },
    { name: 'Расширенная аналитика', href: '/advanced-analytics', icon: BarChart3 },
    { name: 'AI Ассистент', href: '/ai-assistant', icon: Sparkles },
    {
        name: 'Дополнительные инструменты',
        icon: Package,
        children: [
            { name: 'Загрузка данных', href: '/upload', icon: Upload },
            { name: 'Автоответы', href: '/emails', icon: Mail },
            { name: 'КП', href: '/proposals', icon: FileText },
            { name: 'Зарплаты', href: '/salary', icon: Calculator },
            { name: 'Файлы', href: '/files', icon: FileSpreadsheet },
        ]
    }
];

const settingsNav: NavItemType = {
    name: 'Настройки',
    href: '/settings',
    icon: Settings
};

interface NavItemProps {
    item: NavItemType;
    isActive: boolean;
    isCollapsed: boolean;
    onClick?: () => void;
    currentPath: string;
    level?: number;
}

const NavItem = memo(({ item, isActive, isCollapsed, onClick, currentPath, level = 0 }: NavItemProps) => {
    const defaultOpen = item.children ? item.children.some(child => child.href === currentPath) : false;
    const [isOpen, setIsOpen] = useState(defaultOpen);

    useEffect(() => {
        if (item.children && item.children.some(child => child.href === currentPath)) {
            setIsOpen(true);
        }
    }, [currentPath, item.children]);

    const handleToggle = (e: React.MouseEvent) => {
        if (item.children) {
            e.preventDefault();
            setIsOpen(!isOpen);
        } else if (onClick) {
            onClick();
        }
    };

    const isChildActive = item.children ? item.children.some(child => child.href === currentPath) : false;

    if (item.children) {
        return (
            <div className="mb-1">
                <button
                    onClick={handleToggle}
                    title={isCollapsed ? item.name : ''}
                    className={`w-full flex items-center gap-3 px-3 py-3 text-sm rounded-2xl transition-all duration-150 min-h-[44px] ${isChildActive || isOpen
                        ? 'text-white'
                        : 'text-muted-foreground hover:text-foreground hover:opacity-90'
                        } ${isCollapsed ? 'justify-center px-2' : ''}`}
                >
                    <item.icon className="h-5 w-5 shrink-0" />
                    {!isCollapsed && (
                        <>
                            <span className="truncate flex-1 text-left">{item.name}</span>
                            <ChevronDown
                                className={`h-4 w-4 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
                            />
                        </>
                    )}
                </button>
                {!isCollapsed && isOpen && (
                    <div className="ml-4 space-y-1 mt-1 border-l border-[#333333] pl-2">
                        {item.children.map((child) => (
                            <NavItem
                                key={child.name}
                                item={child}
                                isActive={currentPath === child.href}
                                isCollapsed={isCollapsed}
                                onClick={onClick}
                                currentPath={currentPath}
                                level={level + 1}
                            />
                        ))}
                    </div>
                )}
            </div>
        );
    }

    return (
        <Link
            href={item.href!}
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
    );
});

NavItem.displayName = 'NavItem';
// ... (NavItem component remains same)

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
                    <div className="flex items-center gap-3 overflow-hidden">
                        <div className="relative h-8 w-8 shrink-0">
                            <Image src="/belai_logo.png" alt="belAI Logo" fill className="object-contain" />
                        </div>
                        <span className="text-2xl font-bold text-white tracking-wide truncate mt-1">belAI</span>
                    </div>
                )}
                {isCollapsed && (
                    <div className="relative h-8 w-8">
                        <Image src="/belai_logo.png" alt="belAI Logo" fill className="object-contain" />
                    </div>
                )}

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
                        currentPath={pathname}
                    />
                ))}
            </nav>

            {/* Settings */}
            <div className="border-t border-[#333333] p-3 shrink-0">
                <NavItem
                    item={settingsNav}
                    isActive={pathname === '/settings'}
                    isCollapsed={isCollapsed}
                    onClick={handleNavClick}
                    currentPath={pathname}
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
