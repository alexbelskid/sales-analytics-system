"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, Target } from "lucide-react";

interface PlanFactGaugeProps {
    data: {
        period_start: string;
        period_end: string;
        metrics: Array<{
            metric_name: string;
            planned: number;
            actual: number;
            variance: number;
            variance_pct: number;
            completion_pct: number;
        }>;
        overall_completion: number;
        has_plan: boolean;
    };
}

export function PlanFactGauge({ data }: PlanFactGaugeProps) {
    const completion = data.overall_completion;
    const revenueMetric = data.metrics.find((m) => m.metric_name === "Выручка");

    // Calculate circle progress
    const radius = 70;
    const circumference = 2 * Math.PI * radius;
    const progress = (completion / 100) * circumference;

    // Determine color based on completion
    const getColor = (pct: number) => {
        if (pct >= 95) return { stroke: "#06b6d4", glow: "cyan" }; // Cyan
        if (pct >= 80) return { stroke: "#a855f7", glow: "purple" }; // Purple
        return { stroke: "#f97316", glow: "orange" }; // Orange
    };

    const colors = getColor(completion);

    return (
        <div className="glass-panel p-6 sm:p-8 rounded-[40px] border border-white/5 relative overflow-hidden h-full flex flex-col items-center justify-between aspect-square">
            {/* Decorative sheen */}
            <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/20 to-transparent" />

            {/* Header - Compact for square */}
            <div className="w-full flex items-start justify-between">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center shadow-inner">
                        <Target className="w-5 h-5 text-gray-200" />
                    </div>
                    <div>
                        <h3 className="text-lg font-medium text-white tracking-wide leading-tight">План-Факт</h3>
                        <p className="text-[10px] text-gray-400">
                            30 дней
                        </p>
                    </div>
                </div>
            </div>

            {/* Circular Gauge - Responsive */}
            <div className="relative flex items-center justify-center w-full max-w-[220px] aspect-square">
                <svg viewBox="0 0 220 220" className="w-full h-full transform -rotate-90">
                    {/* Background Circle */}
                    <circle
                        cx="110"
                        cy="110"
                        r={radius}
                        stroke="rgba(255,255,255,0.05)"
                        strokeWidth="8"
                        fill="none"
                    />
                    {/* Progress Circle */}
                    <circle
                        cx="110"
                        cy="110"
                        r={radius}
                        stroke={colors.stroke}
                        strokeWidth="8"
                        fill="none"
                        strokeDasharray={circumference}
                        strokeDashoffset={circumference - progress}
                        strokeLinecap="round"
                        className="transition-all duration-1000 ease-out"
                        style={{
                            filter: `drop-shadow(0 0 10px ${colors.stroke}60)`,
                        }}
                    />
                </svg>

                {/* Center Content */}
                <div className="absolute inset-0 flex flex-col items-center justify-center transform translate-y-1">
                    <div className="text-4xl lg:text-5xl font-light text-white tracking-tighter">
                        {completion.toFixed(1)}<span className="text-xl lg:text-2xl text-gray-500">%</span>
                    </div>
                    {revenueMetric && revenueMetric.variance_pct !== 0 && (
                        <div className={`flex items-center gap-1 mt-2 text-xs font-medium px-2 py-0.5 rounded-full
                            ${revenueMetric.variance_pct > 0 ? "bg-green-500/10 text-green-300" : "bg-red-500/10 text-red-300"}`}>
                            {revenueMetric.variance_pct > 0 ? "+" : ""}{revenueMetric.variance_pct.toFixed(1)}%
                        </div>
                    )}
                </div>
            </div>

            {/* Bottom Metrics - Simplified for Square */}
            <div className="w-full grid grid-cols-2 gap-4 pt-4 border-t border-white/5">
                <div className="text-center">
                    <p className="text-[10px] uppercase tracking-widest text-gray-500 mb-1">План</p>
                    <p className="text-sm font-medium text-white">{revenueMetric ? (revenueMetric.planned / 1000).toFixed(0) : 0}k</p>
                </div>
                <div className="text-center">
                    <p className="text-[10px] uppercase tracking-widest text-gray-500 mb-1">Факт</p>
                    <p className="text-sm font-medium text-white">{revenueMetric ? (revenueMetric.actual / 1000).toFixed(0) : 0}k</p>
                </div>
            </div>
        </div>
    );
}
