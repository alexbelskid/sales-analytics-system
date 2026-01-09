'use client';

import { MapPin } from 'lucide-react';
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
    return (
        <div className="ui-card">
            <h3 className="text-lg font-semibold mb-6">Производительность по регионам</h3>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
                {regions.map((region) => {
                    const color =
                        region.fulfillment_percent >= 100 ? 'border-green-500/50 bg-green-500/5' :
                            region.fulfillment_percent >= 80 ? 'border-yellow-500/50 bg-yellow-500/5' :
                                'border-red-500/50 bg-red-500/5';

                    return (
                        <div
                            key={region.region}
                            className={`p-4 rounded-lg border ${color} transition-all hover:scale-105`}
                        >
                            <div className="flex items-center gap-2 mb-3">
                                <MapPin className="h-4 w-4 text-[#808080]" />
                                <h4 className="font-medium">{region.region}</h4>
                            </div>

                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-[#808080]">План</span>
                                    <span>{formatCurrency(region.total_plan)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-[#808080]">Факт</span>
                                    <span>{formatCurrency(region.total_sales)}</span>
                                </div>
                                <div className="flex justify-between items-center pt-2 border-t border-[#262626]">
                                    <span className="text-[#808080]">Выполнение</span>
                                    <span className="font-bold text-lg">
                                        {region.fulfillment_percent.toFixed(1)}%
                                    </span>
                                </div>
                                <div className="text-[#808080] text-xs">
                                    Агентов: {region.agents_count}
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
