"use client";

import { memo, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Edit2, Trash2, Upload, CheckCircle, XCircle } from "lucide-react";

interface TrainingExample {
    id: string;
    question: string;
    answer: string;
    tone: string;
    confidence_score: number;
}

interface TrainingTabProps {
    items: TrainingExample[];
    isDragging: boolean;
    onEdit: (item: TrainingExample) => void;
    onDelete: (id: string) => void;
    onDrop: (e: React.DragEvent) => void;
    onDragOver: (e: React.DragEvent) => void;
    onDragLeave: (e: React.DragEvent) => void;
    onUploadClick: () => void;
}

const TrainingTab = memo(({
    items,
    isDragging,
    onEdit,
    onDelete,
    onDrop,
    onDragOver,
    onDragLeave,
    onUploadClick
}: TrainingTabProps) => {
    return (
        <div className="space-y-6">
            {/* Upload Area */}
            <div
                onDrop={onDrop}
                onDragOver={onDragOver}
                onDragLeave={onDragLeave}
                onClick={onUploadClick}
                className={`border-2 border-dashed rounded-lg p-12 text-center transition-all cursor-pointer ${isDragging
                    ? 'border-white bg-[#1A1A1A]'
                    : 'border-[#2A2A2A] hover:border-[#404040]'
                    }`}
            >
                <div className="flex flex-col items-center">
                    <Upload className="h-10 w-10 text-[#808080] mb-4" />
                    <p className="text-lg font-medium mb-1">Загрузить примеры (CSV)</p>
                    <p className="text-sm text-[#808080]">Перетащите файл сюда или нажмите для выбора</p>
                </div>
            </div>

            {/* Examples List */}
            <div className="space-y-4">
                <h3 className="text-sm font-medium text-[#808080] uppercase tracking-wider mb-4">Существующие примеры ({items.length})</h3>
                <div className="grid grid-cols-1 gap-4">
                    {items.map(example => (
                        <div key={example.id} className="ui-card">
                            <div className="flex justify-between items-start mb-4">
                                <div className="space-y-1">
                                    <div className="flex items-center gap-2">
                                        <span className="text-[10px] uppercase font-bold tracking-widest text-[#808080] bg-[#2A2A2A] px-2 py-0.5 rounded">
                                            Тон: {example.tone}
                                        </span>
                                        <div className="flex items-center gap-1 text-[10px] uppercase font-bold tracking-widest bg-white/5 px-2 py-0.5 rounded">
                                            {example.confidence_score >= 0.8 ? (
                                                <CheckCircle className="h-3 w-3 text-green-500" />
                                            ) : (
                                                <XCircle className="h-3 w-3 text-red-500" />
                                            )}
                                            <span className={example.confidence_score >= 0.8 ? 'text-green-500' : 'text-red-500'}>
                                                Качество: {(example.confidence_score * 100).toFixed(0)}%
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <Button variant="ghost" size="icon" onClick={() => onEdit(example)} className="h-8 w-8 text-[#808080] hover:text-white">
                                        <Edit2 className="h-4 w-4" />
                                    </Button>
                                    <Button variant="ghost" size="icon" onClick={() => onDelete(example.id)} className="h-8 w-8 text-[#808080] hover:text-red-400">
                                        <Trash2 className="h-4 w-4" />
                                    </Button>
                                </div>
                            </div>
                            <div className="grid md:grid-cols-2 gap-6">
                                <div>
                                    <p className="text-[10px] uppercase font-bold text-[#404040] mb-2 tracking-widest">Вопрос</p>
                                    <p className="text-sm text-white leading-relaxed">{example.question}</p>
                                </div>
                                <div>
                                    <p className="text-[10px] uppercase font-bold text-[#404040] mb-2 tracking-widest">Ответ</p>
                                    <p className="text-sm text-[#808080] leading-relaxed">{example.answer}</p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
});

TrainingTab.displayName = "TrainingTab";

export default TrainingTab;
