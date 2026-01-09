'use client';

import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Upload, RefreshCw, Users, Target, Award } from 'lucide-react';
import { agentAnalyticsApi } from '@/lib/api';
import { formatCurrency, formatNumber } from '@/lib/utils';
import AgentCard from './AgentCard';
import RegionalMap from './RegionalMap';

interface Agent {
    agent_id: string;
    agent_name: string;
    agent_email: string;
    region: string;
    plan_amount: number;
    actual_sales: number;
    fulfillment_percent: number;
    forecast_fulfillment_percent?: number;
    ranking?: number;
}

interface DashboardMetrics {
    total_agents: number;
    total_plan: number;
    total_sales: number;
    overall_fulfillment_percent: number;
    regional_performance: Array<any>;
    top_performers: Agent[];
    bottom_performers: Agent[];
}

export default function AgentDashboard() {
    const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
    const [agents, setAgents] = useState<Agent[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedRegion, setSelectedRegion] = useState<string | null>(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [showImporter, setShowImporter] = useState(false);
    const [importFile, setImportFile] = useState<File | null>(null);
    const [importing, setImporting] = useState(false);

    // Period selection
    const [periodStart, setPeriodStart] = useState(() => {
        const today = new Date();
        return `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-01`;
    });
    const [periodEnd, setPeriodEnd] = useState(() => {
        const today = new Date();
        const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0).getDate();
        return `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${lastDay}`;
    });

    useEffect(() => {
        loadDashboard();
    }, [periodStart, periodEnd, selectedRegion]);

    async function loadDashboard() {
        try {
            setLoading(true);
            const [dashboardData, agentsData] = await Promise.all([
                agentAnalyticsApi.getDashboard({
                    period_start: periodStart,
                    period_end: periodEnd,
                    region: selectedRegion || undefined,
                }),
                agentAnalyticsApi.getAgents({
                    period_start: periodStart,
                    period_end: periodEnd,
                    region: selectedRegion || undefined,
                }),
            ]);

            setMetrics(dashboardData);
            setAgents(agentsData);
        } catch (err) {
            console.error('Error loading dashboard:', err);
        } finally {
            setLoading(false);
        }
    }

    async function handleImport() {
        if (!importFile) return;

        try {
            setImporting(true);
            const result = await agentAnalyticsApi.importExcel(importFile, periodStart, periodEnd);

            if (result.success) {
                alert(`Импорт успешен!\n\nАгентов: ${result.agents_imported}\nПланов: ${result.plans_imported}\nПродаж: ${result.daily_sales_imported}`);
                setShowImporter(false);
                setImportFile(null);
                loadDashboard();
            } else {
                alert(`Импорт завершен с ошибками:\n${result.errors.join('\n')}`);
            }
        } catch (err: any) {
            alert(`Ошибка импорта: ${err.message}`);
        } finally {
            setImporting(false);
        }
    }

    // Filter agents by search
    const filteredAgents = agents.filter(agent =>
        agent.agent_name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    // Sort agents by fulfillment
    const sortedAgents = [...filteredAgents].sort((a, b) => b.fulfillment_percent - a.fulfillment_percent);

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            {/* Header */}
            <div className="flex flex-col gap-4">
                <div>
                    <h1 className="text-2xl md:text-[40px] font-semibold tracking-tight mb-2">
                        Аналитика агентов
                    </h1>
                    <p className="text-sm text-[#808080]">
                        Отслеживайте выполнение планов и эффективность работы агентов
                    </p>
                </div>

                {/* Controls */}
                <div className="flex flex-wrap items-center gap-3">
                    <input
                        type="date"
                        value={periodStart}
                        onChange={(e) => setPeriodStart(e.target.value)}
                        className="rounded-full bg-[#111] border border-[#333333] px-4 py-2.5 text-sm text-white min-w-[140px]"
                    />
                    <input
                        type="date"
                        value={periodEnd}
                        onChange={(e) => setPeriodEnd(e.target.value)}
                        className="rounded-full bg-[#111] border border-[#333333] px-4 py-2.5 text-sm text-white min-w-[140px]"
                    />

                    <select
                        value={selectedRegion || ''}
                        onChange={(e) => setSelectedRegion(e.target.value || null)}
                        className="rounded-full bg-[#111] border border-[#333333] px-4 py-2.5 text-sm text-white min-w-[140px]"
                    >
                        <option value="">Все регионы</option>
                        <option value="БРЕСТ">БРЕСТ</option>
                        <option value="ВИТЕБСК">ВИТЕБСК</option>
                        <option value="ГОМЕЛЬ">ГОМЕЛЬ</option>
                        <option value="ГРОДНО">ГРОДНО</option>
                        <option value="МИНСК">МИНСК</option>
                    </select>

                    <button
                        onClick={() => setShowImporter(!showImporter)}
                        className="flex items-center justify-center gap-2 rounded-full border border-[#333333] px-5 py-2.5 text-sm hover:bg-[#262626] transition-colors min-w-[120px]"
                    >
                        <Upload className="h-4 w-4" />
                        <span>Импорт</span>
                    </button>

                    <button
                        onClick={loadDashboard}
                        disabled={loading}
                        className="flex items-center justify-center gap-2 rounded-full bg-rose-800 hover:bg-rose-700 px-5 py-2.5 text-sm disabled:opacity-50 transition-colors min-w-[120px]"
                    >
                        <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                        <span>Обновить</span>
                    </button>
                </div>
            </div>

            {/* Import Section */}
            {showImporter && (
                <div className="bg-[#202020] border border-[#333333] rounded-lg p-6">
                    <h2 className="text-lg font-semibold mb-4">Импорт данных из Excel</h2>
                    <div className="space-y-4">
                        <input
                            type="file"
                            accept=".xlsx,.xls"
                            onChange={(e) => setImportFile(e.target.files?.[0] || null)}
                            className="block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-rose-800 file:text-white hover:file:bg-rose-700"
                        />
                        {importFile && (
                            <button
                                onClick={handleImport}
                                disabled={importing}
                                className="rounded-full bg-rose-800 hover:bg-rose-700 px-6 py-2.5 text-sm disabled:opacity-50"
                            >
                                {importing ? 'Импорт...' : 'Загрузить'}
                            </button>
                        )}
                    </div>
                </div>
            )}

            {/* KPI Metrics */}
            {metrics && (
                <div className="grid gap-4 sm:gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
                    <div className="ui-card">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="p-2 rounded-lg bg-blue-500/10">
                                <Users className="h-5 w-5 text-blue-500" />
                            </div>
                            <p className="text-sm text-[#808080]">Всего агентов</p>
                        </div>
                        <p className="text-3xl font-bold">{metrics.total_agents}</p>
                    </div>

                    <div className="ui-card">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="p-2 rounded-lg bg-purple-500/10">
                                <Target className="h-5 w-5 text-purple-500" />
                            </div>
                            <p className="text-sm text-[#808080]">План продаж</p>
                        </div>
                        <p className="text-3xl font-bold">{formatCurrency(metrics.total_plan)}</p>
                    </div>

                    <div className="ui-card">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="p-2 rounded-lg bg-green-500/10">
                                <TrendingUp className="h-5 w-5 text-green-500" />
                            </div>
                            <p className="text-sm text-[#808080]">Факт продаж</p>
                        </div>
                        <p className="text-3xl font-bold">{formatCurrency(metrics.total_sales)}</p>
                    </div>

                    <div className="ui-card">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="p-2 rounded-lg bg-rose-500/10">
                                <Award className="h-5 w-5 text-rose-500" />
                            </div>
                            <p className="text-sm text-[#808080]">Выполнение</p>
                        </div>
                        <p className="text-3xl font-bold">{metrics.overall_fulfillment_percent.toFixed(1)}%</p>
                    </div>
                </div>
            )}

            {/* Regional Map */}
            {metrics && metrics.regional_performance.length > 0 && (
                <RegionalMap regions={metrics.regional_performance} />
            )}

            {/* Search */}
            <div>
                <input
                    type="text"
                    placeholder="Поиск агента..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full rounded-full bg-[#111] border border-[#333333] px-5 py-3 text-sm text-white focus:outline-none focus:border-rose-800"
                />
            </div>

            {/* Agents Grid */}
            <div>
                <h2 className="text-lg font-semibold mb-4">
                    Агенты ({sortedAgents.length})
                </h2>
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {sortedAgents.map((agent, idx) => (
                        <AgentCard
                            key={agent.agent_id}
                            agent={agent}
                            rank={idx + 1}
                        />
                    ))}
                </div>

                {sortedAgents.length === 0 && (
                    <div className="text-center py-12 text-[#808080]">
                        <p>Нет данных для отображения</p>
                    </div>
                )}
            </div>
        </div>
    );
}
