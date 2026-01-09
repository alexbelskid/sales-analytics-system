'use client';

import { MapPin, Users, TrendingUp } from 'lucide-react';
import { formatCurrency } from '@/lib/utils';

interface RegionalMapProps {
    regions: Array<{
        region: string;
        total_plan: number;
        total_sales: number;
        fulfillment_percent: number;
        agents_count: number;
    }>;
}

export default function RegionalMap({ regions }: RegionalMapProps) {
    // Sort regions by fulfillment for visual ordering
    const sortedRegions = [...regions].sort((a, b) => b.fulfillment_percent - a.fulfillment_percent);

    return (
        <div className="bg-gradient-to-br from-[#1a1a1a] to-[#0f0f0f] rounded-xl border border-[#262626] p-6">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold">Производительность по регионам</h3>
                <div className="flex items-center gap-2 text-xs text-[#666]">
                    <span className="flex items-center gap-1">
                        <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
                        ≥100%
                    </span>
                    <span className="flex items-center gap-1">
                        <div className="w-2 h-2 rounded-full bg-amber-500"></div>
                        ≥80%
                    </span>
                    <span className="flex items-center gap-1">
                        <div className="w-2 h-2 rounded-full bg-rose-500"></div>
                        &lt;80%
                    </span>
                </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
                {sortedRegions.map((region, index) => {
                    const isTop = region.fulfillment_percent >= 100;
                    const isMid = region.fulfillment_percent >= 80 && region.fulfillment_percent < 100;

                    const borderColor = isTop
                        ? 'border-emerald-500/30 hover:border-emerald-500/50'
                        : isMid
                            ? 'border-amber-500/30 hover:border-amber-500/50'
                            : 'border-rose-500/30 hover:border-rose-500/50';

                    const glowColor = isTop
                        ? 'hover:shadow-emerald-500/10'
                        : isMid
                            ? 'hover:shadow-amber-500/10'
                            : 'hover:shadow-rose-500/10';

                    const progressColor = isTop
                        ? 'from-emerald-600 to-emerald-400'
                        : isMid
                            ? 'from-amber-600 to-amber-400'
                            : 'from-rose-600 to-rose-400';

                    const textColor = isTop
                        ? 'text-emerald-400'
                        : isMid
                            ? 'text-amber-400'
                            : 'text-rose-400';

                    return (
                        <div
                            key={region.region}
                            className={`
                                relative overflow-hidden p-4 rounded-xl border bg-[#0a0a0a]/50
                                transition-all duration-300 hover:scale-[1.02] hover:shadow-lg cursor-pointer
                                ${borderColor} ${glowColor}
                            `}
                            style={{ animationDelay: `${index * 50}ms` }}
                        >
                            {/* Top accent line */}
                            <div className={`absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r ${progressColor}`} />

                            {/* Header */}
                            <div className="flex items-center gap-2 mb-4">
                                <div className={`p-1.5 rounded-lg bg-gradient-to-br ${progressColor}`}>
                                    <MapPin className="h-3.5 w-3.5 text-white" />
                                </div>
                                <h4 className="font-medium text-sm truncate">{region.region}</h4>
                            </div>

                            {/* Stats */}
                            <div className="space-y-2.5 text-xs">
                                <div className="flex justify-between items-center">
                                    <span className="text-[#666]">План</span>
                                    <span className="font-medium">{formatCurrency(region.total_plan)}</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-[#666]">Факт</span>
                                    <span className="font-medium">{formatCurrency(region.total_sales)}</span>
                                </div>

                                {/* Progress */}
                                <div className="pt-2 border-t border-[#1f1f1f]">
                                    <div className="flex justify-between items-center mb-1.5">
                                        <span className="text-[#666]">Выполнение</span>
                                        <span className={`font-bold text-base ${textColor}`}>
                                            {region.fulfillment_percent.toFixed(1)}%
                                        </span>
                                    </div>
                                    <div className="w-full h-1.5 bg-[#1a1a1a] rounded-full overflow-hidden">
                                        <div
                                            className={`h-full bg-gradient-to-r ${progressColor} transition-all duration-700 ease-out`}
                                            style={{ width: `${Math.min(region.fulfillment_percent, 100)}%` }}
                                        />
                                    </div>
                                </div>

                                {/* Agents count */}
                                <div className="flex items-center gap-1.5 text-[#555] pt-1">
                                    <Users className="h-3 w-3" />
                                    <span>{region.agents_count} агентов</span>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

