"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, Plus, Trash2, Save, Undo } from "lucide-react";

export default function ToneSettingsPage() {
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [tones, setTones] = useState<any[]>([]);
    const [selectedToneId, setSelectedToneId] = useState<string | null>(null);

    // Form state
    const [formData, setFormData] = useState<any>({
        tone_name: "custom",
        display_name: "Новый тон",
        description: "",
        formality_level: 5,
        friendliness_level: 5,
        detail_level: 5,
        use_emojis: false,
        greeting_style: "formal",
        closing_style: "formal",
        use_you_formal: true,
        custom_instructions: ""
    });

    useEffect(() => {
        loadTones();
    }, []);

    const loadTones = async () => {
        try {
            const data = await api.getToneSettings();
            setTones(data);
            if (data.length > 0 && !selectedToneId) {
                // Select first one or default
                const def = data.find((t: any) => t.is_default) || data[0];
                selectTone(def);
            }
        } catch (error) {
            console.error("Failed to load tones", error);
        } finally {
            setLoading(false);
        }
    };

    const selectTone = (tone: any) => {
        setSelectedToneId(tone.id);
        setFormData(tone);
    };

    const handleCreateNew = () => {
        setSelectedToneId("new");
        setFormData({
            tone_name: "custom_new",
            display_name: "Мой стиль",
            description: "Персональная настройка ответа",
            formality_level: 5,
            friendliness_level: 5,
            detail_level: 5,
            use_emojis: false,
            greeting_style: "formal",
            closing_style: "formal",
            use_you_formal: true,
            custom_instructions: ""
        });
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            if (selectedToneId === "new") {
                const newTone = await api.createToneSetting(formData);
                setTones([...tones, newTone]);
                setSelectedToneId(newTone.id);
            } else if (selectedToneId) {
                const updated = await api.updateToneSetting(selectedToneId, formData);
                setTones(tones.map(t => t.id === selectedToneId ? updated : t));
            }
        } catch (error) {
            alert("Failed to save tone settings");
        } finally {
            setSaving(false);
        }
    };

    const handleDelete = async () => {
        if (!selectedToneId || selectedToneId === "new") return;
        if (!confirm("Вы уверены, что хотите удалить этот пресет?")) return;

        try {
            await api.deleteToneSetting(selectedToneId);
            const remaining = tones.filter(t => t.id !== selectedToneId);
            setTones(remaining);
            if (remaining.length > 0) selectTone(remaining[0]);
            else handleCreateNew();
        } catch (error) {
            alert("Failed to delete tone");
        }
    };

    if (loading) return <div className="flex justify-center p-8"><Loader2 className="h-8 w-8 animate-spin" /></div>;

    return (
        <div className="container mx-auto py-6 max-w-6xl">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Настройка тона ответов</h1>
                    <p className="text-muted-foreground">Управляйте стилем общения AI-ассистента.</p>
                </div>
                <Button onClick={handleCreateNew}>
                    <Plus className="mr-2 h-4 w-4" /> Новый пресет
                </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
                {/* Sidebar List */}
                <div className="md:col-span-3 space-y-2">
                    {tones.map((tone) => (
                        <div
                            key={tone.id}
                            onClick={() => selectTone(tone)}
                            className={`p-3 rounded-lg border cursor-pointer hover:bg-accent transition-colors ${selectedToneId === tone.id ? "bg-accent border-primary" : ""}`}
                        >
                            <div className="font-medium">{tone.display_name}</div>
                            <div className="text-xs text-muted-foreground truncate">{tone.description}</div>
                        </div>
                    ))}
                </div>

                {/* Main Editor */}
                <div className="md:col-span-9">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex justify-between items-center">
                                <Input
                                    value={formData.display_name}
                                    onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
                                    className="text-xl font-bold border-none shadow-none focus-visible:ring-0 p-0 h-auto w-1/2"
                                />
                                {selectedToneId && selectedToneId !== "new" && !formData.is_system && (
                                    <Button variant="ghost" size="icon" onClick={handleDelete} className="text-destructive">
                                        <Trash2 className="h-4 w-4" />
                                    </Button>
                                )}
                            </CardTitle>
                            <CardDescription>
                                <Input
                                    value={formData.description || ""}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    placeholder="Описание стиля..."
                                    className="border-none shadow-none focus-visible:ring-0 p-0 h-auto text-muted-foreground"
                                />
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-8">

                            {/* Sliders */}
                            <div className="grid gap-6">
                                <div className="space-y-2">
                                    <div className="flex justify-between text-sm">
                                        <Label>Формальность</Label>
                                        <span className="text-muted-foreground">{formData.formality_level}/10</span>
                                    </div>
                                    <Slider
                                        value={[formData.formality_level]}
                                        min={1} max={10} step={1}
                                        onValueChange={(v) => setFormData({ ...formData, formality_level: v[0] })}
                                    />
                                    <div className="flex justify-between text-xs text-muted-foreground">
                                        <span>Свободно</span>
                                        <span>Официально</span>
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <div className="flex justify-between text-sm">
                                        <Label>Дружелюбность</Label>
                                        <span className="text-muted-foreground">{formData.friendliness_level}/10</span>
                                    </div>
                                    <Slider
                                        value={[formData.friendliness_level]}
                                        min={1} max={10} step={1}
                                        onValueChange={(v) => setFormData({ ...formData, friendliness_level: v[0] })}
                                    />
                                    <div className="flex justify-between text-xs text-muted-foreground">
                                        <span>Холодно</span>
                                        <span>Тепло</span>
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <div className="flex justify-between text-sm">
                                        <Label>Детализация</Label>
                                        <span className="text-muted-foreground">{formData.detail_level}/10</span>
                                    </div>
                                    <Slider
                                        value={[formData.detail_level]}
                                        min={1} max={10} step={1}
                                        onValueChange={(v) => setFormData({ ...formData, detail_level: v[0] })}
                                    />
                                    <div className="flex justify-between text-xs text-muted-foreground">
                                        <span>Кратко</span>
                                        <span>Подробно</span>
                                    </div>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-6">
                                <div className="space-y-4">
                                    <div className="flex items-center justify-between">
                                        <Label>Использовать эмодзи ✨</Label>
                                        <Switch
                                            checked={formData.use_emojis}
                                            onCheckedChange={(c) => setFormData({ ...formData, use_emojis: c })}
                                        />
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <Label>На "Вы" (формально)</Label>
                                        <Switch
                                            checked={formData.use_you_formal}
                                            onCheckedChange={(c) => setFormData({ ...formData, use_you_formal: c })}
                                        />
                                    </div>
                                </div>

                                <div className="space-y-4">
                                    <div className="space-y-2">
                                        <Label>Приветствие</Label>
                                        <Select value={formData.greeting_style} onValueChange={(v) => setFormData({ ...formData, greeting_style: v })}>
                                            <SelectTrigger><SelectValue /></SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="formal">Здравствуйте / Уважаемый...</SelectItem>
                                                <SelectItem value="friendly">Добрый день / Привет</SelectItem>
                                                <SelectItem value="brief">Просто имя / Без приветствия</SelectItem>
                                            </SelectContent>
                                        </Select>
                                    </div>
                                    <div className="space-y-2">
                                        <Label>Прощание</Label>
                                        <Select value={formData.closing_style} onValueChange={(v) => setFormData({ ...formData, closing_style: v })}>
                                            <SelectTrigger><SelectValue /></SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="formal">С уважением</SelectItem>
                                                <SelectItem value="friendly">Всего доброго / Хорошего дня</SelectItem>
                                                <SelectItem value="brief">Спасибо / До связи</SelectItem>
                                            </SelectContent>
                                        </Select>
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <Label>Дополнительные инструкции для AI</Label>
                                <Textarea
                                    placeholder="Например: 'Всегда предлагать бесплатную демо-версию', 'Не использовать сложные термины'..."
                                    value={formData.custom_instructions || ""}
                                    onChange={(e) => setFormData({ ...formData, custom_instructions: e.target.value })}
                                    rows={4}
                                />
                            </div>

                        </CardContent>
                        <CardFooter className="flex justify-end gap-2">
                            <Button variant="outline" onClick={() => loadTones()}>
                                <Undo className="mr-2 h-4 w-4" /> Сбросить
                            </Button>
                            <Button onClick={handleSave} disabled={saving}>
                                <Save className="mr-2 h-4 w-4" /> {saving ? "Сохранение..." : "Сохранить изменения"}
                            </Button>
                        </CardFooter>
                    </Card>
                </div>
            </div>
        </div>
    );
}
