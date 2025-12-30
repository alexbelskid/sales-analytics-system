'use client';

import { useState } from 'react';
import { Mail, Send, Copy, Sparkles, Tag } from 'lucide-react';
import { emailApi } from '@/lib/api';

export default function EmailsPage() {
    const [emailInput, setEmailInput] = useState({
        subject: '',
        sender: '',
        body: '',
    });
    const [emailType, setEmailType] = useState('general');
    const [generatedReply, setGeneratedReply] = useState('');
    const [loading, setLoading] = useState(false);

    const emailTypes = [
        { id: 'general', name: 'Общий запрос', color: 'bg-gray-500' },
        { id: 'price', name: 'Запрос цены', color: 'bg-blue-500' },
        { id: 'availability', name: 'Наличие', color: 'bg-green-500' },
        { id: 'complaint', name: 'Жалоба', color: 'bg-red-500' },
    ];

    async function classifyEmail() {
        if (!emailInput.subject && !emailInput.body) return;

        try {
            const result = await emailApi.classifyEmail(emailInput.subject, emailInput.body);
            setEmailType(result.email_type);
        } catch (err) {
            console.error('Classification error:', err);
        }
    }

    async function generateReply() {
        if (!emailInput.body) return;

        setLoading(true);
        try {
            const result = await emailApi.generateReply({
                ...emailInput,
                email_type: emailType,
            });
            setGeneratedReply(result.generated_reply);
        } catch (err: any) {
            setGeneratedReply('Ошибка генерации ответа. Проверьте настройки OpenAI API.');
        } finally {
            setLoading(false);
        }
    }

    function copyToClipboard() {
        navigator.clipboard.writeText(generatedReply);
    }

    return (
        <div className="mx-auto max-w-4xl space-y-6 animate-fade-in">
            <div>
                <h1 className="text-2xl font-bold">Автоответы на письма</h1>
                <p className="text-muted-foreground">
                    AI генерирует ответы на входящие письма клиентов
                </p>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
                {/* Input Email */}
                <div className="metric-card space-y-4">
                    <div className="flex items-center gap-2">
                        <Mail className="h-5 w-5 text-primary" />
                        <h3 className="font-semibold">Входящее письмо</h3>
                    </div>

                    <div className="space-y-3">
                        <input
                            type="text"
                            placeholder="От кого"
                            value={emailInput.sender}
                            onChange={(e) => setEmailInput({ ...emailInput, sender: e.target.value })}
                            className="w-full rounded-lg border border-input bg-background px-4 py-2 text-sm"
                        />
                        <input
                            type="text"
                            placeholder="Тема письма"
                            value={emailInput.subject}
                            onChange={(e) => setEmailInput({ ...emailInput, subject: e.target.value })}
                            className="w-full rounded-lg border border-input bg-background px-4 py-2 text-sm"
                        />
                        <textarea
                            placeholder="Текст письма..."
                            value={emailInput.body}
                            onChange={(e) => setEmailInput({ ...emailInput, body: e.target.value })}
                            onBlur={classifyEmail}
                            rows={8}
                            className="w-full rounded-lg border border-input bg-background px-4 py-2 text-sm resize-none"
                        />
                    </div>

                    {/* Email Type */}
                    <div className="flex flex-wrap gap-2">
                        {emailTypes.map((type) => (
                            <button
                                key={type.id}
                                onClick={() => setEmailType(type.id)}
                                className={`flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium transition-all ${emailType === type.id
                                        ? `${type.color} text-white`
                                        : 'bg-secondary text-muted-foreground hover:bg-secondary/80'
                                    }`}
                            >
                                <Tag className="h-3 w-3" />
                                {type.name}
                            </button>
                        ))}
                    </div>

                    <button
                        onClick={generateReply}
                        disabled={!emailInput.body || loading}
                        className="flex w-full items-center justify-center gap-2 rounded-lg bg-primary py-2.5 font-medium text-white transition-all hover:bg-primary/90 disabled:opacity-50"
                    >
                        <Sparkles className="h-4 w-4" />
                        {loading ? 'Генерация...' : 'Сгенерировать ответ'}
                    </button>
                </div>

                {/* Generated Reply */}
                <div className="metric-card space-y-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Send className="h-5 w-5 text-green-500" />
                            <h3 className="font-semibold">Сгенерированный ответ</h3>
                        </div>
                        {generatedReply && (
                            <button
                                onClick={copyToClipboard}
                                className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
                            >
                                <Copy className="h-4 w-4" />
                                Копировать
                            </button>
                        )}
                    </div>

                    <div className="min-h-[300px] rounded-lg border border-input bg-secondary/30 p-4">
                        {generatedReply ? (
                            <pre className="whitespace-pre-wrap text-sm">{generatedReply}</pre>
                        ) : (
                            <p className="text-sm text-muted-foreground">
                                Вставьте текст письма и нажмите "Сгенерировать ответ"
                            </p>
                        )}
                    </div>

                    {generatedReply && (
                        <div className="flex gap-2">
                            <button className="flex-1 rounded-lg border border-border py-2 text-sm font-medium hover:bg-secondary">
                                Сохранить как черновик
                            </button>
                            <button className="flex-1 rounded-lg bg-green-500 py-2 text-sm font-medium text-white hover:bg-green-600">
                                Отправить
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
