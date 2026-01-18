"use client";

import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { TrendingUp, TrendingDown, DollarSign, Users, Package } from "lucide-react";

interface ScenarioResult {
    scenario_name: string;
    base_revenue: number;
    projected_revenue: number;
    revenue_change: number;
    revenue_change_pct: number;
    base_orders: number;
    projected_orders: number;
    base_avg_check: number;
    projected_avg_check: number;
    impact_breakdown: {
        price_impact: number;
        volume_impact: number;
        customer_impact: number;
        total_impact: number;
    };
}

interface WhatIfSimulatorProps {
    baseMetrics?: {
        revenue: number;
        orders: number;
        quantity: number;
        customers: number;
        avg_check: number;
    };
    onSimulate?: (params: {
        price_change_pct: number;
        volume_change_pct: number;
        new_customers_pct: number;
    }) => void;
}

export function WhatIfSimulator({ baseMetrics, onSimulate }: WhatIfSimulatorProps) {
    const [priceChange, setPriceChange] = useState(0);
    const [volumeChange, setVolumeChange] = useState(0);
    const [customerChange, setCustomerChange] = useState(0);
    const [result, setResult] = useState<ScenarioResult | null>(null);

    const presets = [
        {
            name: "Рост цен 10%",
            description: "Повышение цен на 10%",
            params: { price_change_pct: 10, volume_change_pct: -5, new_customers_pct: 0 },
        },
        {
            name: "Агрессивный рост",
            description: "Снижение цен для роста объёмов",
            params: { price_change_pct: -15, volume_change_pct: 30, new_customers_pct: 0 },
        },
        {
            name: "Расширение базы",
            description: "Привлечение новых клиентов",
            params: { price_change_pct: 0, volume_change_pct: 0, new_customers_pct: 20 },
        },
    ];

    // Reactive calculation
    useEffect(() => {
        const base = baseMetrics?.revenue || 0;
        const projected = base * (1 + priceChange / 100) * (1 + volumeChange / 100) * (1 + customerChange / 100);
        const change = projected - base;
        const changePct = base > 0 ? (change / base) * 100 : 0;

        setResult({
            scenario_name: `Price ${priceChange > 0 ? '+' : ''}${priceChange}%, Volume ${volumeChange > 0 ? '+' : ''}${volumeChange}%, Customers ${customerChange > 0 ? '+' : ''}${customerChange}%`,
            base_revenue: base,
            projected_revenue: projected,
            revenue_change: change,
            revenue_change_pct: changePct,
            base_orders: baseMetrics?.orders || 0,
            projected_orders: Math.round((baseMetrics?.orders || 0) * (1 + customerChange / 100)),
            base_avg_check: baseMetrics?.avg_check || 0,
            projected_avg_check: (baseMetrics?.avg_check || 0) * (1 + priceChange / 100),
            impact_breakdown: {
                price_impact: base * (priceChange / 100),
                volume_impact: base * (volumeChange / 100),
                customer_impact: base * (customerChange / 100),
                total_impact: change,
            },
        });

        // Notify parent if needed
        if (onSimulate) {
            onSimulate({
                price_change_pct: priceChange,
                volume_change_pct: volumeChange,
                new_customers_pct: customerChange,
            });
        }
    }, [priceChange, volumeChange, customerChange, baseMetrics, onSimulate]);

    const applyPreset = (preset: typeof presets[0]) => {
        setPriceChange(preset.params.price_change_pct);
        setVolumeChange(preset.params.volume_change_pct);
        setCustomerChange(preset.params.new_customers_pct);
    };

    return (
        <Card className="bg-[#262626] border-[#333333] backdrop-blur-sm rounded-3xl p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-orange-500/20 flex items-center justify-center">
                        <TrendingUp className="w-5 h-5 text-orange-400" />
                    </div>
                    <div>
                        <h3 className="text-lg font-semibold text-white">What-If сценарии</h3>
                        <p className="text-xs text-zinc-500">Симуляция влияния на выручку</p>
                    </div>
                </div>
            </div>

            <Tabs defaultValue="custom" className="w-full">
                <TabsList className="grid w-full grid-cols-2 mb-6 h-auto min-h-[44px]">
                    <TabsTrigger value="custom" className="min-h-[44px]">Настройки</TabsTrigger>
                    <TabsTrigger value="presets" className="min-h-[44px]">Готовые</TabsTrigger>
                </TabsList>

                <TabsContent value="custom" className="space-y-6">
                    {/* Price Slider */}
                    <div className="space-y-2">
                        <div className="flex items-center justify-between">
                            <label className="text-sm text-zinc-400 flex items-center gap-2">
                                <DollarSign className="h-4 w-4" />
                                Цена
                            </label>
                            <Badge variant="secondary" className="rounded-full">
                                {priceChange > 0 ? "+" : ""}
                                {priceChange}%
                            </Badge>
                        </div>
                        <Slider
                            value={[priceChange]}
                            onValueChange={(v) => setPriceChange(v[0])}
                            min={-50}
                            max={50}
                            step={5}
                            className="w-full"
                        />
                    </div>

                    {/* Volume Slider */}
                    <div className="space-y-2">
                        <div className="flex items-center justify-between">
                            <label className="text-sm text-zinc-400 flex items-center gap-2">
                                <Package className="h-4 w-4" />
                                Объём
                            </label>
                            <Badge variant="secondary" className="rounded-full">
                                {volumeChange > 0 ? "+" : ""}
                                {volumeChange}%
                            </Badge>
                        </div>
                        <Slider
                            value={[volumeChange]}
                            onValueChange={(v) => setVolumeChange(v[0])}
                            min={-50}
                            max={50}
                            step={5}
                            className="w-full"
                        />
                    </div>

                    {/* Customer Slider */}
                    <div className="space-y-2">
                        <div className="flex items-center justify-between">
                            <label className="text-sm text-zinc-400 flex items-center gap-2">
                                <Users className="h-4 w-4" />
                                Клиенты
                            </label>
                            <Badge variant="secondary" className="rounded-full">
                                {customerChange > 0 ? "+" : ""}
                                {customerChange}%
                            </Badge>
                        </div>
                        <Slider
                            value={[customerChange]}
                            onValueChange={(v) => setCustomerChange(v[0])}
                            min={-50}
                            max={50}
                            step={5}
                            className="w-full"
                        />
                    </div>

                </TabsContent>

                <TabsContent value="presets" className="space-y-3">
                    {presets.map((preset, idx) => (
                        <button
                            key={idx}
                            onClick={() => applyPreset(preset)}
                            className="w-full p-4 rounded-xl border border-zinc-800 bg-zinc-900/50 hover:bg-zinc-800/50 transition-colors text-left min-h-[44px]"
                        >
                            <h4 className="font-semibold text-white text-sm mb-1">{preset.name}</h4>
                            <p className="text-xs text-zinc-500">{preset.description}</p>
                        </button>
                    ))}
                </TabsContent>
            </Tabs>

            {/* Results */}
            {result && (
                <div className="mt-6 pt-6 border-t border-zinc-800 space-y-4">
                    <h4 className="text-sm font-semibold text-white mb-3">Прогноз</h4>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div className="p-3 rounded-lg bg-zinc-800/50 border border-zinc-700">
                            <p className="text-xs text-zinc-500 mb-1">Базовая выручка</p>
                            <p className="text-lg font-bold text-white">
                                {result.base_revenue.toLocaleString()} Br
                            </p>
                        </div>

                        <div className="p-3 rounded-lg bg-zinc-800/50 border border-zinc-700">
                            <p className="text-xs text-zinc-500 mb-1">Прогноз выручки</p>
                            <p className="text-lg font-bold text-white">
                                {result.projected_revenue.toLocaleString()} Br
                            </p>
                        </div>
                    </div>

                    <div className="p-4 rounded-xl bg-gradient-to-r from-purple-500/10 to-cyan-500/10 border border-purple-500/30">
                        <div className="flex items-center justify-between">
                            <span className="text-sm text-zinc-300">Изменение выручки</span>
                            <Badge
                                variant="secondary"
                                className={`rounded-full text-sm px-3 py-1 ${result.revenue_change >= 0
                                    ? "bg-green-500/20 text-green-300 border-green-500/30"
                                    : "bg-red-500/20 text-red-300 border-red-500/30"
                                    }`}
                            >
                                {result.revenue_change >= 0 ? (
                                    <TrendingUp className="h-4 w-4 mr-1 inline" />
                                ) : (
                                    <TrendingDown className="h-4 w-4 mr-1 inline" />
                                )}
                                {result.revenue_change >= 0 ? "+" : ""}
                                {result.revenue_change_pct.toFixed(1)}%
                            </Badge>
                        </div>
                        <p className="text-2xl font-bold text-white mt-2">
                            {result.revenue_change >= 0 ? "+" : ""}{Math.abs(result.revenue_change).toLocaleString()} Br
                        </p>
                    </div>
                </div>
            )}
        </Card>
    );
}
