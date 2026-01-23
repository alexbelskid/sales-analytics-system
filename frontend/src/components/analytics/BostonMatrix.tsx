"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, Star, HelpCircle, DollarSign, Dog } from "lucide-react";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";

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
    const { products, quadrant_counts } = data;
    const [showModal, setShowModal] = useState(false);
    const [selectedQuadrant, setSelectedQuadrant] = useState<keyof typeof quadrantConfig | null>(null);

    const renderProductRow = (product: BostonProduct) => (
        <div key={product.product_id} className="flex items-center justify-between w-full py-1.5 border-b border-white/5 last:border-0 group/item hover:bg-white/[0.02] px-1 transition-colors cursor-pointer">
            <span className="text-[10px] font-medium text-gray-300 truncate flex-1 min-w-0 mr-2 group-hover/item:text-white transition-colors" title={product.name}>
                {product.name}
            </span>
            <div className="flex items-center gap-2 shrink-0">
                <Badge variant="outline" className={`text-[9px] px-1 py-0 h-4 border-0 ${product.revenue_growth >= 0 ? 'bg-green-500/10 text-green-300' : 'bg-red-500/10 text-red-300'}`}>
                    {product.revenue_growth > 0 ? '+' : ''}{product.revenue_growth.toFixed(0)}%
                </Badge>
                <span className="text-[9px] text-gray-500 tabular-nums font-mono w-[30px] text-right">
                    {product.market_share.toFixed(1)}%
                </span>
            </div>
        </div>
    );

    const renderQuadrant = (quadrant: keyof typeof quadrant_counts) => {
        const config = quadrantConfig[quadrant];
        const Icon = config.icon;
        const allProducts = products.filter((p) => p.quadrant === quadrant);
        const topProducts = allProducts.slice(0, 4); // Limit to 4 for compact view
        const count = quadrant_counts[quadrant];

        return (
            <div
                onClick={() => { setSelectedQuadrant(quadrant); setShowModal(true); }}
                className="relative group w-full h-full flex flex-col pt-3 px-3 pb-0 cursor-pointer overflow-hidden transition-colors hover:bg-white/[0.02]"
            >
                {/* Header - Minimal */}
                <div className="flex items-center justify-between mb-2 shrink-0 px-1">
                    <div className="flex items-center gap-2">
                        <Icon className={`w-3 h-3 ${config.color}`} />
                        <span className="text-xs font-medium text-gray-300">{config.label}</span>
                    </div>
                    <span className="text-[10px] text-gray-600 font-mono group-hover:text-gray-400 transition-colors">
                        {count}
                    </span>
                </div>

                {/* Product List Lines - Fixed Top Items */}
                <div className="flex-1 w-full space-y-0.5">
                    {topProducts.length > 0 ? (
                        topProducts.map(p => renderProductRow(p))
                    ) : (
                        <div className="text-[10px] text-gray-600 italic py-8 text-center h-full flex items-center justify-center">
                            Нет данных
                        </div>
                    )}
                </div>

                {/* Footer / More Indicator */}
                <div className="flex items-center justify-between pt-2 border-t border-white/5 mt-auto pb-2 px-1">
                    <span className="text-[9px] text-gray-600 font-mono tracking-wider opacity-0 group-hover:opacity-100 transition-opacity">
                        ПОДРОБНЕЕ
                    </span>
                    {allProducts.length > 4 && (
                        <span className="text-[9px] text-cyan-400 font-medium">
                            +{allProducts.length - 4} ещё
                        </span>
                    )}
                </div>
            </div>
        );
    };

    return (
        <div className="glass-panel p-8 rounded-[40px] border border-white/5 relative h-full flex flex-col hover:!transform-none hover:!shadow-none transition-none">
            {/* Header */}
            <div className="flex items-center justify-between mb-8 shrink-0">
                <div>
                    <h3 className="text-xl font-medium text-white tracking-wide">BCG Matrix</h3>
                    <p className="text-sm text-gray-400">
                        Стратегический анализ: Рост (Vertical) vs Доля рынка (Horizontal)
                    </p>
                </div>
                <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span className="flex items-center gap-2">
                        <Star className="w-3 h-3 text-purple-400" />
                        <span>Лидеры</span>
                    </span>
                    <span className="flex items-center gap-2">
                        <DollarSign className="w-3 h-3 text-green-400" />
                        <span>Cash Cows</span>
                    </span>
                </div>
            </div>

            {/* Matrix Container */}
            <div className="flex-1 flex gap-4 min-h-0">
                {/* Y-Axis Labels (Growth) */}
                <div className="flex flex-col justify-between py-8 text-gray-400 text-xs font-bold w-6 shrink-0">
                    <div className="h-1/2 flex items-center justify-center -rotate-90 text-[10px] tracking-widest text-gray-500">ВЫСОКИЙ</div>
                    <div className="h-1/2 flex items-center justify-center -rotate-90 text-[10px] tracking-widest text-gray-600">НИЗКИЙ</div>
                </div>

                {/* The Grid + X-Axis Labels */}
                <div className="flex-1 flex flex-col">
                    {/* The 2x2 Grid */}
                    <div className="flex-1 grid grid-cols-2 grid-rows-2 gap-1 rounded-2xl overflow-hidden border border-white/10 shadow-2xl bg-black/40">
                        {/* Row 1 */}
                        <div className="relative border-r border-b border-white/5 bg-white/[0.02]">
                            {renderQuadrant("question_mark")}
                        </div>
                        <div className="relative border-b border-white/5 bg-white/[0.02]">
                            {renderQuadrant("star")}
                        </div>

                        {/* Row 2 */}
                        <div className="relative border-r border-white/5 bg-white/[0.02]">
                            {renderQuadrant("dog")}
                        </div>
                        <div className="relative bg-white/[0.02]">
                            {renderQuadrant("cash_cow")}
                        </div>
                    </div>

                    {/* X-Axis Labels (Share) */}
                    <div className="flex justify-between px-16 pt-4 text-gray-400 text-xs font-bold h-10 shrink-0">
                        <div className="w-1/2 flex justify-center text-center">
                            <span className="text-[10px] tracking-widest text-gray-600">НИЗКАЯ ДОЛЯ</span>
                        </div>
                        <div className="w-1/2 flex justify-center text-center">
                            <span className="text-[10px] tracking-widest text-gray-500">ВЫСОКАЯ ДОЛЯ</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Modal for Details */}
            <Dialog open={showModal} onOpenChange={setShowModal}>
                <DialogContent className="glass-panel border-white/10 text-white max-w-2xl max-h-[80vh] overflow-y-auto">
                    <DialogHeader>
                        <DialogTitle className="text-2xl font-light">
                            {selectedQuadrant && quadrantConfig[selectedQuadrant]?.label}
                        </DialogTitle>
                        <DialogDescription className="text-gray-400">
                            {selectedQuadrant && quadrantConfig[selectedQuadrant]?.description}
                        </DialogDescription>
                    </DialogHeader>
                    <div className="mt-4 space-y-2">
                        {selectedQuadrant && products
                            .filter(p => p.quadrant === selectedQuadrant)
                            .map((p) => (
                                <div key={p.product_id} className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/5">
                                    <span className="text-sm font-medium">{p.name}</span>
                                    <div className="flex items-center gap-6 text-sm text-gray-400">
                                        <div className="flex items-center gap-2">
                                            <TrendingUp className="w-3 h-3 text-gray-500" />
                                            <span>{p.revenue_growth > 0 ? '+' : ''}{p.revenue_growth.toFixed(1)}%</span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <span className="text-xs text-gray-500">Доля:</span>
                                            <span>{p.market_share.toFixed(1)}%</span>
                                        </div>
                                        <span className="font-mono">{p.revenue.toLocaleString()} Br</span>
                                    </div>
                                </div>
                            ))}
                    </div>
                </DialogContent>
            </Dialog>
        </div>
    );
}
