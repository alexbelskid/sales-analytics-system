"use client";

import Link from "next/link";
import { Key, Mail, MessageSquare, ArrowRight, Sparkles } from "lucide-react";

export default function SettingsPage() {
    return (
        <div className="min-h-screen bg-[#0A0A0A] text-white p-8">
            <div className="max-w-4xl mx-auto space-y-8">

                {/* Header */}
                <div>
                    <h1 className="text-[32px] font-semibold">Настройки</h1>
                    <p className="text-sm text-[#808080] mt-1">Конфигурация системы</p>
                </div>

                <div className="h-[1px] bg-[#1A1A1A]" />

                {/* Settings Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

                    {/* Google Gemini API */}
                    <Link href="/settings/gemini">
                        <div className="bg-[#1A1A1A] border border-[#2A2A2A] rounded p-6 hover:border-white/20 transition-colors cursor-pointer group">
                            <div className="flex items-center gap-3 mb-3">
                                <div className="p-2 rounded bg-white/10">
                                    <Sparkles className="h-5 w-5 text-white" />
                                </div>
                                <h3 className="text-lg font-semibold">Google Gemini API</h3>
                            </div>
                            <p className="text-sm text-[#808080] mb-4">
                                Настройка AI ассистента для генерации ответов
                            </p>
                            <div className="flex items-center text-xs text-[#808080] group-hover:text-white transition-colors">
                                Настроить <ArrowRight className="ml-2 h-3 w-3" />
                            </div>
                        </div>
                    </Link>

                    {/* Email Settings */}
                    <Link href="/settings/email">
                        <div className="bg-[#1A1A1A] border border-[#2A2A2A] rounded p-6 hover:border-white/20 transition-colors cursor-pointer group">
                            <div className="flex items-center gap-3 mb-3">
                                <div className="p-2 rounded bg-white/10">
                                    <Mail className="h-5 w-5 text-white" />
                                </div>
                                <h3 className="text-lg font-semibold">Подключение почты</h3>
                            </div>
                            <p className="text-sm text-[#808080] mb-4">
                                Настройка IMAP/SMTP и интеграций
                            </p>
                            <div className="flex items-center text-xs text-[#808080] group-hover:text-white transition-colors">
                                Настроить <ArrowRight className="ml-2 h-3 w-3" />
                            </div>
                        </div>
                    </Link>

                    {/* Response Tone */}
                    <Link href="/settings/response-tone">
                        <div className="bg-[#1A1A1A] border border-[#2A2A2A] rounded p-6 hover:border-white/20 transition-colors cursor-pointer group">
                            <div className="flex items-center gap-3 mb-3">
                                <div className="p-2 rounded bg-white/10">
                                    <MessageSquare className="h-5 w-5 text-white" />
                                </div>
                                <h3 className="text-lg font-semibold">Тон ответов</h3>
                            </div>
                            <p className="text-sm text-[#808080] mb-4">
                                Настройка стилей общения и подписей
                            </p>
                            <div className="flex items-center text-xs text-[#808080] group-hover:text-white transition-colors">
                                Редактировать <ArrowRight className="ml-2 h-3 w-3" />
                            </div>
                        </div>
                    </Link>

                </div>
            </div>
        </div>
    );
}
