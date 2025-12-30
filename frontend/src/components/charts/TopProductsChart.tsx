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

// Demo data
const demoData = [
    { name: 'Товар А', total_quantity: 245, total_amount: 367500 },
    { name: 'Товар Б', total_quantity: 189, total_amount: 283500 },
    { name: 'Товар В', total_quantity: 156, total_amount: 234000 },
    { name: 'Товар Г', total_quantity: 134, total_amount: 201000 },
    { name: 'Товар Д', total_quantity: 98, total_amount: 147000 },
    { name: 'Товар Е', total_quantity: 87, total_amount: 130500 },
];

const COLORS = [
    'hsl(221, 83%, 53%)',  // primary blue
    'hsl(142, 76%, 36%)',  // green
    'hsl(262, 83%, 58%)',  // purple
    'hsl(25, 95%, 53%)',   // orange
    'hsl(199, 89%, 48%)',  // cyan
    'hsl(346, 77%, 50%)',  // pink
];

interface ProductData {
    product_id?: string;
    name: string;
    total_quantity: number;
    total_amount: number;
}

export default function TopProductsChart() {
    const [data, setData] = useState<ProductData[]>(demoData);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, []);

    async function loadData() {
        try {
            const products = await analyticsApi.getTopProducts(6);
            if (products.length > 0) {
                setData(products);
            }
        } catch (err) {
            // Use demo data on error
        } finally {
            setLoading(false);
        }
    }

    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            const item = payload[0].payload;
            return (
                <div className="rounded-lg border bg-background p-3 shadow-lg">
                    <p className="text-sm font-medium">{label}</p>
                    <p className="text-sm text-primary">
                        Выручка: {formatCurrency(item.total_amount)}
                    </p>
                    <p className="text-sm text-muted-foreground">
                        Продано: {formatNumber(item.total_quantity)} шт.
                    </p>
                </div>
            );
        }
        return null;
    };

    return (
        <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                    <XAxis
                        dataKey="name"
                        stroke="hsl(var(--muted-foreground))"
                        fontSize={12}
                        tickLine={false}
                    />
                    <YAxis
                        stroke="hsl(var(--muted-foreground))"
                        fontSize={12}
                        tickLine={false}
                        tickFormatter={(value) => `${(value / 1000).toFixed(0)}K`}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="total_amount" radius={[4, 4, 0, 0]}>
                        {data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}
