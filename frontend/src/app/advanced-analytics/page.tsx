"use client";

import { useEffect, useState } from "react";
import { AdvancedFilters, FilterChip } from "@/components/analytics/AdvancedFilters";
import { ABCXYZMatrix } from "@/components/analytics/ABCXYZMatrix";
import { PlanFactGauge } from "@/components/analytics/PlanFactGauge";
import { GeoMap } from "@/components/analytics/GeoMap";
import { BostonMatrix } from "@/components/analytics/BostonMatrix";
import { WhatIfSimulator } from "@/components/analytics/WhatIfSimulator";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown } from "lucide-react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://athletic-alignment-production-db41.up.railway.app";

export default function AdvancedAnalyticsPage() {
    const [filters, setFilters] = useState<FilterChip[]>([]);
    const [filterOptions, setFilterOptions] = useState<{
        regions: string[];
        categories: string[];
        agents: Array<{ id: string; name: string }>;
    }>({ regions: [], categories: [], agents: [] });

    const [abcXyzData, setAbcXyzData] = useState<any>(null);
    const [planFactData, setPlanFactData] = useState<any>(null);
    const [lflData, setLflData] = useState<any>(null);
    const [geoData, setGeoData] = useState<any>(null);
    const [bostonData, setBostonData] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    // Fetch filter options
    useEffect(() => {
        fetch(`${API_BASE_URL}/api/analytics/filter-options`)
            .then((res) => res.json())
            .then((data) => setFilterOptions(data))
            .catch((err) => console.error("Ошибка загрузки опций фильтрации:", err));
    }, []);

    // Fetch analytics data
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                // ABC-XYZ Матрица
                const abcXyzRes = await fetch(`${API_BASE_URL}/api/analytics/abc-xyz?days=90`);
                const abcXyz = await abcXyzRes.json();
                setAbcXyzData(abcXyz);

                // План-Факт
                const today = new Date();
                const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
                const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0);

                const planFactRes = await fetch(
                    `${API_BASE_URL}/api/analytics/plan-fact?period_start=${firstDay.toISOString().split("T")[0]}&period_end=${lastDay.toISOString().split("T")[0]}`
                );
                const planFact = await planFactRes.json();
                setPlanFactData(planFact);

                // LFL Сравнение (этот месяц vs прошлый месяц)
                const lastMonthFirst = new Date(today.getFullYear(), today.getMonth() - 1, 1);
                const lastMonthLast = new Date(today.getFullYear(), today.getMonth(), 0);

                const lflRes = await fetch(
                    `${API_BASE_URL}/api/analytics/lfl?period1_start=${firstDay.toISOString().split("T")[0]}&period1_end=${lastDay.toISOString().split("T")[0]}&period2_start=${lastMonthFirst.toISOString().split("T")[0]}&period2_end=${lastMonthLast.toISOString().split("T")[0]}`
                );
                const lfl = await lflRes.json();
                setLflData(lfl);

                // Гео визуализация
                const geoRes = await fetch(`${API_BASE_URL}/api/analytics/geo?days=90`);
                const geo = await geoRes.json();
                setGeoData(geo);

                // Бостонская матрица
                const bostonRes = await fetch(`${API_BASE_URL}/api/analytics/boston-matrix?days=90`);
                const boston = await bostonRes.json();
                setBostonData(boston);
            } catch (err) {
                console.error("Ошибка загрузки данных аналитики:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [filters]);

    const handleFiltersChange = (newFilters: FilterChip[]) => {
        setFilters(newFilters);
    };

    return (
        <div className="min-h-screen bg-zinc-950 p-6">
            <div className="max-w-[1600px] mx-auto space-y-6">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold text-white">Аналитика</h1>
                        <p className="text-zinc-500 mt-1">
                            Комплексный анализ продаж: ABC-XYZ, План-Факт и LFL метрики
                        </p>
                    </div>
                </div>

                {/* Advanced Filters */}
                <AdvancedFilters
                    onFiltersChange={handleFiltersChange}
                    availableRegions={filterOptions.regions}
                    availableCategories={filterOptions.categories}
                    availableAgents={filterOptions.agents}
                />

                {/* KPI Карточки с LFL */}
                {lflData && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {lflData.map((metric: any, idx: number) => (
                            <Card
                                key={idx}
                                className="bg-zinc-900/50 border-zinc-800 backdrop-blur-sm rounded-2xl p-6"
                            >
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm text-zinc-500">{metric.metric}</p>
                                        <p className="text-2xl font-bold text-white mt-1">
                                            {metric.period2_value.toLocaleString()}
                                        </p>
                                    </div>
                                    <Badge
                                        variant="secondary"
                                        className={`rounded-full px-2 py-1 ${metric.change_percent > 0
                                            ? "bg-green-500/20 text-green-300 border-green-500/30"
                                            : metric.change_percent < 0
                                                ? "bg-red-500/20 text-red-300 border-red-500/30"
                                                : "bg-zinc-600/20 text-zinc-400 border-zinc-600/30"
                                            }`}
                                    >
                                        {metric.change_percent > 0 ? (
                                            <TrendingUp className="h-3 w-3 mr-1 inline" />
                                        ) : metric.change_percent < 0 ? (
                                            <TrendingDown className="h-3 w-3 mr-1 inline" />
                                        ) : null}
                                        <span className="text-xs font-medium">
                                            {metric.change_percent > 0 ? "+" : ""}
                                            {metric.change_percent.toFixed(1)}% vs ПГ
                                        </span>
                                    </Badge>
                                </div>
                            </Card>
                        ))}
                    </div>
                )}

                {/* Bento Grid Layout - Phase 2 */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* ABC-XYZ Матрица - занимает 2 колонки */}
                    <div className="lg:col-span-2">
                        {abcXyzData && !loading ? (
                            <ABCXYZMatrix data={abcXyzData} />
                        ) : (
                            <Card className="bg-zinc-900/50 border-zinc-800 rounded-3xl p-6 h-[600px] flex items-center justify-center">
                                <div className="text-zinc-500">Загрузка ABC-XYZ Матрицы...</div>
                            </Card>
                        )}
                    </div>

                    {/* План-Факт Индикатор - занимает 1 колонку */}
                    <div className="lg:col-span-1">
                        {planFactData && !loading ? (
                            <PlanFactGauge data={planFactData} />
                        ) : (
                            <Card className="bg-zinc-900/50 border-zinc-800 rounded-3xl p-6 h-[600px] flex items-center justify-center">
                                <div className="text-zinc-500">Загрузка План-Факт...</div>
                            </Card>
                        )}
                    </div>
                </div>

                {/* Фаза 3: Гео + Бостонская матрица */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Гео визуализация */}
                    <div>
                        {geoData && !loading ? (
                            <GeoMap data={geoData} />
                        ) : (
                            <Card className="bg-zinc-900/50 border-zinc-800 rounded-3xl p-6 h-[400px] flex items-center justify-center">
                                <div className="text-zinc-500">Загрузка географии...</div>
                            </Card>
                        )}
                    </div>

                    {/* Бостонская матрица */}
                    <div>
                        {bostonData && !loading ? (
                            <BostonMatrix data={bostonData} />
                        ) : (
                            <Card className="bg-zinc-900/50 border-zinc-800 rounded-3xl p-6 h-[400px] flex items-center justify-center">
                                <div className="text-zinc-500">Загрузка Бостонской матрицы...</div>
                            </Card>
                        )}
                    </div>
                </div>

                {/* Фаза 3: What-If Симулятор */}
                <WhatIfSimulator
                    baseMetrics={{
                        revenue: lflData?.[0]?.period2_value || 0,
                        orders: 0,
                        quantity: 0,
                        customers: 0,
                        avg_check: 0,
                    }}
                />
            </div>
        </div>
    );
}
