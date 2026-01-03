'use client';

import { useEffect, useState } from 'react';
import DataUploader from '@/components/DataUploader';

export default function DashboardPage() {
    const [stats, setStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    const loadStats = async () => {
        try {
            setLoading(true);
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ''}/api/data/analytics/summary`);
            if (response.ok) {
                const data = await response.json();
                setStats(data);
            }
        } catch (error) {
            console.error('Error loading stats:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadStats();

        // Listen for upload events to refresh data
        const handleDataUploaded = () => loadStats();
        window.addEventListener('dataUploaded', handleDataUploaded);
        return () => window.removeEventListener('dataUploaded', handleDataUploaded);
    }, []);

    return (
        <div className="p-8 max-w-7xl mx-auto">
            <h1 className="text-3xl font-bold mb-8 text-white">Dashboard & Analytics</h1>

            {/* Data Upload Section */}
            <DataUploader />

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-[#1A1A1A] border border-[#2A2A2A] rounded-xl p-6 shadow-sm">
                    <div className="text-sm text-gray-400 mb-2 uppercase tracking-wider">Revenue (Month)</div>
                    <div className="text-3xl font-bold text-white">
                        {stats?.monthly?.revenue
                            ? `${stats.monthly.revenue.toLocaleString('ru-RU')} BYN`
                            : '0 BYN'}
                    </div>
                    <div className="text-xs text-gray-500 mt-2 flex items-center gap-1">
                        <span className="w-2 h-2 rounded-full bg-green-500"></span>
                        {stats?.monthly?.period || 'Current Month'}
                    </div>
                </div>

                <div className="bg-[#1A1A1A] border border-[#2A2A2A] rounded-xl p-6 shadow-sm">
                    <div className="text-sm text-gray-400 mb-2 uppercase tracking-wider">Total Orders</div>
                    <div className="text-3xl font-bold text-white">
                        {stats?.monthly?.orders || 0}
                    </div>
                    <div className="text-xs text-gray-500 mt-2">
                        Processed this month
                    </div>
                </div>

                <div className="bg-[#1A1A1A] border border-[#2A2A2A] rounded-xl p-6 shadow-sm">
                    <div className="text-sm text-gray-400 mb-2 uppercase tracking-wider">Avg. Check</div>
                    <div className="text-3xl font-bold text-white">
                        {stats?.monthly?.revenue && stats?.monthly?.orders
                            ? `${(stats.monthly.revenue / stats.monthly.orders).toFixed(2)} BYN`
                            : '0 BYN'
                        }
                    </div>
                    <div className="text-xs text-gray-500 mt-2">
                        Revenue / Orders
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Top Products */}
                <div className="bg-[#1A1A1A] border border-[#2A2A2A] rounded-xl p-6">
                    <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                        <span>🏆</span> Top Products
                    </h2>
                    {stats?.sales?.length > 0 ? (
                        <div className="space-y-4">
                            {stats.sales.slice(0, 5).map((item: any, index: number) => (
                                <div key={index} className="flex justify-between items-center p-3 bg-[#222] rounded-lg border border-[#333]">
                                    <div>
                                        <div className="font-medium text-white">{item.product}</div>
                                        <div className="text-sm text-gray-400">
                                            {item.quantity} units sold
                                        </div>
                                    </div>
                                    <div className="text-green-400 font-semibold">
                                        {item.total.toLocaleString('ru-RU')} BYN
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-gray-500 text-center py-8">
                            No sales data available yet.
                        </div>
                    )}
                </div>

                {/* Top Clients */}
                <div className="bg-[#1A1A1A] border border-[#2A2A2A] rounded-xl p-6">
                    <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                        <span>👥</span> Top Clients
                    </h2>
                    {stats?.clients?.length > 0 ? (
                        <div className="space-y-4">
                            {stats.clients.slice(0, 5).map((client: any, index: number) => (
                                <div key={index} className="flex justify-between items-center p-3 bg-[#222] rounded-lg border border-[#333]">
                                    <div>
                                        <div className="font-medium text-white">{client.client}</div>
                                        <div className="text-sm text-gray-400">
                                            {client.orders} orders
                                        </div>
                                    </div>
                                    <div className="text-green-400 font-semibold">
                                        {client.total.toLocaleString('ru-RU')} BYN
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-gray-500 text-center py-8">
                            No client data available yet.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
