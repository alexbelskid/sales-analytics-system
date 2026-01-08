"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface TrainingExample {
    id: string;
    question: string;
    answer: string;
    tone: string;
    confidence_score: number;
}

interface TrainingModalProps {
    item: TrainingExample | null;
    tones: { id: string; label: string }[];
    onClose: () => void;
    onSave: (data: { question: string; answer: string; tone: string; confidence_score: number }) => Promise<void>;
}

export default function TrainingModal({ item, tones, onClose, onSave }: TrainingModalProps) {
    const [question, setQuestion] = useState(item?.question || "");
    const [answer, setAnswer] = useState(item?.answer || "");
    const [tone, setTone] = useState(item?.tone || "professional");
    const [confidence, setConfidence] = useState(item?.confidence_score || 1.0);
    const [isSaving, setIsSaving] = useState(false);

    const handleSave = async () => {
        if (!question || !answer) return;
        setIsSaving(true);
        try {
            await onSave({ question, answer, tone, confidence_score: confidence });
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50" onClick={onClose}>
            <div className="bg-[#202020] border border-[#333333] rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
                <h2 className="text-xl font-semibold mb-6">
                    {item ? 'Редактировать пример' : 'Добавить пример'}
                </h2>

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm text-[#808080] mb-2">Вопрос</label>
                        <Textarea
                            value={question}
                            onChange={(e) => setQuestion(e.target.value)}
                            placeholder="Какая цена на шоколад?"
                            className="bg-[#262626] border-[#333333] text-white placeholder:text-[#404040] rounded min-h-[100px] p-4 resize-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:border-white transition-colors"
                        />
                    </div>

                    <div>
                        <label className="block text-sm text-[#808080] mb-2">Ответ</label>
                        <Textarea
                            value={answer}
                            onChange={(e) => setAnswer(e.target.value)}
                            placeholder="Здравствуйте! Цена на шоколад..."
                            className="bg-[#262626] border-[#333333] text-white placeholder:text-[#404040] rounded min-h-[150px] p-4 resize-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:border-white transition-colors"
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm text-[#808080] mb-2">Тон</label>
                            <select
                                value={tone}
                                onChange={(e) => setTone(e.target.value)}
                                className="w-full bg-[#262626] border border-[#333333] text-white rounded h-12 px-4 focus:outline-none focus:border-white transition-colors"
                            >
                                {tones.map(t => (
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
                                value={confidence}
                                onChange={(e) => setConfidence(parseFloat(e.target.value))}
                                className="w-full bg-[#262626] border border-[#333333] text-white rounded h-12 px-4 focus:outline-none focus:border-white transition-colors"
                            />
                        </div>
                    </div>

                    <div className="flex gap-3 pt-4">
                        <Button
                            onClick={onClose}
                            variant="outline"
                            className="flex-1 bg-transparent border-[#333333] text-white hover:bg-[#262626] hover:text-white rounded h-10"
                        >
                            Отмена
                        </Button>
                        <Button
                            onClick={handleSave}
                            disabled={isSaving || !question || !answer}
                            className="flex-1 bg-white text-black hover:bg-[#E0E0E0] rounded h-10"
                        >
                            {isSaving ? 'Сохранение...' : 'Сохранить'}
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
}
