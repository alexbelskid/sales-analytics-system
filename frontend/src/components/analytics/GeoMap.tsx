"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MapPin, TrendingUp } from "lucide-react";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";

interface GeoPoint {
    region: string;
    latitude?: number;
    longitude?: number;
    revenue: number;
    orders: number;
    customers: number;
    avg_check: number;
}

interface GeoMapProps {
    data: {
        points: GeoPoint[];
        total_revenue: number;
        total_orders: number;
        center?: { lat: number; lon: number };
    };
}

export function GeoMap({ data }: GeoMapProps) {
    const { points, total_revenue } = data;

    // Sort by revenue descending
    const sortedPoints = [...points].sort((a, b) => b.revenue - a.revenue);

    return (

        <div className="relative overflow-hidden rounded-[40px] border border-white/[0.08] backdrop-blur-[30px] shadow-[0_40px_80px_-20px_rgba(0,0,0,0.8),inset_0_0_40px_0_rgba(255,255,255,0.02)] p-8 flex flex-col highlight-none">
            {/* Decorative sheen */}
            <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/20 to-transparent" />
            <div className="absolute inset-0 bg-gradient-to-b from-white/[0.02] to-transparent pointer-events-none" />

            {/* Header */}
            <div className="flex items-center justify-between mb-8 shrink-0">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-white/5 border border-white/10 flex items-center justify-center shadow-inner">
                        <MapPin className="w-6 h-6 text-gray-200" />
                    </div>
                    <div>
                        <h3 className="text-xl font-medium text-white tracking-wide">География продаж</h3>
                        <p className="text-sm text-gray-400">
                            {points.length} регион{points.length !== 1 ? "ов" : ""} • {total_revenue.toLocaleString()} Br
                        </p>
                    </div>
                </div>
            </div>

            {/* Table View */}
            <div className="flex-1 min-h-0 overflow-hidden bg-white/[0.02] rounded-[24px] border border-white/5">
                <div className="h-full overflow-auto custom-scrollbar p-1">
                    <Table className="border-separate border-spacing-y-1">
                        <TableHeader className="sticky top-0 z-10 before:absolute before:inset-0 before:bg-black/40 before:backdrop-blur-md before:-z-10">
                            <TableRow className="border-none hover:bg-transparent">
                                <TableHead className="text-gray-400 font-medium py-3 px-4">Регион</TableHead>
                                <TableHead className="text-gray-400 text-right font-medium py-3 px-4">Выручка</TableHead>
                                <TableHead className="text-gray-400 text-right font-medium py-3 px-4">Заказы</TableHead>
                                <TableHead className="text-gray-400 text-right font-medium py-3 px-4">Клиенты</TableHead>
                                <TableHead className="text-gray-400 text-right font-medium py-3 px-4">Средний чек</TableHead>
                                <TableHead className="text-gray-400 text-right font-medium py-3 px-4">Доля</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {sortedPoints.length > 0 ? (
                                sortedPoints.map((point, idx) => {
                                    const share = (point.revenue / total_revenue * 100);
                                    return (
                                        <TableRow key={idx} className="group/row">
                                            <TableCell className="font-medium text-white flex items-center gap-3 py-2 px-4 rounded-l-2xl bg-white/[0.02] group-hover:bg-white/[0.06] transition-colors border-y border-l border-white/5 group-hover:border-white/10 h-16">
                                                {point.region !== 'Unknown' && (
                                                    <div className="w-8 h-8 rounded-full bg-white/5 border border-white/10 flex items-center justify-center group-hover/row:bg-white/10 transition-colors shrink-0">
                                                        <MapPin className="h-3.5 w-3.5 text-gray-400 group-hover/row:text-white" />
                                                    </div>
                                                )}
                                                <span className={`truncate ${point.region === 'Unknown' ? 'pl-2' : ''}`}>{point.region}</span>
                                            </TableCell>
                                            <TableCell className="text-right text-gray-200 font-light tracking-wide py-2 px-4 bg-white/[0.02] group-hover:bg-white/[0.06] transition-colors border-y border-white/5 group-hover:border-white/10 h-16">
                                                {point.revenue.toLocaleString()} Br
                                            </TableCell>
                                            <TableCell className="text-right text-gray-400 py-2 px-4 bg-white/[0.02] group-hover:bg-white/[0.06] transition-colors border-y border-white/5 group-hover:border-white/10 h-16">
                                                {point.orders}
                                            </TableCell>
                                            <TableCell className="text-right text-gray-400 py-2 px-4 bg-white/[0.02] group-hover:bg-white/[0.06] transition-colors border-y border-white/5 group-hover:border-white/10 h-16">
                                                {point.customers}
                                            </TableCell>
                                            <TableCell className="text-right text-gray-400 py-2 px-4 bg-white/[0.02] group-hover:bg-white/[0.06] transition-colors border-y border-white/5 group-hover:border-white/10 h-16">
                                                {point.avg_check.toLocaleString()} Br
                                            </TableCell>
                                            <TableCell className="text-right py-2 px-4 rounded-r-2xl bg-white/[0.02] group-hover:bg-white/[0.06] transition-colors border-y border-r border-white/5 group-hover:border-white/10 h-16">
                                                <Badge
                                                    variant="secondary"
                                                    className={`rounded-full px-2.5 py-0.5 border ${share >= 20
                                                        ? "bg-white/10 text-white border-white/20"
                                                        : share >= 10
                                                            ? "bg-white/5 text-gray-300 border-white/10"
                                                            : "bg-transparent text-gray-500 border-white/5"
                                                        }`}
                                                >
                                                    {share.toFixed(1)}%
                                                </Badge>
                                            </TableCell>
                                        </TableRow>
                                    );
                                })
                            ) : (
                                <TableRow>
                                    <TableCell colSpan={6} className="text-center text-gray-500 py-12">
                                        Нет данных по регионам
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </div>
            </div>

            {/* Summary */}
            {points.length > 0 && (
                <div className="mt-8 flex flex-wrap items-center gap-6 text-xs text-gray-400 border-t border-white/5 pt-6 shrink-0">
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-white border border-white/20 shadow-[0_0_8px_rgba(255,255,255,0.4)]"></div>
                        <span className="whitespace-nowrap tracking-wide">&gt;20% доли - лидеры</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-gray-400 border border-white/10"></div>
                        <span className="whitespace-nowrap tracking-wide">10-20% - средние</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-gray-700 border border-white/5"></div>
                        <span className="whitespace-nowrap tracking-wide">&lt;10% - малые</span>
                    </div>
                </div>
            )}
        </div>
    );
}
