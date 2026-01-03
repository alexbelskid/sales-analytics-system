"use client";

import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { Plus, Edit2, Trash2, Upload, FileText } from "lucide-react";

interface TrainingExample {
    id: string;
    question: string;
    answer: string;
    tone: string;
    confidence_score: number;
    created_at?: string;
}

const TONES = [
    { id: 'professional', label: 'Профессиональный' },
    { id: 'friendly', label: 'Дружелюбный' },
    { id: 'formal', label: 'Официальный' },
    { id: 'brief', label: 'Краткий' },
    { id: 'detailed', label: 'Подробный' },
    { id: 'creative', label: 'Креативный' },
];

export default function TrainingPage() {
    const { toast } = useToast();
    const [examples, setExamples] = useState<TrainingExample[]>([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [editingExample, setEditingExample] = useState<TrainingExample | null>(null);
    const [isDragging, setIsDragging] = useState(false);

    // Form state
    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState("");
    const [tone, setTone] = useState("professional");
    const [confidenceScore, setConfidenceScore] = useState(1.0);

    useEffect(() => {
        loadExamples();
    }, []);

    const loadExamples = async () => {
        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/training`);
            const data = await response.json();
            setExamples(data);
        } catch (error) {
            toast({ title: "Ошибка", description: "Не удалось загрузить примеры" });
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        if (!question || !answer) {
            toast({ title: "Ошибка", description: "Заполните вопрос и ответ" });
            return;
        }

        try {
            const url = editingExample
                ? `${process.env.NEXT_PUBLIC_API_URL}/api/training/${editingExample.id}`
                : `${process.env.NEXT_PUBLIC_API_URL}/api/training`;

            const method = editingExample ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question, answer, tone, confidence_score: confidenceScore }),
            });

            if (response.ok) {
                toast({ title: "Успешно", description: editingExample ? "Обновлено" : "Добавлено" });
                loadExamples();
                closeModal();
            }
        } catch (error) {
            toast({ title: "Ошибка", description: "Не удалось сохранить" });
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm("Удалить этот пример?")) return;

        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/training/${id}`, {
                method: 'DELETE',
            });

            if (response.ok) {
                toast({ title: "Удалено" });
                loadExamples();
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
                loadExamples();
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

    const openModal = (example?: TrainingExample) => {
        if (example) {
            setEditingExample(example);
            setQuestion(example.question);
            setAnswer(example.answer);
            setTone(example.tone);
            setConfidenceScore(example.confidence_score);
        } else {
            setEditingExample(null);
            setQuestion("");
            setAnswer("");
            setTone("professional");
            setConfidenceScore(1.0);
        }
        setShowModal(true);
    };

    const closeModal = () => {
        setShowModal(false);
        setEditingExample(null);
        setQuestion("");
        setAnswer("");
        setTone("professional");
        setConfidenceScore(1.0);
    };

    return (
        <div className="min-h-screen bg-[#0A0A0A] text-white p-8">
            <div className="max-w-5xl mx-auto space-y-8">

                {/* Header */}
                <div>
                    <h1 className="text-[32px] font-semibold">Обучение AI</h1>
                    <p className="text-sm text-[#808080] mt-1">Примеры для обучения ассистента</p>
                </div>

                <div className="h-[1px] bg-[#1A1A1A]" />

                {/* File Upload Area */}
                <div
                    onDrop={handleDrop}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${isDragging
                            ? 'border-white bg-[#1A1A1A]'
                            : 'border-[#2A2A2A] hover:border-[#404040]'
                        }`}
                >
                    <Upload className="h-12 w-12 mx-auto mb-4 text-[#808080]" />
                    <p className="text-lg mb-2">Перетащите файлы сюда</p>
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
                    <p className="text-xs text-[#808080] mt-4">Поддержка: .csv</p>
                    <p className="text-xs text-[#808080] mt-1">Формат: question,answer,tone</p>
                </div>

                {/* Manual Add */}
                <div className="flex items-center justify-between">
                    <p className="text-sm text-[#808080]">Или добавьте вручную:</p>
                    <Button
                        onClick={() => openModal()}
                        className="bg-white text-black hover:bg-[#E0E0E0] rounded h-10"
                    >
                        <Plus className="h-4 w-4 mr-2" />
                        Добавить пример
                    </Button>
                </div>

                {/* Examples List */}
                <div className="space-y-3">
                    {examples.length === 0 ? (
                        <div className="bg-[#0F0F0F] border border-[#2A2A2A] rounded p-8 text-center text-[#808080]">
                            Нет примеров для обучения
                        </div>
                    ) : (
                        examples.map((example, index) => (
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
                                            onClick={() => openModal(example)}
                                            className="p-2 hover:bg-[#2A2A2A] rounded transition-colors"
                                        >
                                            <Edit2 className="h-4 w-4" />
                                        </button>
                                        <button
                                            onClick={() => handleDelete(example.id)}
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
                        Обучено примеров: <span className="text-white font-semibold">{examples.length}</span>
                    </p>
                </div>

                {/* Modal */}
                {showModal && (
                    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50" onClick={closeModal}>
                        <div className="bg-[#0A0A0A] border border-[#2A2A2A] rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
                            <h2 className="text-xl font-semibold mb-6">
                                {editingExample ? 'Редактировать пример' : 'Добавить пример'}
                            </h2>

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm text-[#808080] mb-2">Вопрос</label>
                                    <Textarea
                                        value={question}
                                        onChange={(e) => setQuestion(e.target.value)}
                                        placeholder="Какая цена на шоколад?"
                                        className="bg-[#1A1A1A] border-[#2A2A2A] text-white placeholder:text-[#404040] rounded min-h-[100px] p-4 resize-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:border-white transition-colors"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm text-[#808080] mb-2">Ответ</label>
                                    <Textarea
                                        value={answer}
                                        onChange={(e) => setAnswer(e.target.value)}
                                        placeholder="Здравствуйте! Цена на шоколад составляет 5.50 BYN/кг..."
                                        className="bg-[#1A1A1A] border-[#2A2A2A] text-white placeholder:text-[#404040] rounded min-h-[150px] p-4 resize-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:border-white transition-colors"
                                    />
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm text-[#808080] mb-2">Тон</label>
                                        <select
                                            value={tone}
                                            onChange={(e) => setTone(e.target.value)}
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
                                            value={confidenceScore}
                                            onChange={(e) => setConfidenceScore(parseFloat(e.target.value))}
                                            className="w-full bg-[#1A1A1A] border border-[#2A2A2A] text-white rounded h-12 px-4 focus:outline-none focus:border-white transition-colors"
                                        />
                                    </div>
                                </div>

                                <div className="flex gap-3 pt-4">
                                    <Button
                                        onClick={closeModal}
                                        variant="outline"
                                        className="flex-1 bg-transparent border-[#2A2A2A] text-white hover:bg-[#1A1A1A] hover:text-white rounded h-10"
                                    >
                                        Отмена
                                    </Button>
                                    <Button
                                        onClick={handleSave}
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
