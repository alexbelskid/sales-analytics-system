"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, Star, HelpCircle, DollarSign, Dog } from "lucide-react";

interface BostonProduct {
    product_id: string;
    name: string;
    category?: string;
    revenue: number;
    revenue_growth: number;
    market_share: number;
    quadrant: "star" | "question_mark" | "cash_cow" | "dog";
}

interface BostonMatrixProps {
    data: {
        products: BostonProduct[];
        quadrant_counts: {
            star: number;
            question_mark: number;
            cash_cow: number;
            dog: number;
        };
        thresholds: {
            growth: number;
            share: number;
        };
        total_revenue: number;
    };
}

const quadrantConfig = {
    star: {
        icon: Star,
        label: "Звёзды",
        description: "Высокий рост + Высокая доля",
        color: "text-purple-400",
        bgColor: "bg-purple-500/20",
        borderColor: "border-purple-500/30",
    },
    question_mark: {
        icon: HelpCircle,
        label: "Вопросы",
        description: "Высокий рост + Низкая доля",
        color: "text-cyan-400",
        bgColor: "bg-cyan-500/20",
        borderColor: "border-cyan-500/30",
    },
    cash_cow: {
        icon: DollarSign,
        label: "Дойные коровы",
        description: "Низкий рост + Высокая доля",
        color: "text-green-400",
        bgColor: "bg-green-500/20",
        borderColor: "border-green-500/30",
    },
    dog: {
        icon: Dog,
        label: "Собаки",
        description: "Низкий рост + Низкая доля",
        color: "text-zinc-400",
        bgColor: "bg-zinc-600/20",
        borderColor: "border-zinc-600/30",
    },
};

export function BostonMatrix({ data }: BostonMatrixProps) {
    const { products, quadrant_counts, thresholds } = data;

    const getQuadrantProducts = (quadrant: keyof typeof quadrant_counts) => {
        return products.filter((p) => p.quadrant === quadrant).slice(0, 5);
    };

    const renderQuadrant = (quadrant: keyof typeof quadrant_counts) => {
        const config = quadrantConfig[quadrant];
        const Icon = config.icon;
        const quadrantProducts = getQuadrantProducts(quadrant);
        const count = quadrant_counts[quadrant];

        return (
            <div
                className={`rounded-2xl border ${config.bgColor} ${config.borderColor} p-4 min-h-[200px] flex flex-col`}
            >
                {/* Header */}
                <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                        <Icon className={`h-5 w-5 ${config.color}`} />
                        <h4 className="font-semibold text-white text-sm">{config.label}</h4>
                    </div>
                    <Badge variant="outline" className="text-xs">
                        {count}
                    </Badge>
                </div>

                <p className="text-xs text-zinc-500 mb-4">{config.description}</p>

                {/* Products */}
                <div className="space-y-2 flex-1">
                    {quadrantProducts.length > 0 ? (
                        quadrantProducts.map((product) => (
                            <div
                                key={product.product_id}
                                className="bg-zinc-900/50 rounded-lg p-2 border border-zinc-800"
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex-1 min-w-0">
                                        <p className="text-xs font-medium text-white truncate">
                                            {product.name}
                                        </p>
                                        {product.category && (
                                            <p className="text-[10px] text-zinc-500 truncate">{product.category}</p>
                                        )}
                                    </div>
                                    <div className="ml-2 flex flex-col items-end gap-1">
                                        <Badge
                                            variant="secondary"
                                            className={`text-[10px] px-1.5 py-0 ${product.revenue_growth >= 0
                                                ? "bg-green-500/20 text-green-300 border-green-500/30"
                                                : "bg-red-500/20 text-red-300 border-red-500/30"
                                                }`}
                                        >
                                            {product.revenue_growth >= 0 ? "+" : ""}
                                            {product.revenue_growth.toFixed(1)}%
                                        </Badge>
                                        <span className="text-[10px] text-zinc-500">
                                            {product.market_share.toFixed(1)}% доли
                                        </span>
                                    </div>
                                </div>
                            </div>
                        ))
                    ) : (
                        <p className="text-xs text-zinc-600 text-center py-4">Нет продуктов</p>
                    )}
                </div>
            </div>
        );
    };

    return (
        <Card className="bg-zinc-900/50 border-zinc-800 backdrop-blur-sm rounded-3xl p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center">
                        <svg
                            className="w-5 h-5 text-purple-400"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                            />
                        </svg>
                    </div>
                    <div>
                        <h3 className="text-lg font-semibold text-white">Boston Matrix (BCG)</h3>
                        <p className="text-xs text-zinc-500">
                            {products.length} продуктов классифицировано
                        </p>
                    </div>
                </div>
            </div>

            {/* 2x2 Matrix Grid - stacks on very small screens */}
            <div className="grid grid-cols-1 min-[400px]:grid-cols-2 gap-3 md:gap-4">
                {/* Top row: Question Marks | Stars */}
                {renderQuadrant("question_mark")}
                {renderQuadrant("star")}

                {/* Bottom row: Dogs | Cash Cows */}
                {renderQuadrant("dog")}
                {renderQuadrant("cash_cow")}
            </div>

            {/* Axis Labels */}
            <div className="mt-6 grid grid-cols-2 gap-4 text-xs text-zinc-500">
                <div className="text-center">← Низкая доля рынка</div>
                <div className="text-center">Высокая доля рынка →</div>
            </div>

            <div className="mt-2 text-center text-xs text-zinc-500">
                ↑ Высокий рост выручки | Низкий рост ↓
            </div>

            {/* Thresholds */}
            <div className="mt-6 pt-4 border-t border-zinc-800 flex items-center gap-4 text-xs">
                <span className="text-zinc-400">
                    Порог роста: <span className="text-white">{thresholds.growth}%</span>
                </span>
                <span className="text-zinc-400">
                    Порог доли: <span className="text-white">{thresholds.share}%</span>
                </span>
            </div>
        </Card>
    );
}
