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
        <Card className="bg-zinc-900/50 border-zinc-800 backdrop-blur-sm rounded-3xl p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-cyan-500/20 flex items-center justify-center">
                        <MapPin className="w-5 h-5 text-cyan-400" />
                    </div>
                    <div>
                        <h3 className="text-lg font-semibold text-white">География продаж</h3>
                        <p className="text-xs text-zinc-500">
                            {points.length} регион{points.length !== 1 ? "ов" : ""} • ₽{total_revenue.toLocaleString()}
                        </p>
                    </div>
                </div>
            </div>

            {/* Table View */}
            <div className="rounded-xl border border-zinc-800 overflow-hidden">
                <Table>
                    <TableHeader>
                        <TableRow className="border-zinc-800 hover:bg-zinc-800/50">
                            <TableHead className="text-zinc-400">Регион</TableHead>
                            <TableHead className="text-zinc-400 text-right">Выручка</TableHead>
                            <TableHead className="text-zinc-400 text-right">Заказы</TableHead>
                            <TableHead className="text-zinc-400 text-right">Клиенты</TableHead>
                            <TableHead className="text-zinc-400 text-right">Средний чек</TableHead>
                            <TableHead className="text-zinc-400 text-right">Доля</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {sortedPoints.length > 0 ? (
                            sortedPoints.map((point, idx) => {
                                const share = (point.revenue / total_revenue * 100);
                                return (
                                    <TableRow key={idx} className="border-zinc-800 hover:bg-zinc-800/30">
                                        <TableCell className="font-medium text-white flex items-center gap-2">
                                            <MapPin className="h-4 w-4 text-cyan-400" />
                                            {point.region}
                                        </TableCell>
                                        <TableCell className="text-right text-white">
                                            ₽{point.revenue.toLocaleString()}
                                        </TableCell>
                                        <TableCell className="text-right text-zinc-400">
                                            {point.orders}
                                        </TableCell>
                                        <TableCell className="text-right text-zinc-400">
                                            {point.customers}
                                        </TableCell>
                                        <TableCell className="text-right text-zinc-400">
                                            ₽{point.avg_check.toLocaleString()}
                                        </TableCell>
                                        <TableCell className="text-right">
                                            <Badge
                                                variant="secondary"
                                                className={`rounded-full ${share >= 20
                                                        ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/30"
                                                        : share >= 10
                                                            ? "bg-purple-500/20 text-purple-300 border-purple-500/30"
                                                            : "bg-zinc-600/20 text-zinc-400 border-zinc-600/30"
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
                                <TableCell colSpan={6} className="text-center text-zinc-500 py-8">
                                    Нет данных по регионам
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </div>

            {/* Summary */}
            {points.length > 0 && (
                <div className="mt-6 flex items-center gap-4 text-sm">
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-cyan-500"></div>
                        <span className="text-zinc-400">&gt;20% доли - лидеры</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-purple-500"></div>
                        <span className="text-zinc-400">10-20% - средние</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-zinc-600"></div>
                        <span className="text-zinc-400">&lt;10% - малые</span>
                    </div>
                </div>
            )}
        </Card>
    );
}
