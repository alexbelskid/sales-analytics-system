'use client';

import { useState, useEffect } from 'react';
import { X, TrendingUp, Calendar, Package, MoreVertical } from 'lucide-react';
import { agentAnalyticsApi } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
} from "@/components/ui/dialog";

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

    const handleOpenChange = (open: boolean) => {
        if (!open) {
            onClose();
        }
    };

    return (
        <Dialog open={true} onOpenChange={handleOpenChange}>
            {/* 
                Matching style from ABCXYZMatrix:
                className="fixed left-[50%] top-[50%] translate-x-[-50%] translate-y-[-50%] overflow-hidden border border-white/[0.1] backdrop-blur-[40px] shadow-2xl bg-black/50 text-white max-w-2xl max-h-[80vh] overflow-y-auto z-[100]"
                
                Adjustments:
                - max-w-4xl (instead of max-w-2xl) for wider charts
                - max-h-[90vh] (instead of 80vh)
            */}
            <DialogContent className="fixed left-[50%] top-[50%] translate-x-[-50%] translate-y-[-50%] overflow-hidden border border-white/[0.1] backdrop-blur-[40px] shadow-2xl bg-black/40 text-white max-w-4xl w-full max-h-[90vh] overflow-y-auto z-[100] gap-0 p-0 sm:rounded-lg">
                <div className="absolute inset-0 bg-gradient-to-b from-white/[0.05] to-transparent pointer-events-none" />

                {loading ? (
                    <div className="relative z-10">
                        {/* Header Skeleton */}
                        <div className="border-b border-white/5 bg-black/10 backdrop-blur-md p-6 flex items-center justify-between">
                            <div>
                                <DialogTitle className="text-2xl font-light tracking-wide text-white">{agentName}</DialogTitle>
                                <DialogDescription className="text-sm text-gray-400 mt-1">Загрузка данных...</DialogDescription>
                            </div>
                            {/* Close button is handled by DialogPrimitive.Close in DialogContent, but we can keep a visual placeholder if needed or let it be. 
                                DialogContent adds a close button source. We can just rely on that.
                            */}
                        </div>

                        {/* Skeleton Content */}
                        <div className="p-6 space-y-6">
                            {/* Metrics Skeletons */}
                            <div className="grid grid-cols-3 gap-4">
                                {[1, 2, 3].map((i) => (
                                    <div key={i} className="bg-white/[0.03] border border-white/[0.05] rounded-xl p-5 animate-pulse">
                                        <div className="h-3 bg-white/10 rounded w-20 mb-3"></div>
                                        <div className="h-8 bg-white/5 rounded w-24"></div>
                                    </div>
                                ))}
                            </div>

                            {/* Chart Skeleton */}
                            <div className="bg-white/[0.02] border border-white/[0.05] rounded-xl p-6 animate-pulse">
                                <div className="flex items-center gap-2 mb-6">
                                    <div className="p-1.5 rounded-lg bg-white/5 w-8 h-8"></div>
                                    <div className="h-5 bg-white/10 rounded w-32"></div>
                                </div>
                                <div className="h-64 bg-white/[0.02] rounded-lg border border-white/5"></div>
                            </div>

                            {/* List Skeleton */}
                            <div className="bg-white/[0.02] border border-white/[0.05] rounded-xl p-6 animate-pulse">
                                <div className="h-5 bg-white/10 rounded w-40 mb-6"></div>
                                <div className="space-y-4">
                                    {[1, 2, 3].map((i) => (
                                        <div key={i}>
                                            <div className="flex justify-between items-center mb-2">
                                                <div className="h-3 bg-white/10 rounded w-32"></div>
                                                <div className="h-3 bg-white/10 rounded w-16"></div>
                                            </div>
                                            <div className="w-full h-1.5 bg-white/5 rounded-full"></div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                ) : details ? (
                    <div className="relative z-10">
                        {/* Header */}
                        <div className="sticky top-0 z-20 p-6 flex items-center justify-between border-b border-white/5 bg-black/10 backdrop-blur-md">
                            <div>
                                <DialogTitle className="text-2xl font-light tracking-wide">{agentName}</DialogTitle>
                                <DialogDescription className="text-sm text-gray-400 mt-1 flex items-center gap-2">
                                    <span className="inline-block w-2 h-2 rounded-full bg-emerald-500/50"></span>
                                    {details.region}
                                    <span className="text-gray-600">•</span>
                                    {details.agent_email}
                                </DialogDescription>
                            </div>
                        </div>

                        {/* Content */}
                        <div className="p-6 space-y-6">
                            {/* Key Metrics */}
                            <div className="grid grid-cols-3 gap-4">
                                <div className="bg-white/[0.03] border border-white/[0.05] rounded-xl p-5 hover:bg-white/[0.05] transition-colors">
                                    <p className="text-xs text-gray-500 mb-1 uppercase tracking-wider font-medium">План продаж</p>
                                    <p className="text-2xl font-light">{formatCurrency(details.plan_amount)}</p>
                                </div>
                                <div className="bg-white/[0.03] border border-white/[0.05] rounded-xl p-5 hover:bg-white/[0.05] transition-colors">
                                    <p className="text-xs text-gray-500 mb-1 uppercase tracking-wider font-medium">Факт продаж</p>
                                    <p className="text-2xl font-light">{formatCurrency(details.actual_sales)}</p>
                                </div>
                                <div className="bg-white/[0.03] border border-white/[0.05] rounded-xl p-5 hover:bg-white/[0.05] transition-colors">
                                    <p className="text-xs text-gray-500 mb-1 uppercase tracking-wider font-medium">Выполнение</p>
                                    <p className="text-2xl font-medium text-emerald-400 drop-shadow-sm">{details.fulfillment_percent.toFixed(1)}%</p>
                                </div>
                            </div>

                            {/* Daily Sales Trend */}
                            {details.daily_sales_trend && details.daily_sales_trend.length > 0 && (
                                <div className="bg-white/[0.02] border border-white/[0.05] rounded-xl p-6">
                                    <div className="flex items-center gap-2 mb-6">
                                        <div className="p-1.5 rounded-lg bg-white/5">
                                            <TrendingUp className="h-4 w-4 text-emerald-400" />
                                        </div>
                                        <h3 className="font-light text-lg">Динамика продаж</h3>
                                    </div>
                                    <div className="h-64">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <LineChart data={details.daily_sales_trend}>
                                                <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                                                <XAxis
                                                    dataKey="sale_date"
                                                    stroke="#666"
                                                    fontSize={10}
                                                    tickFormatter={(date) => new Date(date).toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })}
                                                    tickLine={false}
                                                    axisLine={false}
                                                    dy={10}
                                                />
                                                <YAxis stroke="#666" fontSize={10} tickLine={false} axisLine={false} dx={-10} />
                                                <Tooltip
                                                    contentStyle={{ background: 'rgba(20,20,20,0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', backdropFilter: 'blur(4px)' }}
                                                    formatter={(value: any) => [formatCurrency(value), 'Продажи']}
                                                    labelStyle={{ color: '#999', marginBottom: '4px' }}
                                                />
                                                <Line
                                                    type="monotone"
                                                    dataKey="amount"
                                                    stroke="#10b981"
                                                    strokeWidth={2}
                                                    dot={false}
                                                    activeDot={{ r: 4, fill: '#10b981', stroke: '#fff', strokeWidth: 2 }}
                                                />
                                            </LineChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>
                            )}

                            {/* Category Breakdown */}
                            {details.category_breakdown && Object.keys(details.category_breakdown).length > 0 && (
                                <div className="bg-white/[0.02] border border-white/[0.05] rounded-xl p-6">
                                    <div className="flex items-center gap-2 mb-6">
                                        <div className="p-1.5 rounded-lg bg-white/5">
                                            <Package className="h-4 w-4 text-amber-400" />
                                        </div>
                                        <h3 className="font-light text-lg">Продажи по категориям</h3>
                                    </div>
                                    <div className="space-y-4">
                                        {Object.entries(details.category_breakdown).map(([category, amount]) => (
                                            <div key={category}>
                                                <div className="flex justify-between items-center mb-2">
                                                    <span className="text-sm text-gray-300">{category}</span>
                                                    <span className="font-medium text-sm">{formatCurrency(amount as number)}</span>
                                                </div>
                                                <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                                                    <div
                                                        className="h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full"
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
                                <div className="bg-white/[0.02] border border-white/[0.05] rounded-xl p-6">
                                    <div className="flex items-center gap-2 mb-6">
                                        <div className="p-1.5 rounded-lg bg-white/5">
                                            <Calendar className="h-4 w-4 text-blue-400" />
                                        </div>
                                        <h3 className="font-light text-lg">История за 6 месяцев</h3>
                                    </div>
                                    <div className="h-64">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <BarChart data={details.monthly_history}>
                                                <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                                                <XAxis dataKey="month" stroke="#666" fontSize={10} tickLine={false} axisLine={false} dy={10} />
                                                <YAxis stroke="#666" fontSize={10} tickLine={false} axisLine={false} dx={-10} />
                                                <Tooltip
                                                    contentStyle={{ background: 'rgba(20,20,20,0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', backdropFilter: 'blur(4px)' }}
                                                    formatter={(value: any) => [formatCurrency(value), 'Продажи']}
                                                    labelStyle={{ color: '#999', marginBottom: '4px' }}
                                                    cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                                                />
                                                <Bar dataKey="sales" fill="#3b82f6" radius={[4, 4, 0, 0]} maxBarSize={40} />
                                            </BarChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>
                            )}

                            {/* AI Insights */}
                            {details.ai_insights && (
                                <div className="bg-gradient-to-br from-indigo-500/10 to-purple-500/10 border border-indigo-500/20 rounded-xl p-6 relative overflow-hidden">
                                    <div className="absolute top-0 right-0 p-3 opacity-20">
                                        <MoreVertical className="w-24 h-24 text-indigo-500" /> {/* Just a visual decoration placeholder if needed */}
                                    </div>
                                    <h3 className="font-medium mb-3 text-indigo-200">AI Инсайты</h3>
                                    <pre className="text-sm text-indigo-100/80 whitespace-pre-wrap font-sans leading-relaxed">
                                        {JSON.stringify(details.ai_insights, null, 2)}
                                    </pre>
                                </div>
                            )}
                        </div>
                    </div>
                ) : null}
            </DialogContent>
        </Dialog>
    );
}
