"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import {
    Plus,
    MessageSquare,
    Book,
    Activity
} from "lucide-react";

import KnowledgeTab from "@/components/ai-assistant/KnowledgeTab";
import StatusTab from "@/components/ai-assistant/StatusTab";
import KnowledgeModal from "@/components/ai-assistant/KnowledgeModal";
import AiAssistantPanel from "@/components/ai-assistant/AiAssistantPanel";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://athletic-alignment-production-db41.up.railway.app';

interface KnowledgeItem {
    id: string;
    category: string;
    title: string;
    content: string;
}

interface AIStatus {
    monthly: {
        revenue: number;
        orders: number;
        customers: number;
        period: string;
    };
    sales: any[];
    clients: any[];
    knowledge: {
        total: number;
        categories: { name: string; count: number }[];
    };
    training: {
        total: number;
        avg_confidence: number;
    };
}

const CATEGORIES = [
    { id: 'products', label: 'Наши продукты' },
    { id: 'terms', label: 'Условия работы' },
    { id: 'contacts', label: 'Контакты' },
    { id: 'faq', label: 'FAQ' },
    { id: 'company_info', label: 'О компании' },
];

type TabType = 'chat' | 'knowledge' | 'status';

export default function AIAssistantPage() {
    const { toast } = useToast();
    const [activeTab, setActiveTab] = useState<TabType>('chat');

    // Data state
    const [knowledgeItems, setKnowledgeItems] = useState<KnowledgeItem[]>([]);
    const [aiStatus, setAIStatus] = useState<AIStatus | null>(null);
    const [loading, setLoading] = useState(false); // Default to false for chat

    // Modal state
    const [showKnowledgeModal, setShowKnowledgeModal] = useState(false);
    const [editingKnowledge, setEditingKnowledge] = useState<KnowledgeItem | null>(null);

    useEffect(() => {
        if (activeTab !== 'chat') {
            loadData();
        }
    }, [activeTab]);

    const loadData = async () => {
        setLoading(true);
        try {
            if (activeTab === 'knowledge') {
                const response = await fetch(`${API_BASE}/api/knowledge`);
                const data = await response.json();
                setKnowledgeItems(data);
            } else if (activeTab === 'status') {
                const response = await fetch(`${API_BASE}/api/data/analytics/summary`);
                const data = await response.json();
                setAIStatus(data);
            }
        } catch (error) {
            console.error(error);
            // Silent error or toast?
            // toast({ title: "Ошибка", description: "Не удалось загрузить данные" });
        } finally {
            setLoading(false);
        }
    };

    // Knowledge Handlers
    const handleSaveKnowledge = async (data: { category: string; title: string; content: string }) => {
        try {
            const url = editingKnowledge
                ? `${API_BASE}/api/knowledge/${editingKnowledge.id}`
                : `${API_BASE}/api/knowledge`;
            const method = editingKnowledge ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });

            if (response.ok) {
                toast({ title: "Успешно", description: editingKnowledge ? "Обновлено" : "Создано" });
                loadData();
                setShowKnowledgeModal(false);
                setEditingKnowledge(null);
            }
        } catch (error) {
            toast({ title: "Ошибка", description: "Не удалось сохранить" });
        }
    };

    const handleDeleteKnowledge = async (id: string) => {
        if (!confirm("Удалить эту запись?")) return;
        try {
            const response = await fetch(`${API_BASE}/api/knowledge/${id}`, { method: 'DELETE' });
            if (response.ok) {
                toast({ title: "Удалено" });
                loadData();
            }
        } catch (error) {
            toast({ title: "Ошибка", description: "Не удалось удалить" });
        }
    };

    return (
        <div className="min-h-screen bg-[#202020] text-white">
            <div className="max-w-7xl mx-auto p-6">
                {/* Header Section */}
                {/* Header Section - Only show continuously if there are actions (like Add button) */}
                {(activeTab === 'knowledge') && (
                    <div className="flex flex-col gap-4 mb-8">
                        <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
                            <div /> {/* Spacer or Title placeholder if needed later, but empty for now to push button right if justify-between */}

                            <Button
                                onClick={() => {
                                    setEditingKnowledge(null);
                                    setShowKnowledgeModal(true);
                                }}
                                className="bg-cyan-600 text-white hover:bg-cyan-500 rounded-full px-6 h-10 font-medium transition-all shadow-lg shadow-cyan-600/25"
                            >
                                <Plus className="mr-2 h-4 w-4" />
                                Добавить запись
                            </Button>
                        </div>
                    </div>
                )}

                {/* Tabs Navigation */}
                <div className="flex gap-2 sm:gap-6 border-b border-[#262626] mb-6 overflow-x-auto scrollbar-hide -mx-4 px-4 sm:mx-0 sm:px-0">
                    {[
                        { id: 'chat', label: 'Чат', icon: MessageSquare },
                        { id: 'status', label: 'Дашборд', icon: Activity },
                        { id: 'knowledge', label: 'База знаний', icon: Book },
                    ].map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id as TabType)}
                            className={`flex items-center gap-2 pb-3 px-1 text-sm font-medium tracking-wide transition-colors relative whitespace-nowrap ${activeTab === tab.id ? 'text-white' : 'text-[#505050] hover:text-[#909090]'
                                }`}
                        >
                            <tab.icon className={`w-4 h-4 ${activeTab === tab.id ? 'text-rose-500' : ''}`} />
                            {tab.label}
                            {activeTab === tab.id && (
                                <div className="absolute bottom-[-1px] left-0 right-0 h-[2px] bg-cyan-500 rounded-full shadow-[0_0_10px_rgba(34,211,238,0.5)]" />
                            )}
                        </button>
                    ))}
                </div>

                {/* Content Area */}
                <div className="animate-in fade-in duration-500 min-h-[500px]">
                    {activeTab === 'chat' && <AiAssistantPanel />}

                    {loading ? (
                        <div className="flex flex-col items-center justify-center py-20 gap-4">
                            <div className="h-8 w-8 border-2 border-rose-500/20 border-t-rose-500 rounded-full animate-spin" />
                            <p className="text-sm text-[#404040]">Загрузка данных...</p>
                        </div>
                    ) : (
                        <>
                            {activeTab === 'knowledge' && (
                                <KnowledgeTab
                                    items={knowledgeItems}
                                    categories={CATEGORIES}
                                    onEdit={(item) => {
                                        setEditingKnowledge(item);
                                        setShowKnowledgeModal(true);
                                    }}
                                    onDelete={handleDeleteKnowledge}
                                />
                            )}
                            {activeTab === 'status' && (
                                <StatusTab
                                    status={aiStatus}
                                    knowledgeCount={knowledgeItems.length}
                                    trainingCount={0}
                                />
                            )}
                        </>
                    )}
                </div>

                {/* Modals */}
                {showKnowledgeModal && (
                    <KnowledgeModal
                        item={editingKnowledge}
                        categories={CATEGORIES}
                        onClose={() => setShowKnowledgeModal(false)}
                        onSave={handleSaveKnowledge}
                    />
                )}
            </div>
        </div>
    );
}
