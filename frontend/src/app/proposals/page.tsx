'use client';

import { useState } from 'react';
import { FileText, Plus, Trash2, Download, Sparkles } from 'lucide-react';
import { proposalsApi } from '@/lib/api';
import { formatCurrency, downloadBlob } from '@/lib/utils';
import LiquidButton from '@/components/LiquidButton';
import GlassInput from '@/components/GlassInput';

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

    const glassTextareaClasses = "w-full resize-none rounded-2xl border border-gray-800 bg-[#050505]/60 px-4 py-3 text-sm text-gray-100 placeholder:text-gray-600 shadow-[inset_0_2px_4px_rgba(0,0,0,0.5)] transition-all duration-300 focus:border-gray-600 focus:ring-1 focus:ring-gray-600/50 focus:bg-gray-900/80 focus:outline-none";

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
                            <GlassInput
                                type="text"
                                placeholder="ФИО контактного лица"
                                value={customer.name}
                                onChange={(e) => setCustomer({ ...customer, name: e.target.value })}
                            />
                            <GlassInput
                                type="text"
                                placeholder="Компания"
                                value={customer.company}
                                onChange={(e) => setCustomer({ ...customer, company: e.target.value })}
                            />
                        </div>
                    </div>

                    {/* Items */}
                    <div className="ui-card">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="font-semibold">Товары/Услуги</h3>
                            <LiquidButton
                                onClick={addItem}
                                icon={Plus}
                                variant="secondary"
                                className="h-8 text-xs font-normal"
                            >
                                Добавить
                            </LiquidButton>
                        </div>

                        <div className="space-y-3">
                            {items.map((item, index) => (
                                <div key={item.id} className="flex flex-col sm:flex-row gap-2 items-start sm:items-center">
                                    <span className="text-sm text-[#808080] w-6 hidden sm:inline">{index + 1}.</span>
                                    <div className="flex flex-col sm:flex-row gap-2 flex-1 w-full">
                                        <div className="flex-1">
                                            <GlassInput
                                                type="text"
                                                placeholder="Наименование"
                                                value={item.product_name}
                                                onChange={(e) => updateItem(item.id, 'product_name', e.target.value)}
                                            />
                                        </div>
                                        <div className="flex gap-2">
                                            <div className="w-24">
                                                <GlassInput
                                                    type="number"
                                                    placeholder="Кол-во"
                                                    value={item.quantity}
                                                    onChange={(e) => updateItem(item.id, 'quantity', Number(e.target.value))}
                                                />
                                            </div>
                                            <div className="w-28">
                                                <GlassInput
                                                    type="number"
                                                    placeholder="Цена"
                                                    value={item.price}
                                                    onChange={(e) => updateItem(item.id, 'price', Number(e.target.value))}
                                                />
                                            </div>
                                            <div className="w-20">
                                                <GlassInput
                                                    type="number"
                                                    placeholder="%"
                                                    value={item.discount}
                                                    onChange={(e) => updateItem(item.id, 'discount', Number(e.target.value))}
                                                />
                                            </div>
                                        </div>
                                    </div>
                                    <LiquidButton
                                        onClick={() => removeItem(item.id)}
                                        variant="secondary"
                                        className="h-11 w-11 p-0 text-red-500/70 hover:text-red-400 hover:bg-red-500/10 border-red-500/20 self-end sm:self-auto"
                                    >
                                        <Trash2 className="h-4 w-4" />
                                    </LiquidButton>
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
                            className={glassTextareaClasses}
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

                        <LiquidButton
                            onClick={generate}
                            disabled={!customer.name || items.length === 0 || loading}
                            icon={Sparkles}
                            variant="primary"
                            className="w-full"
                        >
                            {loading ? 'Генерация...' : 'Сгенерировать текст'}
                        </LiquidButton>

                        {generatedText && (
                            <div className="rounded-2xl bg-white/[0.03] p-6 border border-white/5 shadow-inner backdrop-blur-sm">
                                <pre className="whitespace-pre-wrap text-sm text-gray-300 font-mono leading-relaxed">{generatedText}</pre>
                            </div>
                        )}
                    </div>

                    <div className="ui-card">
                        <h3 className="font-semibold mb-3">Экспорт</h3>
                        <LiquidButton
                            onClick={exportDocx}
                            variant="secondary"
                            icon={Download}
                            className="w-full"
                        >
                            Скачать DOCX
                        </LiquidButton>
                        <LiquidButton
                            onClick={exportPdf}
                            variant="secondary"
                            icon={Download}
                            className="w-full"
                        >
                            Скачать PDF
                        </LiquidButton>
                    </div>
                </div>
            </div>
        </div>
    );
}
