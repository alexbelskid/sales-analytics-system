"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { Plus, Edit2, Trash2, ArrowLeft } from "lucide-react";
import Link from "next/link";

interface KnowledgeItem {
    id: string;
    category: string;
    title: string;
    content: string;
    created_at?: string;
}

const CATEGORIES = [
    { id: 'products', label: 'Наши продукты' },
    { id: 'terms', label: 'Условия работы' },
    { id: 'contacts', label: 'Контакты' },
    { id: 'faq', label: 'FAQ' },
    { id: 'company_info', label: 'О компании' },
];

export default function KnowledgePage() {
    const { toast } = useToast();
    const [items, setItems] = useState<KnowledgeItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [editingItem, setEditingItem] = useState<KnowledgeItem | null>(null);

    // Form state
    const [category, setCategory] = useState("products");
    const [title, setTitle] = useState("");
    const [content, setContent] = useState("");

    useEffect(() => {
        loadKnowledge();
    }, []);

    const loadKnowledge = async () => {
        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/knowledge`);
            const data = await response.json();
            setItems(data);
        } catch (error) {
            toast({ title: "Ошибка", description: "Не удалось загрузить базу знаний" });
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        if (!title || !content) {
            toast({ title: "Ошибка", description: "Заполните все поля" });
            return;
        }

        try {
            const url = editingItem
                ? `${process.env.NEXT_PUBLIC_API_URL}/api/knowledge/${editingItem.id}`
                : `${process.env.NEXT_PUBLIC_API_URL}/api/knowledge`;

            const method = editingItem ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ category, title, content }),
            });

            if (response.ok) {
                toast({ title: "Успешно", description: editingItem ? "Обновлено" : "Создано" });
                loadKnowledge();
                closeModal();
            }
        } catch (error) {
            toast({ title: "Ошибка", description: "Не удалось сохранить" });
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm("Удалить эту запись?")) return;

        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/knowledge/${id}`, {
                method: 'DELETE',
            });

            if (response.ok) {
                toast({ title: "Удалено" });
                loadKnowledge();
            }
        } catch (error) {
            toast({ title: "Ошибка", description: "Не удалось удалить" });
        }
    };

    const openModal = (item?: KnowledgeItem) => {
        if (item) {
            setEditingItem(item);
            setCategory(item.category);
            setTitle(item.title);
            setContent(item.content);
        } else {
            setEditingItem(null);
            setCategory("products");
            setTitle("");
            setContent("");
        }
        setShowModal(true);
    };

    const closeModal = () => {
        setShowModal(false);
        setEditingItem(null);
        setCategory("products");
        setTitle("");
        setContent("");
    };

    const groupedItems = CATEGORIES.map(cat => ({
        ...cat,
        items: items.filter(item => item.category === cat.id)
    }));

    return (
        <div className="min-h-screen bg-[#0A0A0A] text-white p-8">
            <div className="max-w-5xl mx-auto space-y-8">

                {/* Breadcrumbs / Back */}
                <Link href="/settings" className="inline-flex items-center gap-2 text-[#808080] hover:text-white transition-colors mb-4 group">
                    <ArrowLeft className="h-4 w-4 transition-transform group-hover:-translate-x-1" />
                    <span className="text-xs uppercase tracking-widest font-medium">Назад в настройки</span>
                </Link>

                {/* Header */}
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-[32px] font-semibold">База знаний</h1>
                        <p className="text-sm text-[#808080] mt-1">Информация для AI ассистента</p>
                    </div>
                    <Button
                        onClick={() => openModal()}
                        className="bg-white text-black hover:bg-[#E0E0E0] rounded h-10"
                    >
                        <Plus className="h-4 w-4 mr-2" />
                        Добавить
                    </Button>
                </div>

                <div className="h-[1px] bg-[#1A1A1A]" />

                {/* Knowledge Items by Category */}
                <div className="space-y-6">
                    {groupedItems.map(group => (
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
                                                        onClick={() => openModal(item)}
                                                        className="p-2 hover:bg-[#2A2A2A] rounded transition-colors"
                                                    >
                                                        <Edit2 className="h-4 w-4" />
                                                    </button>
                                                    <button
                                                        onClick={() => handleDelete(item.id)}
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

                {/* Modal */}
                {showModal && (
                    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50" onClick={closeModal}>
                        <div className="bg-[#0A0A0A] border border-[#2A2A2A] rounded-lg p-6 w-full max-w-2xl" onClick={(e) => e.stopPropagation()}>
                            <h2 className="text-xl font-semibold mb-6">
                                {editingItem ? 'Редактировать' : 'Добавить информацию'}
                            </h2>

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm text-[#808080] mb-2">Категория</label>
                                    <select
                                        value={category}
                                        onChange={(e) => setCategory(e.target.value)}
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
                                        value={title}
                                        onChange={(e) => setTitle(e.target.value)}
                                        placeholder="Например: Шоколад молочный"
                                        className="bg-[#1A1A1A] border-[#2A2A2A] text-white placeholder:text-[#404040] rounded h-12 px-4 focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:border-white transition-colors"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm text-[#808080] mb-2">Содержание</label>
                                    <Textarea
                                        value={content}
                                        onChange={(e) => setContent(e.target.value)}
                                        placeholder="Цена: 5.50 BYN/кг. Описание..."
                                        className="bg-[#1A1A1A] border-[#2A2A2A] text-white placeholder:text-[#404040] rounded min-h-[150px] p-4 resize-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:border-white transition-colors"
                                    />
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
