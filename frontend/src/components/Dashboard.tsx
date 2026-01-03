'use client';

import { useState, useEffect } from 'react';
import {
    DollarSign,
    ShoppingCart,
    Receipt,
    TrendingUp,
    TrendingDown,
    ArrowUpRight,
    Zap,
    Users,
    Package
} from 'lucide-react';
import { analyticsApi } from '@/lib/api';
import { formatCurrency, formatNumber } from '@/lib/utils';
import SalesTrendChart from '@/components/charts/SalesTrendChart';
import TopCustomersChart from '@/components/charts/TopCustomersChart';
import TopProductsChart from '@/components/charts/TopProductsChart';

interface DashboardMetrics {
    total_revenue: number;
    total_sales: number;
    average_check: number;
}

export default function Dashboard() {
    const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadDashboard();
    }, []);

    async function loadDashboard() {
        try {
            setLoading(true);
            const data = await analyticsApi.getDashboard();
            setMetrics(data);
            setError(null);
        } catch (err) {
            setError('Ошибка загрузки данных');
            // Demo data on error
            setMetrics({
                total_revenue: 2450000,
                total_sales: 156,
                average_check: 15705
            });
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="space-y-8 -m-6 p-6">
            {/* Hero Header with Diagonal Accent */}
            <div className="relative stagger-in">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-5xl font-bold gradient-text mb-2">Дашборд</h1>
                        <p className="text-muted-foreground font-mono text-sm uppercase tracking-wider">
                            Аналитика продаж за текущий период
                        </p>
                    </div>
                    <div className="flex gap-3">
                        <select className="rounded-lg border border-border/50 bg-slate/30 px-4 py-2.5 text-sm font-mono backdrop-blur-sm transition-all hover:border-amber-500/50 focus:outline-none focus:ring-2 focus:ring-amber-500/50">
                            <option>Этот месяц</option>
                            <option>Прошлый месяц</option>
                            <option>Этот квартал</option>
                            <option>Этот год</option>
                        </select>
                    </div>
                </div>
                {/* Diagonal accent line */}
                <div className="absolute -bottom-3 left-0 w-48 h-[3px] bg-gradient-to-r from-amber-500 via-yellow-500 to-transparent"
                    style={{ transform: 'skewY(-8deg)' }} />
            </div>

            {/* Asymmetric Hero Metrics - 70/30 Split */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* HERO METRIC - Revenue (70% width, 2 columns) */}
                <div className="lg:col-span-2 metric-card stagger-in bg-gradient-to-br from-amber-500/10 via-charcoal to-obsidian border-amber-500/20" style={{ animationDelay: '100ms' }}>
                    <div className="flex items-start justify-between mb-6">
                        <div className="flex items-center gap-4">
                            <div className="p-4 rounded-xl bg-amber-500/20 border border-amber-500/30 glow-pulse">
                                <DollarSign className="h-8 w-8 text-amber-400" strokeWidth={2.5} />
                            </div>
                            <div>
                                <p className="text-sm font-mono uppercase tracking-widest text-amber-400/80 mb-1">Общая выручка</p>
                                <p className="text-5xl font-bold text-foreground font-display">
                                    {metrics ? formatCurrency(metrics.total_revenue) : '—'}
                                </p>
                            </div>
                        </div>
                        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                            <TrendingUp className="h-5 w-5 text-emerald-400" />
                            <span className="text-emerald-400 font-semibold font-mono">+12.5%</span>
                        </div>
                    </div>

                    {/* Mini sparkline or additional context */}
                    <div className="flex gap-6 text-sm">
                        <div>
                            <p className="text-muted-foreground font-mono text-xs mb-1">Прошлый месяц</p>
                            <p className="font-semibold font-mono">2.18M ₽</p>
                        </div>
                        <div className="w-[1px] bg-border/30" />
                        <div>
                            <p className="text-muted-foreground font-mono text-xs mb-1">Цель месяца</p>
                            <p className="font-semibold font-mono">2.8M ₽</p>
                        </div>
                        <div className="w-[1px] bg-border/30" />
                        <div>
                            <p className="text-muted-foreground font-mono text-xs mb-1">Прогресс</p>
                            <p className="font-semibold font-mono text-amber-400">87.5%</p>
                        </div>
                    </div>

                    {/* Diagonal accent */}
                    <div className="absolute top-0 right-0 w-[2px] h-full bg-gradient-to-b from-transparent via-amber-500/50 to-transparent"
                        style={{ transform: 'skewY(8deg)', transformOrigin: 'top right' }} />
                </div>

                {/* Mini Stats (30% width) */}
                <div className="space-y-6">
                    {/* Sales Count */}
                    <div className="metric-card stagger-in bg-gradient-to-br from-emerald-500/10 via-charcoal to-obsidian border-emerald-500/20" style={{ animationDelay: '150ms' }}>
                        <div className="flex items-center justify-between mb-3">
                            <div className="p-3 rounded-lg bg-emerald-500/20 border border-emerald-500/30">
                                <ShoppingCart className="h-5 w-5 text-emerald-400" strokeWidth={2.5} />
                            </div>
                            <div className="flex items-center gap-1 text-xs font-mono text-emerald-400">
                                <TrendingUp className="h-3 w-3" />
                                +8.2%
                            </div>
                        </div>
                        <p className="text-xs font-mono uppercase tracking-widest text-muted-foreground mb-1">Продажи</p>
                        <p className="text-3xl font-bold font-display">{metrics ? formatNumber(metrics.total_sales) : '—'}</p>
                    </div>

                    {/* Average Check */}
                    <div className="metric-card stagger-in bg-gradient-to-br from-blue-500/10 via-charcoal to-obsidian border-blue-500/20" style={{ animationDelay: '200ms' }}>
                        <div className="flex items-center justify-between mb-3">
                            <div className="p-3 rounded-lg bg-blue-500/20 border border-blue-500/30">
                                <Receipt className="h-5 w-5 text-blue-400" strokeWidth={2.5} />
                            </div>
                            <div className="flex items-center gap-1 text-xs font-mono text-blue-400">
                                <TrendingUp className="h-3 w-3" />
                                +3.1%
                            </div>
                        </div>
                        <p className="text-xs font-mono uppercase tracking-widest text-muted-foreground mb-1">Средний чек</p>
                        <p className="text-3xl font-bold font-display">{metrics ? formatCurrency(metrics.average_check) : '—'}</p>
                    </div>
                </div>
            </div>

            {/* Charts Row - Asymmetric */}
            <div className="grid gap-6 lg:grid-cols-7">
                {/* Sales Trend - 4 columns */}
                <div className="lg:col-span-4 metric-card stagger-in" style={{ animationDelay: '250ms' }}>
                    <div className="mb-6 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20">
                                <TrendingUp className="h-5 w-5 text-amber-400" />
                            </div>
                            <h3 className="font-bold text-xl font-display">Динамика продаж</h3>
                        </div>
                        <select className="rounded border border-border/50 bg-slate/30 px-3 py-1.5 text-xs font-mono hover:border-amber-500/50 transition-all">
                            <option value="month">По месяцам</option>
                            <option value="week">По неделям</option>
                            <option value="day">По дням</option>
                        </select>
                    </div>
                    <SalesTrendChart />
                </div>

                {/* Top Customers - 3 columns */}
                <div className="lg:col-span-3 metric-card stagger-in diagonal-divider" style={{ animationDelay: '300ms' }}>
                    <div className="mb-6 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                                <Users className="h-5 w-5 text-emerald-400" />
                            </div>
                            <h3 className="font-bold text-xl font-display">Топ клиенты</h3>
                        </div>
                        <a href="/analytics" className="flex items-center gap-1 text-xs text-amber-400 hover:text-amber-300 transition-colors font-mono">
                            Все <ArrowUpRight className="h-3 w-3" />
                        </a>
                    </div>
                    <TopCustomersChart />
                </div>
            </div>

            {/* Top Products - Full Width */}
            <div className="metric-card stagger-in" style={{ animationDelay: '350ms' }}>
                <div className="mb-6 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-blue-500/10 border border-blue-500/20">
                            <Package className="h-5 w-5 text-blue-400" />
                        </div>
                        <h3 className="font-bold text-xl font-display">Топ товаров по продажам</h3>
                    </div>
                    <div className="flex items-center gap-2 text-xs font-mono text-muted-foreground">
                        <Zap className="h-4 w-4 text-amber-400" />
                        Обновлено только что
                    </div>
                </div>
                <TopProductsChart />
            </div>
        </div>
    );
}
