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

    const inputClasses = "rounded-xl border border-[#2A2A2A] bg-[#1A1A1A] px-4 py-2.5 text-sm text-white placeholder:text-[#404040] focus:outline-none focus:border-rose-800 focus:ring-2 focus:ring-rose-800/25 transition-all duration-300";

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Коммерческие предложения</h1>
                    <p className="text-[#808080]">Создание КП с помощью AI</p>
                </div>
            </div>

            <div className="flex flex-col lg:flex-row gap-6">
                {/* Form */}
                <div className="flex-1 space-y-6">
                    {/* Customer */}
                    <div className="ui-card">
                        <h3 className="font-semibold mb-4">Клиент</h3>
                        <div className="grid gap-4 sm:grid-cols-2">
                            <input
                                type="text"
                                placeholder="ФИО контактного лица"
                                value={customer.name}
                                onChange={(e) => setCustomer({ ...customer, name: e.target.value })}
                                className={inputClasses}
                            />
                            <input
                                type="text"
                                placeholder="Компания"
                                value={customer.company}
                                onChange={(e) => setCustomer({ ...customer, company: e.target.value })}
                                className={inputClasses}
                            />
                        </div>
                    </div>

                    {/* Items */}
                    <div className="ui-card">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="font-semibold">Товары/Услуги</h3>
                            <button
                                onClick={addItem}
                                className="flex items-center gap-1 text-sm text-white hover:text-[#808080] transition-colors"
                            >
                                <Plus className="h-4 w-4" /> Добавить
                            </button>
                        </div>

                        <div className="space-y-3">
                            {items.map((item, index) => (
                                <div key={item.id} className="flex flex-col sm:flex-row gap-2 items-start sm:items-center">
                                    <span className="text-sm text-[#808080] w-6 hidden sm:inline">{index + 1}.</span>
                                    <div className="flex flex-col sm:flex-row gap-2 flex-1 w-full">
                                        <input
                                            type="text"
                                            placeholder="Наименование"
                                            value={item.product_name}
                                            onChange={(e) => updateItem(item.id, 'product_name', e.target.value)}
                                            className={`flex-1 ${inputClasses}`}
                                        />
                                        <div className="flex gap-2">
                                            <input
                                                type="number"
                                                placeholder="Кол-во"
                                                value={item.quantity}
                                                onChange={(e) => updateItem(item.id, 'quantity', Number(e.target.value))}
                                                className={`w-24 ${inputClasses}`}
                                            />
                                            <input
                                                type="number"
                                                placeholder="Цена"
                                                value={item.price}
                                                onChange={(e) => updateItem(item.id, 'price', Number(e.target.value))}
                                                className={`w-28 ${inputClasses}`}
                                            />
                                            <input
                                                type="number"
                                                placeholder="%"
                                                value={item.discount}
                                                onChange={(e) => updateItem(item.id, 'discount', Number(e.target.value))}
                                                className={`w-20 ${inputClasses}`}
                                            />
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => removeItem(item.id)}
                                        className="p-2 text-[#808080] hover:text-red-400 transition-colors self-end sm:self-auto"
                                    >
                                        <Trash2 className="h-4 w-4" />
                                    </button>
                                </div>
                            ))}
                        </div>

                        <div className="flex justify-end text-lg font-bold text-white">
                            ИТОГО: {formatCurrency(calculateTotal())}
                        </div>
                    </div>

                    {/* Conditions */}
                    <div className="ui-card">
                        <h3 className="font-semibold mb-4">Условия</h3>
                        <textarea
                            placeholder="Условия оплаты, доставки, гарантии..."
                            value={conditions}
                            onChange={(e) => setConditions(e.target.value)}
                            rows={3}
                            className={`w-full resize-none ${inputClasses}`}
                        />
                    </div>
                </div>

                {/* Preview & Actions */}
                <div className="space-y-4 lg:w-80 flex-shrink-0">
                    <div className="ui-card">
                        <div className="flex items-center gap-2 mb-4">
                            <FileText className="h-5 w-5 text-white" />
                            <h3 className="font-semibold">Предпросмотр</h3>
                        </div>

                        <button
                            onClick={generate}
                            disabled={!customer.name || items.length === 0 || loading}
                            className="flex w-full items-center justify-center gap-2 rounded-full bg-rose-800 hover:bg-rose-700 py-3 font-medium text-white disabled:opacity-50 transition-all duration-300 hover:shadow-lg hover:shadow-rose-800/25"
                        >
                            <Sparkles className="h-4 w-4" />
                            {loading ? 'Генерация...' : 'Сгенерировать текст'}
                        </button>

                        {generatedText && (
                            <div className="rounded-lg bg-[#0A0A0A] p-4 border border-[#2A2A2A]">
                                <pre className="whitespace-pre-wrap text-sm text-[#808080]">{generatedText}</pre>
                            </div>
                        )}
                    </div>

                    <div className="ui-card">
                        <h3 className="font-semibold mb-3">Экспорт</h3>
                        <button
                            onClick={exportDocx}
                            className="flex w-full items-center justify-center gap-2 rounded-full border border-[#2A2A2A] py-2.5 font-medium text-white hover:bg-[#2A2A2A] transition-all duration-300"
                        >
                            <Download className="h-4 w-4" />
                            Скачать DOCX
                        </button>
                        <button
                            onClick={exportPdf}
                            className="flex w-full items-center justify-center gap-2 rounded-full border border-[#2A2A2A] py-2.5 font-medium text-white hover:bg-[#2A2A2A] transition-all duration-300"
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
