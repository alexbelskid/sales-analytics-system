'use client';

import { useState, useEffect } from 'react';
import { X, TrendingUp, Calendar, Package } from 'lucide-react';
import { agentAnalyticsApi } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface AgentDetailsModalProps {
    agentId: string;
    agentName: string;
    onClose: () => void;
}

export default function AgentDetailsModal({ agentId, agentName, onClose }: AgentDetailsModalProps) {
    const [details, setDetails] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadDetails();
    }, [agentId]);

    async function loadDetails() {
        try {
            const data = await agentAnalyticsApi.getAgentDetails(agentId);
            setDetails(data);
        } catch (err) {
            console.error('Error loading details:', err);
        } finally {
            setLoading(false);
        }
    }

    if (loading) {
        return (
            <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4" onClick={onClose}>
                <div
                    className="bg-[#1a1a1a] rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden"
                    onClick={(e) => e.stopPropagation()}
                >
                    {/* Header */}
                    <div className="border-b border-[#262626] p-6 flex items-center justify-between">
                        <div>
                            <h2 className="text-2xl font-semibold">{agentName}</h2>
                            <p className="text-sm text-[#808080]">Загрузка данных...</p>
                        </div>
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-white/10 rounded-full transition-colors text-gray-400 hover:text-white"
                        >
                            <X className="h-5 w-5" />
                        </button>
                    </div>

                    {/* Skeleton Content */}
                    <div className="p-6 space-y-6">
                        <div className="grid grid-cols-3 gap-4">
                            {[1, 2, 3].map((i) => (
                                <div key={i} className="bg-[#202020] border border-[#262626] rounded-lg p-4 animate-pulse">
                                    <div className="h-3 bg-[#333] rounded w-20 mb-3"></div>
                                    <div className="h-8 bg-[#333] rounded w-24"></div>
                                </div>
                            ))}
                        </div>
                        <div className="bg-[#202020] border border-[#262626] rounded-lg p-6 animate-pulse">
                            <div className="h-4 bg-[#333] rounded w-32 mb-4"></div>
                            <div className="h-48 bg-[#333] rounded"></div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    if (!details) {
        return null;
    }

    return (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4" onClick={onClose}>
            <div
                className="bg-[#1a1a1a] rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="sticky top-0 bg-[#1a1a1a] border-b border-[#262626] p-6 flex items-center justify-between">
                    <div>
                        <h2 className="text-2xl font-semibold">{agentName}</h2>
                        <p className="text-sm text-[#808080]">{details.region} • {details.agent_email}</p>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-[#262626] rounded-lg transition-colors"
                    >
                        <X className="h-5 w-5" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    {/* Key Metrics */}
                    <div className="grid grid-cols-3 gap-4">
                        <div className="bg-[#202020] border border-[#262626] rounded-lg p-4">
                            <p className="text-xs text-[#808080] mb-1">План продаж</p>
                            <p className="text-2xl font-bold">{formatCurrency(details.plan_amount)}</p>
                        </div>
                        <div className="bg-[#202020] border border-[#262626] rounded-lg p-4">
                            <p className="text-xs text-[#808080] mb-1">Факт продаж</p>
                            <p className="text-2xl font-bold">{formatCurrency(details.actual_sales)}</p>
                        </div>
                        <div className="bg-[#202020] border border-[#262626] rounded-lg p-4">
                            <p className="text-xs text-[#808080] mb-1">Выполнение</p>
                            <p className="text-2xl font-bold text-green-500">{details.fulfillment_percent.toFixed(1)}%</p>
                        </div>
                    </div>

                    {/* Daily Sales Trend */}
                    {details.daily_sales_trend && details.daily_sales_trend.length > 0 && (
                        <div className="bg-[#202020] border border-[#262626] rounded-lg p-6">
                            <div className="flex items-center gap-2 mb-4">
                                <TrendingUp className="h-5 w-5 text-gray-400" />
                                <h3 className="font-semibold">Динамика продаж</h3>
                            </div>
                            <div className="h-64">
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={details.daily_sales_trend}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
                                        <XAxis
                                            dataKey="sale_date"
                                            stroke="#404040"
                                            fontSize={10}
                                            tickFormatter={(date) => new Date(date).toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })}
                                        />
                                        <YAxis stroke="#404040" fontSize={10} />
                                        <Tooltip
                                            contentStyle={{ background: '#202020', border: '1px solid #333' }}
                                            formatter={(value: any) => formatCurrency(value)}
                                        />
                                        <Line
                                            type="monotone"
                                            dataKey="amount"
                                            stroke="#f43f5e"
                                            strokeWidth={2}
                                            dot={false}
                                        />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    )}

                    {/* Category Breakdown */}
                    {details.category_breakdown && Object.keys(details.category_breakdown).length > 0 && (
                        <div className="bg-[#202020] border border-[#262626] rounded-lg p-6">
                            <div className="flex items-center gap-2 mb-4">
                                <Package className="h-5 w-5 text-gray-400" />
                                <h3 className="font-semibold">Продажи по категориям</h3>
                            </div>
                            <div className="space-y-3">
                                {Object.entries(details.category_breakdown).map(([category, amount]) => (
                                    <div key={category}>
                                        <div className="flex justify-between items-center mb-1">
                                            <span className="text-sm">{category}</span>
                                            <span className="font-medium">{formatCurrency(amount as number)}</span>
                                        </div>
                                        <div className="w-full h-2 bg-[#262626] rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-gradient-to-r from-purple-600 to-purple-400"
                                                style={{
                                                    width: `${((amount as number) / details.actual_sales * 100)}%`
                                                }}
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Monthly History */}
                    {details.monthly_history && details.monthly_history.length > 0 && (
                        <div className="bg-[#202020] border border-[#262626] rounded-lg p-6">
                            <div className="flex items-center gap-2 mb-4">
                                <Calendar className="h-5 w-5 text-gray-400" />
                                <h3 className="font-semibold">История за 6 месяцев</h3>
                            </div>
                            <div className="h-64">
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={details.monthly_history}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
                                        <XAxis dataKey="month" stroke="#404040" fontSize={10} />
                                        <YAxis stroke="#404040" fontSize={10} />
                                        <Tooltip
                                            contentStyle={{ background: '#202020', border: '1px solid #333' }}
                                            formatter={(value: any) => formatCurrency(value)}
                                        />
                                        <Bar dataKey="sales" fill="#f43f5e" radius={[4, 4, 0, 0]} />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    )}

                    {/* AI Insights */}
                    {details.ai_insights && (
                        <div className="bg-gradient-to-br from-purple-500/10 to-rose-500/10 border border-purple-500/20 rounded-lg p-6">
                            <h3 className="font-semibold mb-3">AI Инсайты</h3>
                            <pre className="text-sm text-[#cccccc] whitespace-pre-wrap">
                                {JSON.stringify(details.ai_insights, null, 2)}
                            </pre>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
