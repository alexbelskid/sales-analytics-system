'use client';

import { useState, useEffect } from 'react';
import {
    DollarSign,
    ShoppingCart,
    Receipt,
    TrendingUp,
    TrendingDown,
    ArrowUpRight
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
            // Показываем демо-данные при ошибке
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
            icon: DollarSign,
            color: 'bg-blue-500',
        },
        {
            title: 'Количество продаж',
            value: metrics ? formatNumber(metrics.total_sales) : '—',
            change: '+8.2%',
            trend: 'up',
            icon: ShoppingCart,
            color: 'bg-green-500',
        },
        {
            title: 'Средний чек',
            value: metrics ? formatCurrency(metrics.average_check) : '—',
            change: '+3.1%',
            trend: 'up',
            icon: Receipt,
            color: 'bg-purple-500',
        },
    ];

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-foreground">Дашборд</h1>
                    <p className="text-muted-foreground">Аналитика продаж за текущий период</p>
                </div>
                <div className="flex gap-2">
                    <select className="rounded-lg border border-input bg-background px-3 py-2 text-sm">
                        <option>Этот месяц</option>
                        <option>Прошлый месяц</option>
                        <option>Этот квартал</option>
                        <option>Этот год</option>
                    </select>
                </div>
            </div>

            {/* Metrics Grid */}
            <div className="grid gap-4 md:grid-cols-3">
                {metricCards.map((metric) => (
                    <div key={metric.title} className="metric-card">
                        <div className="flex items-center justify-between">
                            <div className={`rounded-lg p-2 ${metric.color}`}>
                                <metric.icon className="h-5 w-5 text-white" />
                            </div>
                            <div className={`flex items-center gap-1 text-sm ${metric.trend === 'up' ? 'text-green-500' : 'text-red-500'
                                }`}>
                                {metric.trend === 'up' ? (
                                    <TrendingUp className="h-4 w-4" />
                                ) : (
                                    <TrendingDown className="h-4 w-4" />
                                )}
                                {metric.change}
                            </div>
                        </div>
                        <div className="mt-4">
                            <p className="text-sm text-muted-foreground">{metric.title}</p>
                            <p className="text-2xl font-bold">{metric.value}</p>
                        </div>
                    </div>
                ))}
            </div>

            {/* Charts Row */}
            <div className="grid gap-6 lg:grid-cols-2">
                {/* Sales Trend */}
                <div className="metric-card">
                    <div className="mb-4 flex items-center justify-between">
                        <h3 className="font-semibold">Динамика продаж</h3>
                        <select className="rounded border border-input bg-background px-2 py-1 text-sm">
                            <option value="month">По месяцам</option>
                            <option value="week">По неделям</option>
                            <option value="day">По дням</option>
                        </select>
                    </div>
                    <SalesTrendChart />
                </div>

                {/* Top Customers */}
                <div className="metric-card">
                    <div className="mb-4 flex items-center justify-between">
                        <h3 className="font-semibold">Топ клиенты</h3>
                        <a href="/analytics" className="flex items-center gap-1 text-sm text-primary hover:underline">
                            Все клиенты <ArrowUpRight className="h-3 w-3" />
                        </a>
                    </div>
                    <TopCustomersChart />
                </div>
            </div>

            {/* Top Products */}
            <div className="metric-card">
                <div className="mb-4 flex items-center justify-between">
                    <h3 className="font-semibold">Топ товаров по продажам</h3>
                </div>
                <TopProductsChart />
            </div>
        </div>
    );
}
