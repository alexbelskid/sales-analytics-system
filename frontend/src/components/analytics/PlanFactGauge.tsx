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
        <Card className="bg-zinc-900/50 border-zinc-800 backdrop-blur-sm rounded-3xl p-6 h-full flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center">
                        <Target className="w-5 h-5 text-purple-400" />
                    </div>
                    <div>
                        <h3 className="text-lg font-semibold text-white">План-Факт</h3>
                        <p className="text-xs text-zinc-500">
                            {new Date(data.period_start).toLocaleDateString()} -{" "}
                            {new Date(data.period_end).toLocaleDateString()}
                        </p>
                    </div>
                </div>
            </div>

            {/* Circular Gauge */}
            <div className="flex-1 flex items-center justify-center">
                <div className="relative">
                    <svg width="200" height="200" className="transform -rotate-90">
                        {/* Background Circle */}
                        <circle
                            cx="100"
                            cy="100"
                            r={radius}
                            stroke="#27272a"
                            strokeWidth="12"
                            fill="none"
                        />
                        {/* Progress Circle */}
                        <circle
                            cx="100"
                            cy="100"
                            r={radius}
                            stroke={colors.stroke}
                            strokeWidth="12"
                            fill="none"
                            strokeDasharray={circumference}
                            strokeDashoffset={circumference - progress}
                            strokeLinecap="round"
                            className="transition-all duration-1000 ease-out"
                            style={{
                                filter: `drop-shadow(0 0 8px ${colors.stroke}40)`,
                            }}
                        />
                    </svg>

                    {/* Center Content */}
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <div className="text-4xl font-bold text-white">
                            {completion.toFixed(1)}%
                        </div>
                        <div className="text-xs text-zinc-500 mt-1">Выполнение</div>
                    </div>
                </div>
            </div>

            {/* LFL Badge */}
            {revenueMetric && revenueMetric.variance_pct !== 0 && (
                <div className="mt-4 flex items-center justify-center">
                    <Badge
                        variant="secondary"
                        className={`rounded-full px-3 py-1 ${revenueMetric.variance_pct > 0
                            ? "bg-green-500/20 text-green-300 border-green-500/30"
                            : "bg-red-500/20 text-red-300 border-red-500/30"
                            }`}
                    >
                        {revenueMetric.variance_pct > 0 ? (
                            <TrendingUp className="h-3 w-3 mr-1" />
                        ) : (
                            <TrendingDown className="h-3 w-3 mr-1" />
                        )}
                        <span className="text-xs font-medium">
                            {revenueMetric.variance_pct > 0 ? "+" : ""}
                            {revenueMetric.variance_pct.toFixed(1)}% vs ПГ
                        </span>
                    </Badge>
                </div>
            )}

            {/* Metrics */}
            <div className="mt-6 space-y-3">
                {revenueMetric && (
                    <>
                        <div className="flex items-center justify-between text-sm">
                            <span className="text-zinc-400">План:</span>
                            <span className="text-white font-semibold">
                                {revenueMetric.planned.toLocaleString()} Br
                            </span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                            <span className="text-zinc-400">Факт:</span>
                            <span className="text-white font-semibold">
                                {revenueMetric.actual.toLocaleString()} Br
                            </span>
                        </div>
                        {/* Progress Bar */}
                        <div className="w-full h-2 bg-zinc-800 rounded-full overflow-hidden">
                            <div
                                className="h-full rounded-full transition-all duration-500"
                                style={{
                                    width: `${Math.min(completion, 100)}%`,
                                    background: `linear-gradient(90deg, ${colors.stroke}, ${colors.stroke}80)`,
                                }}
                            />
                        </div>
                    </>
                )}
            </div>

            {/* No Plan Warning */}
            {!data.has_plan && (
                <div className="mt-4 p-3 rounded-lg bg-orange-500/10 border border-orange-500/30">
                    <p className="text-xs text-orange-300">Нет данных плана для этого периода</p>
                </div>
            )}
        </Card>
    );
}
