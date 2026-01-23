"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Maximize2, MoreVertical, LayoutDashboard } from "lucide-react";
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
                className="relative group h-full w-full rounded-xl border border-white/20 bg-white/[0.06] hover:bg-white/[0.12] hover:border-white/30 transition-colors duration-300 cursor-pointer flex flex-col p-3 overflow-hidden"
            >
                {/* Product List */}
                <div className="flex-1 w-full space-y-0.5">
                    {topProducts.length > 0 ? (
                        topProducts.map(p => renderProductRow(p, colorHint))
                    ) : (
                        <div className="h-full flex items-center justify-center text-[10px] text-gray-400">
                            Нет данных
                        </div>
                    )}
                </div>

                {/* Count / More Indicator */}
                <div className="flex items-center justify-between pt-2 border-t border-white/10 mt-auto">
                    <span className="text-[9px] text-gray-500 font-mono tracking-wider opacity-0 group-hover:opacity-100 transition-opacity">
                        {key}
                    </span>
                    {products.length > 4 && (
                        <span className="text-[9px] text-cyan-400 font-medium">
                            +{products.length - 4} ещё
                        </span>
                    )}
                    {products.length <= 4 && products.length > 0 && (
                        <span className="text-[9px] text-gray-400">
                            Всего: {products.length}
                        </span>
                    )}
                </div>
            </div>
        );
    };

    return (
        <div className="relative overflow-hidden rounded-[40px] border border-white/[0.08] backdrop-blur-[30px] shadow-[0_40px_80px_-20px_rgba(0,0,0,0.8),inset_0_0_40px_0_rgba(255,255,255,0.02)] p-8 h-full flex flex-col highlight-none">
            <div className="absolute inset-0 bg-gradient-to-b from-white/[0.05] to-transparent pointer-events-none" />
            {/* Header */}
            <div className="flex items-center justify-between mb-8 shrink-0">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-white/5 border border-white/10 flex items-center justify-center shadow-inner">
                        <LayoutDashboard className="w-6 h-6 text-gray-200" />
                    </div>
                    <div>
                        <h3 className="text-xl font-medium text-white tracking-wide">Матрица ABC-XYZ</h3>
                    </div>
                </div>
            </div>

            {/* Matrix Container with Labels */}
            <div className="flex-1 flex gap-4 min-h-0">
                {/* Y-Axis Labels (ABC - Volume) */}
                <div className="grid grid-rows-3 gap-2 text-gray-400 text-xs font-bold w-6 shrink-0">
                    <div className="flex items-center justify-center -rotate-90">A</div>
                    <div className="flex items-center justify-center -rotate-90">B</div>
                    <div className="flex items-center justify-center -rotate-90">C</div>
                </div>

                {/* The Grid + X-Axis Labels */}
                <div className="flex-1 flex flex-col gap-2">
                    {/* The 3x3 Grid */}
                    <div className="flex-1 grid grid-cols-3 grid-rows-3 gap-2">
                        {/* Row A */}
                        {renderCell("AX")} {renderCell("AY")} {renderCell("AZ")}
                        {/* Row B */}
                        {renderCell("BX")} {renderCell("BY")} {renderCell("BZ")}
                        {/* Row C */}
                        {renderCell("CX")} {renderCell("CY")} {renderCell("CZ")}
                    </div>

                    {/* X-Axis Labels (XYZ - Stability) */}
                    <div className="grid grid-cols-3 gap-2 text-gray-400 text-xs font-bold h-6 shrink-0 px-0">
                        <div className="flex items-center justify-center">X</div>
                        <div className="flex items-center justify-center">Y</div>
                        <div className="flex items-center justify-center">Z</div>
                    </div>
                </div>
            </div>

            {/* Modal for Details */}
            <Dialog open={showModal} onOpenChange={setShowModal}>
                <DialogContent className="fixed left-[50%] top-[50%] translate-x-[-50%] translate-y-[-50%] overflow-hidden border border-white/[0.1] backdrop-blur-[40px] shadow-2xl bg-black/40 text-white max-w-2xl max-h-[80vh] overflow-y-auto z-[100]">
                    <div className="absolute inset-0 bg-gradient-to-b from-white/[0.05] to-transparent pointer-events-none" />
                    <DialogHeader>
                        <DialogTitle className="text-2xl font-light">
                            Группа {selectedZone}
                        </DialogTitle>
                    </DialogHeader>
                    <div className="mt-4 space-y-2">
                        {selectedZone && data.matrix[selectedZone]?.map((p) => (
                            <div key={p.product_id} className="grid grid-cols-[1fr,auto] items-center gap-4 p-3 rounded-lg bg-white/5 border border-white/5 hover:border-white/20 transition-colors cursor-default">
                                <span className="text-sm font-medium truncate" title={p.name}>{p.name}</span>
                                <div className="flex items-center gap-4 shrink-0 justify-end w-[180px]">
                                    <span className="text-sm text-gray-400 font-mono w-[80px] text-right">{p.revenue.toLocaleString()} Br</span>
                                    <div className="w-[60px] flex justify-end">
                                        <Badge variant="outline" className="text-[10px] border-white/10 text-gray-300 h-5 px-1.5 min-w-[50px] justify-center">
                                            CV: {p.cv.toFixed(1)}
                                        </Badge>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </DialogContent>
            </Dialog>
        </div>
    );
}
