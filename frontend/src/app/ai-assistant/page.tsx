"use client";

import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import {
    Plus,
    Edit2,
    Trash2,
    Upload,
    Sparkles,
    CheckCircle,
    XCircle,
    BookOpen,
    BrainCircuit,
    Activity
} from "lucide-react";

interface KnowledgeItem {
    id: string;
    category: string;
    title: string;
    content: string;
    created_at?: string;
}

interface TrainingExample {
    id: string;
    question: string;
    answer: string;
    tone: string;
    confidence_score: number;
    created_at?: string;
}

interface AIStatus {
    available: boolean;
    model: string | null;
    api_key_configured: boolean;
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

    // Knowledge state
    const [knowledgeItems, setKnowledgeItems] = useState<KnowledgeItem[]>([]);
    const [showKnowledgeModal, setShowKnowledgeModal] = useState(false);
    const [editingKnowledge, setEditingKnowledge] = useState<KnowledgeItem | null>(null);
    const [knowledgeCategory, setKnowledgeCategory] = useState("products");
    const [knowledgeTitle, setKnowledgeTitle] = useState("");
    const [knowledgeContent, setKnowledgeContent] = useState("");

    // Training state
    const [trainingExamples, setTrainingExamples] = useState<TrainingExample[]>([]);
    const [showTrainingModal, setShowTrainingModal] = useState(false);
    const [editingTraining, setEditingTraining] = useState<TrainingExample | null>(null);
    const [trainingQuestion, setTrainingQuestion] = useState("");
    const [trainingAnswer, setTrainingAnswer] = useState("");
    const [trainingTone, setTrainingTone] = useState("professional");
    const [trainingConfidence, setTrainingConfidence] = useState(1.0);
    const [isDragging, setIsDragging] = useState(false);

    // Status state
    const [aiStatus, setAIStatus] = useState<AIStatus | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, [activeTab]);

    const loadData = async () => {
        setLoading(true);
        try {
            if (activeTab === 'knowledge') {
                const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/knowledge`);
                const data = await response.json();
                setKnowledgeItems(data);
            } else if (activeTab === 'training') {
                const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/training`);
                const data = await response.json();
                setTrainingExamples(data);
            } else if (activeTab === 'status') {
                // Load all data for status tab
                const [statusRes, knowledgeRes, trainingRes] = await Promise.all([
                    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/ai/status`),
                    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/knowledge`),
                    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/training`)
                ]);
                const [statusData, knowledgeData, trainingData] = await Promise.all([
                    statusRes.json(),
                    knowledgeRes.json(),
                    trainingRes.json()
                ]);
                setAIStatus(statusData);
                setKnowledgeItems(knowledgeData);
                setTrainingExamples(trainingData);
            }
        } catch (error) {
            toast({ title: "Ошибка", description: "Не удалось загрузить данные" });
        } finally {
            setLoading(false);
        }
    };

    // Knowledge handlers
    const handleSaveKnowledge = async () => {
        if (!knowledgeTitle || !knowledgeContent) {
            toast({ title: "Ошибка", description: "Заполните все поля" });
            return;
        }

        try {
            const url = editingKnowledge
                ? `${process.env.NEXT_PUBLIC_API_URL}/api/knowledge/${editingKnowledge.id}`
                : `${process.env.NEXT_PUBLIC_API_URL}/api/knowledge`;
            const method = editingKnowledge ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ category: knowledgeCategory, title: knowledgeTitle, content: knowledgeContent }),
            });

            if (response.ok) {
                toast({ title: "Успешно", description: editingKnowledge ? "Обновлено" : "Создано" });
                loadData();
                closeKnowledgeModal();
            }
        } catch (error) {
            toast({ title: "Ошибка", description: "Не удалось сохранить" });
        }
    };

    const handleDeleteKnowledge = async (id: string) => {
        if (!confirm("Удалить эту запись?")) return;

        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/knowledge/${id}`, {
                method: 'DELETE',
            });

            if (response.ok) {
                toast({ title: "Удалено" });
                loadData();
            }
        } catch (error) {
            toast({ title: "Ошибка", description: "Не удалось удалить" });
        }
    };

    const openKnowledgeModal = (item?: KnowledgeItem) => {
        if (item) {
            setEditingKnowledge(item);
            setKnowledgeCategory(item.category);
            setKnowledgeTitle(item.title);
            setKnowledgeContent(item.content);
        } else {
            setEditingKnowledge(null);
            setKnowledgeCategory("products");
            setKnowledgeTitle("");
            setKnowledgeContent("");
        }
        setShowKnowledgeModal(true);
    };

    const closeKnowledgeModal = () => {
        setShowKnowledgeModal(false);
        setEditingKnowledge(null);
        setKnowledgeCategory("products");
        setKnowledgeTitle("");
        setKnowledgeContent("");
    };

    // Training handlers
    const handleSaveTraining = async () => {
        if (!trainingQuestion || !trainingAnswer) {
            toast({ title: "Ошибка", description: "Заполните вопрос и ответ" });
            return;
        }

        try {
            const url = editingTraining
                ? `${process.env.NEXT_PUBLIC_API_URL}/api/training/${editingTraining.id}`
                : `${process.env.NEXT_PUBLIC_API_URL}/api/training`;
            const method = editingTraining ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: trainingQuestion,
                    answer: trainingAnswer,
                    tone: trainingTone,
                    confidence_score: trainingConfidence
                }),
            });

            if (response.ok) {
                toast({ title: "Успешно", description: editingTraining ? "Обновлено" : "Добавлено" });
                loadData();
                closeTrainingModal();
            }
        } catch (error) {
            toast({ title: "Ошибка", description: "Не удалось сохранить" });
        }
    };

    const handleDeleteTraining = async (id: string) => {
        if (!confirm("Удалить этот пример?")) return;

        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/training/${id}`, {
                method: 'DELETE',
            });

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
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/training/upload/csv`, {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const result = await response.json();
                toast({ title: "Успешно", description: `Загружено ${result.count} примеров` });
                loadData();
            } else {
                const error = await response.json();
                toast({ title: "Ошибка", description: error.detail || "Не удалось загрузить файл" });
            }
        } catch (error) {
            toast({ title: "Ошибка", description: "Не удалось загрузить файл" });
        }
    };

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);

        const file = e.dataTransfer.files[0];
        if (file) {
            handleFileUpload(file);
        }
    }, []);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const openTrainingModal = (example?: TrainingExample) => {
        if (example) {
            setEditingTraining(example);
            setTrainingQuestion(example.question);
            setTrainingAnswer(example.answer);
            setTrainingTone(example.tone);
            setTrainingConfidence(example.confidence_score);
        } else {
            setEditingTraining(null);
            setTrainingQuestion("");
            setTrainingAnswer("");
            setTrainingTone("professional");
            setTrainingConfidence(1.0);
        }
        setShowTrainingModal(true);
    };

    const closeTrainingModal = () => {
        setShowTrainingModal(false);
        setEditingTraining(null);
        setTrainingQuestion("");
        setTrainingAnswer("");
        setTrainingTone("professional");
        setTrainingConfidence(1.0);
    };

    const groupedKnowledge = CATEGORIES.map(cat => ({
        ...cat,
        items: knowledgeItems.filter(item => item.category === cat.id)
    }));

    return (
        <div className="min-h-screen bg-[#0A0A0A] text-white p-8">
            <div className="max-w-5xl mx-auto space-y-8">

                {/* Header */}
                <div>
                    <h1 className="text-[40px] font-semibold tracking-tight mb-2">AI Ассистент</h1>
                    <p className="text-sm text-[#808080]">Управление базой знаний, обучающими примерами и статусом нейросети</p>
                </div>

                <div className="h-[1px] bg-gradient-to-r from-[#2A2A2A] to-transparent" />

                {/* Tabs */}
                <div className="flex gap-4 border-b border-[#2A2A2A]">
                    <button
                        onClick={() => setActiveTab('knowledge')}
                        className={`pb-4 px-2 text-sm font-medium transition-colors relative ${activeTab === 'knowledge' ? 'text-white' : 'text-[#808080] hover:text-white'
                            }`}
                    >
                        <div className="flex items-center gap-2">
                            <BookOpen className="h-4 w-4" />
                            <span>База знаний</span>
                        </div>
                        {activeTab === 'knowledge' && (
                            <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-white" />
                        )}
                    </button>
                    <button
                        onClick={() => setActiveTab('training')}
                        className={`pb-4 px-2 text-sm font-medium transition-colors relative ${activeTab === 'training' ? 'text-white' : 'text-[#808080] hover:text-white'
                            }`}
                    >
                        <div className="flex items-center gap-2">
                            <BrainCircuit className="h-4 w-4" />
                            <span>Обучение</span>
                        </div>
                        {activeTab === 'training' && (
                            <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-white" />
                        )}
                    </button>
                    <button
                        onClick={() => setActiveTab('status')}
                        className={`pb-4 px-2 text-sm font-medium transition-colors relative ${activeTab === 'status' ? 'text-white' : 'text-[#808080] hover:text-white'
                            }`}
                    >
                        <div className="flex items-center gap-2">
                            <Activity className="h-4 w-4" />
                            <span>Статус</span>
                        </div>
                        {activeTab === 'status' && (
                            <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-white" />
                        )}
                    </button>
                </div>

                {/* Tab Content */}
                {activeTab === 'knowledge' && (
                    <div className="space-y-6">
                        <div className="flex items-center justify-between">
                            <p className="text-sm text-[#808080]">Информация о продуктах, ценах и условиях компании</p>
                            <Button
                                onClick={() => openKnowledgeModal()}
                                className="bg-white text-black hover:bg-[#E0E0E0] rounded h-10"
                            >
                                <Plus className="h-4 w-4 mr-2" />
                                Добавить
                            </Button>
                        </div>

                        <div className="space-y-6">
                            {groupedKnowledge.map(group => (
                                <div key={group.id}>
                                    <h2 className="text-lg font-semibold mb-3">{group.label}</h2>
                                    {group.items.length === 0 ? (
                                        <div className="bg-[#0F0F0F] border border-[#2A2A2A] rounded p-4 text-center text-[#808080] text-sm">
                                            Нет записей
                                        </div>
                                    ) : (
                                        <div className="space-y-3">
                                            {group.items.map(item => (
                                                <div
                                                    key={item.id}
                                                    className="bg-[#1A1A1A] border border-[#2A2A2A] rounded p-4 hover:border-white/20 transition-colors"
                                                >
                                                    <div className="flex items-start justify-between">
                                                        <div className="flex-1">
                                                            <h3 className="font-semibold mb-2">{item.title}</h3>
                                                            <p className="text-sm text-[#808080] whitespace-pre-wrap">{item.content}</p>
                                                        </div>
                                                        <div className="flex gap-2 ml-4">
                                                            <button
                                                                onClick={() => openKnowledgeModal(item)}
                                                                className="p-2 hover:bg-[#2A2A2A] rounded transition-colors"
                                                            >
                                                                <Edit2 className="h-4 w-4" />
                                                            </button>
                                                            <button
                                                                onClick={() => handleDeleteKnowledge(item.id)}
                                                                className="p-2 hover:bg-[#2A2A2A] rounded transition-colors text-[#808080] hover:text-white"
                                                            >
                                                                <Trash2 className="h-4 w-4" />
                                                            </button>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {activeTab === 'training' && (
                    <div className="space-y-6">
                        {/* CSV Upload */}
                        <div
                            onDrop={handleDrop}
                            onDragOver={handleDragOver}
                            onDragLeave={handleDragLeave}
                            className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${isDragging ? 'border-white bg-[#1A1A1A]' : 'border-[#2A2A2A] hover:border-[#404040]'
                                }`}
                        >
                            <Upload className="h-12 w-12 mx-auto mb-4 text-[#808080]" />
                            <p className="text-lg mb-2">Перетащите CSV файл сюда</p>
                            <p className="text-sm text-[#808080] mb-4">или</p>
                            <label className="cursor-pointer">
                                <input
                                    type="file"
                                    accept=".csv"
                                    className="hidden"
                                    onChange={(e) => {
                                        const file = e.target.files?.[0];
                                        if (file) handleFileUpload(file);
                                    }}
                                />
                                <span className="inline-block bg-white text-black px-6 py-2 rounded hover:bg-[#E0E0E0] transition-colors">
                                    Выберите файл
                                </span>
                            </label>
                            <p className="text-xs text-[#808080] mt-4">Формат: question,answer,tone</p>
                        </div>

                        {/* Manual Add */}
                        <div className="flex items-center justify-between">
                            <p className="text-sm text-[#808080]">Или добавьте пример вручную:</p>
                            <Button
                                onClick={() => openTrainingModal()}
                                className="bg-white text-black hover:bg-[#E0E0E0] rounded h-10"
                            >
                                <Plus className="h-4 w-4 mr-2" />
                                Добавить пример
                            </Button>
                        </div>

                        {/* Examples List */}
                        <div className="space-y-3">
                            {trainingExamples.length === 0 ? (
                                <div className="bg-[#0F0F0F] border border-[#2A2A2A] rounded p-8 text-center text-[#808080]">
                                    Нет примеров для обучения
                                </div>
                            ) : (
                                trainingExamples.map((example, index) => (
                                    <div
                                        key={example.id}
                                        className="bg-[#1A1A1A] border border-[#2A2A2A] rounded p-4 hover:border-white/20 transition-colors"
                                    >
                                        <div className="flex items-start justify-between">
                                            <div className="flex-1">
                                                <div className="flex items-center gap-3 mb-2">
                                                    <span className="text-xs text-[#808080]">Пример #{index + 1}</span>
                                                    <span className="text-xs px-2 py-1 bg-[#0F0F0F] border border-[#2A2A2A] rounded">
                                                        {TONES.find(t => t.id === example.tone)?.label}
                                                    </span>
                                                    <span className="text-xs text-[#808080]">
                                                        Качество: {(example.confidence_score * 100).toFixed(0)}%
                                                    </span>
                                                </div>
                                                <div className="space-y-2">
                                                    <div>
                                                        <p className="text-xs text-[#808080] mb-1">Вопрос:</p>
                                                        <p className="text-sm">{example.question}</p>
                                                    </div>
                                                    <div>
                                                        <p className="text-xs text-[#808080] mb-1">Ответ:</p>
                                                        <p className="text-sm text-[#808080]">{example.answer}</p>
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="flex gap-2 ml-4">
                                                <button
                                                    onClick={() => openTrainingModal(example)}
                                                    className="p-2 hover:bg-[#2A2A2A] rounded transition-colors"
                                                >
                                                    <Edit2 className="h-4 w-4" />
                                                </button>
                                                <button
                                                    onClick={() => handleDeleteTraining(example.id)}
                                                    className="p-2 hover:bg-[#2A2A2A] rounded transition-colors text-[#808080] hover:text-white"
                                                >
                                                    <Trash2 className="h-4 w-4" />
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>

                        {/* Stats */}
                        <div className="bg-[#0F0F0F] border border-[#2A2A2A] rounded p-4">
                            <p className="text-sm text-[#808080]">
                                Обучено примеров: <span className="text-white font-semibold">{trainingExamples.length}</span>
                            </p>
                        </div>
                    </div>
                )}

                {activeTab === 'status' && aiStatus && (
                    <div className="space-y-6">
                        {/* AI Status Card */}
                        <div className="bg-[#1A1A1A] border border-[#2A2A2A] rounded p-6">
                            <div className="flex items-center gap-3 mb-6">
                                {aiStatus.available ? (
                                    <>
                                        <CheckCircle className="h-6 w-6 text-white" />
                                        <div>
                                            <p className="text-lg font-semibold">AI Подключён</p>
                                            <p className="text-xs text-[#808080]">Готов к работе</p>
                                        </div>
                                    </>
                                ) : (
                                    <>
                                        <XCircle className="h-6 w-6 text-[#808080]" />
                                        <div>
                                            <p className="text-lg font-semibold text-[#808080]">AI Не настроен</p>
                                            <p className="text-xs text-[#808080]">Требуется конфигурация</p>
                                        </div>
                                    </>
                                )}
                            </div>

                            <div className="space-y-3 text-sm">
                                <div className="flex items-center justify-between">
                                    <span className="text-[#808080]">Модель:</span>
                                    <span className="font-mono">{aiStatus.model || 'Не настроено'}</span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-[#808080]">API ключ:</span>
                                    <span className={aiStatus.api_key_configured ? 'text-white' : 'text-[#808080]'}>
                                        {aiStatus.api_key_configured ? 'Настроен' : 'Не настроен'}
                                    </span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-[#808080]">База знаний:</span>
                                    <span>{knowledgeItems.length} записей</span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-[#808080]">Обучено:</span>
                                    <span>{trainingExamples.length} примеров</span>
                                </div>
                            </div>
                        </div>

                        {/* Info Card */}
                        {!aiStatus.available && (
                            <div className="bg-[#0F0F0F] border border-[#2A2A2A] rounded p-6">
                                <h3 className="text-sm font-semibold mb-3">Настройка AI Ассистента</h3>
                                <p className="text-xs text-[#808080] mb-4">
                                    Для активации AI требуется добавить Google Gemini API ключ в переменные окружения Railway.
                                </p>
                                <div className="text-xs text-[#808080] space-y-1">
                                    <p>1. Получите ключ на <a href="https://ai.google.dev" target="_blank" className="text-white hover:underline">ai.google.dev</a></p>
                                    <p>2. Добавьте <code className="bg-[#1A1A1A] px-2 py-1 rounded">GOOGLE_GEMINI_API_KEY</code> в Railway</p>
                                    <p>3. Перезапустите backend сервис</p>
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Knowledge Modal */}
                {showKnowledgeModal && (
                    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50" onClick={closeKnowledgeModal}>
                        <div className="bg-[#0A0A0A] border border-[#2A2A2A] rounded-lg p-6 w-full max-w-2xl" onClick={(e) => e.stopPropagation()}>
                            <h2 className="text-xl font-semibold mb-6">
                                {editingKnowledge ? 'Редактировать' : 'Добавить информацию'}
                            </h2>

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm text-[#808080] mb-2">Категория</label>
                                    <select
                                        value={knowledgeCategory}
                                        onChange={(e) => setKnowledgeCategory(e.target.value)}
                                        className="w-full bg-[#1A1A1A] border border-[#2A2A2A] text-white rounded h-12 px-4 focus:outline-none focus:border-white transition-colors"
                                    >
                                        {CATEGORIES.map(cat => (
                                            <option key={cat.id} value={cat.id}>{cat.label}</option>
                                        ))}
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm text-[#808080] mb-2">Название</label>
                                    <Input
                                        value={knowledgeTitle}
                                        onChange={(e) => setKnowledgeTitle(e.target.value)}
                                        placeholder="Например: Шоколад молочный"
                                        className="bg-[#1A1A1A] border-[#2A2A2A] text-white placeholder:text-[#404040] rounded h-12 px-4 focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:border-white transition-colors"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm text-[#808080] mb-2">Содержание</label>
                                    <Textarea
                                        value={knowledgeContent}
                                        onChange={(e) => setKnowledgeContent(e.target.value)}
                                        placeholder="Цена: 5.50 BYN/кг. Описание..."
                                        className="bg-[#1A1A1A] border-[#2A2A2A] text-white placeholder:text-[#404040] rounded min-h-[150px] p-4 resize-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:border-white transition-colors"
                                    />
                                </div>

                                <div className="flex gap-3 pt-4">
                                    <Button
                                        onClick={closeKnowledgeModal}
                                        variant="outline"
                                        className="flex-1 bg-transparent border-[#2A2A2A] text-white hover:bg-[#1A1A1A] hover:text-white rounded h-10"
                                    >
                                        Отмена
                                    </Button>
                                    <Button
                                        onClick={handleSaveKnowledge}
                                        className="flex-1 bg-white text-black hover:bg-[#E0E0E0] rounded h-10"
                                    >
                                        Сохранить
                                    </Button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Training Modal */}
                {showTrainingModal && (
                    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50" onClick={closeTrainingModal}>
                        <div className="bg-[#0A0A0A] border border-[#2A2A2A] rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
                            <h2 className="text-xl font-semibold mb-6">
                                {editingTraining ? 'Редактировать пример' : 'Добавить пример'}
                            </h2>

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm text-[#808080] mb-2">Вопрос</label>
                                    <Textarea
                                        value={trainingQuestion}
                                        onChange={(e) => setTrainingQuestion(e.target.value)}
                                        placeholder="Какая цена на шоколад?"
                                        className="bg-[#1A1A1A] border-[#2A2A2A] text-white placeholder:text-[#404040] rounded min-h-[100px] p-4 resize-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:border-white transition-colors"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm text-[#808080] mb-2">Ответ</label>
                                    <Textarea
                                        value={trainingAnswer}
                                        onChange={(e) => setTrainingAnswer(e.target.value)}
                                        placeholder="Здравствуйте! Цена на шоколад..."
                                        className="bg-[#1A1A1A] border-[#2A2A2A] text-white placeholder:text-[#404040] rounded min-h-[150px] p-4 resize-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:border-white transition-colors"
                                    />
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm text-[#808080] mb-2">Тон</label>
                                        <select
                                            value={trainingTone}
                                            onChange={(e) => setTrainingTone(e.target.value)}
                                            className="w-full bg-[#1A1A1A] border border-[#2A2A2A] text-white rounded h-12 px-4 focus:outline-none focus:border-white transition-colors"
                                        >
                                            {TONES.map(t => (
                                                <option key={t.id} value={t.id}>{t.label}</option>
                                            ))}
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-sm text-[#808080] mb-2">Качество (0-1)</label>
                                        <input
                                            type="number"
                                            min="0"
                                            max="1"
                                            step="0.1"
                                            value={trainingConfidence}
                                            onChange={(e) => setTrainingConfidence(parseFloat(e.target.value))}
                                            className="w-full bg-[#1A1A1A] border border-[#2A2A2A] text-white rounded h-12 px-4 focus:outline-none focus:border-white transition-colors"
                                        />
                                    </div>
                                </div>

                                <div className="flex gap-3 pt-4">
                                    <Button
                                        onClick={closeTrainingModal}
                                        variant="outline"
                                        className="flex-1 bg-transparent border-[#2A2A2A] text-white hover:bg-[#1A1A1A] hover:text-white rounded h-10"
                                    >
                                        Отмена
                                    </Button>
                                    <Button
                                        onClick={handleSaveTraining}
                                        className="flex-1 bg-white text-black hover:bg-[#E0E0E0] rounded h-10"
                                    >
                                        Сохранить
                                    </Button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

            </div>
        </div>
    );
}
