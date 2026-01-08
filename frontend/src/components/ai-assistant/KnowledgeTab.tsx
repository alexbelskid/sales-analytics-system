"use client";

import { memo } from "react";
import { Button } from "@/components/ui/button";
import { Edit2, Trash2 } from "lucide-react";

interface KnowledgeItem {
    id: string;
    category: string;
    title: string;
    content: string;
}

interface KnowledgeTabProps {
    items: KnowledgeItem[];
    categories: { id: string; label: string }[];
    onEdit: (item: KnowledgeItem) => void;
    onDelete: (id: string) => void;
}

const KnowledgeTab = memo(({ items, categories, onEdit, onDelete }: KnowledgeTabProps) => {
    return (
        <div className="space-y-6">
            {categories.map(cat => {
                const catItems = items.filter(i => i.category === cat.id);
                if (catItems.length === 0) return null;

                return (
                    <div key={cat.id}>
                        <h3 className="text-sm font-medium text-[#808080] uppercase tracking-wider mb-4">{cat.label}</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {catItems.map(item => (
                                <div key={item.id} className="ui-card group">
                                    <div className="flex justify-between items-start mb-3">
                                        <h4 className="font-medium text-white flex-1 pr-2">{item.title}</h4>
                                        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <Button variant="ghost" size="icon" onClick={() => onEdit(item)} className="h-8 w-8 text-[#808080] hover:text-white hover:bg-[#333333]">
                                                <Edit2 className="h-4 w-4" />
                                            </Button>
                                            <Button variant="ghost" size="icon" onClick={() => onDelete(item.id)} className="h-8 w-8 text-[#808080] hover:text-red-400 hover:bg-red-400/10">
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                        </div>
                                    </div>
                                    <p className="text-sm text-[#808080] line-clamp-3 leading-relaxed">{item.content}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                );
            })}

            {items.length === 0 && (
                <div className="text-center py-12 border border-dashed border-[#333333] rounded-lg">
                    <p className="text-[#808080]">База знаний пуста. Добавьте первую запись.</p>
                </div>
            )}
        </div>
    );
});

KnowledgeTab.displayName = "KnowledgeTab";

export default KnowledgeTab;
