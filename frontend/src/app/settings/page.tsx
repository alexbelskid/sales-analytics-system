"use client";

import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Mail, MessageSquare, ArrowRight, UserCog } from "lucide-react";

export default function SettingsPage() {
    return (
        <div className="container mx-auto py-8">
            <h1 className="text-3xl font-bold tracking-tight mb-6">Настройки</h1>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <Link href="/settings/email">
                    <Card className="h-full hover:bg-accent/50 transition-colors cursor-pointer group">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Mail className="h-5 w-5 text-primary" />
                                Подключение почты
                            </CardTitle>
                            <CardDescription>
                                Настройка IMAP/SMTP и интеграций с почтовыми сервисами
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="text-sm text-muted-foreground flex items-center group-hover:text-primary transition-colors">
                                Настроить подключение <ArrowRight className="ml-2 h-4 w-4" />
                            </div>
                        </CardContent>
                    </Card>
                </Link>

                <Link href="/settings/response-tone">
                    <Card className="h-full hover:bg-accent/50 transition-colors cursor-pointer group">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <MessageSquare className="h-5 w-5 text-primary" />
                                Тон ответов
                            </CardTitle>
                            <CardDescription>
                                Настройка стилей общения, приветствий и подписей
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="text-sm text-muted-foreground flex items-center group-hover:text-primary transition-colors">
                                Редактировать тона <ArrowRight className="ml-2 h-4 w-4" />
                            </div>
                        </CardContent>
                    </Card>
                </Link>

                {/* Placeholder for future Profile/Team settings */}
                <Card className="h-full opacity-60">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <UserCog className="h-5 w-5" />
                            Профиль и команда
                        </CardTitle>
                        <CardDescription>
                            Управление пользователями (скоро)
                        </CardDescription>
                    </CardHeader>
                </Card>
            </div>
        </div>
    );
}
