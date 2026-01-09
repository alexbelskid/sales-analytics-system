'use client';

import { useState } from 'react';
import { TrendingUp, TrendingDown, MapPin, Trophy, Eye } from 'lucide-react';
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
        agent.fulfillment_percent >= 100 ? 'text-green-500' :
            agent.fulfillment_percent >= 80 ? 'text-yellow-500' :
                'text-red-500';

    const getTrendIcon = () => {
        if (agent.forecast_fulfillment_percent) {
            return agent.forecast_fulfillment_percent >= 100 ?
                <TrendingUp className="h-4 w-4 text-green-500" /> :
                <TrendingDown className="h-4 w-4 text-red-500" />;
        }
        return null;
    };

    return (
        <>
            <div
                onClick={() => setShowDetails(true)}
                className="ui-card cursor-pointer hover:scale-[1.02] transition-transform duration-200"
            >
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                        <h3 className="font-semibold text-lg mb-1">{agent.agent_name}</h3>
                        <div className="flex items-center gap-2 text-sm text-[#808080]">
                            <MapPin className="h-3 w-3" />
                            <span>{agent.region}</span>
                        </div>
                    </div>

                    {rank <= 3 && (
                        <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-yellow-500/10 text-yellow-500 text-xs">
                            <Trophy className="h-3 w-3" />
                            <span>#{rank}</span>
                        </div>
                    )}
                </div>

                {/* Sales Info */}
                <div className="space-y-3 mb-4">
                    <div>
                        <div className="flex justify-between items-center mb-1">
                            <span className="text-xs text-[#808080]">План</span>
                            <span className="text-sm font-medium">{formatCurrency(agent.plan_amount)}</span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-xs text-[#808080]">Факт</span>
                            <span className="text-sm font-medium">{formatCurrency(agent.actual_sales)}</span>
                        </div>
                    </div>

                    {/* Progress Bar */}
                    <div>
                        <div className="flex justify-between items-center mb-2">
                            <span className="text-xs text-[#808080]">Выполнение</span>
                            <span className={`text-lg font-bold ${fulfillmentColor}`}>
                                {agent.fulfillment_percent.toFixed(1)}%
                            </span>
                        </div>
                        <div className="w-full h-2 bg-[#262626] rounded-full overflow-hidden">
                            <div
                                className="h-full bg-gradient-to-r from-rose-600 to-rose-400 transition-all duration-500"
                                style={{ width: `${Math.min(agent.fulfillment_percent, 100)}%` }}
                            />
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between pt-3 border-t border-[#262626]">
                    <div className="flex items-center gap-2">
                        {getTrendIcon()}
                        {agent.forecast_fulfillment_percent && (
                            <span className="text-xs text-[#808080]">
                                Прогноз: {agent.forecast_fulfillment_percent.toFixed(1)}%
                            </span>
                        )}
                    </div>
                    <button
                        onClick={(e) => {
                            e.stopPropagation();
                            setShowDetails(true);
                        }}
                        className="flex items-center gap-1 text-xs text-rose-500 hover:text-rose-400"
                    >
                        <Eye className="h-3 w-3" />
                        <span>Детали</span>
                    </button>
                </div>
            </div>

            {/* Details Modal */}
            {showDetails && (
                <AgentDetailsModal
                    agentId={agent.agent_id}
                    agentName={agent.agent_name}
                    onClose={() => setShowDetails(false)}
                />
            )}
        </>
    );
}
