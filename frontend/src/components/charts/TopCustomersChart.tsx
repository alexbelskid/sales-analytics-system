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
                        fill="hsl(348, 70%, 36%)"
                        radius={[0, 8, 8, 0]}
                    />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}
