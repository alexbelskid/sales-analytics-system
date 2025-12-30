'use client';

import { useState, useEffect } from 'react';
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
} from 'recharts';
import { analyticsApi } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';

// Demo data
const demoData = [
    { period: '2024-01', amount: 1850000, count: 45 },
    { period: '2024-02', amount: 2100000, count: 52 },
    { period: '2024-03', amount: 1950000, count: 48 },
    { period: '2024-04', amount: 2300000, count: 58 },
    { period: '2024-05', amount: 2150000, count: 54 },
    { period: '2024-06', amount: 2450000, count: 62 },
];

interface TrendData {
    period: string;
    amount: number;
    count: number;
}

export default function SalesTrendChart() {
    const [data, setData] = useState<TrendData[]>(demoData);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, []);

    async function loadData() {
        try {
            const trend = await analyticsApi.getSalesTrend('month');
            if (trend.length > 0) {
                setData(trend);
            }
        } catch (err) {
            // Use demo data on error
        } finally {
            setLoading(false);
        }
    }

    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            return (
                <div className="rounded-lg border bg-background p-3 shadow-lg">
                    <p className="text-sm font-medium">{label}</p>
                    <p className="text-sm text-primary">
                        Выручка: {formatCurrency(payload[0].value)}
                    </p>
                    {payload[0].payload.count && (
                        <p className="text-sm text-muted-foreground">
                            Продаж: {payload[0].payload.count}
                        </p>
                    )}
                </div>
            );
        }
        return null;
    };

    return (
        <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data}>
                    <defs>
                        <linearGradient id="colorAmount" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis
                        dataKey="period"
                        stroke="hsl(var(--muted-foreground))"
                        fontSize={12}
                        tickLine={false}
                    />
                    <YAxis
                        stroke="hsl(var(--muted-foreground))"
                        fontSize={12}
                        tickLine={false}
                        tickFormatter={(value) => `${(value / 1000000).toFixed(1)}M`}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Area
                        type="monotone"
                        dataKey="amount"
                        stroke="hsl(var(--primary))"
                        strokeWidth={2}
                        fill="url(#colorAmount)"
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
}
