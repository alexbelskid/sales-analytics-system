"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { Sparkles, Copy, Loader2, Send, CheckCircle2 } from "lucide-react";
import { api } from "@/lib/api";

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

    // Checks
    useEffect(() => {
        api.checkVersion().then(res => {
            if (res.version !== "1.0.0") {
                toast({
                    title: "Обновление доступно",
                    description: `Backend v${res.version} отличается от клиентов. Обновите страницу.`,
                    variant: "destructive"
                });
            }
        }).catch(() => {
            // If health check fails, backend might be down
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
        try {
            const res = await api.generateResponse(sender, subject, body, tone);
            if (res.status === 'success') {
                setGeneratedResponse(res.generated_reply);
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
        <div className="container max-w-4xl mx-auto py-8 px-4 h-full flex flex-col md:flex-row gap-6">

            {/* INPUT COLUMN */}
            <div className="flex-1 flex flex-col gap-4">
                <div className="bg-card border rounded-xl p-6 shadow-sm">
                    <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                        <span className="bg-primary/10 p-2 rounded-lg text-primary">📩</span>
                        Входящее письмо
                    </h2>

                    <div className="space-y-4">
                        <div>
                            <label className="text-sm font-medium mb-1 block text-muted-foreground">От кого (Email или Имя)</label>
                            <Input
                                placeholder="client@example.com"
                                value={sender}
                                onChange={(e) => setSender(e.target.value)}
                            />
                        </div>

                        <div>
                            <label className="text-sm font-medium mb-1 block text-muted-foreground">Тема письма</label>
                            <Input
                                placeholder="Запрос коммерческого предложения..."
                                value={subject}
                                onChange={(e) => setSubject(e.target.value)}
                            />
                        </div>

                        <div>
                            <label className="text-sm font-medium mb-1 block text-muted-foreground">Текст письма *</label>
                            <Textarea
                                placeholder="Скопируйте сюда текст полученного письма..."
                                className="min-h-[200px] resize-y"
                                value={body}
                                onChange={(e) => setBody(e.target.value)}
                            />
                        </div>
                    </div>
                </div>

                <div className="bg-card border rounded-xl p-6 shadow-sm">
                    <h2 className="text-lg font-bold mb-4">Настройки ответа</h2>
                    <div className="flex gap-4 items-end">
                        <div className="flex-1">
                            <label className="text-sm font-medium mb-1 block text-muted-foreground">Тон общения</label>
                            <Select value={tone} onValueChange={setTone}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Выберите тон" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="professional">👔 Профессиональный</SelectItem>
                                    <SelectItem value="friendly">👋 Дружелюбный</SelectItem>
                                    <SelectItem value="formal">⚖️ Официальный</SelectItem>
                                    <SelectItem value="brief">⚡ Краткий</SelectItem>
                                    <SelectItem value="detailed">📝 Подробный</SelectItem>
                                    <SelectItem value="creative">🚀 Креативный</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <Button
                            onClick={handleGenerate}
                            disabled={loading || !body}
                            className="w-1/3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-md transition-all"
                        >
                            {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />}
                            Сгенерировать
                        </Button>
                    </div>
                </div>
            </div>

            {/* OUTPUT COLUMN */}
            <div className="flex-1 flex flex-col h-full min-h-[500px]">
                <div className="bg-card border rounded-xl p-6 shadow-sm h-full flex flex-col relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-green-400 to-emerald-600"></div>

                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-xl font-bold flex items-center gap-2">
                            <span className="bg-green-100 dark:bg-green-900/30 p-2 rounded-lg text-green-600">✨</span>
                            Готовый ответ
                        </h2>
                        {generatedResponse && (
                            <Button variant="outline" size="sm" onClick={handleCopy}>
                                <Copy className="mr-2 h-4 w-4" /> Копировать
                            </Button>
                        )}
                    </div>

                    {generatedResponse ? (
                        <div className="flex-1 flex flex-col">
                            <Textarea
                                className="flex-1 font-mono text-sm leading-relaxed p-4 bg-muted/30 resize-none focus-visible:ring-0 border-0"
                                value={generatedResponse}
                                onChange={(e) => setGeneratedResponse(e.target.value)}
                            />

                            <div className="mt-4 flex gap-2 justify-end">
                                <Button variant="ghost" onClick={() => setGeneratedResponse("")}>Очистить</Button>
                                <Button className="bg-green-600 hover:bg-green-700" onClick={handleCopy}>
                                    <CheckCircle2 className="mr-2 h-4 w-4" /> Скопировать и закрыть
                                </Button>
                            </div>
                        </div>
                    ) : (
                        <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground p-8 border-2 border-dashed rounded-lg bg-muted/10">
                            <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
                                <Sparkles className="h-8 w-8 text-muted-foreground/50" />
                            </div>
                            <h3 className="font-semibold text-lg mb-2">Ответ пока не создан</h3>
                            <p className="text-center text-sm max-w-[250px]">
                                Заполните форму слева и нажмите "Сгенерировать", чтобы получить AI-ответ.
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
