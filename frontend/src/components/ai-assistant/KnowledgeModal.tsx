"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { AlertCircle } from "lucide-react";

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

const REGIONS = [
    { id: "Minsk", label: "Минск" },
    { id: "Brest", label: "Брест" },
    { id: "Grodno", label: "Гродно" },
    { id: "Gomel", label: "Гомель" },
    { id: "Vitebsk", label: "Витебск" },
    { id: "Mogilev", label: "Могилев" },
];

export default function KnowledgeModal({ item, categories, onClose, onSave }: KnowledgeModalProps) {
    const [category, setCategory] = useState(item?.category || "products");
    const [title, setTitle] = useState(item?.title || "");
    const [content, setContent] = useState(item?.content || "");
    const [region, setRegion] = useState("");

    const [errors, setErrors] = useState<{ title?: string, content?: string }>({});
    const [touched, setTouched] = useState<{ title?: boolean, content?: boolean }>({});
    const [isSaving, setIsSaving] = useState(false);

    // Extract region from content if editing
    useEffect(() => {
        if (item?.content) {
            const regionMatch = item.content.match(/^\[Region: (.*?)\]\s/);
            if (regionMatch) {
                setRegion(regionMatch[1]);
                setContent(item.content.replace(/^\[Region: .*?\]\s/, ""));
            }
        }
    }, [item]);

    // Validation
    useEffect(() => {
        const newErrors: { title?: string, content?: string } = {};

        if (!title.trim()) {
            newErrors.title = "Название обязательно";
        }

        if (content.length < 10) {
            newErrors.content = `Минимум 10 символов (сейчас: ${content.length})`;
        }

        setErrors(newErrors);
    }, [title, content]);

    const handleSave = async () => {
        if (Object.keys(errors).length > 0) return;

        setIsSaving(true);
        try {
            const finalContent = region ? `[Region: ${region}] ${content}` : content;
            await onSave({ category, title, content: finalContent });
        } finally {
            setIsSaving(false);
        }
    };

    const hasErrors = Object.keys(errors).length > 0;

    return (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50" onClick={onClose}>
            <div className="bg-[#202020] border border-[#333333] rounded-lg p-6 w-full max-w-2xl shadow-2xl" onClick={(e) => e.stopPropagation()}>
                <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                    {item ? 'Редактировать' : 'Добавить информацию'}
                </h2>

                <div className="space-y-5">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-xs font-medium text-[#808080] mb-2 uppercase tracking-wide">Категория</label>
                            <select
                                value={category}
                                onChange={(e) => setCategory(e.target.value)}
                                className="w-full bg-[#262626] border border-[#333333] text-white rounded-md h-10 px-3 text-sm focus:outline-none focus:border-rose-500 transition-colors"
                            >
                                {categories.map(cat => (
                                    <option key={cat.id} value={cat.id}>{cat.label}</option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-xs font-medium text-[#808080] mb-2 uppercase tracking-wide">Регион</label>
                            <select
                                value={region}
                                onChange={(e) => setRegion(e.target.value)}
                                className="w-full bg-[#262626] border border-[#333333] text-white rounded-md h-10 px-3 text-sm focus:outline-none focus:border-rose-500 transition-colors"
                            >
                                <option value="">Вся Беларусь</option>
                                {REGIONS.map(reg => (
                                    <option key={reg.id} value={reg.id}>{reg.label}</option>
                                ))}
                            </select>
                            {!region && (
                                <p className="text-[10px] text-amber-500/80 mt-1.5 flex items-center gap-1">
                                    <AlertCircle className="w-3 h-3" />
                                    Применится ко всем регионам
                                </p>
                            )}
                        </div>
                    </div>

                    <div>
                        <label className="block text-xs font-medium text-[#808080] mb-2 uppercase tracking-wide">
                            Название <span className="text-rose-500">*</span>
                        </label>
                        <Input
                            value={title}
                            onChange={(e) => { setTitle(e.target.value); setTouched(prev => ({ ...prev, title: true })); }}
                            onBlur={() => setTouched(prev => ({ ...prev, title: true }))}
                            placeholder="Например: Шоколад молочный"
                            className={`bg-[#262626] border-[#333333] text-white placeholder:text-[#404040] h-11 px-4 focus-visible:ring-1 focus-visible:ring-rose-500 transition-colors ${touched.title && errors.title ? "border-rose-500/50 bg-rose-500/5 focus-visible:ring-rose-500" : ""
                                }`}
                        />
                        {touched.title && errors.title && (
                            <p className="text-xs text-rose-500 mt-1.5 font-medium animate-in slide-in-from-top-1">{errors.title}</p>
                        )}
                    </div>

                    <div>
                        <label className="block text-xs font-medium text-[#808080] mb-2 uppercase tracking-wide">
                            Содержание <span className="text-rose-500">*</span>
                        </label>
                        <Textarea
                            value={content}
                            onChange={(e) => { setContent(e.target.value); setTouched(prev => ({ ...prev, content: true })); }}
                            onBlur={() => setTouched(prev => ({ ...prev, content: true }))}
                            placeholder="Цена: 5.50 BYN/кг. Описание..."
                            className={`bg-[#262626] border-[#333333] text-white placeholder:text-[#404040] min-h-[150px] p-4 resize-none focus-visible:ring-1 focus-visible:ring-rose-500 transition-colors ${touched.content && errors.content ? "border-rose-500/50 bg-rose-500/5 focus-visible:ring-rose-500" : ""
                                }`}
                        />
                        {touched.content && errors.content && (
                            <p className="text-xs text-rose-500 mt-1.5 font-medium animate-in slide-in-from-top-1">{errors.content}</p>
                        )}
                    </div>

                    <div className="flex gap-3 pt-4 border-t border-[#333333] mt-2">
                        <Button
                            onClick={onClose}
                            variant="outline"
                            className="flex-1 bg-transparent border-[#333333] text-[#A0A0A0] hover:bg-[#262626] hover:text-white h-11"
                        >
                            Отмена
                        </Button>
                        <Button
                            onClick={handleSave}
                            disabled={isSaving || hasErrors}
                            className="flex-1 bg-white text-black hover:bg-[#E0E0E0] h-11 font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                        >
                            {isSaving ? 'Сохранение...' : 'Сохранить'}
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
}
