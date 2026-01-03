"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { Sparkles, Eye, EyeOff, CheckCircle, XCircle, ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function GeminiSettingsPage() {
    const { toast } = useToast();
    const [apiKey, setApiKey] = useState("");
    const [showKey, setShowKey] = useState(false);
    const [saving, setSaving] = useState(false);
    const [testing, setTesting] = useState(false);
    const [status, setStatus] = useState<{ available: boolean; model: string | null } | null>(null);

    useEffect(() => {
        checkStatus();
    }, []);

    const checkStatus = async () => {
        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/ai/status`);
            const data = await response.json();
            setStatus(data);
        } catch (error) {
            console.error("Failed to check AI status:", error);
        }
    };

    const handleSave = async () => {
        if (!apiKey.trim()) {
            toast({ title: "Ошибка", description: "Введите API ключ" });
            return;
        }

        setSaving(true);
        try {
            // Note: In production, this should save to backend/database
            // For now, we'll just show success and user needs to add to Railway env vars
            toast({
                title: "Инструкция",
                description: "Добавьте GOOGLE_GEMINI_API_KEY в Railway environment variables и перезапустите сервис",
                duration: 10000
            });

            // Clear the input for security
            setApiKey("");
        } catch (error) {
            toast({ title: "Ошибка", description: "Не удалось сохранить" });
        } finally {
            setSaving(false);
        }
    };

    const handleTest = async () => {
        setTesting(true);
        try {
            await checkStatus();
            toast({
                title: status?.available ? "Успешно" : "Не настроен",
                description: status?.available
                    ? `Gemini API работает (${status.model})`
                    : "API ключ не настроен или неверный"
            });
        } catch (error) {
            toast({ title: "Ошибка", description: "Не удалось проверить статус" });
        } finally {
            setTesting(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#0A0A0A] text-white p-8">
            <div className="max-w-3xl mx-auto space-y-8">

                {/* Breadcrumbs / Back */}
                <Link href="/settings" className="inline-flex items-center gap-2 text-[#808080] hover:text-white transition-colors mb-4 group">
                    <ArrowLeft className="h-4 w-4 transition-transform group-hover:-translate-x-1" />
                    <span className="text-xs uppercase tracking-widest font-medium">Назад в настройки</span>
                </Link>

                {/* Header */}
                <div>
                    <h1 className="text-[32px] font-semibold mb-2">Google Gemini API</h1>
                    <p className="text-sm text-[#808080]">Настройка AI ассистента для генерации ответов</p>
                </div>

                <div className="h-[1px] bg-[#1A1A1A]" />

                {/* Status */}
                <div className="bg-[#1A1A1A] border border-[#2A2A2A] rounded p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-semibold">Статус</h2>
                        <Button
                            onClick={handleTest}
                            disabled={testing}
                            variant="outline"
                            className="bg-transparent border-[#2A2A2A] text-white hover:bg-[#2A2A2A] hover:text-white rounded h-9 text-xs"
                        >
                            {testing ? "Проверка..." : "Проверить"}
                        </Button>
                    </div>

                    {status && (
                        <div className="flex items-center gap-3">
                            {status.available ? (
                                <>
                                    <CheckCircle className="h-5 w-5 text-white" />
                                    <div>
                                        <p className="text-sm font-medium">Подключено</p>
                                        <p className="text-xs text-[#808080]">Модель: {status.model}</p>
                                    </div>
                                </>
                            ) : (
                                <>
                                    <XCircle className="h-5 w-5 text-[#808080]" />
                                    <div>
                                        <p className="text-sm font-medium text-[#808080]">Не настроено</p>
                                        <p className="text-xs text-[#808080]">API ключ не найден</p>
                                    </div>
                                </>
                            )}
                        </div>
                    )}
                </div>

                {/* API Key Input */}
                <div className="space-y-6">
                    <div>
                        <h2 className="text-lg font-semibold mb-4">API Ключ</h2>

                        <div className="space-y-4">
                            <div className="relative">
                                <Input
                                    type={showKey ? "text" : "password"}
                                    value={apiKey}
                                    onChange={(e) => setApiKey(e.target.value)}
                                    placeholder="Введите Google Gemini API ключ"
                                    className="bg-[#1A1A1A] border-[#2A2A2A] text-white placeholder:text-[#404040] rounded h-12 px-4 pr-12 focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:border-white transition-colors font-mono text-sm"
                                />
                                <button
                                    onClick={() => setShowKey(!showKey)}
                                    className="absolute right-4 top-1/2 -translate-y-1/2 text-[#808080] hover:text-white transition-colors"
                                >
                                    {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                                </button>
                            </div>

                            <Button
                                onClick={handleSave}
                                disabled={saving || !apiKey.trim()}
                                className="w-full bg-white text-black hover:bg-[#E0E0E0] rounded h-10"
                            >
                                <Sparkles className="mr-2 h-4 w-4" />
                                {saving ? "Сохранение..." : "Сохранить"}
                            </Button>
                        </div>
                    </div>

                    {/* Instructions */}
                    <div className="bg-[#0F0F0F] border border-[#2A2A2A] rounded p-6 space-y-4">
                        <h3 className="text-sm font-semibold">Как получить API ключ:</h3>
                        <ol className="text-sm text-[#808080] space-y-2 list-decimal list-inside">
                            <li>Перейдите на <a href="https://ai.google.dev/" target="_blank" rel="noopener noreferrer" className="text-white hover:underline">ai.google.dev</a></li>
                            <li>Нажмите "Get API key"</li>
                            <li>Создайте проект (бесплатный лимит: 60 запросов/минуту)</li>
                            <li>Скопируйте API ключ</li>
                            <li>Добавьте ключ как переменную окружения <code className="bg-[#1A1A1A] px-2 py-1 rounded text-xs">GOOGLE_GEMINI_API_KEY</code> в Railway</li>
                            <li>Перезапустите backend сервис</li>
                        </ol>
                    </div>

                    {/* Features */}
                    <div className="bg-[#0F0F0F] border border-[#2A2A2A] rounded p-6 space-y-3">
                        <h3 className="text-sm font-semibold">Возможности AI ассистента:</h3>
                        <ul className="text-sm text-[#808080] space-y-2">
                            <li className="flex items-start gap-2">
                                <span className="text-white mt-0.5">•</span>
                                <span>Автоматическая генерация ответов на письма</span>
                            </li>
                            <li className="flex items-start gap-2">
                                <span className="text-white mt-0.5">•</span>
                                <span>Использование базы знаний о продуктах и ценах</span>
                            </li>
                            <li className="flex items-start gap-2">
                                <span className="text-white mt-0.5">•</span>
                                <span>Обучение на примерах ваших ответов</span>
                            </li>
                            <li className="flex items-start gap-2">
                                <span className="text-white mt-0.5">•</span>
                                <span>Поддержка разных тонов общения</span>
                            </li>
                            <li className="flex items-start gap-2">
                                <span className="text-white mt-0.5">•</span>
                                <span>Модель: gemini-1.5-flash (быстрая и экономичная)</span>
                            </li>
                        </ul>
                    </div>
                </div>

            </div>
        </div>
    );
}
