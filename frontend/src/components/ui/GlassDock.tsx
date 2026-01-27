'use client';

import React, { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    Home,
    LineChart,
    BarChart2,
    Bot,
    Grid,
    Upload,
    Mail,
    FileText,
    Calculator,
    File,
    MoreHorizontal,
    Settings
} from 'lucide-react';

const GlassDock = () => {
    const pathname = usePathname();
    const [isMoreOpen, setIsMoreOpen] = useState(false);
    const dockRef = useRef<HTMLDivElement>(null);

    // Close on click outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dockRef.current && !dockRef.current.contains(event.target as Node)) {
                setIsMoreOpen(false);
            }
        };

        if (isMoreOpen) {
            document.addEventListener('mousedown', handleClickOutside);
        }
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [isMoreOpen]);

    const mainNavItems = [
        { name: 'Home', icon: Home, path: '/' },
        { name: 'Sales', icon: LineChart, path: '/sales-dashboard' },
        { name: 'Analytics', icon: BarChart2, path: '/advanced-analytics' },
        { name: 'AI Assistant', icon: Bot, path: '/ai-assistant' },
    ];

    const secondaryNavItems = [
        { name: 'Загрузка данных', icon: Upload, path: '/upload' },
        { name: 'Автоответы', icon: Mail, path: '/emails' },
        { name: 'КП', icon: FileText, path: '/proposals' },
        { name: 'Зарплаты', icon: Calculator, path: '/salary' },
        { name: 'Файлы', icon: File, path: '/files' },
        { name: 'Настройки', icon: Settings, path: '/settings' },
    ];

    return (
        <div className="fixed bottom-8 z-50 flex flex-col items-center gap-4" ref={dockRef}>
            {/* Secondary Menu (Popover) - Monolith Style */}
            <div
                className={`
                    absolute bottom-20 transition-all duration-300 ease-[cubic-bezier(0.2,0.8,0.2,1)] origin-bottom
                    ${isMoreOpen ? 'opacity-100 scale-100 translate-y-0' : 'opacity-0 scale-90 translate-y-4 pointer-events-none'}
                `}
            >
                <div className="flex flex-col gap-1 rounded-3xl border border-gray-700 bg-gray-900/80 p-2 backdrop-blur-2xl shadow-2xl ring-1 ring-white/5 w-64">
                    {secondaryNavItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = pathname === item.path;

                        return (
                            <Link
                                key={item.path}
                                href={item.path}
                                onClick={() => setIsMoreOpen(false)}
                                className={`
                                    flex items-center gap-3 px-4 py-3 rounded-2xl transition-all duration-200
                                    ${isActive
                                        ? 'bg-gray-700/40 text-gray-300 shadow-[inner_0_0_10px_rgba(0,0,0,0.3)]'
                                        : 'text-gray-400 hover:text-white hover:bg-white/5'
                                    }
                                `}
                            >
                                <Icon size={18} />
                                <span className="text-sm font-medium">{item.name}</span>
                            </Link>
                        );
                    })}
                </div>
            </div>

            {/* Main Dock */}
            <div className="flex items-center gap-2 rounded-full border border-gray-700 bg-gray-900/60 p-2 backdrop-blur-xl shadow-2xl ring-1 ring-white/5">
                {mainNavItems.map((item) => {
                    const isActive = pathname === item.path;
                    const Icon = item.icon;

                    return (
                        <Link
                            key={item.path}
                            href={item.path}
                            onClick={() => setIsMoreOpen(false)}
                            className={`group relative flex items-center justify-center rounded-full p-3 transition-all duration-300 ${isActive
                                ? 'text-gray-300 bg-gray-700/40 shadow-[inner_0_0_10px_rgba(0,0,0,0.3)]'
                                : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
                                }`}
                        >
                            <Icon
                                size={20}
                                strokeWidth={isActive ? 2.5 : 2}
                                className={`transition-transform duration-300 group-hover:scale-110 ${isActive ? '' : ''}`}
                            />



                            <span className="absolute -top-10 left-1/2 -translate-x-1/2 rounded-md bg-black/80 px-2 py-1 text-[10px] text-white opacity-0 transition-opacity duration-300 group-hover:opacity-100 whitespace-nowrap border border-white/10 backdrop-blur-md pointer-events-none">
                                {item.name}
                            </span>
                        </Link>
                    );
                })}

                {/* More / Settings Trigger */}
                <button
                    onClick={() => setIsMoreOpen(!isMoreOpen)}
                    className={`group relative flex items-center justify-center rounded-full p-3 transition-all duration-300 ${isMoreOpen
                        ? 'text-gray-300 bg-gray-700/40 shadow-[inner_0_0_10px_rgba(0,0,0,0.3)]'
                        : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
                        }`}
                >
                    <Grid
                        size={20}
                        className={`transition-transform duration-300 ${isMoreOpen ? 'rotate-90 text-gray-300' : ''}`}
                    />
                </button>
            </div>
        </div>
    );
};

export default GlassDock;
