"use client";

import { useEffect, useState } from "react";
import { AdvancedFilters, FilterChip } from "@/components/analytics/AdvancedFilters";
import { ABCXYZMatrix } from "@/components/analytics/ABCXYZMatrix";
import { GeoMap } from "@/components/analytics/GeoMap";
import { BostonMatrix } from "@/components/analytics/BostonMatrix";
import { WhatIfSimulator } from "@/components/analytics/WhatIfSimulator";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

// Use empty string for client-side to leverage Next.js rewrites
const API_BASE_URL = "";

// Glass Panel Helper
function AnalyticsCard({ children, className = "" }: { children: React.ReactNode; className?: string }) {
    return (
        <div className={`glass-panel p-6 ${className}`}>
            {children}
        </div>
    );
}

export default function AdvancedAnalyticsPage() {
    const [filters, setFilters] = useState<FilterChip[]>([]);
    const [filterOptions, setFilterOptions] = useState<{
        regions: string[];
        categories: string[];
        agents: Array<{ id: string; name: string }>;
    }>({ regions: [], categories: [], agents: [] });

    // Data states
    const [abcXyzData, setAbcXyzData] = useState<any>(null);
    const [geoData, setGeoData] = useState<any>(null);
    const [lflData, setLflData] = useState<any>(null);
    const [bostonData, setBostonData] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    // Initial Data Fetch
    useEffect(() => {
        // Options
        fetch(`${API_BASE_URL}/api/analytics/filter-options`)
            .then((res) => res.json())
            .then((data) => setFilterOptions(data))
            .catch((err) => console.error("Filter options error:", err));

        // Main Data
        const fetchData = async () => {
            setLoading(true);
            try {
                // ABC-XYZ
                const abcXyzRes = await fetch(`${API_BASE_URL}/api/analytics/abc-xyz?days=90`);
                setAbcXyzData(await abcXyzRes.json());

                // Geo
                const geoRes = await fetch(`${API_BASE_URL}/api/analytics/geo?days=90`);
                setGeoData(await geoRes.json());

                // LFL
                const today = new Date();
                const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
                const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0);
                const lastMonthFirst = new Date(today.getFullYear(), today.getMonth() - 1, 1);
                const lastMonthLast = new Date(today.getFullYear(), today.getMonth(), 0);
                const lflRes = await fetch(
                    `${API_BASE_URL}/api/analytics/lfl?period1_start=${firstDay.toISOString().split("T")[0]}&period1_end=${lastDay.toISOString().split("T")[0]}&period2_start=${lastMonthFirst.toISOString().split("T")[0]}&period2_end=${lastMonthLast.toISOString().split("T")[0]}`
                );
                setLflData(await lflRes.json());

                // Boston
                const bostonRes = await fetch(`${API_BASE_URL}/api/analytics/boston-matrix?days=90`);
                setBostonData(await bostonRes.json());

            } catch (err) {
                console.error("Analytics data error:", err);
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
        <div className="min-h-screen overflow-x-hidden animate-fade-in">
            <div className="max-w-[1100px] mx-auto space-y-8 p-6 mobile-container">

                {/* 1. Header & Filters (Keep minimal) */}
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <h1 className="text-3xl font-light tracking-tight text-white">Аналитика</h1>
                        {lflData && lflData[0] && (
                            <div className="flex items-center gap-4 text-sm">
                                <span className="text-gray-400">Выручка</span>
                                <span className="text-xl font-bold text-white tracking-wide">{lflData[0].period2_value.toLocaleString()} Br</span>
                                <Badge variant="outline" className={`${lflData[0].change_percent >= 0 ? 'text-green-400 border-green-500/30' : 'text-red-400 border-red-500/30'}`}>
                                    {lflData[0].change_percent > 0 ? '+' : ''}{lflData[0].change_percent}%
                                </Badge>
                            </div>
                        )}
                    </div>
                    <AdvancedFilters
                        onFiltersChange={handleFiltersChange}
                        availableRegions={filterOptions.regions}
                        availableCategories={filterOptions.categories}
                        availableAgents={filterOptions.agents}
                    />
                </div>

                {/* 2. THE CRYSTAL GRID (Vertical Stack: ABC/XYZ & Boston) */}
                <div className="grid grid-cols-1 gap-12">

                    {/* Left: ABC/XYZ Matrix */}
                    <div className="aspect-square w-full">
                        {abcXyzData && !loading ? (
                            <ABCXYZMatrix data={abcXyzData} />
                        ) : (
                            <div className="glass-panel h-full w-full p-8 flex flex-col">
                                <div className="flex items-center gap-4 mb-8">
                                    <Skeleton className="w-12 h-12 rounded-full bg-white/5" />
                                    <Skeleton className="h-6 w-40 bg-white/5" />
                                </div>
                                <div className="flex-1 grid grid-cols-3 grid-rows-3 gap-2">
                                    {Array(9).fill(0).map((_, i) => (
                                        <Skeleton key={i} className="h-full w-full rounded-xl bg-white/5" />
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Right: Boston Matrix */}
                    <div className="aspect-square w-full">
                        {bostonData && !loading ? (
                            <BostonMatrix data={bostonData} />
                        ) : (
                            <div className="glass-panel h-full w-full p-8 flex flex-col">
                                <div className="flex items-center gap-4 mb-8">
                                    <Skeleton className="w-12 h-12 rounded-full bg-white/5" />
                                    <Skeleton className="h-6 w-40 bg-white/5" />
                                </div>
                                <div className="flex-1 grid grid-cols-2 grid-rows-2 gap-2">
                                    {Array(4).fill(0).map((_, i) => (
                                        <Skeleton key={i} className="h-full w-full rounded-xl bg-white/5" />
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                </div>

                {/* 3. SALES GEOGRAPHY (Full Width) */}
                <div>
                    {geoData && !loading ? (
                        <GeoMap data={geoData} />
                    ) : (
                        <div className="glass-panel h-full w-full p-8 flex flex-col">
                            <div className="flex items-center gap-4 mb-8">
                                <Skeleton className="w-12 h-12 rounded-full bg-white/5" />
                                <div className="space-y-2">
                                    <Skeleton className="h-6 w-48 bg-white/5" />
                                    <Skeleton className="h-4 w-32 bg-white/5" />
                                </div>
                            </div>
                            <div className="space-y-4">
                                {Array(5).fill(0).map((_, i) => (
                                    <div key={i} className="flex items-center gap-4">
                                        <Skeleton className="h-12 flex-1 rounded-2xl bg-white/5" />
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* 4. Footer / Additional Tools (What-If) */}
                < div className="pt-8 border-t border-white/5" >
                    <WhatIfSimulator
                        baseMetrics={{
                            revenue: lflData?.[0]?.period2_value || 0,
                            orders: 0,
                            quantity: 0,
                            customers: 0,
                            avg_check: 0,
                        }}
                    />
                </div >

            </div >
        </div >
    );
}
