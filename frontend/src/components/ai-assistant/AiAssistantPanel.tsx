"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Loader2, Send, Database, Globe, Brain, Sparkles, ArrowRight, CheckCircle2, AlertCircle } from "lucide-react";
import GenerativeMessage, { MessageContent } from "./GenerativeMessage";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import GlassInput from "@/components/GlassInput";
import LiquidButton from "@/components/LiquidButton";

interface ChatMessage {
    id: string;
    role: 'user' | 'assistant';
    content: MessageContent;
    timestamp: Date;
    sources?: string[]; // URLs or Source names
    verified?: boolean;
}

const SUGGESTIONS = [
    "Проанализируй продажи за Q4",
    "Сравни показатели с прошлым годом",
    "Найди похожие кейсы на рынке"
];

export default function AiAssistantPanel() {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState("");
    const [isThinking, setIsThinking] = useState(false);
    const [thinkingStep, setThinkingStep] = useState<string>("");
    const [sessionId] = useState(() => `session_${Date.now()}`);
    const [hasStarted, setHasStarted] = useState(false);

    const scrollRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [messages, isThinking, thinkingStep]);

    const handleSend = async (text: string) => {
        if (!text.trim()) return;

        if (!hasStarted) {
            setHasStarted(true);
        }

        const userMsg: ChatMessage = {
            id: Date.now().toString(),
            role: 'user',
            content: { text: text },
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMsg]);
        setInput("");
        setIsThinking(true);

        // Call real API instead of mock
        await processRealQuery(text);
    };

    const processRealQuery = async (query: string) => {
        try {
            // Step 1: Analyze Intent
            setThinkingStep("Анализирую запрос...");
            await new Promise(r => setTimeout(r, 300));

            // Step 2: Call real API
            setThinkingStep("Запрашиваю данные из базы...");

            const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://athletic-alignment-production-db41.up.railway.app';

            const response = await fetch(`${API_BASE}/api/ai-chat/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: query,
                    session_id: sessionId
                })
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            const data = await response.json();

            // Step 3: Process response
            setThinkingStep("Формирую ответ...");
            await new Promise(r => setTimeout(r, 300));

            const aiMsg: ChatMessage = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: {
                    text: data.response || "Не удалось получить ответ"
                },
                timestamp: new Date(),
                sources: data.sources?.map((s: any) => s.type) || []
            };

            setMessages(prev => [...prev, aiMsg]);

        } catch (error) {
            console.error('AI query error:', error);

            const errorMsg: ChatMessage = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: {
                    text: "⚠️ Извините, произошла ошибка при обработке запроса. Проверьте подключение к серверу."
                },
                timestamp: new Date()
            };

            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsThinking(false);
            setThinkingStep("");
        }
    };

    // --- RENDER ---

    if (!hasStarted) {
        // --- INITIAL STATE: JUST THE INPUT ---
        return (
            <div className="h-[600px] flex flex-col items-center justify-center animate-in fade-in zoom-in duration-500">
                <div className="w-full max-w-2xl px-6">
                    <form
                        onSubmit={(e) => { e.preventDefault(); handleSend(input); }}
                        className="relative w-full"
                    >
                        <div className="relative group">
                            <GlassInput
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder="Спросите AI..."
                                className="pr-14 py-6 text-lg rounded-full bg-black/40 border-white/10 focus:border-rose-500/50 transition-all shadow-2xl shadow-black/50 backdrop-blur-xl"
                                autoFocus
                            />
                            <LiquidButton
                                type="submit"
                                disabled={!input.trim()}
                                className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 p-0 min-h-0 rounded-full shadow-lg hover:scale-105 disabled:scale-95 disabled:opacity-0 transition-all duration-300"
                                icon={ArrowRight}
                            >
                            </LiquidButton>
                        </div>
                        <p className="text-center mt-4 text-[#606060] text-sm font-light">
                            Я умею анализировать данные, строить отчеты и искать факты.
                        </p>
                    </form>
                </div>
            </div>
        );
    }

    // --- ACTIVE STATE: FULL CHAT ---
    return (
        <div className="glass-panel h-[600px] flex flex-col animate-in fade-in slide-in-from-bottom-10 duration-700 ease-out">

            {/* Header */}
            <div className="border-b border-[#333333] px-4 py-3 flex items-center justify-between bg-black/20">
                <div className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-rose-500" />
                    <span className="text-sm font-medium text-white">AI Assistant</span>
                </div>
                <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-[10px] border-[#404040] text-emerald-500 bg-emerald-500/10 px-2 h-5">
                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5 animate-pulse" />
                        Online
                    </Badge>
                </div>
            </div>

            {/* Messages Area */}
            <ScrollArea className="flex-1 p-4 space-y-6">
                <div className="space-y-6 pb-4">
                    {messages.map((msg) => (
                        <div key={msg.id} className="space-y-2">
                            <GenerativeMessage content={msg.content} role={msg.role} />

                            {/* Assistant Meta Actions */}
                            {msg.role === 'assistant' && (
                                <div className="flex items-center justify-between ml-1 mr-4 animate-in fade-in slide-in-from-top-2 duration-500">
                                    <div className="flex items-center gap-2">
                                        <button className={cn(
                                            "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[10px] font-medium transition-all",
                                            msg.verified
                                                ? "bg-emerald-500/10 text-emerald-500 border border-emerald-500/20"
                                                : "bg-[#262626] text-[#808080] border border-[#333333] hover:text-white hover:border-[#505050]"
                                        )}>
                                            {msg.verified ? (
                                                <>
                                                    <CheckCircle2 className="w-3 h-3" />
                                                    Проверено
                                                </>
                                            ) : (
                                                <>
                                                    <AlertCircle className="w-3 h-3" />
                                                    Verify Fact
                                                </>
                                            )}
                                        </button>

                                        {msg.sources && msg.sources.length > 0 && (
                                            <div className="flex items-center gap-1 px-2 py-1.5 ">
                                                <span className="text-[10px] text-[#606060]">Источник:</span>
                                                <Badge variant="secondary" className="h-5 bg-[#262626] text-[10px] text-[#A0A0A0] hover:bg-[#333333] border-none">
                                                    CRM
                                                </Badge>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}

                    {/* Thinking Indicator */}
                    {isThinking && (
                        <div className="flex flex-col gap-2 ml-1 max-w-[80%]">
                            <div className="flex items-center gap-3 text-xs text-[#808080] bg-[#262626] px-4 py-3 rounded-xl w-fit animate-in fade-in duration-300 shadow-sm border border-[#333333]">
                                <div className="relative">
                                    <Loader2 className="w-3.5 h-3.5 animate-spin text-rose-500" />
                                    <div className="absolute inset-0 bg-rose-500/20 blur-sm rounded-full" />
                                </div>
                                <span className="typing-cursor font-medium tracking-wide">{thinkingStep}</span>
                            </div>
                        </div>
                    )}
                    <div ref={scrollRef} />
                </div>
            </ScrollArea>

            {/* Input Area */}
            <div className="p-3 border-t border-[#333333] bg-black/20">
                <form
                    onSubmit={(e) => { e.preventDefault(); handleSend(input); }}
                    className="relative w-full"
                >
                    <div className="relative">
                        <GlassInput
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Спросите AI..."
                            className="pr-12"
                            autoFocus
                        />
                        <LiquidButton
                            type="submit"
                            disabled={!input.trim() || isThinking}
                            className="absolute right-1.5 top-1/2 -translate-y-1/2 w-8 h-8 p-0 min-h-0 rounded-full shadow-sm hover:scale-110 disabled:scale-95 disabled:opacity-0"
                            icon={ArrowRight}
                        >
                        </LiquidButton>
                    </div>
                </form>
            </div>
        </div>
    );
}
