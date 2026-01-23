"use client";

import Link from "next/link";
import { Mail, MessageSquare, Lock, FileSpreadsheet } from "lucide-react";
import LiquidButton from "@/components/LiquidButton";

const SETTINGS_CARDS = [
    {
        title: "Подключение почты",
        description: "Настройте IMAP/SMTP для автоматической работы с письмами",
        icon: Mail,
        href: "/settings/email",
        color: "text-white"
    },
    {
        title: "Тон ответов",
        description: "Настройка стилей общения, приветствий и подписей",
        icon: MessageSquare,
        href: "/settings/response-tone",
        color: "text-white"
    },
    {
        title: "Файлы",
        description: "Управление загруженными файлами и документами",
        icon: FileSpreadsheet,
        href: "/files",
        color: "text-white"
    },
    {
        title: "Безопасность",
        description: "Управление доступом и настройка прав пользователей",
        icon: Lock,
        href: "#",
        color: "text-[#404040]",
        disabled: true
    }
];

export default function SettingsPage() {
    return (
        <div className="min-h-screen text-white p-8 animate-fade-in"> { /* global background removed */}
            <div className="max-w-5xl mx-auto space-y-12">

                {/* Header */}
                <div className="space-y-2">
                    <h1 className="text-4xl font-light tracking-tight text-white drop-shadow-lg">
                        Настройки
                    </h1>
                    <p className="text-base text-gray-400 max-w-lg">
                        Персонализируйте работу системы под ваши предпочтения
                    </p>
                </div>

                <div className="h-px bg-gradient-to-r from-white/10 to-transparent" />

                {/* Settings Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {SETTINGS_CARDS.map((card) => {
                        const Icon = card.icon;
                        const Content = (
                            <div className={`
                                group relative h-full p-8 rounded-3xl
                                border border-white/5 bg-white/[0.02] backdrop-blur-sm
                                transition-all duration-500 ease-out
                                ${card.disabled
                                    ? 'opacity-50 grayscale cursor-not-allowed'
                                    : 'hover:bg-white/[0.05] hover:border-white/20 hover:shadow-[0_0_30px_-5px_rgba(255,255,255,0.1)] cursor-pointer'
                                }
                            `}>
                                <div className="flex flex-col h-full justify-between gap-6">
                                    <div>
                                        <div className={`
                                            mb-6 inline-flex p-4 rounded-2xl
                                            bg-gradient-to-br from-white/10 to-transparent
                                            border border-white/5
                                            shadow-inner
                                        `}>
                                            <Icon className={`h-6 w-6 ${card.color}`} />
                                        </div>
                                        <h3 className="text-xl font-medium mb-3 text-white tracking-wide">
                                            {card.title}
                                        </h3>
                                        <p className="text-sm leading-relaxed text-gray-400 group-hover:text-gray-300 transition-colors">
                                            {card.description}
                                        </p>
                                    </div>

                                    {!card.disabled && (
                                        <div className="flex justify-end opacity-0 transform translate-y-2 group-hover:opacity-100 group-hover:translate-y-0 transition-all duration-300">
                                            <span className="text-xs font-bold uppercase tracking-widest text-white/70">
                                                Открыть →
                                            </span>
                                        </div>
                                    )}

                                    {card.disabled && (
                                        <div className="mt-auto pt-4">
                                            <span className="text-[10px] uppercase tracking-widest text-white/20 border border-white/10 rounded-full px-3 py-1">
                                                Скоро
                                            </span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        );

                        if (card.disabled) return <div key={card.title}>{Content}</div>;

                        return (
                            <Link href={card.href} key={card.title}>
                                {Content}
                            </Link>
                        );
                    })}
                </div>

                {/* Footer / System Info */}
                <div className="pt-12 flex items-center justify-between text-[10px] text-gray-600 uppercase tracking-[0.2em] font-medium">
                    <span>Sales Analytics System v2.1.0</span>
                    <span>AI Engine: Groq Llama 3.3</span>
                </div>
            </div>
        </div>
    );
}
