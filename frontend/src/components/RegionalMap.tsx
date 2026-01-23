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
        <div className="w-full space-y-6">
            <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium text-[#808080] uppercase tracking-wider">Производительность по регионам</h3>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
                {sortedRegions.map((region, index) => {
                    const isTop = region.fulfillment_percent >= 100;
                    const isMid = region.fulfillment_percent >= 80 && region.fulfillment_percent < 100;

                    // Unified Accent Color (Mercury -> Cyan/Silver, or standard Rose? User asked to remove Red/Orange. Let's use standard white or keep semantic colors ONLY for the bar)
                    const progressColor = isTop
                        ? 'bg-emerald-500'
                        : isMid
                            ? 'bg-amber-500'
                            : 'bg-rose-500';

                    const textColor = isTop
                        ? 'text-emerald-400'
                        : isMid
                            ? 'text-amber-400'
                            : 'text-rose-400';

                    return (
                        <div
                            key={region.region}
                            className="ui-card relative overflow-hidden group hover:scale-[1.02] transition-all duration-300"
                            style={{ animationDelay: `${index * 50}ms` }}
                        >
                            {/* Header */}
                            <div className="flex items-center gap-3 mb-4">
                                <div className="p-2 rounded-full bg-[#262626]">
                                    <MapPin className="h-4 w-4 text-white" />
                                </div>
                                <h4 className="font-medium text-sm text-white truncate uppercase tracking-wide">{region.region}</h4>
                            </div>

                            {/* Stats */}
                            <div className="space-y-3 text-xs">
                                <div className="flex justify-between items-center">
                                    <span className="text-[#808080]">План</span>
                                    <span className="font-medium text-white">{formatCurrency(region.total_plan)}</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-[#808080]">Факт</span>
                                    <span className="font-medium text-white">{formatCurrency(region.total_sales)}</span>
                                </div>

                                {/* Progress */}
                                <div className="pt-3 border-t border-[#262626]">
                                    <div className="flex justify-between items-center mb-2">
                                        <span className="text-[#808080]">Выполнение</span>
                                        <span className={`font-bold text-base ${textColor}`}>
                                            {region.fulfillment_percent.toFixed(1)}%
                                        </span>
                                    </div>
                                    <div className="w-full h-1.5 bg-[#262626] rounded-full overflow-hidden">
                                        <div
                                            className={`h-full ${progressColor} transition-all duration-700 ease-out`}
                                            style={{ width: `${Math.min(region.fulfillment_percent, 100)}%` }}
                                        />
                                    </div>
                                </div>

                                {/* Agents count */}
                                <div className="flex items-center gap-1.5 text-[#606060] pt-1">
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

