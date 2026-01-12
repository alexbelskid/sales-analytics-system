"use client";

import { useEffect, useState } from "react";
import { AdvancedFilters, FilterChip } from "@/components/analytics/AdvancedFilters";
import { ABCXYZMatrix } from "@/components/analytics/ABCXYZMatrix";
import { PlanFactGauge } from "@/components/analytics/PlanFactGauge";
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
    const [loading, setLoading] = useState(true);

    // Fetch filter options
    useEffect(() => {
        fetch(`${API_BASE_URL}/api/analytics/filter-options`)
            .then((res) => res.json())
            .then((data) => setFilterOptions(data))
            .catch((err) => console.error("Failed to fetch filter options:", err));
    }, []);

    // Fetch analytics data
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                // ABC-XYZ Matrix
                const abcXyzRes = await fetch(`${API_BASE_URL}/api/analytics/abc-xyz?days=90`);
                const abcXyz = await abcXyzRes.json();
                setAbcXyzData(abcXyz);

                // Plan-Fact
                const today = new Date();
                const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
                const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0);

                const planFactRes = await fetch(
                    `${API_BASE_URL}/api/analytics/plan-fact?period_start=${firstDay.toISOString().split("T")[0]}&period_end=${lastDay.toISOString().split("T")[0]}`
                );
                const planFact = await planFactRes.json();
                setPlanFactData(planFact);

                // LFL Comparison (this month vs last month)
                const lastMonthFirst = new Date(today.getFullYear(), today.getMonth() - 1, 1);
                const lastMonthLast = new Date(today.getFullYear(), today.getMonth(), 0);

                const lflRes = await fetch(
                    `${API_BASE_URL}/api/analytics/lfl?period1_start=${firstDay.toISOString().split("T")[0]}&period1_end=${lastDay.toISOString().split("T")[0]}&period2_start=${lastMonthFirst.toISOString().split("T")[0]}&period2_end=${lastMonthLast.toISOString().split("T")[0]}`
                );
                const lfl = await lflRes.json();
                setLflData(lfl);
            } catch (err) {
                console.error("Failed to fetch analytics data:", err);
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
                        <h1 className="text-3xl font-bold text-white">Advanced Analytics</h1>
                        <p className="text-zinc-500 mt-1">
                            Comprehensive sales analysis with ABC-XYZ, Plan-Fact, and LFL metrics
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

                {/* KPI Cards with LFL */}
                {lflData && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {lflData.map((metric: any, idx: number) => (
                            <Card
                                key={idx}
                                className="bg-zinc-900/50 border-zinc-800 backdrop-blur-sm rounded-2xl p-6"
                            >
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm text-zinc-500">{metric.metric_name}</p>
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
                                            {metric.change_percent.toFixed(1)}% vs LY
                                        </span>
                                    </Badge>
                                </div>
                            </Card>
                        ))}
                    </div>
                )}

                {/* Bento Grid Layout */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* ABC-XYZ Matrix - Takes 2 columns */}
                    <div className="lg:col-span-2">
                        {abcXyzData && !loading ? (
                            <ABCXYZMatrix data={abcXyzData} />
                        ) : (
                            <Card className="bg-zinc-900/50 border-zinc-800 rounded-3xl p-6 h-[600px] flex items-center justify-center">
                                <div className="text-zinc-500">Loading ABC-XYZ Matrix...</div>
                            </Card>
                        )}
                    </div>

                    {/* Plan-Fact Gauge - Takes 1 column */}
                    <div className="lg:col-span-1">
                        {planFactData && !loading ? (
                            <PlanFactGauge data={planFactData} />
                        ) : (
                            <Card className="bg-zinc-900/50 border-zinc-800 rounded-3xl p-6 h-[600px] flex items-center justify-center">
                                <div className="text-zinc-500">Loading Plan-Fact...</div>
                            </Card>
                        )}
                    </div>
                </div>

                {/* Pivot Table Placeholder */}
                <Card className="bg-zinc-900/50 border-zinc-800 backdrop-blur-sm rounded-3xl p-6">
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-cyan-500/20 flex items-center justify-center">
                                <svg
                                    className="w-5 h-5 text-cyan-400"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
                                    />
                                </svg>
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold text-white">Comprehensive Sales Pivot</h3>
                                <p className="text-xs text-zinc-500">Drag dimensions to reorganize data</p>
                            </div>
                        </div>
                    </div>

                    {/* Dimension Pills */}
                    <div className="flex flex-wrap gap-2 mb-4">
                        {["Category", "Region", "Sales Rep", "Product Group", "Time Period"].map((dim) => (
                            <Badge
                                key={dim}
                                variant="secondary"
                                className="rounded-full bg-purple-500/20 text-purple-300 border-purple-500/30 px-3 py-1.5 cursor-move hover:bg-purple-500/30 transition-colors"
                            >
                                {dim}
                            </Badge>
                        ))}
                    </div>

                    {/* Placeholder Table */}
                    <div className="text-center text-zinc-600 py-12">
                        <p className="text-sm">Pivot Table component coming soon...</p>
                        <p className="text-xs mt-2">Will support multi-dimensional data aggregation</p>
                    </div>
                </Card>
            </div>
        </div>
    );
}
