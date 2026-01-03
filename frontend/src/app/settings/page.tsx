"use client";

import Link from "next/link";
import { Mail, MessageSquare, Lock } from "lucide-react";

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
        <div className="min-h-screen bg-[#0A0A0A] text-white p-8">
            <div className="max-w-4xl mx-auto space-y-12">

                {/* Header */}
                <div className="space-y-2">
                    <h1 className="text-[40px] font-semibold tracking-tight">Настройки</h1>
                    <p className="text-sm text-[#808080] max-w-md">
                        Персонализируйте работу системы под ваши предпочтения
                    </p>
                </div>

                <div className="h-[1px] bg-gradient-to-r from-[#2A2A2A] to-transparent" />

                {/* Settings Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {SETTINGS_CARDS.map((card) => {
                        const Icon = card.icon;
                        const Content = (
                            <div className={`relative h-full bg-[#1A1A1A] border border-[#2A2A2A] rounded-lg p-6 transition-all duration-300 ${card.disabled ? 'opacity-50 grayscale' : 'hover:border-white/30 hover:bg-[#222222] group cursor-pointer'}`}>
                                <div className="flex flex-col h-full justify-between">
                                    <div>
                                        <div className="mb-6 inline-flex p-3 rounded-lg bg-black border border-[#2A2A2A]">
                                            <Icon className={`h-6 w-6 ${card.color}`} />
                                        </div>
                                        <h3 className="text-lg font-semibold mb-2 group-hover:text-white transition-colors">{card.title}</h3>
                                        <p className="text-xs leading-relaxed text-[#808080] group-hover:text-[#A0A0A0] transition-colors line-clamp-2">
                                            {card.description}
                                        </p>
                                    </div>

                                    {!card.disabled && (
                                        <div className="mt-8 text-[10px] uppercase tracking-widest text-[#404040] group-hover:text-white transition-all duration-300">
                                            <span>Управлять →</span>
                                        </div>
                                    )}

                                    {card.disabled && (
                                        <div className="mt-8 text-[10px] uppercase tracking-widest text-[#404040]">
                                            <span>Скоро доступно</span>
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
                <div className="pt-12 flex items-center justify-between text-[10px] text-[#404040] uppercase tracking-[0.2em]">
                    <span>Sales Analytics System v2.1.0</span>
                    <span>AI Engine: Gemini 1.5 Flash</span>
                </div>
            </div>
        </div>
    );
}
