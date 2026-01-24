"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Loader2, Send, Database, Globe, Brain, Sparkles, ArrowRight } from "lucide-react";
import GenerativeMessage, { MessageContent } from "./GenerativeMessage";
import { cn } from "@/lib/utils";

interface ChatMessage {
    id: string;
    role: 'user' | 'assistant';
    content: MessageContent;
    timestamp: Date;
}

const SUGGESTIONS = [
    "Проанализируй продажи за Q4",
    "Как увеличить выручку на 15%?",
    "Сравни показатели с прошлым годом",
    "Найди похожие кейсы на рынке"
];

export default function ChatInterface() {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState("");
    const [isThinking, setIsThinking] = useState(false);
    const [thinkingStep, setThinkingStep] = useState<string>("");

    const scrollRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    // Auto-scroll to bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [messages, isThinking, thinkingStep]);

    // Use empty string for client-side to leverage Next.js rewrites
    const API_BASE = '';

    const handleSend = async (text: string) => {
        if (!text.trim()) return;

        const userMsg: ChatMessage = {
            id: Date.now().toString(),
            role: 'user',
            content: { text: text },
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMsg]);
        setInput("");
        setIsThinking(true);
        setThinkingStep("Анализирую запрос...");

        try {
            // Start thinking simulation interval
            const thinkingInterval = setInterval(() => {
                setThinkingStep(prev => {
                    if (prev === "Анализирую запрос...") return "Определяю намерения...";
                    if (prev === "Определяю намерения...") return "Проверяю доступные источники...";
                    if (prev === "Проверяю доступные источники...") return "Ищу информацию в базе данных...";
                    if (prev === "Ищу информацию в базе данных...") return "Выполняю внешний поиск...";
                    if (prev === "Выполняю внешний поиск...") return "Синтезирую ответ...";
                    return "Анализирую запрос...";
                });
            }, 2000);

            // Real API Call
            const response = await fetch(`${API_BASE}/api/ai-chat/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: text,
                    session_id: 'user-session-1', // In real app, manage session
                    stream: false
                })
            });

            clearInterval(thinkingInterval);

            if (!response.ok) {
                throw new Error("Failed to fetch response");
            }

            const data = await response.json();

            // Construct content based on response
            const responseContent: MessageContent = {
                text: data.response,
                // Add sources if available to the text or separate
                // Parsing sources to see if we need charts (Future improvement: backend sends chart data)
            };

            // Basic chart detection mock based on text content (backend should ideally send this)
            // For now, we keep the simulated chart if the backend text mentions it, 
            // OR we just remove the chart mock for now to be "real". 
            // The user asked for "Enable" so let's stick to text for now unless we see structured data.
            // But to keep the "WOW" factor, let's try to parse if the backend sends structured data.
            // The backend currently only sends text strings. 
            // We can re-add the chart if the text contains specific keywords? 
            // Let's leave charts out for the *real* data to avoid lying, 
            // UNLESS the user prompt explicitly asked for charts. The previous code had mock charts.
            // I will leave chart undefined for now to be safe.

            const aiMsg: ChatMessage = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: responseContent,
                timestamp: new Date()
            };

            setMessages(prev => [...prev, aiMsg]);

        } catch (error) {
            console.error(error);
            // Error message
            const errorMsg: ChatMessage = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: { text: "Извините, произошла ошибка при обработке запроса. Проверьте соединение или API ключи." },
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsThinking(false);
            setThinkingStep("");
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-140px)] bg-[#202020] rounded-xl overflow-hidden border border-[#333333/50]">

            {/* Messages Area */}
            <ScrollArea className="flex-1 p-4 sm:p-6 space-y-6">
                {messages.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-center opacity-60 mt-20">
                        <div className="w-20 h-20 rounded-full bg-[#262626] flex items-center justify-center mb-6 animate-pulse">
                            <Brain className="w-10 h-10 text-rose-500" />
                        </div>
                        <h3 className="text-xl font-medium text-white mb-2">AI Command Center</h3>
                        <p className="text-[#808080] max-w-md mb-8">
                            Задавайте сложные вопросы, просите аналитику или сравнение рынка. Я подключен к вашей базе данных и интернету.
                        </p>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-2xl px-4">
                            {SUGGESTIONS.map((s, i) => (
                                <button
                                    key={i}
                                    onClick={() => handleSend(s)}
                                    className="p-4 rounded-xl border border-[#333333] bg-[#262626]/50 hover:bg-[#262626] hover:border-rose-500/50 text-[#A0A0A0] hover:text-white text-sm text-left transition-all duration-300"
                                >
                                    {s}
                                </button>
                            ))}
                        </div>
                    </div>
                ) : (
                    <div className="space-y-6 pb-4">
                        {messages.map((msg) => (
                            <div key={msg.id} className="space-y-2">
                                <GenerativeMessage content={msg.content} role={msg.role} />

                                {/* Context Actions for AI messages */}
                                {msg.role === 'assistant' && (
                                    <div className="flex flex-wrap gap-2 ml-4 animate-in fade-in slide-in-from-top-2 duration-500">
                                        <Button variant="outline" size="sm" className="bg-transparent border-[#404040] text-[#A0A0A0] hover:text-white hover:bg-[#333333] h-8 text-xs rounded-full">
                                            <Sparkles className="w-3 h-3 mr-2" />
                                            Детализировать
                                        </Button>
                                        <Button variant="outline" size="sm" className="bg-transparent border-[#404040] text-[#A0A0A0] hover:text-white hover:bg-[#333333] h-8 text-xs rounded-full">
                                            <Database className="w-3 h-3 mr-2" />
                                            Скачать отчет
                                        </Button>
                                    </div>
                                )}
                            </div>
                        ))}

                        {/* Thinking Indicator */}
                        {isThinking && (
                            <div className="flex flex-col gap-2 ml-2 max-w-[80%]">
                                <div className="flex items-center gap-3 text-sm text-[#808080] bg-[#262626] p-3 rounded-lg w-fit animate-in fade-in duration-300">
                                    <Loader2 className="w-4 h-4 animate-spin text-rose-500" />
                                    <span className="typing-cursor">{thinkingStep}</span>
                                </div>
                                {/* Progress step indicators */}
                                <div className="flex gap-1 ml-1">
                                    <div className={cn("h-1 rounded-full transition-all duration-500", thinkingStep.includes("Анализирую") ? "w-4 bg-rose-500" : "w-1 bg-[#404040]")} />
                                    <div className={cn("h-1 rounded-full transition-all duration-500", thinkingStep.includes("CRM") ? "w-4 bg-rose-500" : "w-1 bg-[#404040]")} />
                                    <div className={cn("h-1 rounded-full transition-all duration-500", thinkingStep.includes("внешние") ? "w-4 bg-rose-500" : "w-1 bg-[#404040]")} />
                                </div>
                            </div>
                        )}
                    </div>
                )}
                <div ref={scrollRef} />
            </ScrollArea>

            {/* Input Area */}
            <div className="p-4 bg-[#262626] border-t border-[#333333]">
                <form
                    onSubmit={(e) => { e.preventDefault(); handleSend(input); }}
                    className="relative flex items-center gap-3 max-w-4xl mx-auto"
                >
                    <div className="relative flex-1 group">
                        <Input
                            ref={inputRef}
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Спросите что-нибудь о ваших продажах..."
                            className="w-full bg-[#202020] border-[#404040] text-gray-100 pl-4 pr-12 h-12 rounded-xl focus:ring-1 focus:ring-rose-500/50 transition-all placeholder:text-[#606060]"
                        />
                        <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                            <Button
                                type="submit"
                                disabled={!input.trim() || isThinking}
                                size="sm"
                                className="h-8 w-8 p-0 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white shadow shadow-cyan-600/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <ArrowRight className="w-4 h-4" />
                            </Button>
                        </div>
                    </div>
                </form>
                <div className="text-center mt-2">
                    <p className="text-[10px] text-[#505050] flex items-center justify-center gap-1.5">
                        <Globe className="w-3 h-3" />
                        AI имеет доступ к интернету и вашей базе данных
                    </p>
                </div>
            </div>
        </div>
    );
}
