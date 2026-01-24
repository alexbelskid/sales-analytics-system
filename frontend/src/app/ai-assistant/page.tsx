"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import LiquidButton from "@/components/LiquidButton";
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

// Use empty string for client-side to leverage Next.js rewrites
const API_BASE = '';

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
        <div className="h-[calc(100vh-160px)] flex flex-col overflow-hidden text-white">
            <div className="flex-none p-6 pb-0"> {/* Header fixed at top */}
                {/* Header Section */}
                {/* Header Section - Only show continuously if there are actions (like Add button) */}
                {(activeTab === 'knowledge') && (
                    <div className="flex flex-col gap-4 mb-8">
                        <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
                            <div /> {/* Spacer or Title placeholder if needed later, but empty for now to push button right if justify-between */}

                            <LiquidButton
                                onClick={() => {
                                    setEditingKnowledge(null);
                                    setShowKnowledgeModal(true);
                                }}
                                icon={Plus}
                                variant="primary"
                            >
                                Добавить запись
                            </LiquidButton>
                        </div>
                    </div>
                )}

                {/* Tabs Navigation */}
                <div className="flex flex-wrap gap-2 mb-6">
                    {[
                        { id: 'chat', label: 'Чат', icon: MessageSquare },
                        { id: 'status', label: 'Дашборд', icon: Activity },
                        { id: 'knowledge', label: 'База знаний', icon: Book },
                    ].map((tab) => (
                        <LiquidButton
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id as TabType)}
                            variant={activeTab === tab.id ? 'primary' : 'secondary'}
                            icon={tab.icon}
                            className="min-w-[120px]"
                        >
                            {tab.label}
                        </LiquidButton>
                    ))}
                </div>
            </div>

            {/* Content Area - Scrollable */}
            <div className="flex-1 min-h-0 overflow-hidden relative">
                {activeTab === 'chat' ? (
                    /* Chat handles its own scrolling internally */
                    <div className="h-full">
                        <AiAssistantPanel />
                    </div>
                ) : (
                    /* Other tabs need a scroll container */
                    <div className="h-full overflow-y-auto p-6 pt-0 animate-in fade-in duration-500">
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
    );
}
