"use client";

import { memo } from "react";
import { Zap, BrainCircuit, Activity, BookOpen, Database } from "lucide-react";

interface AIStatus {
    monthly: {
        revenue: number;
        orders: number;
        customers: number;
        period: string;
    };
    sales: any[]; // Consider using proper type
    clients: any[]; // Consider using proper type
    knowledge: {
        total: number;
        categories: { name: string; count: number }[];
    };
    training: {
        total: number;
        avg_confidence: number;
    };
}

interface StatusTabProps {
    status: AIStatus | null;
    knowledgeCount: number; // Ignored in new layout as status has it
    trainingCount: number; // Ignored in new layout as status has it
}

const StatusTab = memo(({ status, knowledgeCount, trainingCount }: StatusTabProps) => {
    if (!status || !status.knowledge) {
        // Fallback or loading state if data structure mismatch
        return (
            <div className="flex flex-col items-center justify-center py-20 gap-4">
                <div className="h-8 w-8 border-2 border-white/10 border-t-white rounded-full animate-spin" />
                <p className="text-sm text-[#404040]">Загрузка статуса AI...</p>
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Gemini Status */}
                <div>
                    <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                        <Zap className="h-5 w-5 text-orange-500" />
                        Groq AI (Llama 3)
                    </h3>
                    <div className="bg-[#1A1A1A] border border-[#2A2A2A] rounded-lg p-5">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse"></div>
                            <span className="font-medium text-green-400">Статус: Подключён</span>
                        </div>
                        <div className="text-sm text-[#808080] ml-5.5">
                            Модель: <span className="text-gray-300">llama-3.3-70b</span>
                        </div>
                    </div>
                </div>

                {/* Data Access */}
                <div>
                    <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                        <Database className="h-5 w-5 text-blue-400" />
                        Доступ к данным
                    </h3>
                    <div className="bg-[#1A1A1A] border border-[#2A2A2A] rounded-lg p-5">
                        <div className="space-y-2 text-sm">
                            <div className="flex justify-between border-b border-[#2A2A2A] pb-2">
                                <span className="text-[#808080]">Анализируемый период:</span>
                                <span className="text-white">{status.monthly.period}</span>
                            </div>
                            <div className="flex justify-between pt-1">
                                <span className="text-[#808080]">Продаж в системе:</span>
                                <span>{status.monthly.orders}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-[#808080]">Клиентов:</span>
                                <span>{status.monthly.customers}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-[#808080]">Выручка:</span>
                                <span className="text-green-500 font-medium">
                                    {status.monthly.revenue.toLocaleString('ru-RU')} BYN
                                </span>
                            </div>
                        </div>
                        <div className="mt-3 pt-3 border-t border-[#2A2A2A] text-xs text-[#606060] flex items-center gap-1">
                            <Activity className="w-3 h-3" />
                            AI имеет полный доступ к этим данным для генерации ответов
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Knowledge Base */}
                <div>
                    <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                        <BookOpen className="h-5 w-5 text-yellow-400" />
                        База знаний
                    </h3>
                    <div className="bg-[#1A1A1A] border border-[#2A2A2A] rounded-lg p-5">
                        <div className="text-3xl font-bold mb-1 pl-1">
                            {status.knowledge.total}
                        </div>
                        <div className="text-sm text-[#808080] pl-1 mb-4">активных записей</div>

                        <div className="space-y-2">
                            {status.knowledge.categories.map((cat: any) => (
                                <div key={cat.name} className="flex justify-between items-center text-sm bg-[#222] px-3 py-2 rounded border border-[#2A2A2A]/50">
                                    <span className="text-gray-300 capitalize">{cat.name === 'product' ? 'Продукты' : cat.name}</span>
                                    <span className="text-gray-500 font-mono">{cat.count}</span>
                                </div>
                            ))}
                            {status.knowledge.categories.length === 0 && (
                                <div className="text-sm text-gray-500 italic">Нет категорий</div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Training */}
                <div>
                    <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                        <BrainCircuit className="h-5 w-5 text-red-400" />
                        Обучение
                    </h3>
                    <div className="bg-[#1A1A1A] border border-[#2A2A2A] rounded-lg p-5">
                        <div className="text-3xl font-bold mb-1 pl-1">
                            {status.training.total}
                        </div>
                        <div className="text-sm text-[#808080] pl-1 mb-6">примеров диалогов</div>

                        <div className="bg-[#222] p-4 rounded-lg border border-[#2A2A2A]/50">
                            <div className="flex justify-between text-sm mb-2">
                                <span className="text-gray-400">Средняя уверенность</span>
                                <span className="text-white font-medium">{(status.training.avg_confidence * 100).toFixed(0)}%</span>
                            </div>
                            <div className="h-2 bg-[#111] rounded-full overflow-hidden">
                                <div
                                    className="bg-gradient-to-r from-red-500 to-green-500 h-full rounded-full transition-all duration-1000"
                                    style={{
                                        width: `${status.training.avg_confidence * 100}%`,
                                    }}
                                ></div>
                            </div>
                            <div className="mt-2 text-xs text-[#555]">
                                Чем выше процент, тем точнее AI копирует стиль ваших ответов.
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <button
                onClick={() => window.location.reload()}
                // A bit of a hack to refresh, ideally pass refetch callback, but parent handles state now.
                // Or better, just don't have a button, data is fresh on mount. 
                // The user asked for an update button, but I'll skip it or rely on tab switching to refresh.
                className="w-full bg-[#222] hover:bg-[#333] border border-[#333] text-white py-3 rounded-lg text-sm transition-colors mt-4"
            >
                Обновить данные статуса
            </button>
        </div>
    );
});

StatusTab.displayName = "StatusTab";

export default StatusTab;
