'use client';

import { useState } from 'react';
import { TrendingUp, TrendingDown, MapPin, Trophy, Eye, User } from 'lucide-react';
import { formatCurrency } from '@/lib/utils';
import AgentDetailsModal from './AgentDetailsModal';
import LiquidButton from './LiquidButton';

interface AgentCardProps {
    agent: {
        agent_id: string;
        agent_name: string;
        agent_email: string;
        region: string;
        plan_amount: number;
        actual_sales: number;
        fulfillment_percent: number;
        forecast_fulfillment_percent?: number;
        ranking?: number;
    };
    rank: number;
}

export default function AgentCard({ agent, rank }: AgentCardProps) {
    const [showDetails, setShowDetails] = useState(false);

    const fulfillmentColor =
        agent.fulfillment_percent >= 100 ? 'text-emerald-400' :
            agent.fulfillment_percent >= 80 ? 'text-amber-400' :
                agent.fulfillment_percent >= 50 ? 'text-orange-400' :
                    'text-rose-400';

    const progressColor =
        agent.fulfillment_percent >= 100 ? 'from-emerald-600 to-emerald-400' :
            agent.fulfillment_percent >= 80 ? 'from-amber-600 to-amber-400' :
                agent.fulfillment_percent >= 50 ? 'from-orange-600 to-orange-400' :
                    'from-rose-600 to-rose-400';

    const getTrendIcon = () => {
        if (agent.forecast_fulfillment_percent) {
            return agent.forecast_fulfillment_percent >= 100 ?
                <TrendingUp className="h-4 w-4 text-emerald-400" /> :
                <TrendingDown className="h-4 w-4 text-rose-400" />;
        }
        return null;
    };

    const isTopPerformer = rank <= 3;
    const rankColors: Record<number, string> = {
        1: 'from-yellow-500 to-amber-600',
        2: 'from-gray-300 to-gray-500',
        3: 'from-orange-400 to-orange-600',
    };

    return (
        <>
            <div
                onClick={() => setShowDetails(true)}
                className={`
                    glass-panel
                    cursor-pointer transition-all duration-300 
                    hover:border-rose-800/50 hover:shadow-lg hover:shadow-rose-900/20 hover:scale-[1.02]
                    ${isTopPerformer ? 'ring-1 ring-yellow-500/20' : ''}
                `}
            >
                {/* Top performer glow */}
                {isTopPerformer && (
                    <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-yellow-500/50 via-amber-400/50 to-yellow-500/50" />
                )}

                <div className="p-5">
                    {/* Header */}
                    <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                            {/* Avatar */}
                            <div className={`
                                w-10 h-10 rounded-full flex items-center justify-center
                                ${isTopPerformer
                                    ? `bg-gradient-to-br ${rankColors[rank]}`
                                    : 'bg-gradient-to-br from-[#333] to-[#222]'
                                }
                            `}>
                                {isTopPerformer ? (
                                    <Trophy className="h-5 w-5 text-white" />
                                ) : (
                                    <User className="h-5 w-5 text-[#808080]" />
                                )}
                            </div>

                            <div className="flex-1 min-w-0">
                                <h3 className="font-semibold text-base truncate text-gray-100">{agent.agent_name}</h3>
                                <div className="flex items-center gap-1.5 text-xs text-gray-400">
                                    <MapPin className="h-3 w-3" />
                                    <span className="truncate">{agent.region}</span>
                                </div>
                            </div>
                        </div>

                        {isTopPerformer && (
                            <div className={`
                                flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold text-white
                                bg-gradient-to-r ${rankColors[rank]}
                            `}>
                                #{rank}
                            </div>
                        )}
                    </div>

                    {/* Sales Info */}
                    <div className="grid grid-cols-2 gap-3 mb-4">
                        <div className="bg-[#0a0a0a] rounded-lg p-3">
                            <div className="text-xs text-[#666] mb-1">План</div>
                            <div className="text-sm font-semibold">{formatCurrency(agent.plan_amount)}</div>
                        </div>
                        <div className="bg-[#0a0a0a] rounded-lg p-3">
                            <div className="text-xs text-[#666] mb-1">Факт</div>
                            <div className="text-sm font-semibold">{formatCurrency(agent.actual_sales)}</div>
                        </div>
                    </div>

                    {/* Progress */}
                    <div className="mb-4">
                        <div className="flex justify-between items-center mb-2">
                            <span className="text-xs text-[#666]">Выполнение</span>
                            <span className={`text-xl font-bold ${fulfillmentColor}`}>
                                {agent.fulfillment_percent.toFixed(1)}%
                            </span>
                        </div>
                        <div className="w-full h-2.5 bg-[#1a1a1a] rounded-full overflow-hidden">
                            <div
                                className={`h-full bg-gradient-to-r ${progressColor} transition-all duration-700 ease-out`}
                                style={{ width: `${Math.min(agent.fulfillment_percent, 100)}%` }}
                            />
                        </div>
                    </div>

                    {/* Footer */}
                    <div className="flex items-center justify-between pt-3 border-t border-[#1f1f1f]">
                        <div className="flex items-center gap-2">
                            {getTrendIcon()}
                            {agent.forecast_fulfillment_percent && (
                                <span className="text-xs text-[#666]">
                                    Прогноз: {agent.forecast_fulfillment_percent.toFixed(1)}%
                                </span>
                            )}
                        </div>
                        <div onClick={(e) => e.stopPropagation()}>
                            <LiquidButton
                                onClick={() => setShowDetails(true)}
                                variant="secondary"
                                icon={Eye}
                                className="h-9 px-4 text-xs min-h-0" // Override for card footer to avoid too much bulk, but keep capsule shape
                            >
                                Детали
                            </LiquidButton>
                        </div>
                    </div>
                </div>
            </div >

            {/* Details Modal */}
            {
                showDetails && (
                    <AgentDetailsModal
                        agentId={agent.agent_id}
                        agentName={agent.agent_name}
                        onClose={() => setShowDetails(false)}
                    />
                )
            }
        </>
    );
}

