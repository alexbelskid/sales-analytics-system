"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import {
    Plus,
} from "lucide-react";

import KnowledgeTab from "@/components/ai-assistant/KnowledgeTab";
import TrainingTab from "@/components/ai-assistant/TrainingTab";
import StatusTab from "@/components/ai-assistant/StatusTab";
import KnowledgeModal from "@/components/ai-assistant/KnowledgeModal";
import TrainingModal from "@/components/ai-assistant/TrainingModal";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

interface KnowledgeItem {
    id: string;
    category: string;
    title: string;
    content: string;
}

interface TrainingExample {
    id: string;
    question: string;
    answer: string;
    tone: string;
    confidence_score: number;
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

const TONES = [
    { id: 'professional', label: 'Профессиональный' },
    { id: 'friendly', label: 'Дружелюбный' },
    { id: 'formal', label: 'Официальный' },
    { id: 'brief', label: 'Краткий' },
    { id: 'detailed', label: 'Подробный' },
    { id: 'creative', label: 'Креативный' },
];

type TabType = 'knowledge' | 'training' | 'status';

export default function AIAssistantPage() {
    const { toast } = useToast();
    const [activeTab, setActiveTab] = useState<TabType>('knowledge');

    // Data state
    const [knowledgeItems, setKnowledgeItems] = useState<KnowledgeItem[]>([]);
    const [trainingExamples, setTrainingExamples] = useState<TrainingExample[]>([]);
    const [aiStatus, setAIStatus] = useState<AIStatus | null>(null);
    const [loading, setLoading] = useState(true);

    // Modal state
    const [showKnowledgeModal, setShowKnowledgeModal] = useState(false);
    const [editingKnowledge, setEditingKnowledge] = useState<KnowledgeItem | null>(null);
    const [showTrainingModal, setShowTrainingModal] = useState(false);
    const [editingTraining, setEditingTraining] = useState<TrainingExample | null>(null);
    const [isDraggingTraining, setIsDraggingTraining] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        loadData();
    }, [activeTab]);

    const loadData = async () => {
        setLoading(true);
        try {
            if (activeTab === 'knowledge') {
                const response = await fetch(`${API_BASE}/api/knowledge`);
                const data = await response.json();
                setKnowledgeItems(data);
            } else if (activeTab === 'training') {
                const response = await fetch(`${API_BASE}/api/training`);
                const data = await response.json();
                setTrainingExamples(data);
            } else if (activeTab === 'status') {
                const response = await fetch(`${API_BASE}/api/data/analytics/summary`);
                const data = await response.json();
                setAIStatus(data);
            }
        } catch (error) {
            toast({ title: "Ошибка", description: "Не удалось загрузить данные" });
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

    // Training Handlers
    const handleSaveTraining = async (data: { question: string; answer: string; tone: string; confidence_score: number }) => {
        try {
            const url = editingTraining
                ? `${API_BASE}/api/training/${editingTraining.id}`
                : `${API_BASE}/api/training`;
            const method = editingTraining ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });

            if (response.ok) {
                toast({ title: "Успешно", description: editingTraining ? "Обновлено" : "Добавлено" });
                loadData();
                setShowTrainingModal(false);
                setEditingTraining(null);
            }
        } catch (error) {
            toast({ title: "Ошибка", description: "Не удалось сохранить" });
        }
    };

    const handleDeleteTraining = async (id: string) => {
        if (!confirm("Удалить этот пример?")) return;
        try {
            const response = await fetch(`${API_BASE}/api/training/${id}`, { method: 'DELETE' });
            if (response.ok) {
                toast({ title: "Удалено" });
                loadData();
            }
        } catch (error) {
            toast({ title: "Ошибка", description: "Не удалось удалить" });
        }
    };

    const handleFileUpload = async (file: File) => {
        if (!file.name.endsWith('.csv')) {
            toast({ title: "Ошибка", description: "Поддерживается только CSV формат" });
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${API_BASE}/api/training/upload/csv`, {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const result = await response.json();
                toast({ title: "Успешно", description: `Загружено ${result.count} примеров` });
                loadData();
            } else {
                toast({ title: "Ошибка", description: "Не удалось загрузить файл" });
            }
        } catch (error) {
            toast({ title: "Ошибка", description: "Не удалось загрузить файл" });
        }
    };

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDraggingTraining(false);
        const file = e.dataTransfer.files[0];
        if (file) handleFileUpload(file);
    }, []);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDraggingTraining(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDraggingTraining(false);
    }, []);

    return (
        <div className="min-h-screen bg-[#202020] text-white">
            <div className="max-w-7xl mx-auto px-8 py-12">
                {/* Header Section */}
                <div className="flex flex-col gap-4 mb-8 sm:mb-12">
                    <div>
                        <h1 className="text-2xl sm:text-4xl lg:text-[48px] font-semibold tracking-tight leading-tight mb-3 sm:mb-4">AI Ассистент</h1>
                        <p className="text-[#808080] text-sm sm:text-lg max-w-2xl leading-relaxed">
                            Управляйте знаниями и обучением вашего искусственного интеллекта для точных и эффективных ответов клиентам.
                        </p>
                    </div>

                    {activeTab !== 'status' && (
                        <Button
                            onClick={() => {
                                if (activeTab === 'knowledge') {
                                    setEditingKnowledge(null);
                                    setShowKnowledgeModal(true);
                                } else {
                                    setEditingTraining(null);
                                    setShowTrainingModal(true);
                                }
                            }}
                            className="bg-rose-800 text-white hover:bg-rose-700 rounded-full px-6 sm:px-8 h-12 font-medium w-full sm:w-auto transition-all duration-300 hover:shadow-lg hover:shadow-rose-800/25 min-h-[44px]"
                        >
                            <Plus className="mr-2 h-5 w-5" />
                            {activeTab === 'knowledge' ? 'Добавить информацию' : 'Добавить пример'}
                        </Button>
                    )}
                </div>

                {/* Tabs Navigation */}
                <div className="flex gap-4 sm:gap-8 border-b border-[#262626] mb-6 sm:mb-10 overflow-x-auto scrollbar-hide -mx-4 px-4 sm:mx-0 sm:px-0">
                    {[
                        { id: 'status', label: 'Статус' },
                        { id: 'knowledge', label: 'База знаний' },
                        { id: 'training', label: 'Обучение' },
                    ].map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id as TabType)}
                            className={`pb-4 text-sm font-medium tracking-wide transition-colors relative whitespace-nowrap ${activeTab === tab.id ? 'text-white' : 'text-[#404040] hover:text-[#808080]'
                                }`}
                        >
                            {tab.label}
                            {activeTab === tab.id && (
                                <div className="absolute bottom-[-1px] left-0 right-0 h-[2px] bg-white rounded-full shadow-[0_0_8px_rgba(255,255,255,0.5)]" />
                            )}
                        </button>
                    ))}
                </div>

                {/* Loading State */}
                {loading ? (
                    <div className="flex flex-col items-center justify-center py-20 gap-4">
                        <div className="h-8 w-8 border-2 border-white/10 border-t-white rounded-full animate-spin" />
                        <p className="text-sm text-[#404040] animate-pulse">Загрузка данных...</p>
                    </div>
                ) : (
                    <div className="animate-in fade-in duration-500">
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
                        {activeTab === 'training' && (
                            <TrainingTab
                                items={trainingExamples}
                                isDragging={isDraggingTraining}
                                onEdit={(item) => {
                                    setEditingTraining(item);
                                    setShowTrainingModal(true);
                                }}
                                onDelete={handleDeleteTraining}
                                onDrop={handleDrop}
                                onDragOver={handleDragOver}
                                onDragLeave={handleDragLeave}
                                onUploadClick={() => fileInputRef.current?.click()}
                            />
                        )}
                        {activeTab === 'status' && (
                            <StatusTab
                                status={aiStatus}
                                knowledgeCount={knowledgeItems.length}
                                trainingCount={trainingExamples.length}
                            />
                        )}
                    </div>
                )}

                {/* Hidden File Input */}
                <input
                    ref={fileInputRef}
                    type="file"
                    accept=".csv"
                    className="hidden"
                    onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) handleFileUpload(file);
                    }}
                />

                {/* Modals */}
                {showKnowledgeModal && (
                    <KnowledgeModal
                        item={editingKnowledge}
                        categories={CATEGORIES}
                        onClose={() => setShowKnowledgeModal(false)}
                        onSave={handleSaveKnowledge}
                    />
                )}

                {showTrainingModal && (
                    <TrainingModal
                        item={editingTraining}
                        tones={TONES}
                        onClose={() => setShowTrainingModal(false)}
                        onSave={handleSaveTraining}
                    />
                )}
            </div>
        </div>
    );
}
