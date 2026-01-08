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
import { TrendingUp } from 'lucide-react';

interface TrendData {
    period: string;
    amount: number;
    count: number;
}

export default function SalesTrendChart() {
    const [data, setData] = useState<TrendData[]>([]);
    const [loading, setLoading] = useState(true);
    const [hasRealData, setHasRealData] = useState(false);

    useEffect(() => {
        loadData();
    }, []);

    async function loadData() {
        try {
            const trend = await analyticsApi.getSalesTrend('month');
            if (trend && trend.length > 0) {
                setData(trend);
                setHasRealData(true);
            }
        } catch (err) {
            console.log('SalesTrend: No data available');
        } finally {
            setLoading(false);
        }
    }

    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            return (
                <div className="rounded-lg border border-[#333333] bg-[#202020] p-3 shadow-lg">
                    <p className="text-sm font-medium text-white">{label}</p>
                    <p className="text-sm text-white">
                        Сумма: {formatCurrency(payload[0].value)}
                    </p>
                    {payload[0].payload.count && (
                        <p className="text-sm text-[#808080]">
                            Продаж: {payload[0].payload.count}
                        </p>
                    )}
                </div>
            );
        }
        return null;
    };

    if (loading) {
        return (
            <div className="h-80 flex items-center justify-center">
                <div className="text-[#808080] text-sm">Загрузка...</div>
            </div>
        );
    }

    if (!hasRealData || data.length === 0) {
        return (
            <div className="h-80 flex flex-col items-center justify-center text-center">
                <TrendingUp className="h-12 w-12 text-[#404040] mb-4" />
                <p className="text-[#808080] text-sm mb-2">Нет данных о продажах</p>
                <p className="text-[#505050] text-xs">Загрузите данные продаж для отображения тренда</p>
            </div>
        );
    }

    if (data.length === 1) {
        return (
            <div className="h-80 flex flex-col items-center justify-center text-center">
                <TrendingUp className="h-12 w-12 text-[#404040] mb-4" />
                <p className="text-[#808080] text-sm mb-2">Недостаточно данных для тренда</p>
                <p className="text-[#505050] text-xs">
                    Текущая сумма: {formatCurrency(data[0].amount)}
                </p>
                <p className="text-[#505050] text-xs mt-1">
                    Загрузите данные за несколько периодов
                </p>
            </div>
        );
    }

    return (
        <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data}>
                    <defs>
                        <linearGradient id="colorAmount" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#FFFFFF" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#FFFFFF" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#262626" vertical={false} />
                    <XAxis
                        dataKey="period"
                        stroke="#404040"
                        fontSize={10}
                        tickLine={false}
                        axisLine={false}
                    />
                    <YAxis
                        stroke="#404040"
                        fontSize={10}
                        tickLine={false}
                        axisLine={false}
                        tickFormatter={(value) => `${(value / 1000).toFixed(0)}K`}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Area
                        type="monotone"
                        dataKey="amount"
                        stroke="#FFFFFF"
                        strokeWidth={2}
                        fill="url(#colorAmount)"
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
}
