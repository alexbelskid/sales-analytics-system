'use client';

import { useState } from 'react';
import { TrendingUp, TrendingDown, MapPin, Trophy, User } from 'lucide-react';
import { formatCurrency } from '@/lib/utils';
import AgentDetailsModal from './AgentDetailsModal';


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
                role="button"
                tabIndex={0}
                aria-label={`View details for ${agent.agent_name}`}
                onClick={() => setShowDetails(true)}
                onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        setShowDetails(true);
                    }
                }}
                className={`
                    relative overflow-hidden
                    rounded-[32px] 
                    border border-white/[0.08] 
                    backdrop-blur-[30px] 
                    bg-gradient-to-br from-white/[0.02] to-transparent
                    shadow-[0_20px_60px_-20px_rgba(0,0,0,0.6),inset_0_0_40px_0_rgba(255,255,255,0.02)]
                    cursor-pointer 
                    transition-all duration-500 ease-out
                    hover:border-rose-500/30 
                    hover:shadow-[0_30px_80px_-20px_rgba(244,63,94,0.4),inset_0_0_60px_0_rgba(255,255,255,0.04)]
                    hover:scale-[1.02]
                    hover:-translate-y-1
                    focus-visible:outline-none
                    focus-visible:ring-2
                    focus-visible:ring-rose-500/50
                    group
                    ${isTopPerformer ? 'ring-1 ring-yellow-500/20' : ''}
                `}
            >
                {/* Gradient Overlay */}
                <div className="absolute inset-0 bg-gradient-to-b from-white/[0.03] to-transparent pointer-events-none" />

                {/* Top Sheen */}
                <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/20 to-transparent" />

                {/* Top performer glow - REMOVED per user request */}

                <div className="relative p-6">
                    {/* Header */}
                    <div className="flex items-start justify-between mb-5">
                        <div className="flex items-center gap-3">
                            {/* Avatar with glass effect */}
                            <div className={`
                                relative w-12 h-12 rounded-full flex items-center justify-center
                                backdrop-blur-sm
                                border border-white/10
                                shadow-lg
                                transition-all duration-300
                                group-hover:scale-110
                                ${isTopPerformer
                                    ? `bg-gradient-to-br ${rankColors[rank]} shadow-${rank === 1 ? 'yellow' : rank === 2 ? 'gray' : 'orange'}-500/40`
                                    : 'bg-gradient-to-br from-white/10 to-white/5'
                                }
                            `}>
                                <div className="absolute inset-0 rounded-full bg-gradient-to-b from-white/10 to-transparent" />
                                {isTopPerformer ? (
                                    <Trophy className="h-6 w-6 text-white relative z-10" />
                                ) : (
                                    <User className="h-6 w-6 text-gray-300 relative z-10" />
                                )}
                            </div>

                            <div className="flex-1 min-w-0">
                                <h3 className="font-semibold text-base truncate text-white mb-1">{agent.agent_name}</h3>
                                <div className="flex items-center gap-1.5 text-xs text-gray-400">
                                    <MapPin className="h-3 w-3" />
                                    <span className="truncate">{agent.region}</span>
                                </div>
                            </div>
                        </div>

                        {isTopPerformer && (
                            <div className={`
                                flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold text-white
                                bg-gradient-to-r ${rankColors[rank]}
                                shadow-lg backdrop-blur-sm
                                border border-white/20
                            `}>
                                <Trophy className="h-3 w-3" />
                                #{rank}
                            </div>
                        )}
                    </div>

                    {/* Sales Info with glass panels */}
                    <div className="grid grid-cols-2 gap-3 mb-5">
                        <div className="relative overflow-hidden rounded-2xl border border-white/5 bg-black/20 backdrop-blur-sm p-4 group/card">
                            <div className="absolute inset-0 bg-gradient-to-br from-white/[0.02] to-transparent" />
                            <div className="relative z-10">
                                <div className="text-xs text-gray-500 mb-1.5 font-medium uppercase tracking-wider">План</div>
                                <div className="text-sm font-bold text-white">{formatCurrency(agent.plan_amount)}</div>
                            </div>
                        </div>
                        <div className="relative overflow-hidden rounded-2xl border border-white/5 bg-black/20 backdrop-blur-sm p-4 group/card">
                            <div className="absolute inset-0 bg-gradient-to-br from-white/[0.02] to-transparent" />
                            <div className="relative z-10">
                                <div className="text-xs text-gray-500 mb-1.5 font-medium uppercase tracking-wider">Факт</div>
                                <div className="text-sm font-bold text-white">{formatCurrency(agent.actual_sales)}</div>
                            </div>
                        </div>
                    </div>

                    {/* Progress with enhanced glass effect */}
                    <div className="mb-5">
                        <div className="flex justify-between items-center mb-3">
                            <span className="text-xs text-gray-500 font-medium uppercase tracking-wider">Выполнение</span>
                            <span className={`text-2xl font-bold ${fulfillmentColor} drop-shadow-lg`}>
                                {agent.fulfillment_percent.toFixed(1)}%
                            </span>
                        </div>
                        <div className="relative w-full h-3 rounded-full overflow-hidden bg-black/40 border border-white/5 backdrop-blur-sm">
                            <div className="absolute inset-0 bg-gradient-to-r from-white/[0.03] to-transparent" />
                            <div
                                className={`
                                    relative h-full bg-gradient-to-r ${progressColor} 
                                    transition-all duration-700 ease-out
                                    shadow-lg
                                    before:absolute before:inset-0 before:bg-gradient-to-r before:from-white/20 before:to-transparent
                                `}
                                style={{ width: `${Math.min(agent.fulfillment_percent, 100)}%` }}
                            />
                        </div>
                    </div>

                    {/* Footer with glass separator */}
                    <div className="flex items-center justify-between pt-4 border-t border-white/5">
                        <div className="flex items-center gap-2">
                            {getTrendIcon()}
                            {agent.forecast_fulfillment_percent && (
                                <span className="text-xs text-gray-500">
                                    Прогноз: {agent.forecast_fulfillment_percent.toFixed(1)}%
                                </span>
                            )}
                        </div>

                    </div>
                </div>
            </div>

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

