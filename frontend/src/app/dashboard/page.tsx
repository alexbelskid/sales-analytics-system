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
            <div className="flex gap-4 mb-8">
                <LiquidButton
                    onClick={() => setActiveTab('sales')}
                    variant={activeTab === 'sales' ? 'primary' : 'secondary'}
                    className="min-w-[120px]"
                >
                    Продажи
                </LiquidButton>
                <LiquidButton
                    onClick={() => setActiveTab('agents')}
                    variant={activeTab === 'agents' ? 'primary' : 'secondary'}
                    className="min-w-[120px]"
                >
                    Агенты
                </LiquidButton>
            </div>

            {/* Tab Content */}
            {activeTab === 'sales' && <Dashboard />}
            {activeTab === 'agents' && <AgentDashboard />}
        </div>
    );
}
