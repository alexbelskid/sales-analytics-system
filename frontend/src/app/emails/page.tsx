"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { Loader2, Copy, Sparkles } from "lucide-react";
import { aiApi, knowledgeApi, trainingApi } from "@/lib/api";

const TONES = [
    { id: 'professional', label: 'Профессиональный' },
    { id: 'friendly', label: 'Дружелюбный' },
    { id: 'formal', label: 'Официальный' },
    { id: 'brief', label: 'Краткий' },
    { id: 'detailed', label: 'Подробный' },
    { id: 'creative', label: 'Креативный' },
];

export default function EmailsPage() {
    const { toast } = useToast();

    // Form State
    const [sender, setSender] = useState("");
    const [subject, setSubject] = useState("");
    const [body, setBody] = useState("");
    const [tone, setTone] = useState("professional");

    // Result State
    const [generatedResponse, setGeneratedResponse] = useState("");
    const [confidence, setConfidence] = useState(0);
    const [loading, setLoading] = useState(false);



    const handleGenerate = async () => {
        if (!body) {
            toast({ title: "Ошибка", description: "Введите текст письма" });
            return;
        }

        setLoading(true);
        try {
            const res = await aiApi.generateResponse(sender, subject, body, tone);

            if (res.success) {
                setGeneratedResponse(res.response);
                setConfidence(res.confidence);
                toast({
                    title: "Готово",
                    description: `Ответ сгенерирован (${(res.confidence * 100).toFixed(0)}% уверенности)`
                });
            } else {
                toast({ title: "Ошибка", description: "Не удалось сгенерировать ответ" });
            }
        } catch (error: any) {
            toast({
                title: "Ошибка",
                description: error.message || "Ошибка соединения"
            });
        } finally {
            setLoading(false);
        }
    };

    const handleCopy = () => {
        navigator.clipboard.writeText(generatedResponse);
        toast({ title: "Скопировано" });
    };

    return (
        <div className="min-h-screen bg-[#0A0A0A] text-white p-8">
            <div className="max-w-4xl mx-auto space-y-8">

                {/* Header */}
                <div>
                    <h1 className="text-[32px] font-semibold mb-2">Автоответы</h1>
                    <div className="h-[1px] bg-[#1A1A1A]" />
                </div>


                {/* Input Form */}
                <div className="space-y-6">
                    {/* Two columns */}
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm text-[#808080] mb-2">От кого</label>
                            <Input
                                placeholder="client@example.com"
                                value={sender}
                                onChange={(e) => setSender(e.target.value)}
                                className="bg-[#1A1A1A] border-[#2A2A2A] text-white placeholder:text-[#404040] rounded-[4px] h-12 px-4 focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:border-white transition-colors"
                            />
                        </div>
                        <div>
                            <label className="block text-sm text-[#808080] mb-2">Тема</label>
                            <Input
                                placeholder="Запрос коммерческого предложения"
                                value={subject}
                                onChange={(e) => setSubject(e.target.value)}
                                className="bg-[#1A1A1A] border-[#2A2A2A] text-white placeholder:text-[#404040] rounded-[4px] h-12 px-4 focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:border-white transition-colors"
                            />
                        </div>
                    </div>

                    {/* Body */}
                    <div>
                        <label className="block text-sm text-[#808080] mb-2">Текст письма</label>
                        <Textarea
                            placeholder="Скопируйте сюда текст полученного письма..."
                            className="bg-[#1A1A1A] border-[#2A2A2A] text-white placeholder:text-[#404040] rounded-[4px] min-h-[200px] p-4 resize-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:border-white transition-colors"
                            value={body}
                            onChange={(e) => setBody(e.target.value)}
                        />
                    </div>

                    {/* Tone Dropdown */}
                    <div>
                        <label className="block text-sm text-[#808080] mb-2">Тон ответа</label>
                        <select
                            value={tone}
                            onChange={(e) => setTone(e.target.value)}
                            className="w-full bg-[#1A1A1A] border border-[#2A2A2A] text-white rounded-[4px] h-12 px-4 focus:outline-none focus:border-white transition-colors appearance-none cursor-pointer"
                            style={{
                                backgroundImage: `url("data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1.5L6 6.5L11 1.5' stroke='white' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E")`,
                                backgroundRepeat: 'no-repeat',
                                backgroundPosition: 'right 16px center',
                            }}
                        >
                            {TONES.map((t) => (
                                <option key={t.id} value={t.id} className="bg-[#1A1A1A]">
                                    {t.label}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Generate Button */}
                    <Button
                        onClick={handleGenerate}
                        disabled={loading || !body}
                        className="w-full bg-white text-black hover:bg-[#E0E0E0] rounded-[4px] h-12 font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? (
                            <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                AI думает...
                            </>
                        ) : (
                            <>
                                <Sparkles className="mr-2 h-4 w-4" />
                                Сгенерировать
                            </>
                        )}
                    </Button>
                </div>

                {/* Divider */}
                <div className="h-[1px] bg-[#1A1A1A]" />

                {/* Response */}
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <label className="block text-sm text-[#808080]">Ответ</label>
                        {generatedResponse && confidence > 0 && (
                            <span className="text-xs text-[#808080]">
                                Уверенность: {(confidence * 100).toFixed(0)}%
                            </span>
                        )}
                    </div>
                    {generatedResponse ? (
                        <div className="space-y-4">
                            <Textarea
                                className="bg-[#0F0F0F] border-[#2A2A2A] text-white rounded-[4px] min-h-[200px] p-5 resize-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:border-white transition-colors"
                                value={generatedResponse}
                                onChange={(e) => setGeneratedResponse(e.target.value)}
                            />
                            <div className="flex gap-3">
                                <Button
                                    onClick={() => {
                                        setGeneratedResponse("");
                                        setConfidence(0);
                                    }}
                                    variant="outline"
                                    className="bg-transparent border-[#2A2A2A] text-white hover:bg-[#1A1A1A] hover:text-white rounded-[4px] h-10"
                                >
                                    Очистить
                                </Button>
                                <Button
                                    onClick={handleCopy}
                                    className="bg-white text-black hover:bg-[#E0E0E0] rounded-[4px] h-10"
                                >
                                    <Copy className="mr-2 h-4 w-4" />
                                    Копировать
                                </Button>
                            </div>
                        </div>
                    ) : (
                        <div className="bg-[#0F0F0F] border border-[#2A2A2A] rounded-[4px] min-h-[200px] flex items-center justify-center">
                            <p className="text-[#404040] text-sm">
                                {aiAvailable
                                    ? "Ответ появится здесь после генерации"
                                    : "Настройте Google Gemini API в настройках"}
                            </p>
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
}
