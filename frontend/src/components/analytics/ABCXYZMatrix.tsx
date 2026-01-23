"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Maximize2, MoreVertical } from "lucide-react";
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"

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
    const [showModal, setShowModal] = useState(false);
    const [selectedZone, setSelectedZone] = useState<keyof typeof data.matrix | null>(null);

    // Filter logic: Show top 3 in cell, click for more
    const renderProductRow = (product: Product, color: string) => (
        <div key={product.product_id} className="flex items-center justify-between w-full py-1.5 border-b border-white/5 last:border-0 group/item">
            <span className="text-[10px] font-medium text-gray-300 truncate flex-1 min-w-0 mr-2 group-hover/item:text-white transition-colors" title={product.name}>
                {product.name}
            </span>
            <div className="flex items-center gap-2 shrink-0">
                <span className="text-[9px] text-gray-500 tabular-nums">
                    {(product.revenue / 1000).toFixed(0)}k
                </span>
            </div>
        </div>
    );

    const renderCell = (key: keyof typeof data.matrix) => {
        const products = data.matrix[key] || [];
        const topProducts = products.slice(0, 4); // List view, fit ~4 items
        // Map zone to color hint
        const colorHint = key.startsWith('A') ? 'rgba(168,85,247,0.4)' : key.startsWith('B') ? 'rgba(6,182,212,0.4)' : 'rgba(113,113,122,0.4)';

        return (
            <div
                key={key}
                onClick={() => { setSelectedZone(key); setShowModal(true); }}
                className="relative group h-full w-full border border-white/5 bg-white/[0.02] hover:bg-white/[0.05] transition-all duration-300 cursor-pointer flex flex-col p-3 overflow-hidden"
            >
                {/* Product List */}
                <div className="flex-1 w-full space-y-0.5">
                    {topProducts.length > 0 ? (
                        topProducts.map(p => renderProductRow(p, colorHint))
                    ) : (
                        <div className="h-full flex items-center justify-center text-[10px] text-gray-600">
                            Нет данных
                        </div>
                    )}
                </div>

                {/* Count / More Indicator */}
                <div className="flex items-center justify-between pt-2 border-t border-white/5 mt-auto">
                    <span className="text-[9px] text-gray-600 font-mono tracking-wider opacity-0 group-hover:opacity-100 transition-opacity">
                        {key}
                    </span>
                    {products.length > 4 && (
                        <span className="text-[9px] text-cyan-400 font-medium">
                            +{products.length - 4} ещё
                        </span>
                    )}
                    {products.length <= 4 && products.length > 0 && (
                        <span className="text-[9px] text-gray-500">
                            Всего: {products.length}
                        </span>
                    )}
                </div>
            </div>
        );
    };

    return (
        <div className="glass-panel p-8 rounded-[40px] border border-white/5 relative h-full flex flex-col hover:!transform-none hover:!shadow-none transition-none">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h3 className="text-xl font-medium text-white tracking-wide">Матрица ABC-XYZ</h3>
                    <p className="text-sm text-gray-400">
                        Глубокий анализ: Объём продаж (Vertical) vs Стабильность (Horizontal)
                    </p>
                </div>
                <div className="flex items-center gap-4 text-xs text-gray-500">
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-purple-400" />
                        <span>Высокий объём</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-cyan-400" />
                        <span>Средний объём</span>
                    </div>
                </div>
            </div>

            {/* Matrix Container with Labels */}
            <div className="flex-1 flex gap-4 min-h-0">
                {/* Y-Axis Labels (ABC - Volume) */}
                <div className="flex flex-col justify-between py-8 text-gray-400 text-xs font-bold w-6 shrink-0">
                    <div className="h-1/3 flex items-center justify-center -rotate-90">A</div>
                    <div className="h-1/3 flex items-center justify-center -rotate-90">B</div>
                    <div className="h-1/3 flex items-center justify-center -rotate-90">C</div>
                </div>

                {/* The Grid + X-Axis Labels */}
                <div className="flex-1 flex flex-col">
                    {/* The 3x3 Grid */}
                    <div className="flex-1 grid grid-cols-3 grid-rows-3 gap-1 rounded-2xl overflow-hidden border border-white/10 shadow-2xl bg-black/40">
                        {/* Row A */}
                        {renderCell("AX")} {renderCell("AY")} {renderCell("AZ")}
                        {/* Row B */}
                        {renderCell("BX")} {renderCell("BY")} {renderCell("BZ")}
                        {/* Row C */}
                        {renderCell("CX")} {renderCell("CY")} {renderCell("CZ")}
                    </div>

                    {/* X-Axis Labels (XYZ - Stability) */}
                    <div className="flex justify-between px-8 pt-4 text-gray-400 text-xs font-bold h-10 shrink-0">
                        <div className="w-1/3 flex justify-center text-center">
                            X<br /><span className="text-[9px] font-normal text-gray-600">Стабильные</span>
                        </div>
                        <div className="w-1/3 flex justify-center text-center">
                            Y<br /><span className="text-[9px] font-normal text-gray-600">Колеблющиеся</span>
                        </div>
                        <div className="w-1/3 flex justify-center text-center">
                            Z<br /><span className="text-[9px] font-normal text-gray-600">Случайные</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Modal for Details */}
            <Dialog open={showModal} onOpenChange={setShowModal}>
                <DialogContent className="glass-panel border-white/10 text-white max-w-2xl max-h-[80vh] overflow-y-auto">
                    <DialogHeader>
                        <DialogTitle className="text-2xl font-light">
                            Группа {selectedZone}
                        </DialogTitle>
                        <DialogDescription className="text-gray-400">
                            Полный список товаров в сегменте
                        </DialogDescription>
                    </DialogHeader>
                    <div className="mt-4 space-y-2">
                        {selectedZone && data.matrix[selectedZone]?.map((p) => (
                            <div key={p.product_id} className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/5">
                                <span className="text-sm font-medium">{p.name}</span>
                                <div className="flex items-center gap-6 text-sm text-gray-400">
                                    <span>{p.revenue.toLocaleString()} Br</span>
                                    <Badge variant="outline" className="text-[10px] border-white/10 text-gray-300">
                                        CV: {p.cv.toFixed(1)}
                                    </Badge>
                                </div>
                            </div>
                        ))}
                    </div>
                </DialogContent>
            </Dialog>
        </div>
    );
}
