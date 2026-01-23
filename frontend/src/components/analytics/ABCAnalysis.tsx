"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, Info } from "lucide-react";

interface ABCAnalysisProps {
    data?: any; // Accepting data prop, though we might use specific detailed summary if available
}

export function ABCAnalysis({ data }: ABCAnalysisProps) {
    // Mock data based on 80/15/5 rule if real data isn't fully structured for this view yet
    const segments = [
        {
            label: "A",
            description: "Лидеры продаж",
            percentage: 80,
            count: 12,
            revenue: "108,593 Br",
            color: "bg-purple-500",
            glow: "shadow-[0_0_15px_rgba(168,85,247,0.4)]",
            textColor: "text-purple-300"
        },
        {
            label: "B",
            description: "Средний сегмент",
            percentage: 15,
            count: 45,
            revenue: "20,361 Br",
            color: "bg-cyan-500",
            glow: "shadow-[0_0_15px_rgba(6,182,212,0.4)]",
            textColor: "text-cyan-300"
        },
        {
            label: "C",
            description: "Аутсайдеры",
            percentage: 5,
            count: 150,
            revenue: "6,787 Br",
            color: "bg-zinc-500",
            glow: "shadow-[0_0_15px_rgba(113,113,122,0.4)]",
            textColor: "text-zinc-300"
        }
    ];

    return (
        <div className="glass-panel p-8 rounded-[40px] border border-white/5 relative overflow-hidden h-full flex flex-col">
            {/* Decorative sheen */}
            <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/20 to-transparent" />

            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-white/5 border border-white/10 flex items-center justify-center shadow-inner">
                        <TrendingUp className="w-6 h-6 text-gray-200" />
                    </div>
                    <div>
                        <h3 className="text-xl font-medium text-white tracking-wide">ABC Анализ</h3>
                        <p className="text-sm text-gray-400">Вклад в выручку (Правило Парето)</p>
                    </div>
                </div>
            </div>

            {/* Content - Glass Columns */}
            <div className="flex-1 flex flex-col justify-center gap-6">
                {segments.map((segment) => (
                    <div key={segment.label} className="relative group">
                        {/* Label Row */}
                        <div className="flex items-end justify-between mb-2 text-sm">
                            <div className="flex items-center gap-2">
                                <span className={`font-bold text-lg ${segment.textColor}`}>{segment.label}</span>
                                <span className="text-gray-400 text-xs uppercase tracking-wide">{segment.description}</span>
                            </div>
                            <div className="text-right">
                                <span className="text-white font-mono">{segment.revenue}</span>
                            </div>
                        </div>

                        {/* Bar Container */}
                        <div className="h-4 bg-white/5 rounded-full overflow-hidden relative backdrop-blur-sm border border-white/5">
                            {/* The Bar */}
                            <div
                                className={`h-full rounded-full transition-all duration-1000 ease-out ${segment.color} ${segment.glow}`}
                                style={{ width: `${segment.percentage}%` }}
                            />
                        </div>

                        {/* Metrics Row */}
                        <div className="flex justify-between mt-2 text-[10px] text-gray-500 uppercase tracking-wider">
                            <span>{segment.percentage}% Выручки</span>
                            <span>{segment.count} Товаров</span>
                        </div>
                    </div>
                ))}
            </div>

            {/* Insight Note */}
            <div className="mt-8 pt-4 border-t border-white/5 flex gap-3 opacity-60">
                <Info className="h-4 w-4 text-cyan-400 mt-0.5" />
                <p className="text-xs text-gray-400 leading-relaxed">
                    Группа <strong className="text-gray-300">A</strong> формирует 80% выручки. Рекомендуется постоянный контроль остатков и маржинальности этих позиций.
                </p>
            </div>
        </div>
    );
}
