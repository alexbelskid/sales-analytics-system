'use client';

import { useState } from 'react';
import Dashboard from '@/components/Dashboard';
import AgentDashboard from '@/components/AgentDashboard';
import LiquidButton from '@/components/LiquidButton';

export default function DashboardPage() {
    const [activeTab, setActiveTab] = useState<'sales' | 'agents'>('agents');

    return (
        <div className="p-8 max-w-7xl mx-auto">
            {/* Tab Navigation */}
            <div className="flex gap-4 mb-8" role="tablist">
                <LiquidButton
                    role="tab"
                    id="tab-sales"
                    aria-selected={activeTab === 'sales'}
                    aria-controls="panel-sales"
                    onClick={() => setActiveTab('sales')}
                    variant={activeTab === 'sales' ? 'primary' : 'secondary'}
                    className="min-w-[120px]"
                >
                    Продажи
                </LiquidButton>
                <LiquidButton
                    role="tab"
                    id="tab-agents"
                    aria-selected={activeTab === 'agents'}
                    aria-controls="panel-agents"
                    onClick={() => setActiveTab('agents')}
                    variant={activeTab === 'agents' ? 'primary' : 'secondary'}
                    className="min-w-[120px]"
                >
                    Агенты
                </LiquidButton>
            </div>

            {/* Tab Content */}
            {activeTab === 'sales' && (
                <div role="tabpanel" id="panel-sales" aria-labelledby="tab-sales">
                    <Dashboard />
                </div>
            )}
            {activeTab === 'agents' && (
                <div role="tabpanel" id="panel-agents" aria-labelledby="tab-agents">
                    <AgentDashboard />
                </div>
            )}
        </div>
    );
}
