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
import { formatCurrency } from '@/lib/utils';

// Demo data
const demoData = [
    { name: 'ООО Альфа', total: 450000 },
    { name: 'ИП Петров', total: 380000 },
    { name: 'ЗАО Бета', total: 320000 },
    { name: 'ООО Гамма', total: 290000 },
    { name: 'АО Дельта', total: 250000 },
];

interface CustomerData {
    customer_id?: string;
    name: string;
    total: number;
}

export default function TopCustomersChart() {
    const [data, setData] = useState<CustomerData[]>(demoData);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, []);

    async function loadData() {
        try {
            const customers = await analyticsApi.getTopCustomers(5);
            if (customers.length > 0) {
                setData(customers);
            }
        } catch (err) {
            // Use demo data on error
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

    const maxTotal = Math.max(...data.map(d => d.total), 1);

    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            return (
                <div className="rounded-lg border bg-background p-3 shadow-lg">
                    <p className="text-sm font-medium">{label}</p>
                    <p className="text-sm text-rose-800">
                        {formatCurrency(payload[0].value)}
                    </p>
                </div>
            );
        }
        return null;
    };

    return (
        <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data} layout="vertical" margin={{ left: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" horizontal={false} />
                    <XAxis
                        type="number"
                        stroke="hsl(var(--muted-foreground))"
                        fontSize={12}
                        tickLine={false}
                        tickFormatter={(value) => `${(value / 1000).toFixed(0)}K`}
                    />
                    <YAxis
                        dataKey="name"
                        type="category"
                        stroke="hsl(var(--muted-foreground))"
                        fontSize={12}
                        tickLine={false}
                        width={100}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar
                        dataKey="total"
                        radius={[0, 8, 8, 0]}
                    >
                        {data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={getRedColor(entry.total, maxTotal)} />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}
