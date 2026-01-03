"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { Sparkles, Copy, Loader2, CheckCircle2, Mail, Zap } from "lucide-react";
import { api } from "@/lib/api";

const TONES = [
    { id: 'professional', label: 'Профессиональный', icon: '👔', color: 'from-blue-500 to-cyan-500' },
    { id: 'friendly', label: 'Дружелюбный', icon: '👋', color: 'from-green-500 to-emerald-500' },
    { id: 'formal', label: 'Официальный', icon: '⚖️', color: 'from-slate-500 to-gray-600' },
    { id: 'brief', label: 'Краткий', icon: '⚡', color: 'from-yellow-500 to-amber-500' },
    { id: 'detailed', label: 'Подробный', icon: '📝', color: 'from-purple-500 to-pink-500' },
    { id: 'creative', label: 'Креативный', icon: '🚀', color: 'from-orange-500 to-red-500' },
];

export default function ManualEmailGeneratorPage() {
    const { toast } = useToast();

    // Form State
    const [sender, setSender] = useState("");
    const [subject, setSubject] = useState("");
    const [body, setBody] = useState("");
    const [tone, setTone] = useState("professional");

    // Result State
    const [generatedResponse, setGeneratedResponse] = useState("");
    const [loading, setLoading] = useState(false);
    const [showTypewriter, setShowTypewriter] = useState(false);

    // Checks
    useEffect(() => {
        api.checkVersion().then(res => {
            if (res.version !== "1.0.0") {
                toast({
                    title: "Обновление доступно",
                    description: `Backend v${res.version} отличается от клиента. Обновите страницу.`,
                    variant: "destructive"
                });
            }
        }).catch(() => {
            toast({
                title: "Нет связи с сервером",
                description: "Backend недоступен.",
                variant: "destructive"
            });
        });
    }, []);

    const handleGenerate = async () => {
        if (!body) {
            toast({ title: "Ошибка", description: "Вставьте текст письма", variant: "destructive" });
            return;
        }

        setLoading(true);
        setShowTypewriter(false);
        try {
            const res = await api.generateResponse(sender, subject, body, tone);
            if (res.status === 'success') {
                setGeneratedResponse(res.generated_reply);
                setShowTypewriter(true);
                toast({ title: "Успешно", description: "Ответ сгенерирован!" });
            } else {
                toast({ title: "Ошибка", description: "Не удалось сгенерировать ответ", variant: "destructive" });
            }
        } catch (error: any) {
            console.error(error);
            toast({ title: "Ошибка", description: error.message || "Ошибка соединения", variant: "destructive" });
        } finally {
            setLoading(false);
        }
    };

    const handleCopy = () => {
        navigator.clipboard.writeText(generatedResponse);
        toast({ title: "Скопировано", description: "Текст ответа скопирован в буфер обмена" });
    };

    return (
        <div className="h-full flex flex-col md:flex-row gap-0 -m-6">

            {/* INPUT COLUMN - 60% */}
            <div className="flex-[6] flex flex-col gap-6 p-8 bg-gradient-to-br from-charcoal via-obsidian to-charcoal stagger-in">
                {/* Hero Header */}
                <div className="relative">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20">
                            <Mail className="h-6 w-6 text-amber-400" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold gradient-text">Генератор ответов</h1>
                            <p className="text-sm text-muted-foreground font-mono">AI-powered email responses</p>
                        </div>
                    </div>
                    {/* Diagonal accent */}
                    <div className="absolute -bottom-2 left-0 w-32 h-[2px] bg-gradient-to-r from-amber-500 to-transparent"
                        style={{ transform: 'skewY(-8deg)' }} />
                </div>

                {/* Input Form */}
                <div className="flex-1 flex flex-col gap-4 metric-card stagger-in" style={{ animationDelay: '100ms' }}>
                    <div className="space-y-4">
                        <div>
                            <label className="text-sm font-semibold mb-2 block text-amber-400/90 uppercase tracking-wider font-mono text-xs">
                                От кого
                            </label>
                            <Input
                                placeholder="client@example.com"
                                value={sender}
                                onChange={(e) => setSender(e.target.value)}
                                className="bg-obsidian/50 border-border/50 focus:border-amber-500/50 transition-all"
                            />
                        </div>

                        <div>
                            <label className="text-sm font-semibold mb-2 block text-amber-400/90 uppercase tracking-wider font-mono text-xs">
                                Тема письма
                            </label>
                            <Input
                                placeholder="Запрос коммерческого предложения..."
                                value={subject}
                                onChange={(e) => setSubject(e.target.value)}
                                className="bg-obsidian/50 border-border/50 focus:border-amber-500/50 transition-all"
                            />
                        </div>

                        <div className="flex-1 flex flex-col">
                            <label className="text-sm font-semibold mb-2 block text-amber-400/90 uppercase tracking-wider font-mono text-xs">
                                Текст письма *
                            </label>
                            <Textarea
                                placeholder="Скопируйте сюда текст полученного письма..."
                                className="flex-1 min-h-[200px] resize-none bg-obsidian/50 border-border/50 focus:border-amber-500/50 transition-all font-mono text-sm"
                                value={body}
                                onChange={(e) => setBody(e.target.value)}
                            />
                        </div>
                    </div>
                </div>

                {/* Tone Selector - Large Editorial Buttons */}
                <div className="stagger-in" style={{ animationDelay: '200ms' }}>
                    <label className="text-sm font-semibold mb-3 block text-amber-400/90 uppercase tracking-wider font-mono text-xs">
                        Выберите тон общения
                    </label>
                    <div className="grid grid-cols-3 gap-3">
                        {TONES.map((t) => (
                            <button
                                key={t.id}
                                onClick={() => setTone(t.id)}
                                className={`relative p-4 rounded-lg border-2 transition-all duration-300 group ${tone === t.id
                                        ? 'border-amber-500 bg-amber-500/10'
                                        : 'border-border/30 bg-slate/20 hover:border-amber-500/50'
                                    }`}
                            >
                                <div className="text-2xl mb-1">{t.icon}</div>
                                <div className="text-sm font-semibold">{t.label}</div>
                                {tone === t.id && (
                                    <div className="absolute inset-0 rounded-lg blur-md bg-amber-500/20 -z-10" />
                                )}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Generate Button */}
                <Button
                    onClick={handleGenerate}
                    disabled={loading || !body}
                    className="glow-button w-full h-14 text-lg font-bold stagger-in"
                    style={{ animationDelay: '300ms' }}
                >
                    {loading ? (
                        <>
                            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                            Генерируем...
                        </>
                    ) : (
                        <>
                            <Sparkles className="mr-2 h-5 w-5" />
                            Сгенерировать ответ
                        </>
                    )}
                </Button>
            </div>

            {/* DIAGONAL DIVIDER */}
            <div className="relative w-[2px] bg-gradient-to-b from-transparent via-amber-500 to-transparent diagonal-divider" />

            {/* OUTPUT COLUMN - 40% */}
            <div className="flex-[4] flex flex-col p-8 bg-gradient-to-br from-slate via-charcoal to-obsidian stagger-in" style={{ animationDelay: '150ms' }}>
                <div className="flex justify-between items-center mb-6">
                    <div className="flex items-center gap-3">
                        <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                            <Zap className="h-6 w-6 text-emerald-400" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold text-emerald-400">Готовый ответ</h2>
                            <p className="text-xs text-muted-foreground font-mono">AI-generated response</p>
                        </div>
                    </div>
                    {generatedResponse && (
                        <Button variant="outline" size="sm" onClick={handleCopy} className="border-emerald-500/30 hover:bg-emerald-500/10">
                            <Copy className="mr-2 h-4 w-4" /> Копировать
                        </Button>
                    )}
                </div>

                {generatedResponse ? (
                    <div className="flex-1 flex flex-col metric-card">
                        <Textarea
                            className={`flex-1 font-mono text-sm leading-relaxed p-4 bg-obsidian/30 resize-none focus-visible:ring-0 border-0 ${showTypewriter ? 'typewriter' : ''
                                }`}
                            value={generatedResponse}
                            onChange={(e) => setGeneratedResponse(e.target.value)}
                        />

                        <div className="mt-4 flex gap-2 justify-end pt-4 border-t border-border/30">
                            <Button variant="ghost" onClick={() => setGeneratedResponse("")} className="hover:bg-slate/50">
                                Очистить
                            </Button>
                            <Button className="bg-emerald-600 hover:bg-emerald-700" onClick={handleCopy}>
                                <CheckCircle2 className="mr-2 h-4 w-4" /> Скопировать
                            </Button>
                        </div>
                    </div>
                ) : (
                    <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground p-8 border-2 border-dashed border-border/30 rounded-lg bg-obsidian/20">
                        <div className="w-20 h-20 rounded-full bg-slate/30 flex items-center justify-center mb-6 glow-pulse">
                            <Sparkles className="h-10 w-10 text-amber-400/50" />
                        </div>
                        <h3 className="font-bold text-xl mb-2 text-foreground">Ожидание генерации</h3>
                        <p className="text-center text-sm max-w-[280px] font-mono">
                            Заполните форму слева и нажмите "Сгенерировать", чтобы получить AI-ответ
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
