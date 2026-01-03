'use client';

import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
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

    useEffect(() => {
        loadDashboard();
    }, []);

    async function loadDashboard() {
        try {
            const data = await analyticsApi.getDashboard();
            setMetrics(data);
        } catch (err) {
            setMetrics({
                total_revenue: 2450000,
                total_sales: 156,
                average_check: 15705
            });
        } finally {
            setLoading(false);
        }
    }

    const metricCards = [
        {
            title: 'Общая выручка',
            value: metrics ? formatCurrency(metrics.total_revenue) : '—',
            change: '+12.5%',
            trend: 'up',
        },
        {
            title: 'Количество продаж',
            value: metrics ? formatNumber(metrics.total_sales) : '—',
            change: '+8.2%',
            trend: 'up',
        },
        {
            title: 'Средний чек',
            value: metrics ? formatCurrency(metrics.average_check) : '—',
            change: '+3.1%',
            trend: 'up',
        },
    ];

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-[32px] font-semibold">Дашборд</h1>
                    <p className="text-sm text-[#808080] mt-1">Аналитика продаж за текущий период</p>
                </div>
                <select className="rounded bg-[#1A1A1A] border border-[#2A2A2A] px-4 py-2 text-sm text-white focus:outline-none focus:border-white transition-colors">
                    <option>Этот месяц</option>
                    <option>Прошлый месяц</option>
                    <option>Этот квартал</option>
                    <option>Этот год</option>
                </select>
            </div>

            {/* Metrics Grid */}
            <div className="grid gap-6 md:grid-cols-3">
                {metricCards.map((metric) => (
                    <div key={metric.title} className="metric-card">
                        <div className="flex items-center justify-between mb-4">
                            <p className="text-sm text-[#808080]">{metric.title}</p>
                            <div className={`flex items-center gap-1 text-xs ${metric.trend === 'up' ? 'text-white' : 'text-[#808080]'
                                }`}>
                                {metric.trend === 'up' ? (
                                    <TrendingUp className="h-3 w-3" />
                                ) : (
                                    <TrendingDown className="h-3 w-3" />
                                )}
                                {metric.change}
                            </div>
                        </div>
                        <p className="text-3xl font-semibold">{metric.value}</p>
                    </div>
                ))}
            </div>

            {/* Charts Row */}
            <div className="grid gap-6 lg:grid-cols-2">
                {/* Sales Trend */}
                <div className="metric-card">
                    <div className="mb-6 flex items-center justify-between">
                        <h3 className="text-lg font-semibold">Динамика продаж</h3>
                        <select className="rounded bg-[#0A0A0A] border border-[#2A2A2A] px-3 py-1 text-xs text-white focus:outline-none focus:border-white transition-colors">
                            <option value="month">По месяцам</option>
                            <option value="week">По неделям</option>
                            <option value="day">По дням</option>
                        </select>
                    </div>
                    <SalesTrendChart />
                </div>

                {/* Top Customers */}
                <div className="metric-card">
                    <div className="mb-6">
                        <h3 className="text-lg font-semibold">Топ клиенты</h3>
                    </div>
                    <TopCustomersChart />
                </div>
            </div>

            {/* Top Products */}
            <div className="metric-card">
                <div className="mb-6">
                    <h3 className="text-lg font-semibold">Топ товаров по продажам</h3>
                </div>
                <TopProductsChart />
            </div>
        </div>
    );
}
