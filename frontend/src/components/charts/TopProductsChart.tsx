'use client';

import { useState, useEffect } from 'react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Cell,
} from 'recharts';
import { analyticsApi } from '@/lib/api';
import { formatCurrency, formatNumber } from '@/lib/utils';
import { Package } from 'lucide-react';

const COLORS = [
    '#FFFFFF',
    '#E0E0E0',
    '#C0C0C0',
    '#A0A0A0',
    '#808080',
    '#606060',
];

interface ProductData {
    product_id?: string;
    name: string;
    total_quantity: number;
    total_amount: number;
}

export default function TopProductsChart() {
    const [data, setData] = useState<ProductData[]>([]);
    const [loading, setLoading] = useState(true);
    const [hasRealData, setHasRealData] = useState(false);

    useEffect(() => {
        loadData();
    }, []);

    async function loadData() {
        try {
            const products = await analyticsApi.getTopProducts(6);
            if (products && products.length > 0) {
                setData(products);
                setHasRealData(true);
            }
        } catch (err) {
            console.log('TopProducts: No data available');
        } finally {
            setLoading(false);
        }
    }

    // Generate red gradient colors based on value
    const getRedColor = (value: number, maxValue: number) => {
        const intensity = value / maxValue;
        // Smoother gradient from light red to dark red
        const lightness = 60 - (intensity * 35); // 60% (light) to 25% (dark)
        return `hsl(348, 85%, ${lightness}%)`;
    };

    const maxAmount = Math.max(...data.map(d => d.total_amount), 1);

    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            const item = payload[0].payload;
            return (
                <div className="rounded-lg border border-[#333333] bg-[#202020] p-3 shadow-lg">
                    <p className="text-sm font-medium text-[#E5E5DC]">{label}</p>
                    <p className="text-sm text-[#E5E5DC]">
                        Сумма: {formatCurrency(item.total_amount)}
                    </p>
                    <p className="text-sm text-[#808080]">
                        Продано: {formatNumber(item.total_quantity)} шт.
                    </p>
                </div>
            );
        }
        return null;
    };

    if (loading) {
        return (
            <div className="h-72 flex items-center justify-center">
                <div className="text-[#808080] text-sm">Загрузка...</div>
            </div>
        );
    }

    if (!hasRealData || data.length === 0) {
        return (
            <div className="h-72 flex flex-col items-center justify-center text-center">
                <Package className="h-12 w-12 text-[#404040] mb-4" />
                <p className="text-[#808080] text-sm mb-2">Нет данных о продуктах</p>
                <p className="text-[#505050] text-xs">Загрузите данные продаж для отображения графика</p>
            </div>
        );
    }

    return (
        <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#262626" horizontal={false} />
                    <XAxis
                        type="number"
                        stroke="#404040"
                        fontSize={10}
                        tickLine={false}
                        axisLine={false}
                        tickFormatter={(value) => `${(value / 1000).toFixed(0)}K`}
                    />
                    <YAxis
                        type="category"
                        dataKey="name"
                        stroke="#404040"
                        fontSize={10}
                        tickLine={false}
                        axisLine={false}
                        width={160}
                        tickFormatter={(value) => value.length > 20 ? value.substring(0, 18) + '...' : value}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="total_amount" radius={[0, 8, 8, 0]}>
                        {data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={getRedColor(entry.total_amount, maxAmount)} />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}
