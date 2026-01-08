"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

interface KnowledgeItem {
    id: string;
    category: string;
    title: string;
    content: string;
}

interface KnowledgeModalProps {
    item: KnowledgeItem | null;
    categories: { id: string; label: string }[];
    onClose: () => void;
    onSave: (data: { category: string; title: string; content: string }) => Promise<void>;
}

export default function KnowledgeModal({ item, categories, onClose, onSave }: KnowledgeModalProps) {
    const [category, setCategory] = useState(item?.category || "products");
    const [title, setTitle] = useState(item?.title || "");
    const [content, setContent] = useState(item?.content || "");
    const [isSaving, setIsSaving] = useState(false);

    const handleSave = async () => {
        if (!title || !content) return;
        setIsSaving(true);
        try {
            await onSave({ category, title, content });
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50" onClick={onClose}>
            <div className="bg-[#202020] border border-[#333333] rounded-lg p-6 w-full max-w-2xl" onClick={(e) => e.stopPropagation()}>
                <h2 className="text-xl font-semibold mb-6">
                    {item ? 'Редактировать' : 'Добавить информацию'}
                </h2>

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm text-[#808080] mb-2">Категория</label>
                        <select
                            value={category}
                            onChange={(e) => setCategory(e.target.value)}
                            className="w-full bg-[#262626] border border-[#333333] text-white rounded h-12 px-4 focus:outline-none focus:border-white transition-colors"
                        >
                            {categories.map(cat => (
                                <option key={cat.id} value={cat.id}>{cat.label}</option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm text-[#808080] mb-2">Название</label>
                        <Input
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            placeholder="Например: Шоколад молочный"
                            className="bg-[#262626] border-[#333333] text-white placeholder:text-[#404040] rounded h-12 px-4 focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:border-white transition-colors"
                        />
                    </div>

                    <div>
                        <label className="block text-sm text-[#808080] mb-2">Содержание</label>
                        <Textarea
                            value={content}
                            onChange={(e) => setContent(e.target.value)}
                            placeholder="Цена: 5.50 BYN/кг. Описание..."
                            className="bg-[#262626] border-[#333333] text-white placeholder:text-[#404040] rounded min-h-[150px] p-4 resize-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:border-white transition-colors"
                        />
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
                            disabled={isSaving || !title || !content}
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
