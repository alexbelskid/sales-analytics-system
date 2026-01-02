"use client";

import { useEffect, useState, useRef } from "react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { useToast } from "@/hooks/use-toast";
import {
    Inbox, Send, Archive, Trash2, Search, RefreshCw, MoreVertical,
    Paperclip, User, Star, Clock, AlertCircle, FileText, Settings, Sparkles, Loader2, Mail, Undo
} from "lucide-react";
import Link from "next/link";
import { formatDistanceToNow } from "date-fns";
import { ru } from "date-fns/locale";

export default function EmailsPage() {
    const [emails, setEmails] = useState<any[]>([]);
    const [selectedEmail, setSelectedEmail] = useState<any>(null);
    const { toast } = useToast();
    const [loading, setLoading] = useState(true);
    const [syncing, setSyncing] = useState(false);
    const [filter, setFilter] = useState("new"); // new, sent, archived
    const [category, setCategory] = useState<string | undefined>(undefined);

    // Response state
    const [draftText, setDraftText] = useState("");
    const [selectedToneId, setSelectedToneId] = useState<string>("default");
    const [tones, setTones] = useState<any[]>([]);
    const [templates, setTemplates] = useState<any[]>([]);
    const [sending, setSending] = useState(false);

    // Settings check
    const [hasSettings, setHasSettings] = useState(true);

    useEffect(() => {
        checkSettingsAndLoad();
    }, [filter, category]);

    useEffect(() => {
        loadTonesAndTemplates();
    }, []);

    const checkSettingsAndLoad = async () => {
        try {
            const settings = await api.getEmailSettings();
            if (!settings) {
                setHasSettings(false);
                setLoading(false);
                return;
            }
            loadEmails();
        } catch (error) {
            console.error(error);
            setLoading(false);
        }
    };

    const loadEmails = async () => {
        setLoading(true);
        try {
            const data = await api.getInbox(filter, category);
            setEmails(data);
        } catch (error) {
            console.error("Failed to load inbox", error);
        } finally {
            setLoading(false);
        }
    };

    const loadTonesAndTemplates = async () => {
        try {
            const [tonesData, templatesData] = await Promise.all([
                api.getToneSettings(),
                api.getTemplates()
            ]);
            setTones(tonesData || []);
            setTemplates(templatesData || []);
        } catch (error) {
            console.error("Failed to load aux data", error);
        }
    };

    const handleSync = async () => {
        setSyncing(true);
        try {
            const res = await api.syncEmails();

            if (res.status === 'timeout') {
                toast({
                    title: "Синхронизация заняла слишком много времени",
                    description: "Попробуйте снова через несколько секунд",
                    variant: "destructive",
                });
            } else if (res.status === 'error') {
                toast({
                    title: "Ошибка синхронизации",
                    description: res.message || "Не удалось синхронизировать почту",
                    variant: "destructive",
                });
            } else if (res.new_emails_count > 0) {
                toast({
                    title: "✅ Синхронизация завершена",
                    description: `Загружено новых писем: ${res.new_emails_count}`,
                });
                loadEmails();
            } else {
                toast({
                    title: "Синхронизация завершена",
                    description: "Нет новых писем",
                });
            }
        } catch (error: any) {
            console.error("Sync failed", error);

            // Handle AbortController timeout
            if (error.name === 'AbortError') {
                toast({
                    title: "Превышено время ожидания",
                    description: "Сервер не отвечает. Проверьте подключение к интернету.",
                    variant: "destructive",
                });
            } else {
                toast({
                    title: "Ошибка синхронизации",
                    description: error.message || "Не удалось подключиться к серверу",
                    variant: "destructive",
                });
            }
        } finally {
            setSyncing(false);
        }
    };

    const handleSelectEmail = async (email: any) => {
        setSelectedEmail(null); // Clear first to show loading state if needed
        // Fetch full details if needed, but for now we have enough in list
        // Wait, list might not have full body? API returns select("*") so it should.
        setSelectedEmail(email);
        setDraftText(""); // specific draft logic later

        // Mark as read? API call needed.
    };

    const handleApplyTemplate = (templateId: string) => {
        const tmpl = templates.find(t => t.id === templateId);
        if (!tmpl) return;

        // Simple placeholder replacement
        let text = tmpl.template_text;
        const clientName = selectedEmail?.sender_name || selectedEmail?.sender_email.split("@")[0] || "Клиент";
        text = text.replace("{client_name}", clientName);
        text = text.replace("{sender_name}", "Менеджер"); // Get from user profile later

        setDraftText(text);
    };

    const handleSendReply = async () => {
        if (!draftText) return;
        setSending(true);
        try {
            await api.sendReply(selectedEmail.id, {
                draft_text: draftText,
                tone_id: selectedToneId === "default" ? undefined : selectedToneId
            });
            // Update local state
            setEmails(emails.map(e => e.id === selectedEmail.id ? { ...e, status: "replied" } : e));
            setSelectedEmail({ ...selectedEmail, status: "replied" });
            toast({
                title: "Успешно",
                description: "Письмо отправлено",
            });
        } catch (error) {
            toast({
                title: "Ошибка",
                description: "Не удалось отправить письмо",
                variant: "destructive",
            });
        } finally {
            setSending(false);
        }
    };

    // Render Logic
    if (!hasSettings) {
        return (
            <div className="flex flex-col items-center justify-center h-[80vh] space-y-4">
                <Mail className="h-16 w-16 text-muted-foreground" />
                <h2 className="text-2xl font-bold">Почта не подключена</h2>
                <p className="text-muted-foreground">Подключите ваш почтовый ящик, чтобы управлять письмами.</p>
                <Link href="/settings/email">
                    <Button>Перейти к настройкам</Button>
                </Link>
            </div>
        );
    }

    return (
        <div className="flex h-[calc(100vh-4rem)] flex-col md:flex-row gap-4 p-4">
            {/* Sidebar / Email List */}
            <div className={`w-full md:w-1/3 lg:w-1/4 flex flex-col gap-4 ${selectedEmail ? "hidden md:flex" : "flex"}`}>
                <div className="flex items-center justify-between">
                    <h2 className="text-xl font-bold">Входящие</h2>
                    <Button variant="ghost" size="icon" onClick={handleSync} disabled={syncing}>
                        <RefreshCw className={`h-4 w-4 ${syncing ? "animate-spin" : ""}`} />
                    </Button>
                </div>

                <div className="flex gap-2">
                    <Input placeholder="Поиск..." className="flex-1" />
                </div>

                <Tabs defaultValue="new" value={filter} onValueChange={setFilter} className="w-full">
                    <TabsList className="grid w-full grid-cols-3">
                        <TabsTrigger value="new">Новые</TabsTrigger>
                        <TabsTrigger value="sent">Отправленные</TabsTrigger>
                        <TabsTrigger value="archived">Архив</TabsTrigger>
                    </TabsList>
                </Tabs>

                <ScrollArea className="flex-1 border rounded-md">
                    <div className="flex flex-col gap-1 p-2">
                        {loading && <div className="text-center p-4"><Loader2 className="animate-spin h-6 w-6 mx-auto" /></div>}
                        {!loading && emails.length === 0 && (
                            <div className="text-center p-8 text-muted-foreground">
                                <Mail className="h-12 w-12 mx-auto mb-3 opacity-20" />
                                <p className="font-medium">Нет новых писем</p>
                                <p className="text-xs mt-1">Нажмите кнопку обновления для синхронизации</p>
                            </div>
                        )}

                        {emails.map((email) => (
                            <div
                                key={email.id}
                                className={`flex flex-col gap-1 p-3 rounded-lg border cursor-pointer hover:bg-accent transition-colors ${selectedEmail?.id === email.id ? "bg-accent border-primary" : "bg-card"}`}
                                onClick={() => handleSelectEmail(email)}
                            >
                                <div className="flex justify-between items-start">
                                    <div className="font-semibold truncate max-w-[70%]">{email.sender_name || email.sender_email}</div>
                                    <span className="text-xs text-muted-foreground whitespace-nowrap">
                                        {formatDistanceToNow(new Date(email.received_at), { addSuffix: true, locale: ru })}
                                    </span>
                                </div>
                                <div className="text-sm font-medium truncate">{email.subject || "(Без темы)"}</div>
                                <div className="text-xs text-muted-foreground line-clamp-2">
                                    {email.body_text?.substring(0, 100) || "Текст письма недоступен..."}
                                </div>
                                <div className="flex gap-2 mt-1">
                                    {email.category && <Badge variant="secondary" className="text-[10px] h-5">{email.category}</Badge>}
                                    {email.priority === 'urgent' && <Badge variant="destructive" className="text-[10px] h-5">Срочно</Badge>}
                                </div>
                            </div>
                        ))}
                    </div>
                </ScrollArea>
            </div>

            {/* Main Area / Email Detail */}
            <div className={`flex-1 flex flex-col border rounded-md bg-card ${!selectedEmail ? "hidden md:flex items-center justify-center text-muted-foreground" : "flex"}`}>
                {!selectedEmail ? (
                    <div className="text-center space-y-2">
                        <Mail className="h-12 w-12 mx-auto opacity-20" />
                        <p>Выберите письмо для просмотра</p>
                    </div>
                ) : (
                    <>
                        {/* Header */}
                        <div className="p-4 border-b flex justify-between items-start">
                            <div className="flex gap-3">
                                <Button variant="ghost" size="icon" className="md:hidden" onClick={() => setSelectedEmail(null)}>
                                    <Undo className="h-4 w-4" />
                                </Button>
                                <Avatar>
                                    <AvatarFallback>{selectedEmail.sender_name?.[0] || selectedEmail.sender_email[0]}</AvatarFallback>
                                </Avatar>
                                <div>
                                    <h3 className="font-bold text-lg">{selectedEmail.subject}</h3>
                                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                        <span>{selectedEmail.sender_name} &lt;{selectedEmail.sender_email}&gt;</span>
                                        <span>•</span>
                                        <span>{new Date(selectedEmail.received_at).toLocaleString("ru")}</span>
                                    </div>
                                </div>
                            </div>
                            <div className="flex gap-1">
                                <TooltipProvider>
                                    <Tooltip>
                                        <TooltipTrigger asChild><Button variant="ghost" size="icon"><Archive className="h-4 w-4" /></Button></TooltipTrigger>
                                        <TooltipContent>В архив</TooltipContent>
                                    </Tooltip>
                                </TooltipProvider>
                                <Button variant="ghost" size="icon"><Trash2 className="h-4 w-4 text-destructive" /></Button>
                            </div>
                        </div>

                        {/* Body */}
                        <ScrollArea className="flex-1 p-6">
                            <div
                                className="prose prose-sm max-w-none dark:prose-invert"
                                dangerouslySetInnerHTML={{ __html: selectedEmail.body_html || selectedEmail.body_text?.replace(/\n/g, "<br/>") }}
                            />
                        </ScrollArea>

                        {/* Response Area */}
                        <div className="border-t p-4 bg-background">
                            <div className="flex justify-between items-center mb-2">
                                <div className="flex gap-2 items-center">
                                    <Select value={selectedToneId} onValueChange={setSelectedToneId}>
                                        <SelectTrigger className="w-[180px] h-8 text-xs">
                                            <SelectValue placeholder="Тон ответа" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="default">Обычный</SelectItem>
                                            {tones.map(t => <SelectItem key={t.id} value={t.id}>{t.display_name}</SelectItem>)}
                                        </SelectContent>
                                    </Select>

                                    <Select onValueChange={handleApplyTemplate}>
                                        <SelectTrigger className="w-[180px] h-8 text-xs">
                                            <SelectValue placeholder="Вставить шаблон" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {templates.map(t => <SelectItem key={t.id} value={t.id}>{t.name}</SelectItem>)}
                                        </SelectContent>
                                    </Select>
                                </div>

                                <Button variant="ghost" size="sm" className="h-8 text-xs" disabled>
                                    <Sparkles className="mr-2 h-3 w-3" /> AI Генерация (скоро)
                                </Button>
                            </div>

                            <Textarea
                                placeholder="Напишите ответ..."
                                className="min-h-[150px] mb-2"
                                value={draftText}
                                onChange={(e) => setDraftText(e.target.value)}
                            />

                            <div className="flex justify-between items-center">
                                <Button variant="ghost" size="sm">
                                    <Link href="/settings/email" className="flex items-center text-muted-foreground text-xs">
                                        <Settings className="mr-1 h-3 w-3" /> Настройки почты
                                    </Link>
                                </Button>
                                <div className="flex gap-2">
                                    <Button variant="outline" size="sm">Черновик</Button>
                                    <Button size="sm" onClick={handleSendReply} disabled={sending || !draftText}>
                                        {sending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Send className="mr-2 h-4 w-4" />}
                                        Отправить
                                    </Button>
                                </div>
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}
