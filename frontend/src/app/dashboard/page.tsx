'use client';

import { useState } from 'react';
import Dashboard from '@/components/Dashboard';
import AgentDashboard from '@/components/AgentDashboard';

export default function DashboardPage() {
    const [activeTab, setActiveTab] = useState<'sales' | 'agents'>('agents');

    return (
        <div className="p-8 max-w-7xl mx-auto">
            {/* Tab Navigation */}
            <div className="flex gap-2 mb-8 border-b border-[#262626]">
                <button
                    onClick={() => setActiveTab('sales')}
                    className={`px-6 py-3 font-medium transition-all ${activeTab === 'sales'
                        ? 'text-white border-b-2 border-rose-800'
                        : 'text-[#808080] hover:text-white'
                        }`}
                >
                    Продажи
                </button>
                <button
                    onClick={() => setActiveTab('agents')}
                    className={`px-6 py-3 font-medium transition-all ${activeTab === 'agents'
                        ? 'text-white border-b-2 border-rose-800'
                        : 'text-[#808080] hover:text-white'
                        }`}
                >
                    Агенты
                </button>
            </div>

            {/* Tab Content */}
            {activeTab === 'sales' && <Dashboard />}
            {activeTab === 'agents' && <AgentDashboard />}
        </div>
    );
}
