"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MoreVertical } from "lucide-react";
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip";

interface Product {
    product_id: string;
    name: string;
    revenue: number;
    abc_class: "A" | "B" | "C";
    xyz_class: "X" | "Y" | "Z";
    cv: number;
}

interface ABCXYZMatrixProps {
    data: {
        matrix: {
            AX: Product[];
            AY: Product[];
            AZ: Product[];
            BX: Product[];
            BY: Product[];
            BZ: Product[];
            CX: Product[];
            CY: Product[];
            CZ: Product[];
        };
        summary: {
            total_products: number;
            abc_distribution: { A: number; B: number; C: number };
            xyz_distribution: { X: number; Y: number; Z: number };
        };
    };
}

const cellColors = {
    AX: "bg-purple-500/20 border-purple-500/40",
    AY: "bg-purple-400/20 border-purple-400/40",
    AZ: "bg-purple-300/20 border-purple-300/40",
    BX: "bg-cyan-500/20 border-cyan-500/40",
    BY: "bg-cyan-400/20 border-cyan-400/40",
    BZ: "bg-cyan-300/20 border-cyan-300/40",
    CX: "bg-zinc-600/20 border-zinc-600/40",
    CY: "bg-zinc-500/20 border-zinc-500/40",
    CZ: "bg-zinc-400/20 border-zinc-400/40",
};

const bubbleColors = {
    AX: "bg-purple-500",
    AY: "bg-purple-400",
    AZ: "bg-purple-300",
    BX: "bg-cyan-500",
    BY: "bg-cyan-400",
    BZ: "bg-cyan-300",
    CX: "bg-zinc-600",
    CY: "bg-zinc-500",
    CZ: "bg-zinc-400",
};

export function ABCXYZMatrix({ data }: ABCXYZMatrixProps) {
    const renderCell = (key: keyof typeof data.matrix, abcClass: string, xyzClass: string) => {
        const products = data.matrix[key] || [];
        const topProducts = products.slice(0, 3);

        return (
            <div
                key={key}
                className={`relative rounded-2xl p-4 border ${cellColors[key]} backdrop-blur-sm min-h-[140px] flex flex-col`}
            >
                {/* Cell Label */}
                <div className="absolute top-2 left-2 flex items-center gap-1">
                    <Badge variant="outline" className="text-[10px] font-mono px-1.5 py-0.5 border-zinc-700">
                        {key}
                    </Badge>
                </div>

                {/* Products as Bubbles */}
                <div className="flex-1 flex flex-wrap items-center justify-center gap-2 mt-6">
                    {topProducts.length > 0 ? (
                        topProducts.map((product, idx) => {
                            const size = idx === 0 ? "w-16 h-16" : idx === 1 ? "w-12 h-12" : "w-10 h-10";
                            return (
                                <TooltipProvider key={product.product_id}>
                                    <Tooltip>
                                        <TooltipTrigger>
                                            <div
                                                className={`${size} ${bubbleColors[key]} rounded-full flex items-center justify-center text-white font-semibold text-xs shadow-lg hover:scale-110 transition-transform cursor-pointer`}
                                            >
                                                {product.name.substring(0, 2).toUpperCase()}
                                            </div>
                                        </TooltipTrigger>
                                        <TooltipContent className="bg-zinc-900 border-zinc-800">
                                            <div className="space-y-1">
                                                <p className="font-semibold text-sm">{product.name}</p>
                                                <p className="text-xs text-zinc-400">
                                                    Выручка: {product.revenue.toLocaleString()} ₽
                                                </p>
                                                <p className="text-xs text-zinc-400">КВ: {product.cv}%</p>
                                            </div>
                                        </TooltipContent>
                                    </Tooltip>
                                </TooltipProvider>
                            );
                        })
                    ) : (
                        <div className="text-xs text-zinc-600 text-center">Нет продуктов</div>
                    )}
                </div>

                {/* Product Count */}
                {products.length > 0 && (
                    <div className="text-[10px] text-zinc-500 text-center mt-2">
                        {products.length} продукт{products.length === 1 ? "" : products.length >= 2 && products.length <= 4 ? "а" : "ов"}
                    </div>
                )}
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
                        <h3 className="text-lg font-semibold text-white">Матрица ABC-XYZ продуктов</h3>
                        <p className="text-xs text-zinc-500">
                            {data.summary.total_products} продуктов классифицировано
                        </p>
                    </div>
                </div>
                <button className="p-2 hover:bg-zinc-800 rounded-lg transition-colors">
                    <MoreVertical className="h-4 w-4 text-zinc-400" />
                </button>
            </div>

            {/* Matrix Grid */}
            <div className="grid grid-cols-3 gap-3">
                {/* Row A */}
                {renderCell("AX", "A", "X")}
                {renderCell("AY", "A", "Y")}
                {renderCell("AZ", "A", "Z")}

                {/* Row B */}
                {renderCell("BX", "B", "X")}
                {renderCell("BY", "B", "Y")}
                {renderCell("BZ", "B", "Z")}

                {/* Row C */}
                {renderCell("CX", "C", "X")}
                {renderCell("CY", "C", "Y")}
                {renderCell("CZ", "C", "Z")}
            </div>

            {/* Axis Labels */}
            <div className="grid grid-cols-3 gap-3 mt-2">
                <div className="text-center text-xs font-medium text-zinc-500">X (Стабильный)</div>
                <div className="text-center text-xs font-medium text-zinc-500">Y (Умеренный)</div>
                <div className="text-center text-xs font-medium text-zinc-500">Z (Переменный)</div>
            </div>

            {/* Legend */}
            <div className="mt-6 pt-4 border-t border-zinc-800 flex items-center justify-between text-xs">
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-purple-500"></div>
                        <span className="text-zinc-400">A: Топ 80% выручки</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-cyan-500"></div>
                        <span className="text-zinc-400">B: Следующие 15% выручки</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-zinc-600"></div>
                        <span className="text-zinc-400">C: Последние 5% выручки</span>
                    </div>
                </div>
            </div>
        </Card>
    );
}
