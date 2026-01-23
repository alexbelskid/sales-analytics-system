"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useDebounce } from "use-debounce";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { Loader2, Copy, Sparkles, GraduationCap, MessageSquare, Plus } from "lucide-react";
import { aiApi } from "@/lib/api";
import TrainingTab from "@/components/ai-assistant/TrainingTab";
import TrainingModal from "@/components/ai-assistant/TrainingModal";
import LiquidButton from "@/components/LiquidButton";
import GlassInput from "@/components/GlassInput";
import GlassSelect from "@/components/GlassSelect";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://athletic-alignment-production-db41.up.railway.app';

interface TrainingExample {
    id: string;
    question: string;
    answer: string;
    tone: string;
    confidence_score: number;
}

const TONES = [
    { id: 'professional', label: 'Профессиональный' },
    { id: 'friendly', label: 'Дружелюбный' },
    { id: 'formal', label: 'Официальный' },
    { id: 'brief', label: 'Краткий' },
    { id: 'detailed', label: 'Подробный' },
    { id: 'creative', label: 'Креативный' },
];

type TabType = 'auto-replies' | 'training';

export default function EmailsPage() {
    const { toast } = useToast();
    const [activeTab, setActiveTab] = useState<TabType>('auto-replies');

    // Auto Replies State
    const [sender, setSender] = useState("");
    const [subject, setSubject] = useState("");
    const [body, setBody] = useState("");
    const [debouncedBody] = useDebounce(body, 300);
    const [tone, setTone] = useState("professional");
    const [generatedResponse, setGeneratedResponse] = useState("");
    const [confidence, setConfidence] = useState(0);
    const [loading, setLoading] = useState(false);

    // Training State
    const [trainingExamples, setTrainingExamples] = useState<TrainingExample[]>([]);
    const [showTrainingModal, setShowTrainingModal] = useState(false);
    const [editingTraining, setEditingTraining] = useState<TrainingExample | null>(null);
    const [isDraggingTraining, setIsDraggingTraining] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [trainingLoading, setTrainingLoading] = useState(false);

    useEffect(() => {
        if (activeTab === 'training') {
            loadTrainingData();
        }
    }, [activeTab]);

    const loadTrainingData = async () => {
        setTrainingLoading(true);
        try {
            const response = await fetch(`${API_BASE}/api/training`);
            const data = await response.json();
            setTrainingExamples(data);
        } catch (error) {
            console.error(error);
            toast({ title: "Ошибка", description: "Не удалось загрузить примеры" });
        } finally {
            setTrainingLoading(false);
        }
    };

    // Auto Replies Handlers
    const handleGenerate = async () => {
        if (!body) {
            toast({ title: "Ошибка", description: "Введите текст письма" });
            return;
        }

        setLoading(true);
        try {
            const res = await aiApi.generateResponse(sender, subject, body, tone);

            if (res.success) {
                setGeneratedResponse(res.response);
                setConfidence(res.confidence);
                toast({
                    title: "Готово",
                    description: `Ответ сгенерирован (${(res.confidence * 100).toFixed(0)}% уверенности)`
                });
            } else {
                toast({ title: "Ошибка", description: "Не удалось сгенерировать ответ" });
            }
        } catch (error: any) {
            toast({
                title: "Ошибка",
                description: error.message || "Ошибка соединения"
            });
        } finally {
            setLoading(false);
        }
    };

    const handleCopy = () => {
        navigator.clipboard.writeText(generatedResponse);
        toast({ title: "Скопировано" });
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
                loadTrainingData();
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
                loadTrainingData();
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
                loadTrainingData();
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
        <div className="min-h-screen text-white">
            <div className="max-w-4xl mx-auto space-y-6 sm:space-y-8 p-6">

                {/* Header */}
                <div className="flex flex-col gap-4">
                    <div className="flex justify-between items-center">
                        <h1 className="text-2xl sm:text-[32px] font-semibold mb-2">Автоответы</h1>

                        {activeTab === 'training' && (
                            <LiquidButton
                                onClick={() => {
                                    setEditingTraining(null);
                                    setShowTrainingModal(true);
                                }}
                                icon={Plus}
                            >
                                Добавить пример
                            </LiquidButton>
                        )}
                    </div>
                    {/* Tabs Navigation */}
                    <div className="flex gap-2 sm:gap-6 border-b border-[#262626] overflow-x-auto scrollbar-hide -mx-4 px-4 sm:mx-0 sm:px-0">
                        <button
                            onClick={() => setActiveTab('auto-replies')}
                            className={`flex items-center gap-2 pb-3 px-1 text-sm font-medium tracking-wide transition-colors relative whitespace-nowrap ${activeTab === 'auto-replies' ? 'text-white' : 'text-[#505050] hover:text-[#909090]'}`}
                        >
                            <MessageSquare className={`w-4 h-4 ${activeTab === 'auto-replies' ? 'text-rose-500' : ''}`} />
                            Генерация
                            {activeTab === 'auto-replies' && (
                                <div className="absolute bottom-[-1px] left-0 right-0 h-[2px] bg-rose-500 rounded-full shadow-[0_0_10px_rgba(225,29,72,0.5)]" />
                            )}
                        </button>
                        <button
                            onClick={() => setActiveTab('training')}
                            className={`flex items-center gap-2 pb-3 px-1 text-sm font-medium tracking-wide transition-colors relative whitespace-nowrap ${activeTab === 'training' ? 'text-white' : 'text-[#505050] hover:text-[#909090]'}`}
                        >
                            <GraduationCap className={`w-4 h-4 ${activeTab === 'training' ? 'text-rose-500' : ''}`} />
                            Обучение
                            {activeTab === 'training' && (
                                <div className="absolute bottom-[-1px] left-0 right-0 h-[2px] bg-rose-500 rounded-full shadow-[0_0_10px_rgba(225,29,72,0.5)]" />
                            )}
                        </button>
                    </div>
                </div>


                {/* Content */}
                <div className="animate-in fade-in duration-500">
                    {activeTab === 'auto-replies' && (
                        <div className="space-y-6">
                            {/* Input Form */}
                            <div className="space-y-6">
                                {/* Two columns */}
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm text-[#808080] mb-2">От кого</label>
                                        <GlassInput
                                            placeholder="client@example.com"
                                            value={sender}
                                            onChange={(e) => setSender(e.target.value)}
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm text-[#808080] mb-2">Тема</label>
                                        <GlassInput
                                            placeholder="Запрос коммерческого предложения"
                                            value={subject}
                                            onChange={(e) => setSubject(e.target.value)}
                                        />
                                    </div>
                                </div>

                                {/* Body */}
                                <div>
                                    <label className="block text-sm text-[#808080] mb-2">Текст письма</label>
                                    <Textarea
                                        placeholder="Скопируйте сюда текст полученного письма..."
                                        className="bg-[#262626] border-[#333333] text-white placeholder:text-[#404040] rounded-2xl min-h-[200px] p-5 resize-none focus-visible:ring-2 focus-visible:ring-rose-800/25 focus-visible:ring-offset-0 focus-visible:border-rose-800 transition-all duration-300"
                                        value={body}
                                        onChange={(e) => setBody(e.target.value)}
                                    />
                                </div>

                                {/* Tone Dropdown */}
                                <div>
                                    <label className="block text-sm text-[#808080] mb-2">Тон ответа</label>
                                    <GlassSelect
                                        value={tone}
                                        onChange={(e) => setTone(e.target.value)}
                                    >
                                        {TONES.map((t) => (
                                            <option key={t.id} value={t.id}>
                                                {t.label}
                                            </option>
                                        ))}
                                    </GlassSelect>
                                </div>

                                {/* Generate Button */}
                                <LiquidButton
                                    onClick={handleGenerate}
                                    disabled={loading || !body}
                                    className="w-full"
                                    icon={loading ? Loader2 : Sparkles}
                                >
                                    {loading ? 'AI думает...' : 'Сгенерировать'}
                                </LiquidButton>
                            </div>

                            {/* Divider */}
                            <div className="h-[1px] bg-[#262626]" />

                            {/* Response */}
                            <div className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <label className="block text-sm text-[#808080]">Ответ</label>
                                    {generatedResponse && confidence > 0 && (
                                        <span className="text-xs text-[#808080]">
                                            Уверенность: {(confidence * 100).toFixed(0)}%
                                        </span>
                                    )}
                                </div>
                                {generatedResponse ? (
                                    <div className="space-y-4">
                                        <Textarea
                                            className="bg-[#0F0F0F] border-[#333333] text-white rounded-2xl min-h-[200px] p-5 resize-none focus-visible:ring-2 focus-visible:ring-rose-800/25 focus-visible:ring-offset-0 focus-visible:border-rose-800 transition-all duration-300"
                                            value={generatedResponse}
                                            onChange={(e) => setGeneratedResponse(e.target.value)}
                                        />
                                        <div className="flex gap-3">
                                            <LiquidButton
                                                onClick={() => {
                                                    setGeneratedResponse("");
                                                    setConfidence(0);
                                                }}
                                                variant="secondary"
                                            >
                                                Очистить
                                            </LiquidButton>
                                            <LiquidButton
                                                onClick={handleCopy}
                                                icon={Copy}
                                            >
                                                Копировать
                                            </LiquidButton>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="bg-[#0F0F0F] border border-[#333333] rounded-[4px] min-h-[200px] flex items-center justify-center">
                                        <p className="text-[#404040] text-sm">
                                            Ответ появится здесь после генерации
                                        </p>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {activeTab === 'training' && (
                        <div>
                            {trainingLoading ? (
                                <div className="flex flex-col items-center justify-center py-20 gap-4">
                                    <div className="h-8 w-8 border-2 border-rose-500/20 border-t-rose-500 rounded-full animate-spin" />
                                    <p className="text-sm text-[#404040]">Загрузка данных...</p>
                                </div>
                            ) : (
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
                        </div>
                    )}
                </div>

                {/* Hidden File Input (for Training tab) */}
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
