'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { TrendingUp, TrendingDown, Upload as UploadIcon, FileSpreadsheet, Check, AlertCircle, Download, RefreshCw, Calendar, Plus } from 'lucide-react';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Area,
    AreaChart,
    BarChart,
    Bar,
} from 'recharts';
import { analyticsApi, uploadApi, forecastApi } from '@/lib/api';
import { formatCurrency, formatNumber } from '@/lib/utils';
import SalesTrendChart from '@/components/charts/SalesTrendChart';
import TopCustomersChart from '@/components/charts/TopCustomersChart';
import TopProductsChart from '@/components/charts/TopProductsChart';
import { ExcelImport } from '@/components/ExcelImport';

interface DashboardMetrics {
    total_revenue: number;
    total_sales: number;
    average_check: number;
}

type DataType = 'sales' | 'customers' | 'products';

export default function Dashboard() {
    // Metrics state
    const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
    const [loading, setLoading] = useState(true);

    // Upload state
    const [selectedType, setSelectedType] = useState<DataType>('sales');
    const [uploadMode, setUploadMode] = useState<'append' | 'replace'>('append');
    const [file, setFile] = useState<File | null>(null);
    const [uploadLoading, setUploadLoading] = useState(false);
    const [uploadResult, setUploadResult] = useState<{ success: boolean; message: string } | null>(null);
    const [isDragging, setIsDragging] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Forecast state
    const [monthsAhead, setMonthsAhead] = useState(3);
    const [forecast, setForecast] = useState<any[]>([]);
    const [seasonality, setSeasonality] = useState<any>(null);
    const [training, setTraining] = useState(false);

    const [showUploader, setShowUploader] = useState(false);
    const [refreshing, setRefreshing] = useState(false);
    const [importTab, setImportTab] = useState<'csv' | 'excel'>('excel');

    useEffect(() => {
        loadDashboard();
        loadForecast();
        loadSeasonality();
    }, []);

    async function handleRefresh() {
        setRefreshing(true);
        try {
            // Clear cache and reload all data
            await analyticsApi.refresh();
            await loadDashboard();
            await loadForecast();
            await loadSeasonality();
        } catch (err) {
            console.error('Refresh error:', err);
        } finally {
            setRefreshing(false);
        }
    }

    useEffect(() => {
        loadForecast();
    }, [monthsAhead]);

    async function loadDashboard() {
        try {
            const data = await analyticsApi.getDashboard();
            setMetrics(data);
        } catch (err) {
            setMetrics({
                total_revenue: 0,
                total_sales: 0,
                average_check: 0
            });
        } finally {
            setLoading(false);
        }
    }

    async function loadForecast() {
        try {
            const result = await forecastApi.predict(monthsAhead);
            setForecast(result.forecast);
        } catch (err) {
            // Generative mock data for demo - 12 month outlook
            const mockForecast = [];
            const now = new Date();
            const months = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'];

            for (let i = 1; i <= monthsAhead; i++) {
                const date = new Date(now.getFullYear(), now.getMonth() + i, 1);
                const monthLabel = `${months[date.getMonth()]} ${date.getFullYear() % 100}`;
                mockForecast.push({
                    date: monthLabel,
                    predicted: 2500000 + Math.sin(i / 2) * 300000 + (Math.random() * 100000),
                    lower_bound: 2200000 + Math.sin(i / 2) * 300000,
                    upper_bound: 2900000 + Math.sin(i / 2) * 300000 + 200000,
                });
            }
            setForecast(mockForecast);
        }
    }

    async function loadSeasonality() {
        try {
            const result = await forecastApi.getSeasonality();
            setSeasonality(result);
        } catch (err) {
            setSeasonality({
                monthly: [
                    { month: 'Янв', index: 85 }, { month: 'Фев', index: 90 }, { month: 'Мар', index: 105 },
                    { month: 'Апр', index: 110 }, { month: 'Май', index: 95 }, { month: 'Июн', index: 80 },
                    { month: 'Июл', index: 75 }, { month: 'Авг', index: 85 }, { month: 'Сен', index: 115 },
                    { month: 'Окт', index: 120 }, { month: 'Ноя', index: 125 }, { month: 'Дек', index: 115 },
                ],
            });
        }
    }

    async function handleUpload() {
        if (!file) return;

        setUploadLoading(true);
        setUploadResult(null);

        try {
            const response = await uploadApi.uploadExcel(file, selectedType, uploadMode);
            const skippedText = response.skipped > 0 ? ` (пропущено ${response.skipped} дубликатов)` : '';
            setUploadResult({
                success: true,
                message: `Успешно загружено ${response.imported} из ${response.total} записей${skippedText}`,
            });
            setFile(null);
            loadDashboard(); // Refresh dashboard after upload
            setTimeout(() => setShowUploader(false), 2000);
        } catch (err: any) {
            setUploadResult({
                success: false,
                message: err.message || 'Ошибка загрузки файла',
            });
        } finally {
            setUploadLoading(false);
        }
    }

    async function trainModel() {
        setTraining(true);
        try {
            await forecastApi.train();
            await loadForecast();
        } catch (err) {
            console.error('Training error:', err);
        } finally {
            setTraining(false);
        }
    }

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile) setFile(droppedFile);
    }, []);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            return (
                <div className="rounded-lg border border-[#333333] bg-[#202020] p-3 shadow-lg">
                    <p className="text-sm font-medium">{label}</p>
                    <p className="text-sm text-white">
                        Прогноз: {formatCurrency(payload[0].value)}
                    </p>
                    {payload[1] && (
                        <p className="text-xs text-[#808080]">
                            Диапазон: {formatCurrency(payload[1].payload.lower_bound)} - {formatCurrency(payload[1].payload.upper_bound)}
                        </p>
                    )}
                </div>
            );
        }
        return null;
    };

    const metricCards = [
        {
            title: 'Сумма продаж',
            value: metrics ? formatCurrency(metrics.total_revenue) : '—',
            change: null, // No previous period data available
            trend: null,
        },
        {
            title: 'Количество продаж',
            value: metrics ? formatNumber(metrics.total_sales) : '—',
            change: null,
            trend: null,
        },
        {
            title: 'Средний чек',
            value: metrics ? formatCurrency(metrics.average_check) : '—',
            change: null,
            trend: null,
        },
    ];

    const dataTypes = [
        { id: 'sales', name: 'Продажи', icon: <FileSpreadsheet className="h-4 w-4" /> },
        { id: 'customers', name: 'Клиенты', icon: <UploadIcon className="h-4 w-4" /> },
        { id: 'products', name: 'Товары', icon: <RefreshCw className="h-4 w-4" /> },
    ];

    return (
        <div className="space-y-8 animate-in fade-in duration-500 p-6">
            {/* Header */}
            <div className="flex flex-col gap-4">


                <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
                    <select className="rounded-full bg-[#111] border border-[#333333] px-5 h-[44px] text-sm text-white focus:outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/25 transition-all duration-300 cursor-pointer">
                        <option>Этот месяц</option>
                        <option>Прошлый месяц</option>
                        <option>Этот квартал</option>
                        <option>Этот год</option>
                    </select>

                    <button
                        onClick={() => setShowUploader(!showUploader)}
                        className={`flex items-center justify-center gap-2 rounded-full border px-5 py-3 sm:py-2.5 text-sm transition-all duration-300 min-h-[44px] hover:scale-[1.02] ${showUploader ? 'bg-cyan-600/20 border-cyan-500 text-white shadow-lg shadow-cyan-600/25' : 'border-[#333333] hover:bg-[#262626]'}`}
                    >
                        <UploadIcon className="h-4 w-4" />
                        <span>Загрузить данные</span>
                    </button>

                    <button
                        onClick={handleRefresh}
                        disabled={refreshing}
                        className="flex items-center justify-center gap-2 rounded-full bg-cyan-600 hover:bg-cyan-500 px-5 py-3 sm:py-2.5 text-sm transition-all duration-300 min-h-[44px] disabled:opacity-50 shadow-lg shadow-cyan-600/25 font-medium"
                        title="Обновить все данные"
                    >
                        <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
                        <span className="hidden sm:inline">{refreshing ? 'Обновление...' : 'Обновить'}</span>
                    </button>
                </div>
            </div>

            {/* Collapsible Upload Section */}
            {showUploader && (
                <div className="bg-[#202020] border border-[#333333] rounded-lg p-6 animate-in slide-in-from-top-4 duration-300">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-semibold">Загрузить данные</h2>
                        <button onClick={() => setShowUploader(false)} className="text-[#404040] hover:text-white transition-colors">
                            <Plus className="h-4 w-4 rotate-45" />
                        </button>
                    </div>

                    {/* Tab selector */}
                    <div className="flex gap-2 mb-4">
                        <button
                            onClick={() => setImportTab('excel')}
                            className={`flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-medium transition-all duration-300 h-[44px] ${importTab === 'excel'
                                ? 'bg-green-600 text-white shadow-lg shadow-green-600/25'
                                : 'bg-[#262626] text-[#808080] hover:text-white'
                                }`}
                        >
                            <FileSpreadsheet className="h-4 w-4" />
                            Excel (64МБ)
                        </button>
                        <button
                            onClick={() => setImportTab('csv')}
                            className={`flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-medium transition-all duration-300 h-[44px] ${importTab === 'csv'
                                ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-600/25'
                                : 'bg-[#262626] text-[#808080] hover:text-white'
                                }`}
                        >
                            <UploadIcon className="h-4 w-4" />
                            CSV
                        </button>
                    </div>

                    {/* Excel Import */}
                    {importTab === 'excel' && (
                        <ExcelImport onComplete={() => {
                            handleRefresh();
                            setShowUploader(false);
                        }} />
                    )}

                    {/* CSV Import */}
                    {importTab === 'csv' && (
                        <>
                            <div className="grid gap-3 md:grid-cols-3 mb-4">
                                {dataTypes.map((type) => (
                                    <button
                                        key={type.id}
                                        onClick={() => setSelectedType(type.id as DataType)}
                                        className={`flex items-center gap-3 rounded border p-3 text-left transition-all ${selectedType === type.id
                                            ? 'border-white bg-[#262626]'
                                            : 'border-[#333333] hover:border-[#333]'
                                            }`}
                                    >
                                        <span className={`${selectedType === type.id ? 'text-white' : 'text-[#404040]'}`}>{type.icon}</span>
                                        <span className="text-sm font-medium">{type.name}</span>
                                    </button>
                                ))}
                            </div>

                            <div
                                onDrop={handleDrop}
                                onDragOver={handleDragOver}
                                onDragLeave={handleDragLeave}
                                onClick={() => fileInputRef.current?.click()}
                                className={`cursor-pointer rounded border-2 border-dashed p-8 text-center transition-all ${isDragging ? 'border-white bg-[#262626]' :
                                    file ? 'border-white bg-[#262626]' : 'border-[#333333] hover:border-[#333]'
                                    }`}
                            >
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    accept=".xlsx,.xls,.csv"
                                    className="hidden"
                                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                                />
                                <UploadIcon className="mx-auto mb-3 h-8 w-8 text-[#404040]" />
                                {file ? (
                                    <div>
                                        <p className="font-medium text-white">{file.name}</p>
                                        <p className="text-sm text-[#808080]">{(file.size / 1024).toFixed(1)} KB</p>
                                    </div>
                                ) : (
                                    <div>
                                        <p className="font-medium">Перетащите файл сюда</p>
                                        <p className="text-sm text-[#808080]">или нажмите для выбора (Excel, CSV)</p>
                                    </div>
                                )}
                            </div>

                            {uploadResult && (
                                <div className={`mt-4 flex items-center gap-3 rounded p-3 ${uploadResult.success ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'
                                    }`}>
                                    {uploadResult.success ? <Check className="h-5 w-5" /> : <AlertCircle className="h-5 w-5" />}
                                    <span className="text-sm">{uploadResult.message}</span>
                                </div>
                            )}

                            <div className="mt-4 flex flex-col gap-4">
                                <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                                    <button
                                        onClick={handleUpload}
                                        disabled={!file || uploadLoading}
                                        className="flex items-center justify-center gap-2 rounded-full bg-cyan-600 hover:bg-cyan-500 px-6 py-3 font-medium text-white transition-all duration-300 hover:shadow-lg hover:shadow-cyan-600/25 disabled:opacity-50 min-h-[44px]"
                                    >
                                        {uploadLoading ? 'Загрузка...' : 'Загрузить'}
                                    </button>

                                    <div className="flex items-center gap-6 text-sm">
                                        <label className="flex items-center gap-2 cursor-pointer group min-h-[44px]">
                                            <input
                                                type="radio"
                                                name="uploadMode"
                                                checked={uploadMode === 'append'}
                                                onChange={() => setUploadMode('append')}
                                                className="accent-white w-4 h-4"
                                            />
                                            <span className={uploadMode === 'append' ? 'text-white' : 'text-[#808080] group-hover:text-gray-300'}>
                                                Добавить
                                            </span>
                                        </label>
                                        <label className="flex items-center gap-2 cursor-pointer group min-h-[44px]">
                                            <input
                                                type="radio"
                                                name="uploadMode"
                                                checked={uploadMode === 'replace'}
                                                onChange={() => setUploadMode('replace')}
                                                className="accent-white w-4 h-4"
                                            />
                                            <span className={uploadMode === 'replace' ? 'text-white' : 'text-[#808080] group-hover:text-gray-300'}>
                                                Заменить
                                            </span>
                                        </label>
                                    </div>
                                </div>

                                {uploadMode === 'replace' && (
                                    <div className="flex items-center gap-2 text-xs text-red-400/80 bg-red-400/5 px-3 py-2 rounded border border-red-400/10">
                                        <AlertCircle className="h-3 w-3 flex-shrink-0" />
                                        <span>Все существующие данные будут удалены</span>
                                    </div>
                                )}
                            </div>
                        </>
                    )}
                </div>
            )}

            <div className="h-[1px] bg-[#262626]" />

            {/* Metrics Grid */}
            <div>
                <h2 className="text-lg font-semibold mb-4">Ключевые метрики</h2>
                <div className="grid gap-4 sm:gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
                    {metricCards.map((metric) => (
                        <div key={metric.title} className="ui-card">
                            <div className="flex items-center justify-between mb-4">
                                <p className="text-sm text-[#808080] group-hover:text-gray-400 transition-colors uppercase tracking-wider text-[10px]">{metric.title}</p>
                                {metric.change !== null && (
                                    <div className={`flex items-center gap-1 text-xs px-2 py-0.5 rounded-full ${metric.trend === 'up' ? 'bg-green-500/10 text-green-500' : 'bg-gray-500/10 text-gray-400'
                                        }`}>
                                        {metric.trend === 'up' ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                                        {metric.change}
                                    </div>
                                )}
                            </div>
                            <p className="text-3xl font-bold tracking-tight">{metric.value}</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Charts Row */}
            <div className="grid gap-6 sm:grid-cols-2">
                <div className="ui-card">
                    <h3 className="text-lg font-semibold mb-6">Тренд продаж</h3>
                    <SalesTrendChart />
                </div>
                <div className="ui-card">
                    <h3 className="text-lg font-semibold mb-6">Топ продуктов</h3>
                    <TopProductsChart />
                </div>
            </div>

            <div className="ui-card">
                <h3 className="text-lg font-semibold mb-6">Топ клиенты</h3>
                <TopCustomersChart />
            </div>

            <div className="h-[1px] bg-[#262626]" />

            {/* Forecast Section */}
            <div className="space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-lg font-semibold">Прогнозирование продаж</h2>
                        <p className="text-sm text-[#808080]">Прогноз на основе исторических данных</p>
                    </div>

                    <select
                        value={monthsAhead}
                        onChange={(e) => setMonthsAhead(Number(e.target.value))}
                        className="rounded-full bg-[#111] border border-[#333333] px-5 h-[44px] text-sm text-white focus:outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/25 transition-all duration-300 cursor-pointer"
                    >
                        <option value={1}>1 месяц</option>
                        <option value={3}>3 месяца</option>
                        <option value={6}>6 месяцев</option>
                        <option value={12}>12 месяцев</option>
                    </select>
                </div>

                {/* Forecast Chart */}
                <div className="ui-card overflow-hidden">
                    <div className="mb-6 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <TrendingUp className="h-5 w-5 text-gray-400" />
                            <h3 className="font-medium">Прогноз выручки на {monthsAhead} мес.</h3>
                        </div>
                    </div>
                    <div className="h-80 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={forecast}>
                                <defs>
                                    <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#FFFFFF" stopOpacity={0.2} />
                                        <stop offset="95%" stopColor="#FFFFFF" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#262626" vertical={false} />
                                <XAxis
                                    dataKey="date"
                                    stroke="#404040"
                                    fontSize={10}
                                    tickLine={false}
                                    axisLine={false}
                                    dy={10}
                                />
                                <YAxis
                                    stroke="#404040"
                                    fontSize={10}
                                    tickLine={false}
                                    axisLine={false}
                                    tickFormatter={(v) => `${(v / 1000000).toFixed(1)}M`}
                                />
                                <Tooltip content={<CustomTooltip />} />
                                <Area
                                    type="monotone"
                                    dataKey="predicted"
                                    stroke="#FFFFFF"
                                    strokeWidth={2}
                                    fill="url(#colorForecast)"
                                    animationDuration={1500}
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Seasonality Chart */}
                <div className="bg-[#202020] border border-[#262626] rounded-lg p-6">
                    <div className="mb-6 flex items-center gap-2">
                        <Calendar className="h-5 w-5 text-gray-400" />
                        <h3 className="font-medium">Сезонность по месяцам</h3>
                    </div>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={seasonality?.monthly || []}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#262626" vertical={false} />
                                <XAxis
                                    dataKey="month"
                                    stroke="#404040"
                                    fontSize={10}
                                    tickLine={false}
                                    axisLine={false}
                                />
                                <YAxis
                                    stroke="#404040"
                                    fontSize={10}
                                    domain={[0, 150]}
                                    tickLine={false}
                                    axisLine={false}
                                />
                                <Tooltip
                                    contentStyle={{ background: '#202020', border: '1px solid #333333', borderRadius: '8px' }}
                                    itemStyle={{ color: '#white' }}
                                />
                                <Bar dataKey="index" fill="#FFFFFF" radius={[2, 2, 0, 0]} opacity={0.8} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="mt-4 flex items-center justify-center gap-6 text-[10px] text-[#404040]">
                        <div className="flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-white opacity-80" />
                            <span>Сезонный индекс</span>
                        </div>
                        <p>100 = средний уровень продаж</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
