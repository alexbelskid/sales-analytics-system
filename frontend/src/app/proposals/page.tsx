'use client';

import { useState } from 'react';
import { FileText, Plus, Trash2, Download, Sparkles } from 'lucide-react';
import { proposalsApi } from '@/lib/api';
import { formatCurrency, downloadBlob } from '@/lib/utils';

interface ProposalItem {
    id: string;
    product_name: string;
    quantity: number;
    price: number;
    discount: number;
}

export default function ProposalsPage() {
    const [customer, setCustomer] = useState({ name: '', company: '' });
    const [items, setItems] = useState<ProposalItem[]>([
        { id: '1', product_name: '', quantity: 1, price: 0, discount: 0 },
    ]);
    const [conditions, setConditions] = useState('');
    const [generatedText, setGeneratedText] = useState('');
    const [loading, setLoading] = useState(false);

    function addItem() {
        setItems([
            ...items,
            { id: Date.now().toString(), product_name: '', quantity: 1, price: 0, discount: 0 },
        ]);
    }

    function removeItem(id: string) {
        setItems(items.filter((item) => item.id !== id));
    }

    function updateItem(id: string, field: keyof ProposalItem, value: any) {
        setItems(items.map((item) => (item.id === id ? { ...item, [field]: value } : item)));
    }

    function calculateTotal() {
        return items.reduce((sum, item) => {
            const amount = item.quantity * item.price * (1 - item.discount / 100);
            return sum + amount;
        }, 0);
    }

    async function generate() {
        setLoading(true);
        try {
            const result = await proposalsApi.generate({
                customer_name: customer.name,
                customer_company: customer.company,
                items: items.map((i) => ({
                    product_name: i.product_name,
                    quantity: i.quantity,
                    price: i.price,
                    discount: i.discount,
                })),
                conditions,
                use_ai: true,
            });
            if (result.generated_text) {
                setGeneratedText(result.generated_text);
            }
        } catch (err) {
            console.error('Error generating proposal:', err);
        } finally {
            setLoading(false);
        }
    }

    async function exportDocx() {
        const blob = await proposalsApi.exportDocx({
            customer_name: customer.name,
            customer_company: customer.company,
            items: items.map((i) => ({
                product_name: i.product_name,
                quantity: i.quantity,
                price: i.price,
                discount: i.discount,
            })),
            conditions,
            valid_days: 30,
        });
        downloadBlob(blob, `KP_${customer.name.replace(/\s/g, '_')}.docx`);
    }

    async function exportPdf() {
        const blob = await proposalsApi.exportPdf({
            customer_name: customer.name,
            customer_company: customer.company,
            items: items.map((i) => ({
                product_name: i.product_name,
                quantity: i.quantity,
                price: i.price,
                discount: i.discount,
            })),
            conditions,
            valid_days: 30,
        });
        downloadBlob(blob, `KP_${customer.name.replace(/\s/g, '_')}.pdf`);
    }

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Коммерческие предложения</h1>
                    <p className="text-muted-foreground">Создание КП с помощью AI</p>
                </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
                {/* Form */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Customer */}
                    <div className="metric-card space-y-4">
                        <h3 className="font-semibold">Клиент</h3>
                        <div className="grid gap-4 md:grid-cols-2">
                            <input
                                type="text"
                                placeholder="ФИО контактного лица"
                                value={customer.name}
                                onChange={(e) => setCustomer({ ...customer, name: e.target.value })}
                                className="rounded-lg border border-input bg-background px-4 py-2"
                            />
                            <input
                                type="text"
                                placeholder="Компания"
                                value={customer.company}
                                onChange={(e) => setCustomer({ ...customer, company: e.target.value })}
                                className="rounded-lg border border-input bg-background px-4 py-2"
                            />
                        </div>
                    </div>

                    {/* Items */}
                    <div className="metric-card space-y-4">
                        <div className="flex items-center justify-between">
                            <h3 className="font-semibold">Товары/Услуги</h3>
                            <button
                                onClick={addItem}
                                className="flex items-center gap-1 text-sm text-primary hover:underline"
                            >
                                <Plus className="h-4 w-4" /> Добавить
                            </button>
                        </div>

                        <div className="space-y-3">
                            {items.map((item, index) => (
                                <div key={item.id} className="flex gap-2 items-center">
                                    <span className="text-sm text-muted-foreground w-6">{index + 1}.</span>
                                    <input
                                        type="text"
                                        placeholder="Наименование"
                                        value={item.product_name}
                                        onChange={(e) => updateItem(item.id, 'product_name', e.target.value)}
                                        className="flex-1 rounded-lg border border-input bg-background px-3 py-2 text-sm"
                                    />
                                    <input
                                        type="number"
                                        placeholder="Кол-во"
                                        value={item.quantity}
                                        onChange={(e) => updateItem(item.id, 'quantity', Number(e.target.value))}
                                        className="w-20 rounded-lg border border-input bg-background px-3 py-2 text-sm"
                                    />
                                    <input
                                        type="number"
                                        placeholder="Цена"
                                        value={item.price}
                                        onChange={(e) => updateItem(item.id, 'price', Number(e.target.value))}
                                        className="w-28 rounded-lg border border-input bg-background px-3 py-2 text-sm"
                                    />
                                    <input
                                        type="number"
                                        placeholder="%"
                                        value={item.discount}
                                        onChange={(e) => updateItem(item.id, 'discount', Number(e.target.value))}
                                        className="w-16 rounded-lg border border-input bg-background px-3 py-2 text-sm"
                                    />
                                    <button
                                        onClick={() => removeItem(item.id)}
                                        className="p-2 text-muted-foreground hover:text-destructive"
                                    >
                                        <Trash2 className="h-4 w-4" />
                                    </button>
                                </div>
                            ))}
                        </div>

                        <div className="flex justify-end text-lg font-bold">
                            ИТОГО: {formatCurrency(calculateTotal())}
                        </div>
                    </div>

                    {/* Conditions */}
                    <div className="metric-card space-y-4">
                        <h3 className="font-semibold">Условия</h3>
                        <textarea
                            placeholder="Условия оплаты, доставки, гарантии..."
                            value={conditions}
                            onChange={(e) => setConditions(e.target.value)}
                            rows={3}
                            className="w-full rounded-lg border border-input bg-background px-4 py-2 resize-none"
                        />
                    </div>
                </div>

                {/* Preview & Actions */}
                <div className="space-y-4">
                    <div className="metric-card space-y-4">
                        <div className="flex items-center gap-2">
                            <FileText className="h-5 w-5 text-primary" />
                            <h3 className="font-semibold">Предпросмотр</h3>
                        </div>

                        <button
                            onClick={generate}
                            disabled={!customer.name || items.length === 0 || loading}
                            className="flex w-full items-center justify-center gap-2 rounded-lg bg-primary py-2.5 font-medium text-white hover:bg-primary/90 disabled:opacity-50"
                        >
                            <Sparkles className="h-4 w-4" />
                            {loading ? 'Генерация...' : 'Сгенерировать текст'}
                        </button>

                        {generatedText && (
                            <div className="rounded-lg bg-secondary/50 p-4">
                                <pre className="whitespace-pre-wrap text-sm">{generatedText}</pre>
                            </div>
                        )}
                    </div>

                    <div className="metric-card space-y-3">
                        <h3 className="font-semibold">Экспорт</h3>
                        <button
                            onClick={exportDocx}
                            className="flex w-full items-center justify-center gap-2 rounded-lg border border-border py-2.5 font-medium hover:bg-secondary"
                        >
                            <Download className="h-4 w-4" />
                            Скачать DOCX
                        </button>
                        <button
                            onClick={exportPdf}
                            className="flex w-full items-center justify-center gap-2 rounded-lg border border-border py-2.5 font-medium hover:bg-secondary"
                        >
                            <Download className="h-4 w-4" />
                            Скачать PDF
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
