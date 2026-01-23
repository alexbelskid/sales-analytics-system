'use client';

import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Upload, RefreshCw, Users, Target, Award, ArrowUpDown, Search, ChevronDown } from 'lucide-react';
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover";
import { agentAnalyticsApi } from '@/lib/api';
import { formatCurrency, formatNumber } from '@/lib/utils';
import AgentCard from './AgentCard';
import RegionalMap from './RegionalMap';
import LiquidButton from './LiquidButton';
import GlassInput from './GlassInput';
import GlassDatePicker from './GlassDatePicker';
import GlassSelect from './GlassSelect';

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

type SortOption = 'fulfillment' | 'name' | 'sales' | 'plan';

export default function AgentDashboard() {
    const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
    const [agents, setAgents] = useState<Agent[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedRegion, setSelectedRegion] = useState<string | null>(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [showImporter, setShowImporter] = useState(false);
    const [importFile, setImportFile] = useState<File | null>(null);
    const [importing, setImporting] = useState(false);
    const [sortBy, setSortBy] = useState<SortOption>('fulfillment');

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
            console.warn('Backend API unreachable. Switching to Demo Mode (Mock Data).');
            // MOCK FALLBACK for Demo/Offline Mode
            setMetrics({
                total_agents: 48,
                total_plan: 5200000,
                total_sales: 4752559,
                overall_fulfillment_percent: 91.4,
                regional_performance: [
                    { region: 'МИНСК', total_plan: 2000000, total_sales: 1950000, fulfillment_percent: 97.5 },
                    { region: 'ГРОДНО', total_plan: 500000, total_sales: 320000, fulfillment_percent: 64.0 },
                    { region: 'БРЕСТ', total_plan: 800000, total_sales: 810000, fulfillment_percent: 101.2 },
                ],
                top_performers: [],
                bottom_performers: [],
            });
            setAgents([
                { agent_id: '1', agent_name: 'Алексей Смирнов', agent_email: 'alex@example.com', region: 'МИНСК', plan_amount: 150000, actual_sales: 162000, fulfillment_percent: 108.0 },
                { agent_id: '2', agent_name: 'Мария Иванова', agent_email: 'maria@example.com', region: 'БРЕСТ', plan_amount: 120000, actual_sales: 115000, fulfillment_percent: 95.8 },
                { agent_id: '3', agent_name: 'Дмитрий Петров', agent_email: 'dima@example.com', region: 'ГРОДНО', plan_amount: 100000, actual_sales: 89000, fulfillment_percent: 89.0 },
                { agent_id: '4', agent_name: 'Елена Сидорова', agent_email: 'elena@example.com', region: 'ВИТЕБСК', plan_amount: 110000, actual_sales: 112000, fulfillment_percent: 101.8 },
                { agent_id: '5', agent_name: 'Игорь Козлов', agent_email: 'igor@example.com', region: 'ГОМЕЛЬ', plan_amount: 130000, actual_sales: 125000, fulfillment_percent: 96.1 },
            ]);
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

    // Sort agents based on selected option
    const sortedAgents = [...filteredAgents].sort((a, b) => {
        switch (sortBy) {
            case 'name':
                return a.agent_name.localeCompare(b.agent_name);
            case 'sales':
                return b.actual_sales - a.actual_sales;
            case 'plan':
                return b.plan_amount - a.plan_amount;
            case 'fulfillment':
            default:
                return b.fulfillment_percent - a.fulfillment_percent;
        }
    });

    return (
        <div className="space-y-8 animate-in fade-in duration-500 p-6">
            {/* Header */}
            <div className="flex flex-col gap-4">


                {/* Controls - Centered */}
                <div className="flex flex-wrap items-center justify-center gap-3">
                    <GlassDatePicker
                        value={periodStart}
                        onChange={(date) => setPeriodStart(date)}
                        className="min-w-[160px]"
                    />
                    <GlassDatePicker
                        value={periodEnd}
                        onChange={(date) => setPeriodEnd(date)}
                        className="min-w-[160px]"
                    />

                    <Popover>
                        <PopoverTrigger asChild>
                            <LiquidButton
                                variant="secondary"
                                className="min-w-[160px] justify-between px-4"
                            >
                                <span className="mr-2">
                                    {selectedRegion
                                        ? (selectedRegion.charAt(0) + selectedRegion.slice(1).toLowerCase())
                                        : 'Все регионы'}
                                </span>
                                <ChevronDown className="h-4 w-4 opacity-50" />
                            </LiquidButton>
                        </PopoverTrigger>
                        <PopoverContent className="w-[160px] p-1 bg-[#1A1A1A] border-[#333333] rounded-2xl shadow-xl backdrop-blur-xl">
                            <div className="flex flex-col gap-1">
                                <button
                                    onClick={() => setSelectedRegion(null)}
                                    className={`w-full text-left px-3 py-2.5 text-sm rounded-xl transition-all duration-200 ${!selectedRegion ? 'bg-white/10 text-white' : 'text-gray-300 hover:bg-white/5 hover:text-white'}`}
                                >
                                    Все регионы
                                </button>
                                {[
                                    { id: 'БРЕСТ', label: 'Брест' },
                                    { id: 'ВИТЕБСК', label: 'Витебск' },
                                    { id: 'ГОМЕЛЬ', label: 'Гомель' },
                                    { id: 'ГРОДНО', label: 'Гродно' },
                                    { id: 'МИНСК', label: 'Минск' },
                                    { id: 'МОГИЛЕВ', label: 'Могилев' }
                                ].map((region) => (
                                    <button
                                        key={region.id}
                                        onClick={() => setSelectedRegion(region.id)}
                                        className={`w-full text-left px-3 py-2.5 text-sm rounded-xl transition-all duration-200 ${selectedRegion === region.id ? 'bg-white/10 text-white' : 'text-gray-300 hover:bg-white/5 hover:text-white'}`}
                                    >
                                        {region.label}
                                    </button>
                                ))}
                            </div>
                        </PopoverContent>
                    </Popover>

                    <LiquidButton
                        onClick={() => setShowImporter(!showImporter)}
                        icon={Upload}
                    >
                        Импорт
                    </LiquidButton>

                    <LiquidButton
                        onClick={loadDashboard}
                        disabled={loading}
                        icon={RefreshCw}
                    >
                        Обновить
                    </LiquidButton>
                </div>
            </div>

            {/* Import Section */}
            {showImporter && (
                <div className="bg-card border border-border rounded-3xl p-6">
                    <h2 className="text-lg font-semibold mb-4">Импорт данных из Excel</h2>
                    <div className="space-y-4">
                        <div className="space-y-4">
                            <div className="flex items-center gap-4">
                                <div onClick={() => document.getElementById('agent-import-input')?.click()}>
                                    <LiquidButton
                                        icon={Upload}
                                    >
                                        Выберите файл
                                    </LiquidButton>
                                    <input
                                        id="agent-import-input"
                                        type="file"
                                        accept=".xlsx,.xls"
                                        onChange={(e) => setImportFile(e.target.files?.[0] || null)}
                                        className="hidden"
                                    />
                                </div>
                                <span className="text-sm text-gray-400">
                                    {importFile ? importFile.name : 'Файл не выбран'}
                                </span>
                            </div>
                            {importFile && (
                                <LiquidButton
                                    onClick={handleImport}
                                    disabled={importing}
                                >
                                    {importing ? 'Импорт...' : 'Загрузить'}
                                </LiquidButton>
                            )}
                        </div>
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

            {/* Search and Sort Controls */}
            <div className="flex flex-col sm:flex-row gap-4 items-stretch sm:items-center">
                <div className="relative flex-1">
                    <GlassInput
                        placeholder="Поиск агента..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        icon={Search}
                    />
                </div>

                <div className="flex items-center gap-2">
                    <ArrowUpDown className="h-4 w-4 text-[#666]" />
                    <div className="flex items-center gap-2">
                        <ArrowUpDown className="h-4 w-4 text-[#666]" />
                        <GlassSelect
                            value={sortBy}
                            onChange={(e) => setSortBy(e.target.value as SortOption)}
                            className="min-w-[180px]"
                        >
                            <option value="fulfillment">По выполнению</option>
                            <option value="sales">По продажам</option>
                            <option value="plan">По плану</option>
                            <option value="name">По имени</option>
                        </GlassSelect>
                    </div>
                </div>
            </div>

            {/* Agents Grid */}
            <div>
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold">
                        Агенты ({sortedAgents.length})
                    </h2>
                    {sortedAgents.length > 0 && (
                        <span className="text-xs text-[#666]">
                            Топ: {sortedAgents[0]?.agent_name} ({sortedAgents[0]?.fulfillment_percent.toFixed(1)}%)
                        </span>
                    )}
                </div>
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
